package pe.edu.upeu.garritas.citas.mapper;

import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.citas.dto.CitaRequest;
import pe.edu.upeu.garritas.citas.dto.CitaResponse;
import pe.edu.upeu.garritas.citas.entity.Cita;
import pe.edu.upeu.garritas.citas.entity.EstadoCita;

@Component
public class CitaMapper {

  public Cita toEntity(CitaRequest request) {
    return Cita.builder()
        .idCliente(pe.edu.upeu.garritas.common.CurrentUser.subject())
        .profesionalId(request.getProfesionalId())
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
        .profesionalId(cita.getProfesionalId())
        .nombreMascota(cita.getNombreMascota())
        .nombreSede(cita.getNombreSede())
        .nombreProfesional(cita.getNombreProfesional())
        .idCliente(cita.getIdCliente())
        .idMascota(cita.getIdMascota())
        .idSede(cita.getIdSede())
        .fechaHora(cita.getFechaHora())
        .motivo(cita.getMotivo())
        .estado(cita.getEstado())
        .build();
  }
}
