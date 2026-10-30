package pe.edu.upeu.garritas.usuario.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.usuario.entity.PeriodoSuscripcion;

public interface PeriodoSuscripcionRepository extends JpaRepository<PeriodoSuscripcion, Long> {
  java.util.Optional<PeriodoSuscripcion> findByUsuarioIdAndIdempotencyKey(
      Long usuario, java.util.UUID key);
}
