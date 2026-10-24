package pe.edu.upeu.garritas.bienestar.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.bienestar.dto.*;
import pe.edu.upeu.garritas.bienestar.entity.*;
import pe.edu.upeu.garritas.bienestar.repository.*;
import pe.edu.upeu.garritas.common.*;

@Service
@RequiredArgsConstructor
@Transactional
public class BienestarService {
  private final ProfesionalRepository profesionales;
  private final EspecialidadRepository especialidades;
  private final ServiceClient services;

  public List<ProfesionalResponse> listar() {
    return profesionales.findAll().stream()
        .filter(p -> CurrentUser.admin() || p.getActivo())
        .sorted(Comparator.comparing(Profesional::getNombre))
        .map(this::response)
        .toList();
  }

  public ProfesionalResponse obtener(Long id) {
    Profesional p = profesional(id);
    if (!p.getActivo() && !CurrentUser.admin())
      throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Profesional no disponible");
    return response(p);
  }

  public ProfesionalResponse guardar(Long id, ProfesionalRequest r) {
    if (r.sedeId() != null) {
      Reference sede =
          services.get("garritas-institucion-ms", "/api/v1/sedes/" + r.sedeId(), Reference.class);
      if (!Boolean.TRUE.equals(sede.activo()))
        throw new ResponseStatusException(HttpStatus.CONFLICT, "La sede no está activa");
    }
    Set<Long> ids = new HashSet<>(r.especialidadIds());
    List<Especialidad> found = especialidades.findAllById(ids);
    if (found.size() != ids.size() || found.stream().anyMatch(e -> !e.getActivo()))
      throw new ResponseStatusException(
          HttpStatus.BAD_REQUEST, "Selecciona especialidades existentes y activas");
    Profesional p = id == null ? new Profesional() : profesional(id);
    p.setNombre(r.nombre().trim());
    p.setEmail(r.email().trim().toLowerCase());
    p.setTelefono(r.telefono());
    p.setSedeId(r.sedeId());
    p.setActivo(r.activo());
    p.setEspecialidades(new HashSet<>(found));
    return response(profesionales.saveAndFlush(p));
  }

  public void eliminar(Long id) {
    Profesional p = profesional(id);
    p.setActivo(false);
    profesionales.save(p);
  }

  public List<Especialidad> especialidades() {
    return especialidades.findAll().stream()
        .filter(e -> CurrentUser.admin() || e.getActivo())
        .sorted(Comparator.comparing(Especialidad::getNombre))
        .toList();
  }

  public Especialidad guardarEspecialidad(Long id, EspecialidadRequest r) {
    Especialidad e =
        id == null
            ? new Especialidad()
            : especialidades
                .findById(id)
                .orElseThrow(
                    () ->
                        new ResponseStatusException(
                            HttpStatus.NOT_FOUND, "Especialidad no encontrada"));
    e.setNombre(r.nombre().trim());
    e.setDescripcion(r.descripcion());
    e.setActivo(r.activo());
    return especialidades.saveAndFlush(e);
  }

  public void eliminarEspecialidad(Long id) {
    Especialidad e =
        especialidades
            .findById(id)
            .orElseThrow(
                () ->
                    new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Especialidad no encontrada"));
    if (profesionales.countByEspecialidades_Id(id) > 0)
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Primero quita la especialidad de sus profesionales");
    especialidades.delete(e);
  }

  private Profesional profesional(Long id) {
    return profesionales
        .findById(id)
        .orElseThrow(
            () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Profesional no encontrado"));
  }

  private ProfesionalResponse response(Profesional p) {
    return new ProfesionalResponse(
        p.getId(),
        p.getNombre(),
        p.getEmail(),
        p.getTelefono(),
        p.getSedeId(),
        p.getActivo(),
        p.getEspecialidades().stream()
            .sorted(Comparator.comparing(Especialidad::getNombre))
            .toList());
  }
}
