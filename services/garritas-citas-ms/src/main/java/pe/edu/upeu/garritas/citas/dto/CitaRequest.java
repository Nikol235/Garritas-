package pe.edu.upeu.garritas.citas.dto;

import jakarta.validation.constraints.*;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CitaRequest {
  @NotEmpty
  @Size(max = 8)
  private java.util.List<@NotNull @Positive Long> prestacionIds;

  @NotNull @Positive private Long idMascota;
  @NotNull @Positive private Long idSede;
  @NotNull @Positive private Long profesionalId;
  @NotNull @Future private Instant fechaHora;

  @NotBlank
  @Size(max = 255)
  private String motivo;
}
