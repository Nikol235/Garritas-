package pe.edu.upeu.garritas.usuario.service;

import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.usuario.dto.RolRequest;
import pe.edu.upeu.garritas.usuario.dto.RolResponse;
import pe.edu.upeu.garritas.usuario.entity.Rol;
import pe.edu.upeu.garritas.usuario.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.usuario.mapper.RolMapper;
import pe.edu.upeu.garritas.usuario.repository.RolRepository;

@Service
@Transactional
@RequiredArgsConstructor
public class RolService {

  private final RolRepository rolRepository;
  private final RolMapper rolMapper;
  private final org.springframework.jdbc.core.JdbcTemplate jdbc;

  public List<RolResponse> listar() {
    return rolRepository.findAll().stream().map(rolMapper::toResponse).toList();
  }

  public RolResponse obtener(Long id) {
    return rolMapper.toResponse(buscarOFallar(id));
  }

  public RolResponse crear(RolRequest request) {
    validarNombre(request.getNombre(), null);
    Rol rol = rolMapper.toEntity(request);
    rol.setNombre(request.getNombre().strip().toUpperCase(java.util.Locale.ROOT));
    return rolMapper.toResponse(rolRepository.save(rol));
  }

  public RolResponse actualizar(Long id, RolRequest request) {
    Rol rol = buscarOFallar(id);
    if (java.util.Set.of("ADMIN", "CLIENTE").contains(rol.getNombre())
        && !rol.getNombre().equalsIgnoreCase(request.getNombre().strip()))
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.CONFLICT, "No se puede renombrar un rol base");
    validarNombre(request.getNombre(), id);
    rol.setNombre(request.getNombre().strip().toUpperCase(java.util.Locale.ROOT));
    rol.setDescripcion(request.getDescripcion());
    return rolMapper.toResponse(rolRepository.save(rol));
  }

  public void eliminar(Long id) {
    Rol rol = buscarOFallar(id);
    if (java.util.Set.of("ADMIN", "CLIENTE").contains(rol.getNombre()))
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.CONFLICT, "Los roles base no se eliminan");
    if (jdbc.queryForObject("SELECT count(*) FROM usuario_rol WHERE id_rol=?", Long.class, id) > 0)
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.CONFLICT,
          "Retira las asignaciones del rol antes de eliminarlo");
    rolRepository.delete(rol);
  }

  private void validarNombre(String nombre, Long id) {
    rolRepository
        .findByNombreIgnoreCase(nombre.strip())
        .ifPresent(
            r -> {
              if (!java.util.Objects.equals(r.getId(), id))
                throw new org.springframework.web.server.ResponseStatusException(
                    org.springframework.http.HttpStatus.CONFLICT,
                    "Ya existe un rol con ese nombre");
            });
  }

  public Rol buscarOFallar(Long id) {
    return rolRepository
        .findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Rol no encontrado: " + id));
  }
}
