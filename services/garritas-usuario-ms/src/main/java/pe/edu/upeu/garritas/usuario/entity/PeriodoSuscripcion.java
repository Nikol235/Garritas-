package pe.edu.upeu.garritas.usuario.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;
import lombok.*;

@Entity
@Table(name = "suscripcion_periodos")
@Getter
@Setter
@NoArgsConstructor
public class PeriodoSuscripcion {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_suscripcion")
  private Suscripcion suscripcion;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_usuario")
  private Usuario usuario;

  @Column(name = "idempotency_key", nullable = false)
  private UUID idempotencyKey;

  @Column(nullable = false, length = 10)
  private String tipo;

  @Column(name = "fecha_inicio", nullable = false)
  private Instant fechaInicio;

  @Column(name = "fecha_fin", nullable = false)
  private Instant fechaFin;

  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal precio;
}
