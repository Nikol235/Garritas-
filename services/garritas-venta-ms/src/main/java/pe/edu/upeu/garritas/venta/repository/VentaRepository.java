package pe.edu.upeu.garritas.venta.repository;

import pe.edu.upeu.garritas.venta.entity.Venta;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface VentaRepository extends JpaRepository<Venta, Long> {
    List<Venta> findByIdCliente(Long idCliente);
}
