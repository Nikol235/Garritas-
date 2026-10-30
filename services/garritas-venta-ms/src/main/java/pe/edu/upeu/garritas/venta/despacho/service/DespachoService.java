package pe.edu.upeu.garritas.venta.despacho.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.*;
import pe.edu.upeu.garritas.venta.despacho.dto.*;
import pe.edu.upeu.garritas.venta.despacho.entity.*;
import pe.edu.upeu.garritas.venta.despacho.mapper.DespachoMapper;
import pe.edu.upeu.garritas.venta.despacho.repository.DespachoRepository;

@Service
@RequiredArgsConstructor
@Transactional
public class DespachoService {
  private final DespachoRepository repository;
  private final DespachoMapper mapper;
  private final ServiceClient services;
  private final pe.edu.upeu.garritas.venta.repository.VentaRepository ventas;

  public List<DespachoResponse> listar() {
    return (CurrentUser.admin()
            ? repository.findAll()
            : repository.findByIdCliente(CurrentUser.subject()))
        .stream().map(mapper::toResponse).toList();
  }

  public DespachoResponse obtener(Long id) {
    return mapper.toResponse(owned(id));
  }

  public DespachoResponse crear(DespachoRequest r) {
    var venta =
        ventas
            .findById(r.getIdVenta())
            .orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Venta no encontrada"));
    CurrentUser.requireOwner(venta.getIdCliente());
    if (!"PAGADA".equals(venta.getEstado().name()))
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Solo se puede solicitar envío para una venta pagada");
    Cobertura cobertura =
        services.get(
            "garritas-envio-ms",
            "/api/v1/transportistas/" + r.getTransportistaId() + "/zonas/" + r.getZonaId(),
            Cobertura.class);
    if (!Boolean.TRUE.equals(cobertura.activo()))
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "No existe cobertura activa para esa entrega");
    Despacho e = mapper.toEntity(r);
    e.setZonaId(r.getZonaId());
    e.setTransportistaId(r.getTransportistaId());
    e.setTarifa(cobertura.tarifa());
    e.setTransportista(cobertura.transportista());
    e.setFechaEntregaEstimada(
        java.time.Instant.now()
            .plus(cobertura.diasEstimados(), java.time.temporal.ChronoUnit.DAYS));
    e.setIdCliente(venta.getIdCliente());

    e.setFechaEnvio(null);
    return mapper.toResponse(repository.saveAndFlush(e));
  }

  public DespachoResponse marcarEnTransito(Long id) {
    Despacho e = owned(id);
    if (e.getEstado() != EstadoDespacho.PENDIENTE)
      throw new ResponseStatusException(HttpStatus.CONFLICT, "El envío no está pendiente");
    e.setEstado(EstadoDespacho.EN_TRANSITO);
    e.setFechaEnvio(java.time.Instant.now());
    return mapper.toResponse(repository.save(e));
  }

  public DespachoResponse marcarEntregado(Long id) {
    Despacho e = owned(id);
    if (e.getEstado() != EstadoDespacho.EN_TRANSITO)
      throw new ResponseStatusException(HttpStatus.CONFLICT, "El envío no está en tránsito");
    e.setEstado(EstadoDespacho.ENTREGADO);
    return mapper.toResponse(repository.save(e));
  }

  public DespachoResponse cancelar(Long id) {
    Despacho e = owned(id);
    if (e.getEstado() == EstadoDespacho.ENTREGADO
        || (!CurrentUser.admin() && e.getEstado() == EstadoDespacho.EN_TRANSITO))
      throw new ResponseStatusException(HttpStatus.CONFLICT, "Este envío ya no se puede cancelar");
    e.setEstado(EstadoDespacho.CANCELADO);
    return mapper.toResponse(repository.save(e));
  }

  private record Cobertura(
      Boolean activo, String transportista, java.math.BigDecimal tarifa, int diasEstimados) {}

  private Despacho owned(Long id) {
    Despacho e =
        repository
            .findById(id)
            .orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Envío no encontrado"));
    CurrentUser.requireOwner(e.getIdCliente());
    return e;
  }
}
