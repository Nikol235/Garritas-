package pe.edu.upeu.garritas.envio;

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
import pe.edu.upeu.garritas.envio.dto.*;
import pe.edu.upeu.garritas.envio.service.*;

@SpringBootTest
@Transactional
class LogisticaIntegrationTests {
  @Autowired LogisticaService service;

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
  void supportsManyCarriersManyZonesAndSoftDeactivation() {
    auth("prueba");
    String key = UUID.randomUUID().toString();
    var a = service.guardarTransportista(null, new TransportistaRequest("T1 " + key, "999", true));
    var b = service.guardarTransportista(null, new TransportistaRequest("T2 " + key, "999", true));
    var x = service.guardarZona(null, new ZonaRequest("Z1 " + key, "Lima", true));
    var y = service.guardarZona(null, new ZonaRequest("Z2 " + key, "Cusco", true));
    var original =
        service.guardarCobertura(new CoberturaRequest(a.id(), x.id(), BigDecimal.TEN, 1, true));
    service.guardarCobertura(new CoberturaRequest(b.id(), x.id(), BigDecimal.TEN, 2, true));
    service.guardarCobertura(new CoberturaRequest(a.id(), y.id(), BigDecimal.TEN, 3, true));
    var updated =
        service.guardarCobertura(
            new CoberturaRequest(a.id(), x.id(), new BigDecimal("12.00"), 2, true));
    assertEquals(original.id(), updated.id());
    assertEquals(new BigDecimal("12.00"), service.cobertura(a.id(), x.id()).tarifa());
    service.borrarZona(x.id());
    assertThrows(
        org.springframework.web.server.ResponseStatusException.class,
        () -> service.cobertura(a.id(), x.id()));
    assertTrue(service.cobertura(a.id(), y.id()).activo());
  }
}
