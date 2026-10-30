package pe.edu.upeu.garritas.envio.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import lombok.*;

@Entity
@Table(name = "coberturas")
@Getter
@Setter
@NoArgsConstructor
public class Cobertura {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_transportista")
  private Transportista transportista;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "id_zona")
  private Zona zona;

  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal tarifa;

  @Column(name = "dias_estimados", nullable = false)
  private Integer diasEstimados;

  @Column(nullable = false)
  private Boolean activo = true;
}
