package pe.edu.upeu.garritas.envio.repository;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.envio.entity.Envio;

public interface EnvioRepository extends JpaRepository<Envio, Long> {
  java.util.List<Envio> findByIdCliente(String idCliente);

  List<Envio> findByIdVenta(Long idVenta);
}
