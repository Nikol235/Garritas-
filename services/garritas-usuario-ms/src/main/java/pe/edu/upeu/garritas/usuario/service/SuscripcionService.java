package pe.edu.upeu.garritas.usuario.service;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.CurrentUser;
import pe.edu.upeu.garritas.usuario.dto.*;
import pe.edu.upeu.garritas.usuario.entity.*;
import pe.edu.upeu.garritas.usuario.repository.*;

@Service
@RequiredArgsConstructor
@Transactional
public class SuscripcionService {
  private final PlanRepository planes;
  private final SuscripcionRepository suscripciones;
  private final PeriodoSuscripcionRepository periodos;
  private final UsuarioService usuarios;
  private final JdbcTemplate jdbc;

  public List<PlanResponse> planes() {
    return planes.findAll().stream()
        .filter(p -> CurrentUser.admin() || p.getActivo())
        .sorted(Comparator.comparing(Plan::getNombre))
        .map(this::responsePlan)
        .toList();
  }

  public PlanResponse guardarPlan(Long id, PlanRequest r) {
    Plan p = id == null ? new Plan() : plan(id);
    p.setNombre(r.nombre().strip());
    p.setDescripcion(r.descripcion());
    p.setPrecio(r.precio());
    p.setDuracionDias(r.duracionDias());
    p.setActivo(r.activo());
    return responsePlan(planes.saveAndFlush(p));
  }

  public void desactivarPlan(Long id) {
    plan(id).setActivo(false);
  }

  public List<SuscripcionResponse> listar() {
    return (CurrentUser.admin()
            ? suscripciones.findAll()
            : suscripciones.findByUsuarioIdOrderByIdDesc(usuarios.miUsuario().getId()))
        .stream()
            .sorted(Comparator.comparing(Suscripcion::getId).reversed())
            .map(this::response)
            .toList();
  }

  public SuscripcionResponse obtener(Long id) {
    return response(owned(id));
  }

  public SuscripcionResponse contratar(SuscripcionRequest r, UUID key) {
    if (CurrentUser.admin())
      throw new org.springframework.security.access.AccessDeniedException(
          "Utiliza una cuenta de cliente para contratar un plan");
    Usuario u = usuarios.miUsuario();
    lock(u, key);
    var old = periodos.findByUsuarioIdAndIdempotencyKey(u.getId(), key);
    if (old.isPresent()) {
      var p = old.get();
      if (!p.getTipo().equals("ALTA") || !p.getSuscripcion().getPlan().getId().equals(r.planId()))
        throw error(409, "La clave de reintento ya corresponde a otra operación");
      return response(p.getSuscripcion());
    }
    Plan p = plan(r.planId());
    if (!p.getActivo()) throw error(409, "El plan no está disponible");
    for (Suscripcion active :
        suscripciones.findByUsuarioIdAndPlanIdAndEstado(u.getId(), p.getId(), "ACTIVA")) {
      if (active.getFechaFin().isAfter(Instant.now()))
        throw error(409, "Ya tienes este plan activo; utiliza Renovar");
      active.setEstado("VENCIDA");
    }
    suscripciones.flush();
    Suscripcion s = new Suscripcion();
    s.setUsuario(u);
    s.setPlan(p);
    s.setNombrePlan(p.getNombre());
    s.setEstado("ACTIVA");
    s.setFechaInicio(Instant.now());
    s.setFechaFin(s.getFechaInicio().plus(p.getDuracionDias(), ChronoUnit.DAYS));
    suscripciones.saveAndFlush(s);
    addPeriod(s, key, "ALTA", s.getFechaInicio(), s.getFechaFin(), p.getPrecio());
    return response(s);
  }

  public SuscripcionResponse renovar(Long id, UUID key) {
    Suscripcion s = owned(id);
    Usuario u = s.getUsuario();
    lock(u, key);
    suscripciones.flush(); // reload after the owner lock to avoid a stale period end
    jakarta.persistence.EntityManager em = entityManager;
    em.refresh(s);
    var old = periodos.findByUsuarioIdAndIdempotencyKey(u.getId(), key);
    if (old.isPresent()) {
      var p = old.get();
      if (!p.getTipo().equals("RENOVACION") || !p.getSuscripcion().getId().equals(id))
        throw error(409, "La clave de reintento ya corresponde a otra operación");
      return response(s);
    }
    if (s.getEstado().equals("CANCELADA"))
      throw error(409, "Una suscripción cancelada no se renueva");
    Plan p = s.getPlan();
    if (!p.getActivo()) throw error(409, "El plan ya no está disponible");
    var other = suscripciones.findByUsuarioIdAndPlanIdAndEstado(u.getId(), p.getId(), "ACTIVA");
    if (other.stream()
        .anyMatch(x -> !x.getId().equals(id) && x.getFechaFin().isAfter(Instant.now())))
      throw error(409, "Ya existe otra suscripción activa para el plan");
    other.stream()
        .filter(x -> !x.getId().equals(id) && !x.getFechaFin().isAfter(Instant.now()))
        .forEach(x -> x.setEstado("VENCIDA"));
    suscripciones.flush();
    Instant start = s.getFechaFin().isAfter(Instant.now()) ? s.getFechaFin() : Instant.now();
    Instant end = start.plus(p.getDuracionDias(), ChronoUnit.DAYS);
    s.setFechaFin(end);
    s.setEstado("ACTIVA");
    addPeriod(s, key, "RENOVACION", start, end, p.getPrecio());
    return response(s);
  }

  private final jakarta.persistence.EntityManager entityManager;

  public SuscripcionResponse cancelar(Long id) {
    Suscripcion s = owned(id);
    jdbc.queryForObject("SELECT pg_advisory_xact_lock(?)", Object.class, s.getUsuario().getId());
    entityManager.refresh(s);
    s.setEstado("CANCELADA");
    return response(suscripciones.saveAndFlush(s));
  }

  private void lock(Usuario u, UUID key) {
    jdbc.queryForObject(
        "SELECT pg_advisory_xact_lock(hashtextextended(?,0))", Object.class, u.getId() + ":" + key);
    jdbc.queryForObject("SELECT pg_advisory_xact_lock(?)", Object.class, u.getId());
  }

  private void addPeriod(
      Suscripcion s, UUID key, String tipo, Instant start, Instant end, BigDecimal precio) {
    PeriodoSuscripcion p = new PeriodoSuscripcion();
    p.setSuscripcion(s);
    p.setUsuario(s.getUsuario());
    p.setIdempotencyKey(key);
    p.setTipo(tipo);
    p.setFechaInicio(start);
    p.setFechaFin(end);
    p.setPrecio(precio);
    periodos.saveAndFlush(p);
    s.getPeriodos().add(p);
    suscripciones.saveAndFlush(s);
  }

  private Plan plan(Long id) {
    return planes.findById(id).orElseThrow(() -> error(404, "Plan no encontrado"));
  }

  private Suscripcion owned(Long id) {
    Suscripcion s =
        suscripciones.findById(id).orElseThrow(() -> error(404, "Suscripción no encontrada"));
    CurrentUser.requireOwner(s.getUsuario().getSubject());
    return s;
  }

  private SuscripcionResponse response(Suscripcion s) {
    return new SuscripcionResponse(
        s.getId(),
        s.getUsuario().getId(),
        s.getUsuario().getNombre(),
        s.getPlan().getId(),
        s.getNombrePlan(),
        s.getEstado().equals("ACTIVA") && !s.getFechaFin().isAfter(Instant.now())
            ? "VENCIDA"
            : s.getEstado(),
        s.getFechaInicio(),
        s.getFechaFin(),
        s.getPeriodos().stream()
            .map(PeriodoSuscripcion::getPrecio)
            .reduce(BigDecimal.ZERO, BigDecimal::add),
        s.getPeriodos().stream()
            .map(
                p ->
                    new SuscripcionResponse.PeriodoResponse(
                        p.getId(), p.getTipo(), p.getFechaInicio(), p.getFechaFin(), p.getPrecio()))
            .toList());
  }

  private ResponseStatusException error(int code, String msg) {
    return new ResponseStatusException(HttpStatus.valueOf(code), msg);
  }

  private PlanResponse responsePlan(Plan p) {
    return new PlanResponse(
        p.getId(),
        p.getNombre(),
        p.getDescripcion(),
        p.getPrecio(),
        p.getDuracionDias(),
        p.getActivo());
  }
}
