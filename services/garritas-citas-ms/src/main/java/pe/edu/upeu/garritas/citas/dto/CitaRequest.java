package pe.edu.upeu.garritas.citas.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
public class CitaRequest {

    @NotNull
    private Long idCliente;

    @NotNull
    private Long idMascota;

    @NotNull
    private Long idSede;

    @NotNull
    private Instant fechaHora;

    @Size(max = 255)
    private String motivo;
}
