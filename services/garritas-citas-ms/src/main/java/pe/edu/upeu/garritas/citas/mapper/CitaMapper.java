package pe.edu.upeu.garritas.citas.mapper;

import pe.edu.upeu.garritas.citas.dto.CitaRequest;
import pe.edu.upeu.garritas.citas.dto.CitaResponse;
import pe.edu.upeu.garritas.citas.entity.Cita;
import pe.edu.upeu.garritas.citas.entity.EstadoCita;
import org.springframework.stereotype.Component;

@Component
public class CitaMapper {

    public Cita toEntity(CitaRequest request) {
        return Cita.builder()
                .idCliente(request.getIdCliente())
                .idMascota(request.getIdMascota())
                .idSede(request.getIdSede())
                .fechaHora(request.getFechaHora())
                .motivo(request.getMotivo())
                .estado(EstadoCita.PROGRAMADA)
                .build();
    }

    public CitaResponse toResponse(Cita cita) {
        return CitaResponse.builder()
                .id(cita.getId())
                .idCliente(cita.getIdCliente())
                .idMascota(cita.getIdMascota())
                .idSede(cita.getIdSede())
                .fechaHora(cita.getFechaHora())
                .motivo(cita.getMotivo())
                .estado(cita.getEstado())
                .build();
    }
}
