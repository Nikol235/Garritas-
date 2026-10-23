package pe.edu.upeu.garritas.pago.controller;

import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.pago.dto.PagoResponse;
import pe.edu.upeu.garritas.pago.service.PagoService;

@RestController
@RequestMapping("/api/v1/pagos")
@RequiredArgsConstructor
public class PagoController {
  private final PagoService service;

  @GetMapping
  public List<PagoResponse> listar() {
    return service.listar();
  }

  @GetMapping("/{id}")
  public PagoResponse obtener(@PathVariable Long id) {
    return service.obtener(id);
  }

  @GetMapping("/venta/{id}")
  public PagoResponse porVenta(@PathVariable Long id) {
    return service.porVenta(id);
  }
}
