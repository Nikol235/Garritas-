package pe.edu.upeu.garritas.citas.dto;

import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pe.edu.upeu.garritas.citas.entity.EstadoCita;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CitaResponse {
  private java.math.BigDecimal total;
  private Integer duracionMinutos;
  private java.util.List<DetalleCitaResponse> detalles;
  private Long id;
  private Long profesionalId;
  private String nombreMascota;
  private String nombreSede;
  private String nombreProfesional;
  private String idCliente;
  private Long idMascota;
  private Long idSede;
  private Instant fechaHora;
  private String motivo;
  private EstadoCita estado;
}
