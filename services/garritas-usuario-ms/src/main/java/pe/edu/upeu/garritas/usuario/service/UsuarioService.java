package pe.edu.upeu.garritas.usuario.service;

import java.util.HashSet;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.usuario.dto.UsuarioRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioResponse;
import pe.edu.upeu.garritas.usuario.entity.Rol;
import pe.edu.upeu.garritas.usuario.entity.Usuario;
import pe.edu.upeu.garritas.usuario.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.usuario.mapper.UsuarioMapper;
import pe.edu.upeu.garritas.usuario.repository.RolRepository;
import pe.edu.upeu.garritas.usuario.repository.UsuarioRepository;

@Transactional
@Service
@RequiredArgsConstructor
public class UsuarioService {

  private final UsuarioRepository usuarioRepository;
  private final RolRepository rolRepository;
  private final UsuarioMapper usuarioMapper;

  public List<UsuarioResponse> listar() {
    return usuarioRepository.findAll().stream().map(usuarioMapper::toResponse).toList();
  }

  public Page<UsuarioResponse> listarPaginado(String q, String rol, Pageable pageable) {
    return usuarioRepository.buscarConRol(q, rol, pageable).map(usuarioMapper::toResponse);
  }

  public UsuarioResponse obtener(Long id) {
    return usuarioMapper.toResponse(buscarOFallar(id));
  }

  public UsuarioResponse crear(UsuarioRequest request) {
    Usuario usuario = usuarioMapper.toEntity(request);
    asignarRolesDesdeRequest(usuario, request);
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public UsuarioResponse actualizar(Long id, UsuarioRequest request) {
    Usuario usuario = buscarOFallar(id);
    usuario.setNombre(request.getNombre());
    usuario.setEmail(request.getEmail());
    usuario.setTelefono(request.getTelefono());
    usuario.setDireccion(request.getDireccion());
    usuario.setDni(request.getDni());
    if (request.getRoleIds() != null) {
      usuario.setRoles(new HashSet<>(rolRepository.findAllById(request.getRoleIds())));
    }
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public void eliminar(Long id) {
    usuarioRepository.delete(buscarOFallar(id));
  }

  public UsuarioResponse asignarRol(Long idUsuario, Long idRol) {
    Usuario usuario = buscarOFallar(idUsuario);
    Rol rol =
        rolRepository
            .findById(idRol)
            .orElseThrow(() -> new ResourceNotFoundException("Rol no encontrado: " + idRol));
    usuario.getRoles().add(rol);
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public UsuarioResponse removerRol(Long idUsuario, Long idRol) {
    Usuario usuario = buscarOFallar(idUsuario);
    Rol rol =
        rolRepository
            .findById(idRol)
            .orElseThrow(() -> new ResourceNotFoundException("Rol no encontrado: " + idRol));
    usuario.getRoles().remove(rol);
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public UsuarioResponse me() {
    Usuario u = miUsuario();
    if (pe.edu.upeu.garritas.common.CurrentUser.admin()) {
      rolRepository.findByNombre("ADMIN").ifPresent(r -> {
        if (u.getRoles().stream().noneMatch(existing -> "ADMIN".equalsIgnoreCase(existing.getNombre()))) {
          u.getRoles().add(r);
          usuarioRepository.save(u);
        }
      });
    }
    return usuarioMapper.toResponse(u);
  }

  public UsuarioResponse guardarMe(UsuarioRequest request) {
    Usuario usuario =
        usuarioRepository
            .findBySubject(pe.edu.upeu.garritas.common.CurrentUser.subject())
            .orElseGet(() -> usuarioMapper.toEntity(request));
    usuario.setSubject(pe.edu.upeu.garritas.common.CurrentUser.subject());
    usuario.setNombre(request.getNombre());
    usuario.setEmail(request.getEmail());
    usuario.setTelefono(request.getTelefono());
    usuario.setDireccion(request.getDireccion());
    usuario.setDni(request.getDni());
    if (usuario.getRoles().isEmpty()) {
      if (pe.edu.upeu.garritas.common.CurrentUser.admin()) {
        rolRepository.findByNombre("ADMIN").ifPresent(r -> usuario.getRoles().add(r));
      } else {
        rolRepository.findByNombre("CLIENTE").ifPresent(r -> usuario.getRoles().add(r));
      }
    }
    return usuarioMapper.toResponse(usuarioRepository.saveAndFlush(usuario));
  }

  public Usuario miUsuario() {
    String sub = pe.edu.upeu.garritas.common.CurrentUser.subject();
    Usuario usuario = usuarioRepository
        .findBySubject(sub)
        .orElseGet(
            () -> {
              var auth =
                  org.springframework.security.core.context.SecurityContextHolder.getContext()
                      .getAuthentication();
              String email =
                  "cliente@"
                      + (sub != null && sub.length() > 8 ? sub.substring(0, 8) : "garritas")
                      + ".com";
              String nombre = (sub != null && !sub.isBlank()) ? sub : "Usuario Garritas";
              if (auth != null
                  && auth.getPrincipal()
                      instanceof org.springframework.security.oauth2.jwt.Jwt jwt) {
                if (jwt.hasClaim("email") && jwt.getClaimAsString("email") != null) {
                  email = jwt.getClaimAsString("email");
                }
                if (jwt.hasClaim("name") && jwt.getClaimAsString("name") != null) {
                  nombre = jwt.getClaimAsString("name");
                } else if (jwt.hasClaim("preferred_username")
                    && jwt.getClaimAsString("preferred_username") != null) {
                  nombre = jwt.getClaimAsString("preferred_username");
                }
              }
              var existing = usuarioRepository.findByEmail(email);
              if (existing.isPresent()) {
                Usuario u = existing.get();
                u.setSubject(sub);
                return usuarioRepository.save(u);
              }
              Usuario u =
                  Usuario.builder()
                      .subject(sub)
                      .nombre(nombre)
                      .email(email)
                      .build();
              if (pe.edu.upeu.garritas.common.CurrentUser.admin()) {
                rolRepository.findByNombre("ADMIN").ifPresent(r -> u.getRoles().add(r));
              } else {
                rolRepository.findByNombre("CLIENTE").ifPresent(r -> u.getRoles().add(r));
              }
              return usuarioRepository.save(u);
            });

    if (pe.edu.upeu.garritas.common.CurrentUser.admin()) {
      rolRepository.findByNombre("ADMIN").ifPresent(r -> {
        if (usuario.getRoles().stream().noneMatch(existing -> "ADMIN".equalsIgnoreCase(existing.getNombre()))) {
          usuario.getRoles().add(r);
          usuarioRepository.save(usuario);
        }
      });
    }

    return usuario;
  }

  Usuario buscarOFallar(Long id) {
    Usuario usuario =
        usuarioRepository
            .findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Usuario no encontrado: " + id));
    pe.edu.upeu.garritas.common.CurrentUser.requireOwner(usuario.getSubject());
    return usuario;
  }

  private void asignarRolesDesdeRequest(Usuario usuario, UsuarioRequest request) {
    if (request.getRoleIds() != null && !request.getRoleIds().isEmpty()) {
      usuario.setRoles(new HashSet<>(rolRepository.findAllById(request.getRoleIds())));
    } else {
      rolRepository.findByNombre("CLIENTE").ifPresent(r -> usuario.getRoles().add(r));
    }
  }
}
