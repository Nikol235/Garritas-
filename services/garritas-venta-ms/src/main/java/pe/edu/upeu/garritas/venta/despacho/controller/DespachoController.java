package pe.edu.upeu.garritas.venta.despacho.controller;

import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.venta.despacho.dto.DespachoRequest;
import pe.edu.upeu.garritas.venta.despacho.dto.DespachoResponse;
import pe.edu.upeu.garritas.venta.despacho.service.DespachoService;

@RestController
@RequestMapping({"/api/v1/despachos", "/api/v1/envios"})
@RequiredArgsConstructor
public class DespachoController {

  private final DespachoService envioService;

  @GetMapping
  public List<DespachoResponse> listar() {
    return envioService.listar();
  }

  @GetMapping("/{id}")
  public DespachoResponse obtener(@PathVariable Long id) {
    return envioService.obtener(id);
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public DespachoResponse crear(@Valid @RequestBody DespachoRequest request) {
    return envioService.crear(request);
  }

  @PostMapping("/{id}/en-transito")
  public DespachoResponse marcarEnTransito(@PathVariable Long id) {
    return envioService.marcarEnTransito(id);
  }

  @PostMapping("/{id}/entregado")
  public DespachoResponse marcarEntregado(@PathVariable Long id) {
    return envioService.marcarEntregado(id);
  }

  @PostMapping("/{id}/cancelar")
  public DespachoResponse cancelar(@PathVariable Long id) {
    return envioService.cancelar(id);
  }
}
