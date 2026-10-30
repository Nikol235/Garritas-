package pe.edu.upeu.garritas.venta.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class VentaRequest {
  @NotNull @Positive private Long sedeId;

  @NotNull
  @Pattern(regexp = "RECOJO|ENVIO")
  private String tipoEntrega = "RECOJO";

  @Size(max = 255)
  private String direccionEntrega;

  @Positive private Long zonaId;
  @Positive private Long transportistaId;

  @DecimalMin("0.00")
  @Digits(integer = 8, fraction = 2)
  private java.math.BigDecimal tarifaCotizada;

  @NotNull
  @Pattern(regexp = "TARJETA|YAPE|PLIN|TRANSFERENCIA")
  private String metodoPago;

  @NotEmpty
  @Size(max = 50)
  @Valid
  private List<DetalleVentaRequest> detalles;
}
