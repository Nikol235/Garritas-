package pe.edu.upeu.garritas.envio.dto;

import jakarta.validation.constraints.*;

public record ZonaRequest(
    @NotBlank @Size(max = 100) String nombre,
    @NotBlank @Size(max = 100) String ciudad,
    @NotNull Boolean activo) {}
