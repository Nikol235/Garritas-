package pe.edu.upeu.garritas.envio.dto;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public record CoberturaRequest(
    @NotNull @Positive Long transportistaId,
    @NotNull @Positive Long zonaId,
    @NotNull @DecimalMin("0.00") @Digits(integer = 8, fraction = 2) BigDecimal tarifa,
    @NotNull @Min(1) @Max(30) Integer diasEstimados,
    @NotNull Boolean activo) {}
