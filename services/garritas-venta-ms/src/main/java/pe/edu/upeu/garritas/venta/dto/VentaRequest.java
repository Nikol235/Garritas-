package pe.edu.upeu.garritas.venta.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class VentaRequest {
  @NotNull
  @Pattern(regexp = "TARJETA|YAPE|PLIN|TRANSFERENCIA")
  private String metodoPago;

  @NotEmpty
  @Size(max = 50)
  @Valid
  private List<DetalleVentaRequest> detalles;
}
