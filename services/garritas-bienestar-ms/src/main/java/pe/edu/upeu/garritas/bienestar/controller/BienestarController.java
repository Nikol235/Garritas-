package pe.edu.upeu.garritas.bienestar.controller;

import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.bienestar.dto.*;
import pe.edu.upeu.garritas.bienestar.entity.Especialidad;
import pe.edu.upeu.garritas.bienestar.service.BienestarService;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class BienestarController {
  private final BienestarService service;

  @GetMapping("/especialistas")
  public List<ProfesionalResponse> listar() {
    return service.listar();
  }

  @GetMapping("/especialistas/{id}")
  public ProfesionalResponse obtener(@PathVariable Long id) {
    return service.obtener(id);
  }

  @PostMapping("/especialistas")
  @ResponseStatus(HttpStatus.CREATED)
  public ProfesionalResponse crear(@Valid @RequestBody ProfesionalRequest r) {
    return service.guardar(null, r);
  }

  @PutMapping("/especialistas/{id}")
  public ProfesionalResponse editar(
      @PathVariable Long id, @Valid @RequestBody ProfesionalRequest r) {
    return service.guardar(id, r);
  }

  @DeleteMapping("/especialistas/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void eliminar(@PathVariable Long id) {
    service.eliminar(id);
  }

  @GetMapping("/especialidades")
  public List<Especialidad> especialidades() {
    return service.especialidades();
  }

  @PostMapping("/especialidades")
  @ResponseStatus(HttpStatus.CREATED)
  public Especialidad crearEspecialidad(@Valid @RequestBody EspecialidadRequest r) {
    return service.guardarEspecialidad(null, r);
  }

  @PutMapping("/especialidades/{id}")
  public Especialidad editarEspecialidad(
      @PathVariable Long id, @Valid @RequestBody EspecialidadRequest r) {
    return service.guardarEspecialidad(id, r);
  }

  @DeleteMapping("/especialidades/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrarEspecialidad(@PathVariable Long id) {
    service.eliminarEspecialidad(id);
  }
}
