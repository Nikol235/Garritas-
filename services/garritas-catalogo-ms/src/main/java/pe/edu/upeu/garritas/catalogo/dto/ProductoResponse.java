package pe.edu.upeu.garritas.catalogo.dto;

import java.math.BigDecimal;
import java.util.Set;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProductoResponse {
  private Long id;
  private String nombre;
  private String descripcion;
  private BigDecimal precio;
  private Integer stock;
  private Boolean activo;
  private CategoriaResponse categoria;
  private Set<CategoriaResponse> categorias;
}
