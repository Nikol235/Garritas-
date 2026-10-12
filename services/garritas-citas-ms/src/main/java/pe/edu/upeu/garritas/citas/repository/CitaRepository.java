package pe.edu.upeu.garritas.citas.repository;

import pe.edu.upeu.garritas.citas.entity.Cita;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CitaRepository extends JpaRepository<Cita, Long> {
    List<Cita> findByIdCliente(Long idCliente);
}
