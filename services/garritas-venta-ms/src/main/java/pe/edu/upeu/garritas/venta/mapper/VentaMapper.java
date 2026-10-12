package pe.edu.upeu.garritas.venta.mapper;

import pe.edu.upeu.garritas.venta.dto.VentaRequest;
import pe.edu.upeu.garritas.venta.dto.VentaResponse;
import pe.edu.upeu.garritas.venta.entity.EstadoVenta;
import pe.edu.upeu.garritas.venta.entity.Venta;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;

@Component
@RequiredArgsConstructor
public class VentaMapper {

    private final DetalleVentaMapper detalleVentaMapper;

    public Venta toEntity(VentaRequest request) {
        Venta venta = Venta.builder()
                .idCliente(request.getIdCliente())
                .fecha(Instant.now())
                .estado(EstadoVenta.CARRITO)
                .total(BigDecimal.ZERO)
                .build();

        request.getDetalles().forEach(d -> {
            var detalle = detalleVentaMapper.toEntity(d);
            detalle.setVenta(venta);
            venta.getDetalles().add(detalle);
        });

        BigDecimal total = venta.getDetalles().stream()
                .map(pe.edu.upeu.garritas.venta.entity.DetalleVenta::getSubtotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        venta.setTotal(total);
        return venta;
    }

    public VentaResponse toResponse(Venta venta) {
        return VentaResponse.builder()
                .id(venta.getId())
                .idCliente(venta.getIdCliente())
                .fecha(venta.getFecha())
                .estado(venta.getEstado())
                .total(venta.getTotal())
                .detalles(venta.getDetalles().stream().map(detalleVentaMapper::toResponse).toList())
                .build();
    }
}
