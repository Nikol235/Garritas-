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

  public List<RolResponse> listar() {
    return rolRepository.findAll().stream().map(rolMapper::toResponse).toList();
  }

  public RolResponse obtener(Long id) {
    return rolMapper.toResponse(buscarOFallar(id));
  }

  public RolResponse crear(RolRequest request) {
    Rol rol = rolMapper.toEntity(request);
    return rolMapper.toResponse(rolRepository.save(rol));
  }

  public RolResponse actualizar(Long id, RolRequest request) {
    Rol rol = buscarOFallar(id);
    rol.setNombre(request.getNombre());
    rol.setDescripcion(request.getDescripcion());
    return rolMapper.toResponse(rolRepository.save(rol));
  }

  public void eliminar(Long id) {
    rolRepository.delete(buscarOFallar(id));
  }

  public Rol buscarOFallar(Long id) {
    return rolRepository
        .findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Rol no encontrado: " + id));
  }
}
