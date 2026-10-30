package pe.edu.upeu.garritas.catalogo.repository;

import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.upeu.garritas.catalogo.entity.Producto;

public interface ProductoRepository extends JpaRepository<Producto, Long> {

  @Query(
      "SELECT DISTINCT p FROM Producto p LEFT JOIN FETCH p.categoria LEFT JOIN FETCH p.categorias")
  List<Producto> findAllConCategoria();

  @Query(
      value =
          "SELECT DISTINCT p FROM Producto p LEFT JOIN p.categorias c LEFT JOIN p.categoria"
              + " principal WHERE (:q IS NULL OR :q = '' OR LOWER(p.nombre) LIKE LOWER(CONCAT('%',"
              + " :q, '%')) OR LOWER(COALESCE(p.descripcion, '')) LIKE LOWER(CONCAT('%', :q, '%')))"
              + " AND (:categoriaId IS NULL OR :categoriaId = 0 OR c.id = :categoriaId OR"
              + " principal.id = :categoriaId)",
      countQuery =
          "SELECT count(DISTINCT p) FROM Producto p LEFT JOIN p.categorias c LEFT JOIN p.categoria"
              + " principal WHERE (:q IS NULL OR :q = '' OR LOWER(p.nombre) LIKE LOWER(CONCAT('%',"
              + " :q, '%')) OR LOWER(COALESCE(p.descripcion, '')) LIKE LOWER(CONCAT('%', :q, '%')))"
              + " AND (:categoriaId IS NULL OR :categoriaId = 0 OR c.id = :categoriaId OR"
              + " principal.id = :categoriaId)")
  Page<Producto> buscar(
      @Param("q") String q, @Param("categoriaId") Long categoriaId, Pageable pageable);
}
