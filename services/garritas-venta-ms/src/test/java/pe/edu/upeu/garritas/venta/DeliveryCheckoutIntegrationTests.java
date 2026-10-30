package pe.edu.upeu.garritas.venta;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.math.BigDecimal;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.*;
import pe.edu.upeu.garritas.venta.client.*;
import pe.edu.upeu.garritas.venta.dto.*;
import pe.edu.upeu.garritas.venta.service.VentaService;

@SpringBootTest
@Transactional
class DeliveryCheckoutIntegrationTests {
  @Autowired VentaService service;
  @MockitoBean CatalogoConsulta catalogo;
  @MockitoBean LogisticaConsulta logistica;
  @MockitoBean ServiceClient remote;

  @BeforeEach
  void setup() {
    auth("CLIENTE");
    when(remote.get(eq("garritas-institucion-ms"), anyString(), eq(Reference.class)))
        .thenReturn(new Reference(1L, "Sede", true, null, null, null));
    when(catalogo.obtener(1L))
        .thenReturn(new ProductoClient.Producto(1L, "Alimento", new BigDecimal("15.00"), 10, true));
    when(logistica.obtener(2L, 3L))
        .thenReturn(
            new LogisticaClient.Cobertura(true, "Transportista", new BigDecimal("12.50"), 2));
  }

  void auth(String role) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            new UsernamePasswordAuthenticationToken(
                "test-delivery", "", List.of(new SimpleGrantedAuthority("ROLE_" + role))));
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  VentaRequest request() {
    var r = new VentaRequest();
    r.setSedeId(1L);
    r.setMetodoPago("YAPE");
    r.setTipoEntrega("ENVIO");
    r.setZonaId(3L);
    r.setTransportistaId(2L);
    r.setDireccionEntrega("Av. Perú 123, Lima");
    r.setTarifaCotizada(new BigDecimal("12.50"));
    var d = new DetalleVentaRequest();
    d.setIdProducto(1L);
    d.setCantidad(2);
    r.setDetalles(List.of(d));
    return r;
  }

  @Test
  void includesValidatedShippingInPaymentAndReusesTheSameOrder() {
    var r = request();
    var key = UUID.randomUUID();
    var first = service.crear(r, key);
    assertEquals(0, new BigDecimal("42.50").compareTo(first.getTotal()));
    assertEquals(0, new BigDecimal("30.00").compareTo(first.getSubtotal()));
    assertEquals(0, new BigDecimal("12.50").compareTo(first.getCostoEnvio()));
    assertEquals(first.getId(), service.crear(r, key).getId());
    verify(logistica, times(1)).obtener(2L, 3L);
    r.setDireccionEntrega("Otra dirección 999, Lima");
    assertEquals(
        409,
        assertThrows(ResponseStatusException.class, () -> service.crear(r, key))
            .getStatusCode()
            .value());
  }

  @Test
  void rejectsChangedTariffInsteadOfChargingAnUnconfirmedAmount() {
    var r = request();
    r.setTarifaCotizada(BigDecimal.ZERO);
    assertEquals(
        409,
        assertThrows(ResponseStatusException.class, () -> service.crear(r, UUID.randomUUID()))
            .getStatusCode()
            .value());
  }

  @Test
  void administratorCannotPurchaseEvenWhenCallingServiceDirectly() {
    auth("ADMIN");
    assertThrows(
        org.springframework.security.access.AccessDeniedException.class,
        () -> service.crear(request(), UUID.randomUUID()));
    verifyNoInteractions(remote, catalogo, logistica);
  }

  @Test
  void pickupCannotSmuggleShippingDetails() {
    var r = request();
    r.setTipoEntrega("RECOJO");
    assertEquals(
        400,
        assertThrows(ResponseStatusException.class, () -> service.crear(r, UUID.randomUUID()))
            .getStatusCode()
            .value());
    verifyNoInteractions(remote, catalogo, logistica);
  }
}
