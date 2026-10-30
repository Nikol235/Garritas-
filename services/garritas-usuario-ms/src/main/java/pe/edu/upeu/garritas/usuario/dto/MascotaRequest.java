package pe.edu.upeu.garritas.usuario.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MascotaRequest {

  @NotBlank
  @Size(max = 100)
  private String nombre;

  @NotBlank
  @Size(max = 50)
  private String especie;

  @Size(max = 100)
  private String raza;

  @jakarta.validation.constraints.NotNull
  private pe.edu.upeu.garritas.usuario.entity.UnidadEdad edadUnidad;

  @jakarta.validation.constraints.NotNull
  @jakarta.validation.constraints.Max(36500)
  @Min(0)
  @jakarta.validation.constraints.Digits(
      integer = 5,
      fraction = 0,
      message = "La edad debe ser un número entero de días o meses")
  private java.math.BigDecimal edad;
}
