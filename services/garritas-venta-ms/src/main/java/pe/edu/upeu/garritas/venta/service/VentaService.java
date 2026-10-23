package pe.edu.upeu.garritas.venta.service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.*;
import pe.edu.upeu.garritas.venta.client.CatalogoConsulta;
import pe.edu.upeu.garritas.venta.dto.*;
import pe.edu.upeu.garritas.venta.entity.*;
import pe.edu.upeu.garritas.venta.mapper.VentaMapper;
import pe.edu.upeu.garritas.venta.repository.VentaRepository;

@Service
@RequiredArgsConstructor
public class VentaService {
  private final VentaRepository repository;
  private final VentaMapper mapper;
  private final CatalogoConsulta catalogo;
  private final Outbox outbox;
  private final JdbcTemplate jdbc;

  @Transactional(readOnly = true)
  public List<VentaResponse> listar() {
    var ventas =
        CurrentUser.admin()
            ? repository.findAll()
            : repository.findByIdCliente(CurrentUser.subject());
    return ventas.stream()
        .sorted(Comparator.comparing(Venta::getFecha).reversed())
        .map(mapper::toResponse)
        .toList();
  }

  @Transactional(readOnly = true)
  public VentaResponse obtener(Long id) {
    return mapper.toResponse(owned(id));
  }

  @Transactional
  public VentaResponse crear(VentaRequest request, UUID key) {
    String owner = CurrentUser.subject();
    // Serialize equal request keys across instances without holding a distributed transaction.
    jdbc.queryForObject(
        "SELECT pg_advisory_xact_lock(hashtextextended(?,0))", Object.class, owner + ":" + key);
    var existing = repository.findByIdClienteAndIdempotencyKey(owner, key);
    if (existing.isPresent()) {
      Venta old = existing.get();
      var original = new TreeMap<Long, Integer>();
      old.getDetalles()
          .forEach(d -> original.merge(d.getIdProducto(), d.getCantidad(), Integer::sum));
      var incoming = new TreeMap<Long, Integer>();
      request
          .getDetalles()
          .forEach(d -> incoming.merge(d.getIdProducto(), d.getCantidad(), Integer::sum));
      if (!old.getMetodoPago().equals(request.getMetodoPago()) || !original.equals(incoming))
        throw new ResponseStatusException(
            HttpStatus.CONFLICT, "Idempotency-Key ya utilizado con otros datos");
      return mapper.toResponse(old);
    }
    var quantities = new TreeMap<Long, Integer>();
    request
        .getDetalles()
        .forEach(d -> quantities.merge(d.getIdProducto(), d.getCantidad(), Math::addExact));
    Venta venta =
        Venta.builder()
            .idCliente(owner)
            .idempotencyKey(key)
            .metodoPago(request.getMetodoPago())
            .fecha(Instant.now())
            .estado(EstadoVenta.PENDIENTE_STOCK)
            .total(BigDecimal.ZERO)
            .build();
    for (var item : quantities.entrySet()) {
      var producto = catalogo.obtener(item.getKey());
      if (!Boolean.TRUE.equals(producto.activo()) || producto.stock() < item.getValue())
        throw new ResponseStatusException(
            HttpStatus.CONFLICT, "Producto inactivo o stock insuficiente: " + item.getKey());
      var subtotal = producto.precio().multiply(BigDecimal.valueOf(item.getValue()));
      venta
          .getDetalles()
          .add(
              DetalleVenta.builder()
                  .venta(venta)
                  .idProducto(item.getKey())
                  .cantidad(item.getValue())
                  .precioUnitario(producto.precio())
                  .subtotal(subtotal)
                  .build());
      venta.setTotal(venta.getTotal().add(subtotal));
    }
    if (venta.getTotal().signum() <= 0
        || venta.getTotal().compareTo(new BigDecimal("99999999.99")) > 0)
      throw new ResponseStatusException(
          HttpStatus.UNPROCESSABLE_CONTENT, "Total fuera del rango permitido");
    repository.saveAndFlush(venta);
    outbox.append(
        new SagaEvent(
            UUID.randomUUID(),
            1,
            "venta.creada",
            venta.getId(),
            owner,
            venta.getTotal(),
            venta.getMetodoPago(),
            Optional.ofNullable(MDC.get("traceId")).orElseGet(() -> UUID.randomUUID().toString()),
            venta.getDetalles().stream()
                .map(
                    d ->
                        new SagaEvent.Item(
                            d.getIdProducto(), d.getCantidad(), d.getPrecioUnitario()))
                .toList(),
            Instant.now()));
    return mapper.toResponse(venta);
  }

  private Venta owned(Long id) {
    Venta v =
        repository
            .findById(id)
            .orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Venta no encontrada"));
    CurrentUser.requireOwner(v.getIdCliente());
    return v;
  }
}
