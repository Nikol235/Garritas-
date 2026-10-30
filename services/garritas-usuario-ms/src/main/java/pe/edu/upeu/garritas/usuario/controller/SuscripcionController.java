package pe.edu.upeu.garritas.usuario.controller;

import jakarta.validation.Valid;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.usuario.dto.*;
import pe.edu.upeu.garritas.usuario.service.SuscripcionService;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class SuscripcionController {
  private final SuscripcionService service;

  @GetMapping("/planes")
  public List<PlanResponse> planes() {
    return service.planes();
  }

  @PostMapping("/planes")
  @ResponseStatus(HttpStatus.CREATED)
  public PlanResponse crearPlan(@Valid @RequestBody PlanRequest r) {
    return service.guardarPlan(null, r);
  }

  @PutMapping("/planes/{id}")
  public PlanResponse editarPlan(@PathVariable Long id, @Valid @RequestBody PlanRequest r) {
    return service.guardarPlan(id, r);
  }

  @DeleteMapping("/planes/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrarPlan(@PathVariable Long id) {
    service.desactivarPlan(id);
  }

  @GetMapping("/suscripciones")
  public List<SuscripcionResponse> listar() {
    return service.listar();
  }

  @GetMapping("/suscripciones/{id}")
  public SuscripcionResponse obtener(@PathVariable Long id) {
    return service.obtener(id);
  }

  @PostMapping("/suscripciones")
  @ResponseStatus(HttpStatus.CREATED)
  public SuscripcionResponse contratar(
      @Valid @RequestBody SuscripcionRequest r, @RequestHeader("Idempotency-Key") UUID key) {
    return service.contratar(r, key);
  }

  @PostMapping("/suscripciones/{id}/renovar")
  public SuscripcionResponse renovar(
      @PathVariable Long id, @RequestHeader("Idempotency-Key") UUID key) {
    return service.renovar(id, key);
  }

  @PostMapping("/suscripciones/{id}/cancelar")
  public SuscripcionResponse cancelar(@PathVariable Long id) {
    return service.cancelar(id);
  }
}
