package pe.edu.upeu.garritas.usuario.mapper;

import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.usuario.dto.MascotaRequest;
import pe.edu.upeu.garritas.usuario.dto.MascotaResponse;
import pe.edu.upeu.garritas.usuario.entity.Mascota;

@Component
public class MascotaMapper {

  public Mascota toEntity(MascotaRequest request) {
    return Mascota.builder()
        .nombre(request.getNombre())
        .especie(request.getEspecie())
        .raza(request.getRaza())
        .edad(request.getEdad().intValueExact())
        .edadUnidad(request.getEdadUnidad())
        .build();
  }

  public MascotaResponse toResponse(Mascota mascota) {
    return MascotaResponse.builder()
        .id(mascota.getId())
        .nombre(mascota.getNombre())
        .especie(mascota.getEspecie())
        .raza(mascota.getRaza())
        .edad(mascota.getEdad())
        .edadUnidad(mascota.getEdadUnidad())
        .build();
  }
}
