package pe.edu.upeu.garritas.institucion.controller;

import jakarta.validation.Valid;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.institucion.dto.*;
import pe.edu.upeu.garritas.institucion.service.PrestacionService;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class PrestacionController {
  private final PrestacionService service;

  @GetMapping("/prestaciones")
  public List<PrestacionResponse> listar() {
    return service.listar();
  }

  @PostMapping("/prestaciones")
  @ResponseStatus(HttpStatus.CREATED)
  public PrestacionResponse crear(@Valid @RequestBody PrestacionRequest r) {
    return service.guardar(null, r);
  }

  @PutMapping("/prestaciones/{id}")
  public PrestacionResponse editar(@PathVariable Long id, @Valid @RequestBody PrestacionRequest r) {
    return service.guardar(id, r);
  }

  @DeleteMapping("/prestaciones/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrar(@PathVariable Long id) {
    service.desactivar(id);
  }

  @GetMapping("/sedes/{id}/prestaciones")
  public List<OfertaResponse> ofertas(@PathVariable Long id) {
    return service.ofertas(id);
  }

  @PutMapping("/sedes/{id}/prestaciones")
  public OfertaResponse oferta(@PathVariable Long id, @Valid @RequestBody OfertaRequest r) {
    return service.guardarOferta(id, r);
  }
}
