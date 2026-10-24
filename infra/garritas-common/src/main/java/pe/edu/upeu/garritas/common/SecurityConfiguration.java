package pe.edu.upeu.garritas.common;

import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.*;

@Import({HttpServices.class, DomainErrors.class})
@Configuration(proxyBeanMethods = false)
public class SecurityConfiguration {
  @Bean
  SecurityFilterChain security(
      HttpSecurity http,
      @Value("${garritas.cors.allowed-origins:http://localhost:4200}") String origins,
      @Value("${spring.application.name}") String app)
      throws Exception {
    var converter = new JwtAuthenticationConverter();
    converter.setJwtGrantedAuthoritiesConverter(
        jwt -> {
          Map<String, Object> realm = jwt.getClaimAsMap("realm_access");
          if (realm == null || !(realm.get("roles") instanceof Collection<?> roles))
            return List.of();
          return roles.stream()
              .filter(String.class::isInstance)
              .map(
                  r ->
                      (org.springframework.security.core.GrantedAuthority)
                          new SimpleGrantedAuthority("ROLE_" + r))
              .toList();
        });
    if (app.equals("garritas-gateway")) {
      var cors = new CorsConfiguration();
      cors.setAllowedOrigins(Arrays.asList(origins.split(",")));
      cors.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
      cors.setAllowedHeaders(
          List.of("Authorization", "Content-Type", "X-Trace-ID", "Idempotency-Key"));
      cors.setExposedHeaders(List.of("X-Trace-ID"));
      var source = new UrlBasedCorsConfigurationSource();
      source.registerCorsConfiguration("/**", cors);
      http.cors(c -> c.configurationSource(source));
    }
    http.csrf(c -> c.disable())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(
            a ->
                a.dispatcherTypeMatchers(jakarta.servlet.DispatcherType.ERROR)
                    .permitAll()
                    .requestMatchers(
                        "/actuator/health/**", "/actuator/health", "/actuator/prometheus")
                    .permitAll()
                    .requestMatchers(
                        HttpMethod.GET, "/api/v1/productos/**", "/api/v1/categorias/**")
                    .permitAll()
                    .requestMatchers(
                        HttpMethod.GET,
                        "/api/v1/sedes/**",
                        "/api/v1/especialistas/**",
                        "/api/v1/especialidades/**")
                    .permitAll()
                    .requestMatchers(
                        HttpMethod.POST,
                        "/api/v1/citas/*/confirmar",
                        "/api/v1/citas/*/atender",
                        "/api/v1/envios/*/en-transito",
                        "/api/v1/envios/*/entregado")
                    .hasRole("ADMIN")
                    .requestMatchers(
                        "/api/v1/usuarios/me/**",
                        "/api/v1/usuarios/*/mascotas/**",
                        "/api/v1/mascotas/**",
                        "/api/v1/citas/**",
                        "/api/v1/envios/**",
                        "/api/v1/ventas/**")
                    .hasAnyRole("CLIENTE", "ADMIN")
                    .requestMatchers(HttpMethod.GET, "/api/v1/pagos/**")
                    .hasAnyRole("CLIENTE", "ADMIN")
                    .anyRequest()
                    .hasRole("ADMIN"))
        .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(converter)));
    return http.build();
  }
}
