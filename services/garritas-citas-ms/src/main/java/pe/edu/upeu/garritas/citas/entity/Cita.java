package pe.edu.upeu.garritas.citas.entity;

import jakarta.persistence.*;
import java.time.Instant;
import lombok.*;

@Entity
@Table(name = "citas")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Cita {
  @Version private Long version;

  @Column(nullable = false, precision = 10, scale = 2)
  @Builder.Default
  private java.math.BigDecimal total = java.math.BigDecimal.ZERO;

  @Column(name = "duracion_minutos", nullable = false)
  @Builder.Default
  private Integer duracionMinutos = 30;

  @OneToMany(mappedBy = "cita", cascade = CascadeType.ALL)
  @OrderBy("id ASC")
  @Builder.Default
  private java.util.List<DetalleCita> detalles = new java.util.ArrayList<>();

  @Column(name = "id_profesional")
  private Long profesionalId;

  @Column(name = "nombre_mascota", length = 100)
  private String nombreMascota;

  @Column(name = "nombre_sede", length = 100)
  private String nombreSede;

  @Column(name = "nombre_profesional", length = 100)
  private String nombreProfesional;

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "id_cliente", nullable = false)
  private String idCliente;

  @Column(name = "id_mascota", nullable = false)
  private Long idMascota;

  @Column(name = "id_sede", nullable = false)
  private Long idSede;

  @Column(name = "fecha_hora", nullable = false)
  private Instant fechaHora;

  @Column(name = "motivo", length = 255)
  private String motivo;

  @Enumerated(EnumType.STRING)
  @Column(name = "estado", nullable = false, length = 20)
  private EstadoCita estado;
}
