package pe.edu.upeu.garritas.pago.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import lombok.*;

@Entity
@Table(name = "pagos")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Pago {

  @Column(name = "id_cliente")
  private String idCliente;

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "id_venta", nullable = false)
  private Long idVenta;

  @Column(name = "monto", nullable = false, precision = 10, scale = 2)
  private BigDecimal monto;

  @Enumerated(EnumType.STRING)
  @Column(name = "metodo", nullable = false, length = 20)
  private MetodoPago metodo;

  @Enumerated(EnumType.STRING)
  @Column(name = "estado", nullable = false, length = 20)
  private EstadoPago estado;

  @Column(name = "fecha_pago", nullable = false)
  private Instant fechaPago;

  @Column(name = "referencia_externa", length = 100)
  private String referenciaExterna;
}
