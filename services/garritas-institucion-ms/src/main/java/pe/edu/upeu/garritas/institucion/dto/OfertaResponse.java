package pe.edu.upeu.garritas.institucion.dto;

import java.math.BigDecimal;

public record OfertaResponse(
    Long id,
    Long sedeId,
    Long prestacionId,
    String nombre,
    BigDecimal precio,
    Integer duracionMinutos,
    Boolean activo,
    java.util.List<ComponenteResponse> componentes) {}
