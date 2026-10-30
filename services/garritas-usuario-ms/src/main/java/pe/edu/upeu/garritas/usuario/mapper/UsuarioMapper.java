package pe.edu.upeu.garritas.usuario.mapper;

import java.util.Collections;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.usuario.dto.UsuarioRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioResponse;
import pe.edu.upeu.garritas.usuario.entity.Usuario;

@Component
@RequiredArgsConstructor
public class UsuarioMapper {

  private final MascotaMapper mascotaMapper;
  private final RolMapper rolMapper;

  public Usuario toEntity(UsuarioRequest request) {
    if (request == null) return null;
    return Usuario.builder()
        .nombre(request.getNombre())
        .email(request.getEmail())
        .telefono(request.getTelefono())
        .direccion(request.getDireccion())
        .dni(request.getDni())
        .build();
  }

  public UsuarioResponse toResponse(Usuario usuario) {
    if (usuario == null) return null;
    return UsuarioResponse.builder()
        .id(usuario.getId())
        .nombre(usuario.getNombre())
        .email(usuario.getEmail())
        .telefono(usuario.getTelefono())
        .direccion(usuario.getDireccion())
        .dni(usuario.getDni())
        .mascotas(
            usuario.getMascotas() == null
                ? Collections.emptyList()
                : usuario.getMascotas().stream().map(mascotaMapper::toResponse).toList())
        .roles(
            usuario.getRoles() == null
                ? Collections.emptyList()
                : usuario.getRoles().stream().map(rolMapper::toResponse).toList())
        .build();
  }
}
