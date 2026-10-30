package pe.edu.upeu.garritas.usuario.mapper;

import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.usuario.dto.RolRequest;
import pe.edu.upeu.garritas.usuario.dto.RolResponse;
import pe.edu.upeu.garritas.usuario.entity.Rol;

@Component
public class RolMapper {

  public Rol toEntity(RolRequest request) {
    if (request == null) return null;
    return Rol.builder().nombre(request.getNombre()).descripcion(request.getDescripcion()).build();
  }

  public RolResponse toResponse(Rol rol) {
    if (rol == null) return null;
    return RolResponse.builder()
        .id(rol.getId())
        .nombre(rol.getNombre())
        .descripcion(rol.getDescripcion())
        .build();
  }
}
