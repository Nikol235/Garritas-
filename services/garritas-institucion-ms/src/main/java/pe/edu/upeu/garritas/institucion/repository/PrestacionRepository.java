package pe.edu.upeu.garritas.institucion.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.institucion.entity.Prestacion;

public interface PrestacionRepository extends JpaRepository<Prestacion, Long> {}
