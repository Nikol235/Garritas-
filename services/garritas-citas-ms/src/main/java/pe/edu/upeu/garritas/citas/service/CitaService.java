package pe.edu.upeu.garritas.citas.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.citas.dto.*;
import pe.edu.upeu.garritas.citas.entity.*;
import pe.edu.upeu.garritas.citas.mapper.CitaMapper;
import pe.edu.upeu.garritas.citas.repository.CitaRepository;
import pe.edu.upeu.garritas.common.*;

@Service
@RequiredArgsConstructor
@Transactional
public class CitaService {
  private final CitaRepository repository;
  private final CitaMapper mapper;
  private final ServiceClient services;

  public List<CitaResponse> listar() {
    return (CurrentUser.admin()
            ? repository.findAll()
            : repository.findByIdCliente(CurrentUser.subject()))
        .stream()
            .sorted(Comparator.comparing(Cita::getFechaHora).reversed())
            .map(mapper::toResponse)
            .toList();
  }

  public CitaResponse obtener(Long id) {
    return mapper.toResponse(owned(id));
  }

  public CitaResponse crear(CitaRequest r) {
    if (r.getFechaHora().getEpochSecond() % 1800 != 0 || r.getFechaHora().getNano() != 0)
      throw new ResponseStatusException(
          HttpStatus.BAD_REQUEST, "Selecciona un horario en intervalos de 30 minutos");
    Reference mascota =
        services.get(
            "garritas-usuario-ms",
            "/api/v1/usuarios/me/mascotas/" + r.getIdMascota(),
            Reference.class);
    Reference sede =
        services.get("garritas-institucion-ms", "/api/v1/sedes/" + r.getIdSede(), Reference.class);
    Reference profesional =
        services.get(
            "garritas-bienestar-ms",
            "/api/v1/especialistas/" + r.getProfesionalId(),
            Reference.class);
    if (!Boolean.TRUE.equals(sede.activo())
        || !Boolean.TRUE.equals(profesional.activo())
        || (profesional.sedeId() != null && !profesional.sedeId().equals(r.getIdSede())))
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Sede o profesional no disponible para esta cita");
    Cita c = mapper.toEntity(r);
    c.setNombreMascota(mascota.nombre());
    c.setNombreSede(sede.nombre());
    c.setNombreProfesional(profesional.nombre());
    return mapper.toResponse(repository.saveAndFlush(c));
  }

  public CitaResponse confirmar(Long id) {
    return transition(id, EstadoCita.CONFIRMADA, EstadoCita.PROGRAMADA);
  }

  public CitaResponse atender(Long id) {
    return transition(id, EstadoCita.ATENDIDA, EstadoCita.CONFIRMADA);
  }

  public CitaResponse cancelar(Long id) {
    Cita c = owned(id);
    if (c.getEstado() == EstadoCita.ATENDIDA)
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Una cita atendida no se puede cancelar");
    c.setEstado(EstadoCita.CANCELADA);
    return mapper.toResponse(repository.save(c));
  }

  private CitaResponse transition(Long id, EstadoCita next, EstadoCita expected) {
    Cita c = owned(id);
    if (c.getEstado() != expected && c.getEstado() != next)
      throw new ResponseStatusException(HttpStatus.CONFLICT, "Transición de cita no permitida");
    c.setEstado(next);
    return mapper.toResponse(repository.save(c));
  }

  private Cita owned(Long id) {
    Cita c =
        repository
            .findById(id)
            .orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Cita no encontrada"));
    CurrentUser.requireOwner(c.getIdCliente());
    return c;
  }
}
