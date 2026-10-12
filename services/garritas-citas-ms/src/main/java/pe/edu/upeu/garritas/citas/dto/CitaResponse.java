package pe.edu.upeu.garritas.citas.dto;

import pe.edu.upeu.garritas.citas.entity.EstadoCita;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CitaResponse {
    private Long id;
    private Long idCliente;
    private Long idMascota;
    private Long idSede;
    private Instant fechaHora;
    private String motivo;
    private EstadoCita estado;
}
