package pe.edu.upeu.garritas.usuario.dto;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UsuarioResponse {
  private Long id;
  private String nombre;
  private String email;
  private String telefono;
  private String direccion;
  private String dni;
  private List<MascotaResponse> mascotas;
  private List<RolResponse> roles;
}
