package pe.edu.upeu.garritas.usuario.dto;

import jakarta.validation.constraints.*;

public record SuscripcionRequest(@NotNull @Positive Long planId) {}
