package pe.edu.upeu.garritas.envio.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "transportistas")
@Getter
@Setter
@NoArgsConstructor
public class Transportista {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 100)
  private String nombre;

  @Column(length = 20)
  private String telefono;

  @Column(nullable = false)
  private Boolean activo = true;
}
