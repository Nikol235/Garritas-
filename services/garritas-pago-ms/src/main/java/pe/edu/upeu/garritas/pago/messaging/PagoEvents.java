package pe.edu.upeu.garritas.pago.messaging;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.slf4j.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.common.*;
import tools.jackson.databind.ObjectMapper;

@Component
@RequiredArgsConstructor
public class PagoEvents {
  private static final Logger log = LoggerFactory.getLogger(PagoEvents.class);
  private final JdbcTemplate jdbc;
  private final Inbox inbox;
  private final Outbox outbox;
  private final ObjectMapper json;

  @Value("${app.pagos.metodo-rechazado:TRANSFERENCIA}")
  private String metodoRechazado;

  @KafkaListener(topics = "${app.kafka.topic:garritas.ventas.v1}")
  @Transactional
  public void consume(String payload) {
    SagaEvent e = json.readValue(payload, SagaEvent.class);
    if (!e.type().equals("inventario.reservado")) return;
    if (!inbox.claim(e)) return;
    try (var scope = MDC.putCloseable("traceId", e.traceId())) {
      boolean aprobado = !e.metodo().equals(metodoRechazado);
      int created =
          jdbc.update(
              "INSERT INTO"
                  + " pagos(id_venta,id_cliente,monto,metodo,estado,fecha_pago,referencia_externa)"
                  + " VALUES (?,?,?,?,?,CURRENT_TIMESTAMP,?) ON CONFLICT(id_venta) DO NOTHING",
              e.ventaId(),
              e.clienteId(),
              e.total(),
              e.metodo(),
              aprobado ? "APROBADO" : "RECHAZADO",
              UUID.randomUUID().toString());
      if (created == 1) outbox.append(e.next(aprobado ? "pago.validado" : "pago.fallido"));
      log.info(
          "component=pago ventaId={} estado={} created={}",
          e.ventaId(),
          aprobado ? "APROBADO" : "RECHAZADO",
          created);
    }
  }
}
