package pe.edu.upeu.garritas.citas.dto;

import java.math.BigDecimal;

public record OfertaReferencia(
    Long prestacionId, String nombre, BigDecimal precio, Integer duracionMinutos, Boolean activo) {}
