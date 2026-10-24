package pe.edu.upeu.garritas.common;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.support.TransactionSynchronizationManager;

public class Inbox {
  private final JdbcTemplate jdbc;

  public Inbox(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  public boolean claim(SagaEvent event) {
    event.validate();
    if (!TransactionSynchronizationManager.isActualTransactionActive())
      throw new IllegalStateException("Inbox requiere una transacción local");
    return jdbc.update(
            "INSERT INTO inbox_event(event_id) VALUES (?) ON CONFLICT DO NOTHING", event.eventId())
        == 1;
  }
}
