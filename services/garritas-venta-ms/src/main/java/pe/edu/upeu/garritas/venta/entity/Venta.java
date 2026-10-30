package pe.edu.upeu.garritas.venta.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import lombok.*;

@Entity
@Table(name = "ventas")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Venta {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "id_cliente", nullable = false)
  private String idCliente;

  @Column(name = "fecha", nullable = false)
  private Instant fecha;

  @Enumerated(EnumType.STRING)
  @Column(name = "estado", nullable = false, length = 20)
  private EstadoVenta estado;

  @Column(name = "total", nullable = false, precision = 10, scale = 2)
  private BigDecimal total;

  @Builder.Default
  @Column(name = "tipo_entrega", nullable = false)
  private String tipoEntrega = "RECOJO";

  @Builder.Default
  @Column(name = "costo_envio", nullable = false)
  private BigDecimal costoEnvio = BigDecimal.ZERO;

  private String direccionEntrega;
  private Long zonaId;
  private Long transportistaId;
  private String transportistaNombre;
  private Integer diasEntrega;

  @Column(name = "id_sede")
  private Long sedeId;

  @Column(name = "metodo_pago", nullable = false)
  private String metodoPago;

  @Column(name = "idempotency_key")
  private java.util.UUID idempotencyKey;

  @Builder.Default
  @OneToMany(
      mappedBy = "venta",
      cascade = CascadeType.ALL,
      orphanRemoval = true,
      fetch = FetchType.LAZY)
  private List<DetalleVenta> detalles = new ArrayList<>();
}
