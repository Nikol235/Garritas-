package pe.edu.upeu.garritas.usuario.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.usuario.entity.Plan;

public interface PlanRepository extends JpaRepository<Plan, Long> {}
