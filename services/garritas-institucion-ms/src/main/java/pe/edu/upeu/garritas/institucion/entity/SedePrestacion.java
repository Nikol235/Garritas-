package pe.edu.upeu.garritas.institucion.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import lombok.*;

@Entity
@Table(name = "sede_prestacion")
@Getter
@Setter
@NoArgsConstructor
public class SedePrestacion {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_sede")
  private Sede sede;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_prestacion")
  private Prestacion prestacion;

  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal precio;

  @Column(name = "duracion_minutos", nullable = false)
  private Integer duracionMinutos;

  @Column(nullable = false)
  private Boolean activo = true;
}
