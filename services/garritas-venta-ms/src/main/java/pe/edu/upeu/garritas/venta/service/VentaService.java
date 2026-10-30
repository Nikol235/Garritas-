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
  private final pe.edu.upeu.garritas.venta.client.LogisticaConsulta logistica;
  private final Outbox outbox;
  private final JdbcTemplate jdbc;
  private final ServiceClient services;

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
    if (CurrentUser.admin())
      throw new org.springframework.security.access.AccessDeniedException(
          "El administrador gestiona la tienda; utiliza una cuenta de cliente para comprar");
    validarEntrega(request);
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
      if (!Objects.equals(old.getSedeId(), request.getSedeId())
          || !old.getMetodoPago().equals(request.getMetodoPago())
          || !original.equals(incoming)
          || !Objects.equals(old.getTipoEntrega(), request.getTipoEntrega())
          || !Objects.equals(old.getZonaId(), request.getZonaId())
          || !Objects.equals(old.getTransportistaId(), request.getTransportistaId())
          || !Objects.equals(old.getDireccionEntrega(), direccion(request)))
        throw new ResponseStatusException(
            HttpStatus.CONFLICT, "Idempotency-Key ya utilizado con otros datos");
      return mapper.toResponse(old);
    }
    Reference sede =
        services.get(
            "garritas-institucion-ms", "/api/v1/sedes/" + request.getSedeId(), Reference.class);
    if (!Boolean.TRUE.equals(sede.activo()))
      throw new ResponseStatusException(HttpStatus.CONFLICT, "La sede no está disponible");
    var quantities = new TreeMap<Long, Integer>();
    request
        .getDetalles()
        .forEach(d -> quantities.merge(d.getIdProducto(), d.getCantidad(), Math::addExact));
    Venta venta =
        Venta.builder()
            .idCliente(owner)
            .sedeId(request.getSedeId())
            .idempotencyKey(key)
            .metodoPago(request.getMetodoPago())
            .fecha(Instant.now())
            .estado(EstadoVenta.PENDIENTE_STOCK)
            .total(BigDecimal.ZERO)
            .build();
    venta.setTipoEntrega(request.getTipoEntrega());
    if ("ENVIO".equals(request.getTipoEntrega())) {
      var cobertura = logistica.obtener(request.getTransportistaId(), request.getZonaId());
      if (!Boolean.TRUE.equals(cobertura.activo())
          || cobertura.tarifa() == null
          || cobertura.tarifa().signum() < 0
          || cobertura.diasEstimados() < 1)
        throw new ResponseStatusException(HttpStatus.CONFLICT, "Cobertura no disponible");
      if (cobertura.tarifa().compareTo(request.getTarifaCotizada()) != 0)
        throw new ResponseStatusException(
            HttpStatus.CONFLICT,
            "La tarifa de envío cambió. Actualiza las opciones y confirma el nuevo total");
      venta.setCostoEnvio(cobertura.tarifa());
      venta.setDireccionEntrega(direccion(request));
      venta.setZonaId(request.getZonaId());
      venta.setTransportistaId(request.getTransportistaId());
      venta.setTransportistaNombre(cobertura.transportista());
      venta.setDiasEntrega(cobertura.diasEstimados());
    }
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
    venta.setTotal(venta.getTotal().add(venta.getCostoEnvio()));
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

  private static String direccion(VentaRequest r) {
    return r.getDireccionEntrega() == null ? null : r.getDireccionEntrega().strip();
  }

  private void validarEntrega(VentaRequest r) {
    if ("ENVIO".equals(r.getTipoEntrega())) {
      if (r.getZonaId() == null
          || r.getTransportistaId() == null
          || r.getTarifaCotizada() == null
          || direccion(r) == null
          || direccion(r).length() < 10)
        throw new ResponseStatusException(
            HttpStatus.BAD_REQUEST,
            "Selecciona zona, transportista y una dirección de al menos 10 caracteres");
    } else if (r.getZonaId() != null
        || r.getTransportistaId() != null
        || r.getDireccionEntrega() != null
        || r.getTarifaCotizada() != null)
      throw new ResponseStatusException(
          HttpStatus.BAD_REQUEST, "El recojo en sede no lleva datos ni cargos de envío");
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
