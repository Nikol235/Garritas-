package pe.edu.upeu.garritas.bienestar;

import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.bienestar.dto.EspecialidadRequest;
import pe.edu.upeu.garritas.bienestar.dto.ProfesionalRequest;
import pe.edu.upeu.garritas.bienestar.repository.ProfesionalRepository;
import pe.edu.upeu.garritas.bienestar.service.BienestarService;

@SpringBootTest
@Transactional
class EspecialidadesIntegrationTests {
  @Autowired BienestarService service;
  @Autowired ProfesionalRepository profesionales;

  @BeforeEach
  void admin() {
    SecurityContextHolder.getContext()
        .setAuthentication(
            new UsernamePasswordAuthenticationToken(
                "test-admin", "", List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void manyToManyAssociationsArePersistedDeduplicatedAndEditable() {
    String key = UUID.randomUUID().toString();
    var general =
        service.guardarEspecialidad(null, new EspecialidadRequest("General " + key, "Test", true));
    var nutricion =
        service.guardarEspecialidad(
            null, new EspecialidadRequest("Nutrición " + key, "Test", true));
    var first =
        service.guardar(
            null,
            new ProfesionalRequest(
                "Primero",
                key + "1@example.test",
                "",
                null,
                true,
                List.of(general.getId(), nutricion.getId(), general.getId())));
    var second =
        service.guardar(
            null,
            new ProfesionalRequest(
                "Segundo", key + "2@example.test", "", null, true, List.of(general.getId())));
    assertEquals(2, first.especialidades().size());
    assertEquals(2, profesionales.countByEspecialidades_Id(general.getId()));
    assertEquals(1, second.especialidades().size());
    service.guardar(
        first.id(),
        new ProfesionalRequest(
            first.nombre(), first.email(), "", null, true, List.of(nutricion.getId())));
    assertEquals(1, profesionales.countByEspecialidades_Id(general.getId()));
    var conflict =
        assertThrows(
            ResponseStatusException.class, () -> service.eliminarEspecialidad(general.getId()));
    assertEquals(409, conflict.getStatusCode().value());
  }
}
