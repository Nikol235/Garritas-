package pe.edu.upeu.garritas.usuario.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import java.util.HashSet;
import java.util.Set;
import lombok.*;

@Entity
@Table(name = "rol")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class Rol {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @EqualsAndHashCode.Include
  private Long id;

  @Column(name = "nombre", nullable = false, unique = true, length = 50)
  @EqualsAndHashCode.Include
  private String nombre;

  @Column(name = "descripcion", length = 255)
  private String descripcion;

  @JsonIgnore
  @Builder.Default
  @ManyToMany(mappedBy = "roles", fetch = FetchType.LAZY)
  private Set<Usuario> usuarios = new HashSet<>();
}

