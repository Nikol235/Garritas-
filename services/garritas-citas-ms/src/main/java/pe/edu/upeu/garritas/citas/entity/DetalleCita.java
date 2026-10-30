package pe.edu.upeu.garritas.citas.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import lombok.*;

@Entity
@Table(name = "cita_detalles")
@Getter
@Setter
@NoArgsConstructor
public class DetalleCita {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_cita")
  private Cita cita;

  @Column(name = "id_prestacion", nullable = false)
  private Long prestacionId;

  @Column(nullable = false, length = 100)
  private String nombre;

  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal precio;

  @Column(name = "duracion_minutos", nullable = false)
  private Integer duracionMinutos;
}
