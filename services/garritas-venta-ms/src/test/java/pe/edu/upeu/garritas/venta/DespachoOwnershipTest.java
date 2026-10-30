package pe.edu.upeu.garritas.venta;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import pe.edu.upeu.garritas.common.ServiceClient;
import pe.edu.upeu.garritas.venta.despacho.dto.DespachoRequest;
import pe.edu.upeu.garritas.venta.despacho.mapper.DespachoMapper;
import pe.edu.upeu.garritas.venta.despacho.repository.DespachoRepository;
import pe.edu.upeu.garritas.venta.despacho.service.DespachoService;
import pe.edu.upeu.garritas.venta.entity.*;
import pe.edu.upeu.garritas.venta.repository.VentaRepository;

class DespachoOwnershipTest {
  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void rejectsForeignOrderBeforeRevealingPaymentStateOrCallingLogistics() {
    SecurityContextHolder.getContext()
        .setAuthentication(
            new UsernamePasswordAuthenticationToken(
                "otro-cliente", "", List.of(new SimpleGrantedAuthority("ROLE_CLIENTE"))));
    VentaRepository ventas = mock(VentaRepository.class);
    ServiceClient remote = mock(ServiceClient.class);
    DespachoRepository despachos = mock(DespachoRepository.class);
    DespachoMapper mapper = mock(DespachoMapper.class);
    when(ventas.findById(10L))
        .thenReturn(
            Optional.of(
                Venta.builder()
                    .id(10L)
                    .idCliente("propietario")
                    .estado(EstadoVenta.CANCELADA)
                    .build()));
    DespachoService service = new DespachoService(despachos, mapper, remote, ventas);
    DespachoRequest request = new DespachoRequest();
    request.setIdVenta(10L);
    assertThrows(
        org.springframework.security.access.AccessDeniedException.class,
        () -> service.crear(request));
    verifyNoInteractions(remote, despachos, mapper);
  }
}
