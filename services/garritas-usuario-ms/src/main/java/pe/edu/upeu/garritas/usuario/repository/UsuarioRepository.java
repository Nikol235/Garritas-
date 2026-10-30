package pe.edu.upeu.garritas.usuario.repository;

import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.upeu.garritas.usuario.entity.Usuario;

public interface UsuarioRepository extends JpaRepository<Usuario, Long> {
  Optional<Usuario> findBySubject(String subject);

  Optional<Usuario> findByEmail(String email);

  @Query(
      "SELECT DISTINCT u FROM Usuario u LEFT JOIN u.roles r WHERE "
          + "(:rol IS NULL OR :rol = '' OR UPPER(r.nombre) = UPPER(:rol)) AND "
          + "(:q IS NULL OR :q = '' "
          + "OR LOWER(COALESCE(u.dni, '')) LIKE LOWER(CONCAT('%', :q, '%')) "
          + "OR LOWER(u.nombre) LIKE LOWER(CONCAT('%', :q, '%')) "
          + "OR LOWER(u.email) LIKE LOWER(CONCAT('%', :q, '%')))")
  Page<Usuario> buscarConRol(
      @Param("q") String q, @Param("rol") String rol, Pageable pageable);
}
