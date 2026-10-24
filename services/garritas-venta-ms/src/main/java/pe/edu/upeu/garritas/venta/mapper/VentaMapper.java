package pe.edu.upeu.garritas.venta.mapper;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.venta.dto.VentaResponse;
import pe.edu.upeu.garritas.venta.entity.Venta;

@Component
@RequiredArgsConstructor
public class VentaMapper {

  private final DetalleVentaMapper detalleVentaMapper;

  public VentaResponse toResponse(Venta venta) {
    return VentaResponse.builder()
        .id(venta.getId())
        .sedeId(venta.getSedeId())
        .idCliente(venta.getIdCliente())
        .fecha(venta.getFecha())
        .estado(venta.getEstado())
        .total(venta.getTotal())
        .detalles(venta.getDetalles().stream().map(detalleVentaMapper::toResponse).toList())
        .build();
  }
}
