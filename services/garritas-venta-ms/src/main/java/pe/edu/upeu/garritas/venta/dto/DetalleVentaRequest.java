package pe.edu.upeu.garritas.venta.dto;

import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class DetalleVentaRequest {
  @NotNull @Positive private Long idProducto;

  @NotNull
  @Min(1)
  @Max(10000)
  private Integer cantidad;
}
