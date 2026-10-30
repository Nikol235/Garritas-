package pe.edu.upeu.garritas.venta.despacho.repository;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.venta.despacho.entity.Despacho;

public interface DespachoRepository extends JpaRepository<Despacho, Long> {
  java.util.List<Despacho> findByIdCliente(String idCliente);

  List<Despacho> findByIdVenta(Long idVenta);
}
