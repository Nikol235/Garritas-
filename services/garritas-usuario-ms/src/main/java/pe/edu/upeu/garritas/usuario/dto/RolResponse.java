package pe.edu.upeu.garritas.usuario.dto;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RolResponse {
  private Long id;
  private String nombre;
  private String descripcion;
}

