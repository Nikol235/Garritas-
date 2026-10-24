package pe.edu.upeu.garritas.bienestar.entity;

import jakarta.persistence.*;
import java.util.*;
import lombok.*;

@Entity
@Table(name = "profesionales")
@Getter
@Setter
@NoArgsConstructor
public class Profesional {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 100)
  private String nombre;

  @Column(nullable = false, unique = true, length = 150)
  private String email;

  @Column(length = 20)
  private String telefono;

  @Column(name = "id_sede")
  private Long sedeId;

  @Column(nullable = false)
  private Boolean activo;

  @ManyToMany
  @JoinTable(
      name = "profesional_especialidad",
      joinColumns = @JoinColumn(name = "id_profesional"),
      inverseJoinColumns = @JoinColumn(name = "id_especialidad"))
  private Set<Especialidad> especialidades = new HashSet<>();
}
