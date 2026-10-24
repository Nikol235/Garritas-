package pe.edu.upeu.garritas.venta.dto;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pe.edu.upeu.garritas.venta.entity.EstadoVenta;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VentaResponse {
  private Long id;
  private Long sedeId;
  private String idCliente;
  private Instant fecha;
  private EstadoVenta estado;
  private BigDecimal total;
  private List<DetalleVentaResponse> detalles;
}
