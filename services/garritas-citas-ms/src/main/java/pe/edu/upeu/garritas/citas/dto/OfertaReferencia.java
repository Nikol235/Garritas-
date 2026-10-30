package pe.edu.upeu.garritas.citas.dto;

import java.math.BigDecimal;

public record OfertaReferencia(
    Long prestacionId,
    String nombre,
    BigDecimal precio,
    Integer duracionMinutos,
    Boolean activo,
    java.util.List<Componente> componentes) {
  public OfertaReferencia(
      Long id, String nombre, BigDecimal precio, Integer duracion, Boolean activo) {
    this(id, nombre, precio, duracion, activo, java.util.List.of());
  }

  public record Componente(Long id, String nombre) {}
}
