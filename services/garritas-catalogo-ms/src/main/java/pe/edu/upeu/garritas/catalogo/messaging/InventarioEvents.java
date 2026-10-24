package pe.edu.upeu.garritas.catalogo.messaging;

import java.math.BigDecimal;
import java.util.*;
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
public class InventarioEvents {
  private static final Logger log = LoggerFactory.getLogger(InventarioEvents.class);
  private final JdbcTemplate jdbc;
  private final Inbox inbox;
  private final Outbox outbox;
  private final ObjectMapper json;

  @KafkaListener(topics = "${app.kafka.topic:garritas.ventas.v1}")
  @Transactional
  public void consume(String payload) {
    SagaEvent e = json.readValue(payload, SagaEvent.class);
    if (!Set.of("venta.creada", "pago.fallido").contains(e.type())) return;
    if (!inbox.claim(e)) return;
    try (var scope = MDC.putCloseable("traceId", e.traceId())) {
      if (e.type().equals("venta.creada")) reservar(e, payload);
      else liberar(e);
      log.info(
          "component=inventario ventaId={} eventType={} status=processed", e.ventaId(), e.type());
    }
  }

  private void reservar(SagaEvent e, String payload) {
    // Also deduplicate semantic replays carrying a different eventId.
    if (jdbc.update(
            "INSERT INTO reservas_stock(id_venta,estado,payload) VALUES (?,'NUEVA',?) ON CONFLICT"
                + " DO NOTHING",
            e.ventaId(),
            payload)
        == 0) return;
    var quantities = new TreeMap<Long, Integer>();
    e.items().forEach(i -> quantities.merge(i.productoId(), i.cantidad(), Math::addExact));
    boolean valid = true;
    // Lock in deterministic product order; validate every line before changing any stock.
    for (var item : quantities.entrySet()) {
      var rows =
          jdbc.queryForList(
              "SELECT stock,activo,precio FROM productos WHERE id=? FOR UPDATE", item.getKey());
      if (rows.isEmpty()) {
        valid = false;
        continue;
      }
      var p = rows.getFirst();
      if (!(Boolean) p.get("activo") || (Integer) p.get("stock") < item.getValue()) valid = false;
      for (var detail : e.items())
        if (detail.productoId().equals(item.getKey())
            && ((BigDecimal) p.get("precio")).compareTo(detail.precio()) != 0) valid = false;
    }
    if (valid)
      for (var item : quantities.entrySet())
        jdbc.update(
            "UPDATE productos SET stock=stock-?,version=version+1 WHERE id=?",
            item.getValue(),
            item.getKey());
    jdbc.update(
        "UPDATE reservas_stock SET estado=? WHERE id_venta=?",
        valid ? "RESERVADA" : "RECHAZADA",
        e.ventaId());
    outbox.append(e.next(valid ? "inventario.reservado" : "inventario.rechazado"));
  }

  private void liberar(SagaEvent e) {
    var rows =
        jdbc.queryForList(
            "SELECT estado,payload FROM reservas_stock WHERE id_venta=? FOR UPDATE", e.ventaId());
    if (rows.isEmpty()) throw new IllegalStateException("Reserva inexistente: " + e.ventaId());
    if (!rows.getFirst().get("estado").equals("RESERVADA")) return;
    var original = json.readValue(rows.getFirst().get("payload").toString(), SagaEvent.class);
    for (var item :
        original.items().stream().sorted(Comparator.comparing(SagaEvent.Item::productoId)).toList())
      jdbc.update(
          "UPDATE productos SET stock=stock+?,version=version+1 WHERE id=?",
          item.cantidad(),
          item.productoId());
    jdbc.update("UPDATE reservas_stock SET estado='LIBERADA' WHERE id_venta=?", e.ventaId());
    outbox.append(original.next("inventario.liberado"));
  }
}
