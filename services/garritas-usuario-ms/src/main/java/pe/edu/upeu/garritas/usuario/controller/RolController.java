package pe.edu.upeu.garritas.usuario.controller;

import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.usuario.dto.RolRequest;
import pe.edu.upeu.garritas.usuario.dto.RolResponse;
import pe.edu.upeu.garritas.usuario.service.RolService;

@RestController
@RequestMapping({"/api/v1/roles", "/api/v1/usuarios/roles"})
@RequiredArgsConstructor
public class RolController {

  private final RolService rolService;

  @GetMapping
  public List<RolResponse> listar() {
    return rolService.listar();
  }

  @GetMapping("/{id}")
  public RolResponse obtener(@PathVariable Long id) {
    return rolService.obtener(id);
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public RolResponse crear(@Valid @RequestBody RolRequest request) {
    return rolService.crear(request);
  }

  @PutMapping("/{id}")
  public RolResponse actualizar(@PathVariable Long id, @Valid @RequestBody RolRequest request) {
    return rolService.actualizar(id, request);
  }

  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void eliminar(@PathVariable Long id) {
    rolService.eliminar(id);
  }
}
