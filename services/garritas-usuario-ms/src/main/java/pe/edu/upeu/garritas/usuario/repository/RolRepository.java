package pe.edu.upeu.garritas.usuario.repository;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.upeu.garritas.usuario.entity.Rol;

public interface RolRepository extends JpaRepository<Rol, Long> {
  Optional<Rol> findByNombre(String nombre);

  Optional<Rol> findByNombreIgnoreCase(String nombre);
}
