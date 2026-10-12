package pe.edu.upeu.garritas.envio.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
public class EnvioRequest {

    @NotNull
    private Long idVenta;

    @NotBlank
    @Size(max = 255)
    private String direccionEntrega;

    @Size(max = 100)
    private String transportista;

    private Instant fechaEntregaEstimada;
}
