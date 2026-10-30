package pe.edu.upeu.garritas.catalogo.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.HashSet;
import java.util.Set;
import lombok.*;

@Entity
@Table(name = "productos")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Producto {

  @Version private Long version;

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "nombre", nullable = false, length = 100)
  private String nombre;

  @Column(name = "descripcion", length = 255)
  private String descripcion;

  @Column(name = "precio", nullable = false, precision = 10, scale = 2)
  private BigDecimal precio;

  @Column(name = "stock", nullable = false)
  private Integer stock;

  @Column(name = "activo", nullable = false)
  private Boolean activo;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "id_categoria")
  private Categoria categoria;

  @Builder.Default
  @ManyToMany(fetch = FetchType.LAZY)
  @JoinTable(
      name = "producto_categoria",
      joinColumns = @JoinColumn(name = "id_producto"),
      inverseJoinColumns = @JoinColumn(name = "id_categoria"))
  private Set<Categoria> categorias = new HashSet<>();
}
