package pe.edu.upeu.garritas.institucion.dto;

import jakarta.validation.constraints.*;

public record PrestacionRequest(
    @NotBlank @Size(max = 100) String nombre,
    @Size(max = 255) String descripcion,
    @NotNull Boolean activo) {}
