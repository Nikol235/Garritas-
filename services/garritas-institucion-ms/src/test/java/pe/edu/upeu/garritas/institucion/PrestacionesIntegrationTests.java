package pe.edu.upeu.garritas.institucion;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.institucion.dto.*;
import pe.edu.upeu.garritas.institucion.entity.*;
import pe.edu.upeu.garritas.institucion.repository.*;
import pe.edu.upeu.garritas.institucion.service.*;

@SpringBootTest
@Transactional
class PrestacionesIntegrationTests {
  @Autowired PrestacionService service;
  @Autowired SedeRepository sedes;

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

  Sede sede(String n) {
    Sede s =
        Sede.builder()
            .nombre(n)
            .direccion("Dirección de prueba")
            .ciudad("Lima")
            .activo(true)
            .build();
    return sedes.saveAndFlush(s);
  }

  @Test
  void sharesPrestacionesAcrossSedesWithoutDuplicatingAssociation() {
    auth("prueba");
    var a = sede("Sede A");
    var b = sede("Sede B");
    var p =
        service.guardar(
            null, new PrestacionRequest("Prestación " + UUID.randomUUID(), "Test", true));
    var r = new OfertaRequest(p.id(), new BigDecimal("60.00"), 30, true);
    var first = service.guardarOferta(a.getId(), r);
    service.guardarOferta(b.getId(), r);
    var changed =
        service.guardarOferta(
            a.getId(), new OfertaRequest(p.id(), new BigDecimal("75.00"), 60, true));
    assertEquals(first.id(), changed.id());
    assertEquals(1, service.ofertas(a.getId()).size());
    assertEquals(1, service.ofertas(b.getId()).size());
    service.desactivar(p.id());
    assertFalse(service.ofertas(a.getId()).getFirst().activo());
  }

  @Test
  void rejectsNonSchedulingDuration() {
    auth("prueba");
    var s = sede("Sede C");
    var p = service.guardar(null, new PrestacionRequest("P " + UUID.randomUUID(), "Test", true));
    assertThrows(
        org.springframework.web.server.ResponseStatusException.class,
        () ->
            service.guardarOferta(s.getId(), new OfertaRequest(p.id(), BigDecimal.ONE, 45, true)));
  }
}
