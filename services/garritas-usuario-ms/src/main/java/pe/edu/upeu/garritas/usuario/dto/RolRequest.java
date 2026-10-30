package pe.edu.upeu.garritas.usuario.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RolRequest {

  @NotBlank
  @Size(max = 50)
  private String nombre;

  @Size(max = 255)
  private String descripcion;
}
