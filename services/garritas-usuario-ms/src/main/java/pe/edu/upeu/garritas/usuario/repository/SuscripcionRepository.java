package pe.edu.upeu.garritas.usuario.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.usuario.entity.Suscripcion;

public interface SuscripcionRepository extends JpaRepository<Suscripcion, Long> {
  java.util.List<Suscripcion> findByUsuarioIdOrderByIdDesc(Long id);

  java.util.List<Suscripcion> findByUsuarioIdAndPlanIdAndEstado(
      Long usuario, Long plan, String estado);
}
