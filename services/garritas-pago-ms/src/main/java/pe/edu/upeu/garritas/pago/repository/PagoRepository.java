package pe.edu.upeu.garritas.pago.repository;

import pe.edu.upeu.garritas.pago.entity.Pago;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PagoRepository extends JpaRepository<Pago, Long> {
    List<Pago> findByIdVenta(Long idVenta);
}
