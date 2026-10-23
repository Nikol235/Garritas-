package pe.edu.upeu.garritas.common;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

/** Versioned wire contract. No JPA entities or Java type headers cross service boundaries. */
public record SagaEvent(
    UUID eventId,
    int version,
    String type,
    Long ventaId,
    String clienteId,
    BigDecimal total,
    String metodo,
    String traceId,
    List<Item> items,
    Instant occurredAt) {
  public record Item(Long productoId, int cantidad, BigDecimal precio) {}

  public SagaEvent next(String nextType) {
    return new SagaEvent(
        UUID.randomUUID(),
        1,
        nextType,
        ventaId,
        clienteId,
        total,
        metodo,
        traceId,
        items,
        Instant.now());
  }

  public void validate() {
    if (eventId == null
        || version != 1
        || ventaId == null
        || ventaId <= 0
        || type == null
        || clienteId == null
        || total == null
        || total.signum() <= 0
        || metodo == null
        || items == null
        || items.isEmpty()
        || items.stream()
            .anyMatch(
                i ->
                    i.productoId() == null
                        || i.cantidad() <= 0
                        || i.precio() == null
                        || i.precio().signum() < 0)) {
      throw new IllegalArgumentException("Contrato de evento inválido o versión no soportada");
    }
  }
}
