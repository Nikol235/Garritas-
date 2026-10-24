package pe.edu.upeu.garritas.usuario.service;

import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import pe.edu.upeu.garritas.usuario.dto.UsuarioRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioResponse;
import pe.edu.upeu.garritas.usuario.entity.Usuario;
import pe.edu.upeu.garritas.usuario.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.usuario.mapper.UsuarioMapper;
import pe.edu.upeu.garritas.usuario.repository.UsuarioRepository;

@org.springframework.transaction.annotation.Transactional
@Service
@RequiredArgsConstructor
public class UsuarioService {

  private final UsuarioRepository usuarioRepository;
  private final UsuarioMapper usuarioMapper;

  public List<UsuarioResponse> listar() {
    return usuarioRepository.findAll().stream().map(usuarioMapper::toResponse).toList();
  }

  public UsuarioResponse obtener(Long id) {
    return usuarioMapper.toResponse(buscarOFallar(id));
  }

  public UsuarioResponse crear(UsuarioRequest request) {
    Usuario usuario = usuarioMapper.toEntity(request);
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public UsuarioResponse actualizar(Long id, UsuarioRequest request) {
    Usuario usuario = buscarOFallar(id);
    usuario.setNombre(request.getNombre());
    usuario.setEmail(request.getEmail());
    usuario.setTelefono(request.getTelefono());
    usuario.setDireccion(request.getDireccion());
    return usuarioMapper.toResponse(usuarioRepository.save(usuario));
  }

  public void eliminar(Long id) {
    usuarioRepository.delete(buscarOFallar(id));
  }

  public UsuarioResponse me() {
    return usuarioMapper.toResponse(miUsuario());
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
    return usuarioMapper.toResponse(usuarioRepository.saveAndFlush(usuario));
  }

  public Usuario miUsuario() {
    return usuarioRepository
        .findBySubject(pe.edu.upeu.garritas.common.CurrentUser.subject())
        .orElseThrow(
            () ->
                new org.springframework.web.server.ResponseStatusException(
                    org.springframework.http.HttpStatus.NOT_FOUND, "Primero completa tu perfil"));
  }

  Usuario buscarOFallar(Long id) {
    Usuario usuario =
        usuarioRepository
            .findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Usuario no encontrado: " + id));
    pe.edu.upeu.garritas.common.CurrentUser.requireOwner(usuario.getSubject());
    return usuario;
  }
}
