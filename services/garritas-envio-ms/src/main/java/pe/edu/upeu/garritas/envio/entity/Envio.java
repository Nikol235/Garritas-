package pe.edu.upeu.garritas.envio.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

@Entity
@Table(name = "envios")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Envio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "id_venta", nullable = false)
    private Long idVenta;

    @Column(name = "direccion_entrega", nullable = false, length = 255)
    private String direccionEntrega;

    @Column(name = "transportista", length = 100)
    private String transportista;

    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false, length = 20)
    private EstadoEnvio estado;

    @Column(name = "fecha_envio")
    private Instant fechaEnvio;

    @Column(name = "fecha_entrega_estimada")
    private Instant fechaEntregaEstimada;
}
