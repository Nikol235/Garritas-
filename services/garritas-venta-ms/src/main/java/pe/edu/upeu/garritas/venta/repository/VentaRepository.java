package pe.edu.upeu.garritas.venta.repository;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.venta.entity.Venta;

public interface VentaRepository extends JpaRepository<Venta, Long> {
  java.util.List<Venta> findByIdCliente(String idCliente);

  java.util.Optional<Venta> findByIdClienteAndIdempotencyKey(String idCliente, java.util.UUID key);

  List<Venta> findByIdCliente(Long idCliente);
}
