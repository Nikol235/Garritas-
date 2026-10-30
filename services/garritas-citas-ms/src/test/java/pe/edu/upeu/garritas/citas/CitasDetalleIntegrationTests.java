package pe.edu.upeu.garritas.citas;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.citas.dto.*;
import pe.edu.upeu.garritas.citas.service.*;
import pe.edu.upeu.garritas.common.*;

@SpringBootTest
@Transactional
class CitasDetalleIntegrationTests {
  @Autowired CitaService service;
  @MockitoBean ServiceClient remote;

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

  @Test
  void snapshotsDetailsAndRejectsOverlappingAppointments() {
    auth("cita-prueba");
    long pro = Math.abs(UUID.randomUUID().getMostSignificantBits() % 1000000000L) + 1000000000L;
    when(remote.get("garritas-usuario-ms", "/api/v1/usuarios/me/mascotas/1", Reference.class))
        .thenReturn(new Reference(1L, "Luna", null, null, null, null));
    when(remote.get("garritas-institucion-ms", "/api/v1/sedes/1", Reference.class))
        .thenReturn(new Reference(1L, "Lima", true, null, null, null));
    when(remote.get("garritas-bienestar-ms", "/api/v1/especialistas/" + pro, Reference.class))
        .thenReturn(new Reference(pro, "Dra. Prueba", true, null, null, null));
    when(remote.get(
            "garritas-institucion-ms", "/api/v1/sedes/1/prestaciones", OfertaReferencia[].class))
        .thenReturn(
            new OfertaReferencia[] {
              new OfertaReferencia(1L, "Consulta", new BigDecimal("60.00"), 60, true),
              new OfertaReferencia(2L, "Vacuna", new BigDecimal("40.00"), 30, true)
            });
    long slot = (Instant.now().getEpochSecond() / 1800 + 1000) * 1800;
    CitaRequest r = new CitaRequest();
    r.setIdMascota(1L);
    r.setIdSede(1L);
    r.setProfesionalId(pro);
    r.setMotivo("Prueba cabecera detalle");
    r.setFechaHora(Instant.ofEpochSecond(slot));
    r.setPrestacionIds(List.of(1L, 2L));
    var c = service.crear(r);
    assertEquals(2, c.getDetalles().size());
    assertEquals(new BigDecimal("100.00"), c.getTotal());
    assertEquals(90, c.getDuracionMinutos());
    r.setFechaHora(Instant.ofEpochSecond(slot + 1800));
    assertThrows(
        org.springframework.web.server.ResponseStatusException.class, () -> service.crear(r));
    service.cancelar(c.getId());
    assertNotNull(service.crear(r).getId());
  }
}
