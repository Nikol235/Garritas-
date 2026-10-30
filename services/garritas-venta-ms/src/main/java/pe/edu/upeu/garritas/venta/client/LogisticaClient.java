package pe.edu.upeu.garritas.venta.client;

import java.math.BigDecimal;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

@FeignClient(name = "garritas-envio-ms")
public interface LogisticaClient {
  record Cobertura(Boolean activo, String transportista, BigDecimal tarifa, int diasEstimados) {}

  @GetMapping("/api/v1/transportistas/{t}/zonas/{z}")
  Cobertura obtener(@PathVariable("t") Long transportista, @PathVariable("z") Long zona);
}
