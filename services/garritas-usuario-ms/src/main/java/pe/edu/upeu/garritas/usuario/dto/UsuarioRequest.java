package pe.edu.upeu.garritas.usuario.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Set;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UsuarioRequest {

  @NotBlank
  @Size(max = 100)
  private String nombre;

  @NotBlank
  @Email
  @Size(max = 150)
  private String email;

  @Size(max = 20)
  @jakarta.validation.constraints.Pattern(
      regexp = "^$|9[0-9]{8}",
      message = "El celular peruano debe tener 9 dígitos y comenzar con 9")
  private String telefono;

  @Size(max = 255)
  private String direccion;

  @Size(max = 20)
  @jakarta.validation.constraints.Pattern(
      regexp = "^$|[0-9]{8}",
      message = "El DNI debe tener 8 dígitos")
  private String dni;

  private Set<Long> roleIds;
}
