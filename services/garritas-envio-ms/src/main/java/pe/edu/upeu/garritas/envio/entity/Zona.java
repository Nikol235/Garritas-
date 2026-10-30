package pe.edu.upeu.garritas.envio.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "zonas")
@Getter
@Setter
@NoArgsConstructor
public class Zona {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 100)
  private String nombre;

  @Column(nullable = false, length = 100)
  private String ciudad;

  @Column(nullable = false)
  private Boolean activo = true;
}
