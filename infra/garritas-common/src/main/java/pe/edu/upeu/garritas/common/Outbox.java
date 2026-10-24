package pe.edu.upeu.garritas.common;

import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import tools.jackson.databind.ObjectMapper;

/**
 * DB + outbox commit together. A crash after Kafka ack can duplicate delivery; consumers use Inbox.
 */
public class Outbox {
  private static final Logger log = LoggerFactory.getLogger(Outbox.class);
  private final JdbcTemplate jdbc;
  private final KafkaTemplate<String, String> kafka;
  private final ObjectMapper json;
  private final String topic;

  public Outbox(
      JdbcTemplate jdbc,
      KafkaTemplate<String, String> kafka,
      ObjectMapper json,
      @Value("${app.kafka.topic:garritas.ventas.v1}") String topic) {
    this.jdbc = jdbc;
    this.kafka = kafka;
    this.json = json;
    this.topic = topic;
  }

  public void append(SagaEvent event) {
    if (!TransactionSynchronizationManager.isActualTransactionActive())
      throw new IllegalStateException("Outbox requiere una transacción local");
    event.validate();
    jdbc.update(
        "INSERT INTO outbox_event(event_id,aggregate_id,payload) VALUES (?,?,?)",
        event.eventId(),
        event.ventaId().toString(),
        json.writeValueAsString(event));
  }

  @Scheduled(fixedDelayString = "${app.outbox.delay:500}")
  @Transactional
  public void publish() {
    var pending =
        jdbc.queryForList(
            "SELECT event_id,aggregate_id,payload FROM outbox_event WHERE published_at IS NULL"
                + " ORDER BY sequence LIMIT 20 FOR UPDATE SKIP LOCKED");
    for (var row : pending) {
      try {
        kafka
            .send(topic, row.get("aggregate_id").toString(), row.get("payload").toString())
            .get(10, TimeUnit.SECONDS);
        jdbc.update(
            "UPDATE outbox_event SET published_at=CURRENT_TIMESTAMP WHERE event_id=?",
            row.get("event_id"));
        log.info(
            "component=outbox eventId={} aggregateId={} status=published",
            row.get("event_id"),
            row.get("aggregate_id"));
      } catch (InterruptedException ex) {
        Thread.currentThread().interrupt();
        return;
      } catch (Exception ex) {
        log.warn(
            "component=outbox eventId={} status=retry error={}",
            row.get("event_id"),
            ex.getMessage());
        return;
      }
    }
  }
}
