package pe.edu.upeu.garritas.institucion.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SedeRequest {

  @NotBlank
  @Size(max = 100)
  private String nombre;

  @NotBlank
  @Size(max = 255)
  private String direccion;

  @NotBlank
  @Size(max = 100)
  private String ciudad;

  @Size(max = 20)
  @jakarta.validation.constraints.Pattern(
      regexp = "^$|9[0-9]{8}",
      message = "El celular peruano debe tener 9 dígitos y comenzar con 9")
  private String telefono;

  @NotNull private Boolean activo;
}
