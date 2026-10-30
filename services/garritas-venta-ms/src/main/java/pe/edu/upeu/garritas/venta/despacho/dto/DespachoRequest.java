package pe.edu.upeu.garritas.venta.despacho.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class DespachoRequest {
  @NotNull @jakarta.validation.constraints.Positive private Long zonaId;
  @NotNull @jakarta.validation.constraints.Positive private Long transportistaId;

  @NotNull @jakarta.validation.constraints.Positive private Long idVenta;

  @NotBlank
  @Size(max = 255)
  private String direccionEntrega;

  @Size(max = 100)
  private String transportista;

  private Instant fechaEntregaEstimada;
}
