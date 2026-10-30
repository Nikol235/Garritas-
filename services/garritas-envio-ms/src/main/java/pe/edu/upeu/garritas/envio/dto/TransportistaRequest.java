package pe.edu.upeu.garritas.envio.dto;

import jakarta.validation.constraints.*;

public record TransportistaRequest(
    @NotBlank @Size(max = 100) String nombre,
    @jakarta.validation.constraints.Pattern(
            regexp = "^$|9[0-9]{8}",
            message = "El celular peruano debe tener 9 dígitos y comenzar con 9")
        String telefono,
    @NotNull Boolean activo) {}
