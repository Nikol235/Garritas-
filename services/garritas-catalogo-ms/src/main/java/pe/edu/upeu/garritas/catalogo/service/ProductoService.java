package pe.edu.upeu.garritas.catalogo.service;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.catalogo.dto.ProductoRequest;
import pe.edu.upeu.garritas.catalogo.dto.ProductoResponse;
import pe.edu.upeu.garritas.catalogo.entity.Categoria;
import pe.edu.upeu.garritas.catalogo.entity.Producto;
import pe.edu.upeu.garritas.catalogo.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.catalogo.mapper.ProductoMapper;
import pe.edu.upeu.garritas.catalogo.repository.CategoriaRepository;
import pe.edu.upeu.garritas.catalogo.repository.ProductoRepository;

@Transactional
@Service
@RequiredArgsConstructor
public class ProductoService {

  private final ProductoRepository productoRepository;
  private final ProductoMapper productoMapper;
  private final CategoriaRepository categoriaRepository;
  private final MeterRegistry meterRegistry;

  public List<ProductoResponse> listar() {
    return productoRepository.findAllConCategoria().stream()
        .map(productoMapper::toResponse)
        .toList();
  }

  public Page<ProductoResponse> listarPaginado(String q, Long categoriaId, Pageable pageable) {
    return productoRepository.buscar(q, categoriaId, pageable).map(productoMapper::toResponse);
  }

  public ProductoResponse obtener(Long id) {
    return productoMapper.toResponse(buscarOFallar(id));
  }

  public ProductoResponse crear(ProductoRequest request) {
    Producto producto = productoMapper.toEntity(request);
    asignarCategoriasDesdeRequest(producto, request);
    ProductoResponse response = productoMapper.toResponse(productoRepository.save(producto));
    meterRegistry.counter("garritas_productos_creados_total").increment();
    return response;
  }

  public ProductoResponse actualizar(Long id, ProductoRequest request) {
    Producto producto = buscarOFallar(id);
    producto.setNombre(request.getNombre());
    producto.setDescripcion(request.getDescripcion());
    producto.setPrecio(request.getPrecio());
    producto.setStock(request.getStock());
    producto.setActivo(request.getActivo());
    asignarCategoriasDesdeRequest(producto, request);
    return productoMapper.toResponse(productoRepository.save(producto));
  }

  public void eliminar(Long id) {
    // Preserve inventory and historical references while asynchronous sagas finish.
    Producto producto = buscarOFallar(id);
    producto.setActivo(false);
    productoRepository.save(producto);
  }

  private void asignarCategoriasDesdeRequest(Producto producto, ProductoRequest request) {
    Set<Categoria> cats = new HashSet<>();
    if (request.getCategoriaIds() != null && !request.getCategoriaIds().isEmpty()) {
      cats.addAll(categoriaRepository.findAllById(request.getCategoriaIds()));
      if (cats.size() != request.getCategoriaIds().size())
        throw new org.springframework.web.server.ResponseStatusException(
            org.springframework.http.HttpStatus.BAD_REQUEST,
            "Una de las categorías seleccionadas no existe");
    } else if (request.getCategoriaIds() == null && request.getCategoriaId() != null) {
      cats.add(buscarCategoriaOFallar(request.getCategoriaId()));
    }
    producto.setCategorias(cats);
    producto.setCategoria(
        cats.stream().min(java.util.Comparator.comparing(Categoria::getId)).orElse(null));
  }

  private Producto buscarOFallar(Long id) {
    return productoRepository
        .findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Producto no encontrado: " + id));
  }

  private Categoria buscarCategoriaOFallar(Long categoriaId) {
    return categoriaRepository
        .findById(categoriaId)
        .orElseThrow(
            () -> new ResourceNotFoundException("Categoria no encontrada: " + categoriaId));
  }
}
