package pe.edu.upeu.garritas.institucion.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "prestaciones")
@Getter
@Setter
@NoArgsConstructor
public class Prestacion {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 100)
  private String nombre;

  @Column(length = 255)
  private String descripcion;

  @Column(nullable = false)
  private Boolean activo = true;
}
