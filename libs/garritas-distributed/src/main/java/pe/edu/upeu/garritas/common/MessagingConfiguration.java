package pe.edu.upeu.garritas.common;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.*;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.util.backoff.FixedBackOff;
import tools.jackson.databind.ObjectMapper;

@Configuration(proxyBeanMethods = false)
@EnableScheduling
public class MessagingConfiguration {
  @Bean
  Outbox outbox(
      JdbcTemplate jdbc,
      KafkaTemplate<String, String> kafka,
      ObjectMapper json,
      @Value("${app.kafka.topic:garritas.ventas.v1}") String topic) {
    return new Outbox(jdbc, kafka, json, topic);
  }

  @Bean
  Inbox inbox(JdbcTemplate jdbc) {
    return new Inbox(jdbc);
  }

  @Bean
  NewTopic sagaTopic(@Value("${app.kafka.topic:garritas.ventas.v1}") String topic) {
    return new NewTopic(topic, 3, (short) 1);
  }

  @Bean
  NewTopic deadLetterTopic(@Value("${app.kafka.topic:garritas.ventas.v1}") String topic) {
    return new NewTopic(topic + ".DLT", 3, (short) 1);
  }

  @Bean
  DefaultErrorHandler kafkaErrorHandler(KafkaTemplate<String, String> kafka) {
    var recoverer = new DeadLetterPublishingRecoverer(kafka);
    recoverer.setFailIfSendResultIsError(true);
    return new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 9L));
  }
}
