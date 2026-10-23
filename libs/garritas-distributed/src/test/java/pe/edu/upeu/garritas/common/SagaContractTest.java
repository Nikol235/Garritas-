package pe.edu.upeu.garritas.common;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;

class SagaContractTest {
  private SagaEvent event(int version, int cantidad) {
    return new SagaEvent(
        UUID.randomUUID(),
        version,
        "venta.creada",
        1L,
        "cliente-a",
        BigDecimal.TEN,
        "YAPE",
        "trace-test",
        List.of(new SagaEvent.Item(1L, cantidad, BigDecimal.TEN)),
        Instant.now());
  }

  @Test
  void rejectsUnsupportedVersionsAndNonpositiveQuantities() {
    assertDoesNotThrow(() -> event(1, 1).validate());
    assertThrows(IllegalArgumentException.class, () -> event(2, 1).validate());
    assertThrows(IllegalArgumentException.class, () -> event(1, 0).validate());
  }

  @Test
  void nextEventKeepsCorrelationAndAggregateButHasNewIdentity() {
    var original = event(1, 1);
    var next = original.next("inventario.reservado");
    assertNotEquals(original.eventId(), next.eventId());
    assertEquals(original.ventaId(), next.ventaId());
    assertEquals(original.traceId(), next.traceId());
    assertEquals(original.items(), next.items());
  }

  @Test
  void ownershipIsEnforcedExceptForAdministrator() {
    try {
      SecurityContextHolder.getContext()
          .setAuthentication(
              new UsernamePasswordAuthenticationToken(
                  "cliente-a", "", List.of(new SimpleGrantedAuthority("ROLE_CLIENTE"))));
      assertDoesNotThrow(() -> CurrentUser.requireOwner("cliente-a"));
      assertThrows(AccessDeniedException.class, () -> CurrentUser.requireOwner("cliente-b"));
      SecurityContextHolder.getContext()
          .setAuthentication(
              new UsernamePasswordAuthenticationToken(
                  "admin", "", List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
      assertDoesNotThrow(() -> CurrentUser.requireOwner("cliente-b"));
    } finally {
      SecurityContextHolder.clearContext();
    }
  }
}
