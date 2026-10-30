package pe.edu.upeu.garritas.usuario.entity;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.*;
import lombok.*;

@Entity
@Table(name = "suscripciones")
@Getter
@Setter
@NoArgsConstructor
public class Suscripcion {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_usuario")
  private Usuario usuario;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_plan")
  private Plan plan;

  @Column(name = "nombre_plan", nullable = false, length = 100)
  private String nombrePlan;

  @Column(nullable = false, length = 10)
  private String estado;

  @Column(name = "fecha_inicio", nullable = false)
  private Instant fechaInicio;

  @Column(name = "fecha_fin", nullable = false)
  private Instant fechaFin;

  @Version private Long version;

  @OneToMany(mappedBy = "suscripcion", cascade = CascadeType.ALL)
  @OrderBy("id ASC")
  private List<PeriodoSuscripcion> periodos = new ArrayList<>();
}
