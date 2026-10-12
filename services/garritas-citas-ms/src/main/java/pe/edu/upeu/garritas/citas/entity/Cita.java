package pe.edu.upeu.garritas.citas.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

@Entity
@Table(name = "citas")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Cita {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "id_cliente", nullable = false)
    private Long idCliente;

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
