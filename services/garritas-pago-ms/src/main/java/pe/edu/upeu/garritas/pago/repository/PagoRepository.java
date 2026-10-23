package pe.edu.upeu.garritas.pago.repository;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.pago.entity.Pago;

public interface PagoRepository extends JpaRepository<Pago, Long> {
  List<Pago> findByIdVenta(Long idVenta);

  List<Pago> findByIdCliente(String idCliente);
}
