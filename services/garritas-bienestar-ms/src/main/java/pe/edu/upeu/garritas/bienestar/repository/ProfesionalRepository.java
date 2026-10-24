package pe.edu.upeu.garritas.bienestar.repository;

import java.util.*;
import org.springframework.data.jpa.repository.*;
import pe.edu.upeu.garritas.bienestar.entity.Profesional;

public interface ProfesionalRepository extends JpaRepository<Profesional, Long> {
  @Override
  @EntityGraph(attributePaths = "especialidades")
  List<Profesional> findAll();

  @Override
  @EntityGraph(attributePaths = "especialidades")
  Optional<Profesional> findById(Long id);

  long countByEspecialidades_Id(Long id);
}
