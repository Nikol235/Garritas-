package pe.edu.upeu.garritas.institucion.dto;

import jakarta.validation.constraints.*;

public record PrestacionRequest(
    @NotBlank @Size(max = 100) String nombre,
    @Size(max = 255) String descripcion,
    @NotNull Boolean activo,
    @Size(max = 8) java.util.Set<@NotNull @Positive Long> componenteIds) {
  public PrestacionRequest(String nombre, String descripcion, Boolean activo) {
    this(nombre, descripcion, activo, java.util.Set.of());
  }
}
