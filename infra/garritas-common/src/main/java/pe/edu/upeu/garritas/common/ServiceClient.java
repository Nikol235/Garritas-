package pe.edu.upeu.garritas.common;

import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

/** Bounded, read-only inter-service calls through Eureka, preserving caller identity. */
public class ServiceClient {
  private final RestClient client;
  private final org.springframework.cloud.client.loadbalancer.LoadBalancerClient loadBalancer;

  public ServiceClient(
      RestClient client,
      org.springframework.cloud.client.loadbalancer.LoadBalancerClient loadBalancer) {
    this.client = client;
    this.loadBalancer = loadBalancer;
  }

  public <T> T get(String service, String path, Class<T> type) {
    try {
      var instance = loadBalancer.choose(service);
      if (instance == null)
        throw new ResponseStatusException(
            HttpStatus.SERVICE_UNAVAILABLE,
            "El servicio " + service + " no está disponible; vuelve a intentarlo");
      var request = client.get().uri(instance.getUri().toString() + path);
      var auth = SecurityContextHolder.getContext().getAuthentication();
      if (auth instanceof JwtAuthenticationToken jwt)
        request.header("Authorization", "Bearer " + jwt.getToken().getTokenValue());
      String trace = MDC.get("traceId");
      if (trace != null) request.header("X-Trace-ID", trace);
      return request.retrieve().body(type);
    } catch (HttpClientErrorException ex) {
      throw new ResponseStatusException(
          ex.getStatusCode(), "Referencia no disponible o sin permiso: " + path);
    } catch (RestClientException ex) {
      throw new ResponseStatusException(
          HttpStatus.SERVICE_UNAVAILABLE,
          "El servicio " + service + " no está disponible; vuelve a intentarlo",
          ex);
    }
  }
}
