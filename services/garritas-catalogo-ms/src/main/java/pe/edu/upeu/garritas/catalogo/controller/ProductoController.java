package pe.edu.upeu.garritas.catalogo.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.catalogo.dto.ProductoRequest;
import pe.edu.upeu.garritas.catalogo.dto.ProductoResponse;
import pe.edu.upeu.garritas.catalogo.service.ProductoService;

@RestController
@RequestMapping("/api/v1/productos")
@RequiredArgsConstructor
public class ProductoController {

  private final ProductoService productoService;

  @GetMapping
  public Object listar(
      @RequestParam(required = false) String q,
      @RequestParam(required = false) Long categoriaId,
      @RequestParam(required = false) Integer page,
      @RequestParam(required = false, defaultValue = "12") int size) {
    if (size < 1 || size > 100 || (page != null && page < 0))
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.BAD_REQUEST,
          "La página debe ser >= 0 y el tamaño entre 1 y 100");
    if (page != null || (q != null && !q.isBlank()) || (categoriaId != null && categoriaId > 0)) {
      int pageNum = (page != null && page >= 0) ? page : 0;
      return productoService.listarPaginado(
          q, categoriaId, PageRequest.of(pageNum, size, Sort.by(Sort.Direction.DESC, "id")));
    }
    return productoService.listar();
  }

  @GetMapping("/{id}")
  public ProductoResponse obtener(@PathVariable Long id) {
    return productoService.obtener(id);
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public ProductoResponse crear(@Valid @RequestBody ProductoRequest request) {
    return productoService.crear(request);
  }

  @PutMapping("/{id}")
  public ProductoResponse actualizar(
      @PathVariable Long id, @Valid @RequestBody ProductoRequest request) {
    return productoService.actualizar(id, request);
  }

  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void eliminar(@PathVariable Long id) {
    productoService.eliminar(id);
  }
}
