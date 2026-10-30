package pe.edu.upeu.garritas.usuario.dto;

public record PlanResponse(
    Long id,
    String nombre,
    String descripcion,
    java.math.BigDecimal precio,
    Integer duracionDias,
    Boolean activo) {}
