package pe.edu.upeu.garritas.usuario.controller;

import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.usuario.dto.*;
import pe.edu.upeu.garritas.usuario.service.*;

@RestController
@RequestMapping("/api/v1/usuarios/me")
@RequiredArgsConstructor
public class MiCuentaController {
  private final UsuarioService usuarios;
  private final MascotaService mascotas;

  @GetMapping
  public UsuarioResponse me() {
    return usuarios.me();
  }

  @PutMapping
  public UsuarioResponse guardar(@Valid @RequestBody UsuarioRequest body) {
    return usuarios.guardarMe(body);
  }

  @GetMapping("/mascotas")
  public List<MascotaResponse> mascotas() {
    return mascotas.listarPorUsuario(usuarios.miUsuario().getId());
  }

  @GetMapping("/mascotas/{id}")
  public MascotaResponse mascota(@PathVariable Long id) {
    mascotas.verificarUsuario(usuarios.miUsuario().getId(), id);
    return mascotas.obtener(id);
  }

  @PostMapping("/mascotas")
  @ResponseStatus(HttpStatus.CREATED)
  public MascotaResponse crear(@Valid @RequestBody MascotaRequest body) {
    return mascotas.crear(usuarios.miUsuario().getId(), body);
  }

  @PutMapping("/mascotas/{id}")
  public MascotaResponse editar(@PathVariable Long id, @Valid @RequestBody MascotaRequest body) {
    mascotas.verificarUsuario(usuarios.miUsuario().getId(), id);
    return mascotas.actualizar(id, body);
  }

  @DeleteMapping("/mascotas/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void eliminar(@PathVariable Long id) {
    mascotas.verificarUsuario(usuarios.miUsuario().getId(), id);
    mascotas.eliminar(id);
  }
}
