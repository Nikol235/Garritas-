package pe.edu.upeu.garritas.institucion.mapper;

import pe.edu.upeu.garritas.institucion.dto.SedeRequest;
import pe.edu.upeu.garritas.institucion.dto.SedeResponse;
import pe.edu.upeu.garritas.institucion.entity.Sede;
import org.springframework.stereotype.Component;

@Component
public class SedeMapper {

    public Sede toEntity(SedeRequest request) {
        return Sede.builder()
                .nombre(request.getNombre())
                .direccion(request.getDireccion())
                .ciudad(request.getCiudad())
                .telefono(request.getTelefono())
                .activo(request.getActivo())
                .build();
    }

    public SedeResponse toResponse(Sede sede) {
        return SedeResponse.builder()
                .id(sede.getId())
                .nombre(sede.getNombre())
                .direccion(sede.getDireccion())
                .ciudad(sede.getCiudad())
                .telefono(sede.getTelefono())
                .activo(sede.getActivo())
                .build();
    }
}
