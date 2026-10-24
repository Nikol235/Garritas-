package pe.edu.upeu.garritas.venta.mapper;

import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.venta.dto.DetalleVentaResponse;
import pe.edu.upeu.garritas.venta.entity.DetalleVenta;

@Component
public class DetalleVentaMapper {

  public DetalleVentaResponse toResponse(DetalleVenta detalle) {
    return DetalleVentaResponse.builder()
        .id(detalle.getId())
        .idProducto(detalle.getIdProducto())
        .cantidad(detalle.getCantidad())
        .precioUnitario(detalle.getPrecioUnitario())
        .subtotal(detalle.getSubtotal())
        .build();
  }
}
