package pe.edu.upeu.garritas.venta.client;

import feign.FeignException;
import lombok.RequiredArgsConstructor;
import org.springframework.cloud.client.circuitbreaker.CircuitBreakerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class LogisticaConsulta {
  private final LogisticaClient client;
  private final CircuitBreakerFactory<?, ?> breakers;

  public LogisticaClient.Cobertura obtener(Long t, Long z) {
    return breakers
        .create("logistica")
        .run(
            () -> client.obtener(t, z),
            ex -> {
              if (ex instanceof FeignException f && (f.status() == 404 || f.status() == 409))
                throw new ResponseStatusException(
                    HttpStatus.CONFLICT, "La cobertura ya no está disponible");
              throw new ResponseStatusException(
                  HttpStatus.SERVICE_UNAVAILABLE,
                  "No se pudo validar el delivery. No se registró la compra; reintenta más tarde",
                  ex);
            });
  }
}
