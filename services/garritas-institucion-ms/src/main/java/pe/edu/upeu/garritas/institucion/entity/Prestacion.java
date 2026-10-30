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

  @ManyToMany(fetch = FetchType.LAZY)
  @JoinTable(
      name = "prestacion_componentes",
      joinColumns = @JoinColumn(name = "id_paquete"),
      inverseJoinColumns = @JoinColumn(name = "id_componente"))
  private java.util.Set<Prestacion> componentes = new java.util.HashSet<>();
}
