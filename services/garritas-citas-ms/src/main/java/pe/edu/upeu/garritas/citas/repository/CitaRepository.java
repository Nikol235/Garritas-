package pe.edu.upeu.garritas.citas.repository;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.citas.entity.Cita;

public interface CitaRepository extends JpaRepository<Cita, Long> {
  java.util.List<Cita> findByIdCliente(String idCliente);

  List<Cita> findByIdCliente(Long idCliente);
}
