package pe.edu.upeu.garritas.institucion.repository;

import java.util.*;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.institucion.entity.SedePrestacion;

public interface SedePrestacionRepository extends JpaRepository<SedePrestacion, Long> {
  @EntityGraph(attributePaths = {"sede", "prestacion"})
  List<SedePrestacion> findBySedeId(Long id);

  Optional<SedePrestacion> findBySedeIdAndPrestacionId(Long sede, Long prestacion);
}
