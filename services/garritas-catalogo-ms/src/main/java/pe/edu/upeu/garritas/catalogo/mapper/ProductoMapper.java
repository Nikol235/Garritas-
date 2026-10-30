package pe.edu.upeu.garritas.catalogo.mapper;

import java.util.Collections;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import pe.edu.upeu.garritas.catalogo.dto.CategoriaResponse;
import pe.edu.upeu.garritas.catalogo.dto.ProductoRequest;
import pe.edu.upeu.garritas.catalogo.dto.ProductoResponse;
import pe.edu.upeu.garritas.catalogo.entity.Producto;

@Component
@RequiredArgsConstructor
public class ProductoMapper {

  private final CategoriaMapper categoriaMapper;

  public Producto toEntity(ProductoRequest request) {
    if (request == null) return null;
    return Producto.builder()
        .nombre(request.getNombre())
        .descripcion(request.getDescripcion())
        .precio(request.getPrecio())
        .stock(request.getStock())
        .activo(request.getActivo())
        .build();
  }

  public ProductoResponse toResponse(Producto producto) {
    if (producto == null) return null;
    Set<CategoriaResponse> categoriasResp =
        (producto.getCategorias() == null || producto.getCategorias().isEmpty())
            ? (producto.getCategoria() != null
                ? Set.of(categoriaMapper.toResponse(producto.getCategoria()))
                : Collections.emptySet())
            : producto.getCategorias().stream()
                .map(categoriaMapper::toResponse)
                .collect(Collectors.toSet());

    CategoriaResponse primaryCategoria =
        producto.getCategoria() != null
            ? categoriaMapper.toResponse(producto.getCategoria())
            : (!categoriasResp.isEmpty() ? categoriasResp.iterator().next() : null);

    return ProductoResponse.builder()
        .id(producto.getId())
        .nombre(producto.getNombre())
        .descripcion(producto.getDescripcion())
        .precio(producto.getPrecio())
        .stock(producto.getStock())
        .activo(producto.getActivo())
        .categoria(primaryCategoria)
        .categorias(categoriasResp)
        .build();
  }
}
