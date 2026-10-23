package pe.edu.upeu.garritas.venta.client;

import feign.FeignException;
import lombok.RequiredArgsConstructor;
import org.springframework.cloud.client.circuitbreaker.CircuitBreakerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class CatalogoConsulta {
  private final ProductoClient client;
  private final CircuitBreakerFactory<?, ?> breakers;

  public ProductoClient.Producto obtener(Long id) {
    return breakers
        .create("catalogo")
        .run(
            () -> client.obtener(id),
            ex -> {
              if (ex instanceof FeignException.NotFound)
                throw new ResponseStatusException(
                    HttpStatus.UNPROCESSABLE_CONTENT, "Producto no encontrado");
              throw new ResponseStatusException(
                  HttpStatus.SERVICE_UNAVAILABLE, "Catálogo no disponible; inténtalo de nuevo", ex);
            });
  }
}
