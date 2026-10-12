package pe.edu.upeu.garritas.venta.mapper;

import pe.edu.upeu.garritas.venta.dto.DetalleVentaRequest;
import pe.edu.upeu.garritas.venta.dto.DetalleVentaResponse;
import pe.edu.upeu.garritas.venta.entity.DetalleVenta;
import org.springframework.stereotype.Component;

@Component
public class DetalleVentaMapper {

    public DetalleVenta toEntity(DetalleVentaRequest request) {
        var subtotal = request.getPrecioUnitario().multiply(java.math.BigDecimal.valueOf(request.getCantidad()));
        return DetalleVenta.builder()
                .idProducto(request.getIdProducto())
                .cantidad(request.getCantidad())
                .precioUnitario(request.getPrecioUnitario())
                .subtotal(subtotal)
                .build();
    }

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
