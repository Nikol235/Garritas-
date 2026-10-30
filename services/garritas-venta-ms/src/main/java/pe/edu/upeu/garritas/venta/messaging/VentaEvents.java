package pe.edu.upeu.garritas.venta.messaging;

import lombok.RequiredArgsConstructor;
import org.slf4j.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.common.*;
import tools.jackson.databind.ObjectMapper;

@Component
@RequiredArgsConstructor
public class VentaEvents {
  private static final Logger log = LoggerFactory.getLogger(VentaEvents.class);
  private final JdbcTemplate jdbc;
  private final Inbox inbox;
  private final ObjectMapper json;

  @KafkaListener(topics = "${app.kafka.topic:garritas.ventas.v1}")
  @Transactional
  public void consume(String payload) {
    SagaEvent e = json.readValue(payload, SagaEvent.class);
    if (!java.util.Set.of(
            "inventario.reservado",
            "inventario.rechazado",
            "pago.validado",
            "pago.fallido",
            "inventario.liberado")
        .contains(e.type())) return;
    if (!inbox.claim(e)) return;
    try (var scope = MDC.putCloseable("traceId", e.traceId())) {
      String state =
          switch (e.type()) {
            case "inventario.reservado" -> "PENDIENTE_PAGO";
            case "pago.validado" -> "PAGADA";
            case "pago.fallido" -> "COMPENSANDO";
            default -> "CANCELADA";
          };
      String expected =
          switch (e.type()) {
            case "inventario.reservado", "inventario.rechazado" -> "PENDIENTE_STOCK";
            case "pago.validado", "pago.fallido" -> "PENDIENTE_PAGO";
            default -> "COMPENSANDO";
          };
      int changed =
          jdbc.update(
              "UPDATE ventas SET estado=? WHERE id=? AND estado=?", state, e.ventaId(), expected);
      if (changed == 1 && "pago.validado".equals(e.type())) {
        // Same local transaction as inbox and sale transition: no paid order without its dispatch.
        jdbc.update(
            """
            INSERT INTO despachos(id_venta,id_cliente,direccion_entrega,transportista,estado,fecha_entrega_estimada,id_zona,id_transportista,tarifa)
            SELECT id,id_cliente,direccion_entrega,transportista_nombre,'PENDIENTE',CURRENT_TIMESTAMP + dias_entrega * interval '1 day',zona_id,transportista_id,costo_envio
            FROM ventas WHERE id=? AND tipo_entrega='ENVIO'
            ON CONFLICT(id_venta) DO NOTHING
            """,
            e.ventaId());
      }
      log.info(
          "component=saga ventaId={} eventType={} estado={} changed={}",
          e.ventaId(),
          e.type(),
          state,
          changed);
    }
  }
}
