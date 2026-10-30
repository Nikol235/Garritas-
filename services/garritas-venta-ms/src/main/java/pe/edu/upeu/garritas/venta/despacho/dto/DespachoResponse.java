package pe.edu.upeu.garritas.venta.despacho.dto;

import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pe.edu.upeu.garritas.venta.despacho.entity.EstadoDespacho;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DespachoResponse {
  private Long zonaId;
  private Long transportistaId;
  private java.math.BigDecimal tarifa;
  private Long id;
  private Long idVenta;
  private String direccionEntrega;
  private String transportista;
  private EstadoDespacho estado;
  private Instant fechaEnvio;
  private Instant fechaEntregaEstimada;
}
