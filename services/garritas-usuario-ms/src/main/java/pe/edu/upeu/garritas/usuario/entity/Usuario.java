package pe.edu.upeu.garritas.usuario.entity;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import lombok.*;

@Entity
@Table(name = "usuarios")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Usuario {

  @Column(name = "subject", unique = true, length = 100)
  private String subject;

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "nombre", nullable = false, length = 100)
  private String nombre;

  @Column(name = "email", nullable = false, length = 150, unique = true)
  private String email;

  @Column(name = "telefono", length = 20)
  private String telefono;

  @Column(name = "direccion", length = 255)
  private String direccion;

  @Column(name = "dni", length = 20)
  private String dni;

  @Builder.Default
  @OneToMany(
      mappedBy = "usuario",
      cascade = CascadeType.ALL,
      orphanRemoval = true,
      fetch = FetchType.LAZY)
  private List<Mascota> mascotas = new ArrayList<>();

  @Builder.Default
  @ManyToMany(fetch = FetchType.LAZY)
  @JoinTable(
      name = "usuario_rol",
      joinColumns = @JoinColumn(name = "id_usuario"),
      inverseJoinColumns = @JoinColumn(name = "id_rol"))
  private Set<Rol> roles = new HashSet<>();
}
