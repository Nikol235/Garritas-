package pe.edu.upeu.garritas.institucion.dto;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public record OfertaRequest(
    @NotNull @Positive Long prestacionId,
    @NotNull @DecimalMin("0.00") @Digits(integer = 8, fraction = 2) BigDecimal precio,
    @NotNull @Min(30) @Max(240) Integer duracionMinutos,
    @NotNull Boolean activo) {}
