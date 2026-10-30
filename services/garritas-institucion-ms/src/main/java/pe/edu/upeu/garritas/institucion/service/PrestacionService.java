package pe.edu.upeu.garritas.institucion.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.CurrentUser;
import pe.edu.upeu.garritas.institucion.dto.*;
import pe.edu.upeu.garritas.institucion.entity.*;
import pe.edu.upeu.garritas.institucion.repository.*;

@Service
@RequiredArgsConstructor
@Transactional
public class PrestacionService {
  private final PrestacionRepository prestaciones;
  private final SedeRepository sedes;
  private final SedePrestacionRepository ofertas;
  private final org.springframework.jdbc.core.JdbcTemplate jdbc;

  public List<PrestacionResponse> listar() {
    return prestaciones.findAll().stream()
        .filter(p -> CurrentUser.admin() || disponible(p))
        .sorted(Comparator.comparing(Prestacion::getNombre))
        .map(this::responsePrestacion)
        .toList();
  }

  public PrestacionResponse guardar(Long id, PrestacionRequest r) {
    // Serialize graph edits across replicas so concurrent requests cannot introduce nested
    // packages.
    jdbc.queryForObject(
        "SELECT pg_advisory_xact_lock(hashtextextended(?,0))", Object.class, "garritas:paquetes");
    Prestacion p =
        id == null
            ? new Prestacion()
            : prestaciones.findById(id).orElseThrow(() -> error(404, "Prestación no encontrada"));
    var ids = r.componenteIds() == null ? java.util.Set.<Long>of() : r.componenteIds();
    if (!ids.isEmpty()) {
      if (ids.size() < 2) throw error(400, "Un paquete necesita al menos dos servicios distintos");
      if (id != null && ids.contains(id))
        throw error(400, "Un paquete no puede incluirse a sí mismo");
      var componentes = new java.util.HashSet<>(prestaciones.findAllById(ids));
      if (componentes.size() != ids.size())
        throw error(400, "Uno de los servicios del paquete no existe");
      if (componentes.stream().anyMatch(x -> !x.getActivo() || !x.getComponentes().isEmpty()))
        throw error(
            409,
            "Selecciona servicios individuales activos; no se permiten paquetes dentro de"
                + " paquetes");
      if (id != null
          && jdbc.queryForObject(
                  "SELECT count(*) FROM prestacion_componentes WHERE id_componente=?",
                  Long.class,
                  id)
              > 0) throw error(409, "Este servicio ya forma parte de otro paquete");
      p.setComponentes(componentes);
    } else {
      p.getComponentes().clear();
    }
    p.setNombre(r.nombre().strip());
    p.setDescripcion(r.descripcion());
    p.setActivo(r.activo());
    return responsePrestacion(prestaciones.saveAndFlush(p));
  }

  public void desactivar(Long id) {
    Prestacion p =
        prestaciones.findById(id).orElseThrow(() -> error(404, "Prestación no encontrada"));
    p.setActivo(false);
  }

  public List<OfertaResponse> ofertas(Long sede) {
    Sede s = sedes.findById(sede).orElseThrow(() -> error(404, "Sede no encontrada"));
    if (!s.getActivo() && !CurrentUser.admin()) throw error(404, "Sede no disponible");
    return ofertas.findBySedeId(sede).stream()
        .map(this::response)
        .filter(o -> CurrentUser.admin() || o.activo())
        .toList();
  }

  public OfertaResponse guardarOferta(Long sede, OfertaRequest r) {
    if (r.duracionMinutos() % 30 != 0)
      throw error(400, "La duración debe ser múltiplo de 30 minutos");
    Sede s = sedes.findById(sede).orElseThrow(() -> error(404, "Sede no encontrada"));
    Prestacion p =
        prestaciones
            .findById(r.prestacionId())
            .orElseThrow(() -> error(404, "Prestación no encontrada"));
    if (r.activo() && (!s.getActivo() || !disponible(p)))
      throw error(409, "Activa la sede y la prestación antes de ofrecerla");
    SedePrestacion o =
        ofertas.findBySedeIdAndPrestacionId(sede, p.getId()).orElseGet(SedePrestacion::new);
    o.setSede(s);
    o.setPrestacion(p);
    o.setPrecio(r.precio());
    o.setDuracionMinutos(r.duracionMinutos());
    o.setActivo(r.activo());
    return response(ofertas.saveAndFlush(o));
  }

  private OfertaResponse response(SedePrestacion o) {
    return new OfertaResponse(
        o.getId(),
        o.getSede().getId(),
        o.getPrestacion().getId(),
        o.getPrestacion().getNombre(),
        o.getPrecio(),
        o.getDuracionMinutos(),
        o.getActivo() && o.getSede().getActivo() && disponible(o.getPrestacion()),
        componentes(o.getPrestacion()));
  }

  private boolean disponible(Prestacion p) {
    return p.getActivo() && p.getComponentes().stream().allMatch(Prestacion::getActivo);
  }

  private java.util.List<ComponenteResponse> componentes(Prestacion p) {
    return p.getComponentes().stream()
        .sorted(java.util.Comparator.comparing(Prestacion::getId))
        .map(x -> new ComponenteResponse(x.getId(), x.getNombre()))
        .toList();
  }

  private ResponseStatusException error(int s, String m) {
    return new ResponseStatusException(HttpStatus.valueOf(s), m);
  }

  private PrestacionResponse responsePrestacion(Prestacion p) {
    return new PrestacionResponse(
        p.getId(), p.getNombre(), p.getDescripcion(), disponible(p), componentes(p));
  }
}
