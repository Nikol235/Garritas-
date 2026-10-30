package pe.edu.upeu.garritas.usuario.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.usuario.dto.UsuarioRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioResponse;
import pe.edu.upeu.garritas.usuario.service.UsuarioService;

@RestController
@RequestMapping("/api/v1/usuarios")
@RequiredArgsConstructor
public class UsuarioController {

  private final UsuarioService usuarioService;

  @GetMapping
  public Object listar(
      @RequestParam(required = false) String q,
      @RequestParam(required = false) String rol,
      @RequestParam(required = false) Integer page,
      @RequestParam(required = false, defaultValue = "10") int size) {
    if (size < 1 || size > 100 || (page != null && page < 0))
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.BAD_REQUEST,
          "La página debe ser >= 0 y el tamaño entre 1 y 100");
    if (page != null || (q != null && !q.isBlank()) || (rol != null && !rol.isBlank())) {
      int pageNum = (page != null && page >= 0) ? page : 0;
      return usuarioService.listarPaginado(
          q, rol, PageRequest.of(pageNum, size, Sort.by(Sort.Direction.DESC, "id")));
    }
    return usuarioService.listar();
  }

  @GetMapping("/{id}")
  public UsuarioResponse obtener(@PathVariable Long id) {
    return usuarioService.obtener(id);
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public UsuarioResponse crear(@Valid @RequestBody UsuarioRequest request) {
    return usuarioService.crear(request);
  }

  @PutMapping("/{id}")
  public UsuarioResponse actualizar(
      @PathVariable Long id, @Valid @RequestBody UsuarioRequest request) {
    return usuarioService.actualizar(id, request);
  }

  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void eliminar(@PathVariable Long id) {
    usuarioService.eliminar(id);
  }

  @PostMapping("/{id}/roles/{idRol}")
  public UsuarioResponse asignarRol(@PathVariable Long id, @PathVariable Long idRol) {
    return usuarioService.asignarRol(id, idRol);
  }

  @DeleteMapping("/{id}/roles/{idRol}")
  public UsuarioResponse removerRol(@PathVariable Long id, @PathVariable Long idRol) {
    return usuarioService.removerRol(id, idRol);
  }
}
