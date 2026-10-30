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

  public List<PrestacionResponse> listar() {
    return prestaciones.findAll().stream()
        .filter(p -> CurrentUser.admin() || p.getActivo())
        .sorted(Comparator.comparing(Prestacion::getNombre))
        .map(this::responsePrestacion)
        .toList();
  }

  public PrestacionResponse guardar(Long id, PrestacionRequest r) {
    Prestacion p =
        id == null
            ? new Prestacion()
            : prestaciones.findById(id).orElseThrow(() -> error(404, "Prestación no encontrada"));
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
    if (r.activo() && (!s.getActivo() || !p.getActivo()))
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
        o.getActivo() && o.getSede().getActivo() && o.getPrestacion().getActivo());
  }

  private ResponseStatusException error(int s, String m) {
    return new ResponseStatusException(HttpStatus.valueOf(s), m);
  }

  private PrestacionResponse responsePrestacion(Prestacion p) {
    return new PrestacionResponse(p.getId(), p.getNombre(), p.getDescripcion(), p.getActivo());
  }
}
