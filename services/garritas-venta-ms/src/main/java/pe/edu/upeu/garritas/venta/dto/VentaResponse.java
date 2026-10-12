package pe.edu.upeu.garritas.venta.dto;

import pe.edu.upeu.garritas.venta.entity.EstadoVenta;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VentaResponse {
    private Long id;
    private Long idCliente;
    private Instant fecha;
    private EstadoVenta estado;
    private BigDecimal total;
    private List<DetalleVentaResponse> detalles;
}
