package pe.edu.upeu.garritas.usuario.dto;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

public record SuscripcionResponse(
    Long id,
    Long usuarioId,
    String cliente,
    Long planId,
    String nombrePlan,
    String estado,
    Instant fechaInicio,
    Instant fechaFin,
    BigDecimal totalContratado,
    List<PeriodoResponse> periodos) {
  public record PeriodoResponse(
      Long id, String tipo, Instant fechaInicio, Instant fechaFin, BigDecimal precio) {}
}
