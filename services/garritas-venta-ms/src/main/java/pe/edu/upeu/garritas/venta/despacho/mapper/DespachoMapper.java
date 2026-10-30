package pe.edu.upeu.garritas.venta.despacho.mapper;

import java.time.Instant;
import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.venta.despacho.dto.DespachoRequest;
import pe.edu.upeu.garritas.venta.despacho.dto.DespachoResponse;
import pe.edu.upeu.garritas.venta.despacho.entity.Despacho;
import pe.edu.upeu.garritas.venta.despacho.entity.EstadoDespacho;

@Component
public class DespachoMapper {

  public Despacho toEntity(DespachoRequest request) {
    return Despacho.builder()
        .idVenta(request.getIdVenta())
        .direccionEntrega(request.getDireccionEntrega())
        .transportista(request.getTransportista())
        .estado(EstadoDespacho.PENDIENTE)
        .fechaEnvio(Instant.now())
        .fechaEntregaEstimada(request.getFechaEntregaEstimada())
        .build();
  }

  public DespachoResponse toResponse(Despacho envio) {
    return DespachoResponse.builder()
        .id(envio.getId())
        .zonaId(envio.getZonaId())
        .transportistaId(envio.getTransportistaId())
        .tarifa(envio.getTarifa())
        .idVenta(envio.getIdVenta())
        .direccionEntrega(envio.getDireccionEntrega())
        .transportista(envio.getTransportista())
        .estado(envio.getEstado())
        .fechaEnvio(envio.getFechaEnvio())
        .fechaEntregaEstimada(envio.getFechaEntregaEstimada())
        .build();
  }
}
