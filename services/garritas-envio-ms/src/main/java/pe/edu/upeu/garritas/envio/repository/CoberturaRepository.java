package pe.edu.upeu.garritas.envio.repository;

import java.util.*;
import org.springframework.data.jpa.repository.*;
import pe.edu.upeu.garritas.envio.entity.Cobertura;

public interface CoberturaRepository extends JpaRepository<Cobertura, Long> {
  @EntityGraph(attributePaths = {"transportista", "zona"})
  List<Cobertura> findAll();

  @EntityGraph(attributePaths = {"transportista", "zona"})
  Optional<Cobertura> findByTransportistaIdAndZonaId(Long t, Long z);
}
