package pe.edu.upeu.garritas.envio.repository;

import pe.edu.upeu.garritas.envio.entity.Envio;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface EnvioRepository extends JpaRepository<Envio, Long> {
    List<Envio> findByIdVenta(Long idVenta);
}
