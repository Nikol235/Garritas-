package pe.edu.upeu.garritas.usuario.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "mascotas")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Mascota {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "id_usuario", nullable = false)
  private Usuario usuario;

  @Column(name = "nombre", nullable = false, length = 100)
  private String nombre;

  @Column(name = "especie", nullable = false, length = 50)
  private String especie;

  @Column(name = "raza", length = 100)
  private String raza;

  @Enumerated(EnumType.STRING)
  @Column(name = "edad_unidad", nullable = false, length = 5)
  @Builder.Default
  private UnidadEdad edadUnidad = UnidadEdad.MESES;

  @Column(name = "edad")
  private Integer edad;
}
