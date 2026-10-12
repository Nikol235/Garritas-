package pe.edu.upeu.garritas.venta.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class VentaRequest {

    @NotNull
    private Long idCliente;

    @NotEmpty
    @Valid
    private List<DetalleVentaRequest> detalles;
}
