package pe.edu.upeu.garritas.envio.mapper;

import pe.edu.upeu.garritas.envio.dto.EnvioRequest;
import pe.edu.upeu.garritas.envio.dto.EnvioResponse;
import pe.edu.upeu.garritas.envio.entity.EstadoEnvio;
import pe.edu.upeu.garritas.envio.entity.Envio;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class EnvioMapper {

    public Envio toEntity(EnvioRequest request) {
        return Envio.builder()
                .idVenta(request.getIdVenta())
                .direccionEntrega(request.getDireccionEntrega())
                .transportista(request.getTransportista())
                .estado(EstadoEnvio.PENDIENTE)
                .fechaEnvio(Instant.now())
                .fechaEntregaEstimada(request.getFechaEntregaEstimada())
                .build();
    }

    public EnvioResponse toResponse(Envio envio) {
        return EnvioResponse.builder()
                .id(envio.getId())
                .idVenta(envio.getIdVenta())
                .direccionEntrega(envio.getDireccionEntrega())
                .transportista(envio.getTransportista())
                .estado(envio.getEstado())
                .fechaEnvio(envio.getFechaEnvio())
                .fechaEntregaEstimada(envio.getFechaEntregaEstimada())
                .build();
    }
}
