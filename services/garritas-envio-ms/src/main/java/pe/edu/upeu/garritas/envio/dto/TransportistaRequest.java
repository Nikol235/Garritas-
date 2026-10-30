package pe.edu.upeu.garritas.envio.dto;

import jakarta.validation.constraints.*;

public record TransportistaRequest(
    @NotBlank @Size(max = 100) String nombre,
    @Size(max = 20) String telefono,
    @NotNull Boolean activo) {}
