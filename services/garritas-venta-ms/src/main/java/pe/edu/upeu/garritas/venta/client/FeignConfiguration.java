package pe.edu.upeu.garritas.venta.client;

import feign.RequestInterceptor;
import org.slf4j.MDC;
import org.springframework.context.annotation.*;

@Configuration(proxyBeanMethods = false)
public class FeignConfiguration {
  @Bean
  RequestInterceptor traceInterceptor() {
    return t -> {
      var trace = MDC.get("traceId");
      if (trace != null) t.header("X-Trace-ID", trace);
    };
  }
}
