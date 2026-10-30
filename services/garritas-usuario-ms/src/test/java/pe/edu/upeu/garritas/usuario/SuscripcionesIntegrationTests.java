package pe.edu.upeu.garritas.usuario;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.usuario.dto.*;
import pe.edu.upeu.garritas.usuario.repository.*;
import pe.edu.upeu.garritas.usuario.service.*;

@SpringBootTest
@Transactional
class SuscripcionesIntegrationTests {
  @Autowired SuscripcionService service;
  @Autowired UsuarioService usuarios;
  @Autowired SuscripcionRepository repository;

  void auth(String sub) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            new UsernamePasswordAuthenticationToken(
                sub, "", List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  String user() {
    String key = UUID.randomUUID().toString();
    auth(key);
    UsuarioRequest r = new UsuarioRequest();
    r.setNombre("Prueba");
    r.setEmail(key + "@example.test");
    usuarios.guardarMe(r);
    return key;
  }

  @Test
  void contractsRenewsAndDeduplicatesWhilePreservingPriceHistory() {
    user();
    var plan =
        service.guardarPlan(
            null,
            new PlanRequest(
                "Plan " + UUID.randomUUID(), "Prueba", new BigDecimal("25.00"), 30, true));
    UUID key = UUID.randomUUID();
    var s = service.contratar(new SuscripcionRequest(plan.id()), key);
    assertEquals(s.id(), service.contratar(new SuscripcionRequest(plan.id()), key).id());
    assertEquals(1, service.obtener(s.id()).periodos().size());
    service.guardarPlan(
        plan.id(),
        new PlanRequest(plan.nombre(), "Nuevo precio", new BigDecimal("30.00"), 30, true));
    UUID renew = UUID.randomUUID();
    var extended = service.renovar(s.id(), renew);
    assertEquals(2, service.renovar(s.id(), renew).periodos().size());
    assertEquals(new BigDecimal("55.00"), extended.totalContratado());
    assertTrue(extended.fechaFin().isAfter(s.fechaFin()));
    assertThrows(
        org.springframework.web.server.ResponseStatusException.class,
        () -> service.contratar(new SuscripcionRequest(plan.id()), UUID.randomUUID()));
    service.cancelar(s.id());
    assertThrows(
        org.springframework.web.server.ResponseStatusException.class,
        () -> service.renovar(s.id(), UUID.randomUUID()));
  }

  @Test
  void demonstratesSharedPlanAndIsolationBetweenOwners() {
    String first = user();
    var p =
        service.guardarPlan(
            null,
            new PlanRequest("Compartido " + UUID.randomUUID(), "Prueba", BigDecimal.TEN, 30, true));
    var a = service.contratar(new SuscripcionRequest(p.id()), UUID.randomUUID());
    user();
    var b = service.contratar(new SuscripcionRequest(p.id()), UUID.randomUUID());
    assertEquals(a.planId(), b.planId());
    assertNotEquals(a.usuarioId(), b.usuarioId());
    SecurityContextHolder.getContext()
        .setAuthentication(
            new UsernamePasswordAuthenticationToken(
                Current(), "", List.of(new SimpleGrantedAuthority("ROLE_CLIENTE"))));
    assertThrows(
        org.springframework.security.access.AccessDeniedException.class,
        () -> service.obtener(a.id()));
  }

  String Current() {
    return SecurityContextHolder.getContext().getAuthentication().getName();
  }

  @Test
  void canContractAgainAfterExpiryWithoutDuplicateActiveHeader() {
    user();
    var p =
        service.guardarPlan(
            null,
            new PlanRequest("Vence " + UUID.randomUUID(), "Prueba", BigDecimal.TEN, 30, true));
    var s = service.contratar(new SuscripcionRequest(p.id()), UUID.randomUUID());
    var old = repository.findById(s.id()).orElseThrow();
    old.setFechaInicio(Instant.now().minusSeconds(1000));
    old.setFechaFin(Instant.now().minusSeconds(1));
    repository.saveAndFlush(old);
    var next = service.contratar(new SuscripcionRequest(p.id()), UUID.randomUUID());
    assertNotEquals(s.id(), next.id());
    assertEquals("VENCIDA", service.obtener(s.id()).estado());
  }
}
