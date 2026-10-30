package pe.edu.upeu.garritas.usuario.dto;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public record PlanRequest(
    @NotBlank @Size(max = 100) String nombre,
    @Size(max = 255) String descripcion,
    @NotNull @DecimalMin("0.01") @Digits(integer = 8, fraction = 2) BigDecimal precio,
    @NotNull @Min(1) @Max(366) Integer duracionDias,
    @NotNull Boolean activo) {}
