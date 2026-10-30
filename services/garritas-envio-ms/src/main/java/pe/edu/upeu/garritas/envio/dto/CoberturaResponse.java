package pe.edu.upeu.garritas.envio.dto;

import java.math.BigDecimal;

public record CoberturaResponse(
    Long id,
    Long transportistaId,
    Long zonaId,
    String transportista,
    String zona,
    BigDecimal tarifa,
    Integer diasEstimados,
    Boolean activo) {}
