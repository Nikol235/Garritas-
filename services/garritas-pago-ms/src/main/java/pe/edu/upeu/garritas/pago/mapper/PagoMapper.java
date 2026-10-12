package pe.edu.upeu.garritas.pago.mapper;

import pe.edu.upeu.garritas.pago.dto.PagoRequest;
import pe.edu.upeu.garritas.pago.dto.PagoResponse;
import pe.edu.upeu.garritas.pago.entity.EstadoPago;
import pe.edu.upeu.garritas.pago.entity.Pago;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class PagoMapper {

    public Pago toEntity(PagoRequest request) {
        return Pago.builder()
                .idVenta(request.getIdVenta())
                .monto(request.getMonto())
                .metodo(request.getMetodo())
                .estado(EstadoPago.PENDIENTE)
                .fechaPago(Instant.now())
                .build();
    }

    public PagoResponse toResponse(Pago pago) {
        return PagoResponse.builder()
                .id(pago.getId())
                .idVenta(pago.getIdVenta())
                .monto(pago.getMonto())
                .metodo(pago.getMetodo())
                .estado(pago.getEstado())
                .fechaPago(pago.getFechaPago())
                .referenciaExterna(pago.getReferenciaExterna())
                .build();
    }
}
