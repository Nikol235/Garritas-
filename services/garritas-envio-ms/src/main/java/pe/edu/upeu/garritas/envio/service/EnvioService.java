package pe.edu.upeu.garritas.envio.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.*;
import pe.edu.upeu.garritas.envio.dto.*;
import pe.edu.upeu.garritas.envio.entity.*;
import pe.edu.upeu.garritas.envio.mapper.EnvioMapper;
import pe.edu.upeu.garritas.envio.repository.EnvioRepository;

@Service
@RequiredArgsConstructor
@Transactional
public class EnvioService {
  private final EnvioRepository repository;
  private final EnvioMapper mapper;
  private final ServiceClient services;

  public List<EnvioResponse> listar() {
    return (CurrentUser.admin()
            ? repository.findAll()
            : repository.findByIdCliente(CurrentUser.subject()))
        .stream().map(mapper::toResponse).toList();
  }

  public EnvioResponse obtener(Long id) {
    return mapper.toResponse(owned(id));
  }

  public EnvioResponse crear(EnvioRequest r) {
    Reference venta =
        services.get("garritas-venta-ms", "/api/v1/ventas/" + r.getIdVenta(), Reference.class);
    if (!"PAGADA".equals(venta.estado()))
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Solo se puede solicitar envío para una venta pagada");
    CurrentUser.requireOwner(venta.idCliente());
    Envio e = mapper.toEntity(r);
    e.setIdCliente(venta.idCliente());
    if (!CurrentUser.admin()) e.setTransportista("Por asignar");
    e.setFechaEnvio(null);
    return mapper.toResponse(repository.saveAndFlush(e));
  }

  public EnvioResponse marcarEnTransito(Long id) {
    Envio e = owned(id);
    if (e.getEstado() != EstadoEnvio.PENDIENTE)
      throw new ResponseStatusException(HttpStatus.CONFLICT, "El envío no está pendiente");
    e.setEstado(EstadoEnvio.EN_TRANSITO);
    e.setFechaEnvio(java.time.Instant.now());
    return mapper.toResponse(repository.save(e));
  }

  public EnvioResponse marcarEntregado(Long id) {
    Envio e = owned(id);
    if (e.getEstado() != EstadoEnvio.EN_TRANSITO)
      throw new ResponseStatusException(HttpStatus.CONFLICT, "El envío no está en tránsito");
    e.setEstado(EstadoEnvio.ENTREGADO);
    return mapper.toResponse(repository.save(e));
  }

  public EnvioResponse cancelar(Long id) {
    Envio e = owned(id);
    if (e.getEstado() == EstadoEnvio.ENTREGADO
        || (!CurrentUser.admin() && e.getEstado() == EstadoEnvio.EN_TRANSITO))
      throw new ResponseStatusException(HttpStatus.CONFLICT, "Este envío ya no se puede cancelar");
    e.setEstado(EstadoEnvio.CANCELADO);
    return mapper.toResponse(repository.save(e));
  }

  private Envio owned(Long id) {
    Envio e =
        repository
            .findById(id)
            .orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Envío no encontrado"));
    CurrentUser.requireOwner(e.getIdCliente());
    return e;
  }
}
