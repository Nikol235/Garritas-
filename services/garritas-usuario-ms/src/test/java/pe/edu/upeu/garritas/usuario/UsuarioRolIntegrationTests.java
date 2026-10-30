package pe.edu.upeu.garritas.usuario;

import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.upeu.garritas.usuario.dto.RolRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioRequest;
import pe.edu.upeu.garritas.usuario.dto.UsuarioResponse;
import pe.edu.upeu.garritas.usuario.repository.RolRepository;
import pe.edu.upeu.garritas.usuario.repository.UsuarioRepository;
import pe.edu.upeu.garritas.usuario.service.RolService;
import pe.edu.upeu.garritas.usuario.service.UsuarioService;

@SpringBootTest
@Transactional
@Import(UsuarioRolIntegrationTests.TestSecurityConfig.class)
class UsuarioRolIntegrationTests {

  @TestConfiguration
  static class TestSecurityConfig {
    @Bean
    JwtDecoder jwtDecoder() {
      return token ->
          org.springframework.security.oauth2.jwt.Jwt.withTokenValue(token)
              .header("alg", "none")
              .claim("sub", "test-user")
              .claim("preferred_username", "test-admin")
              .build();
    }
  }

  @Autowired UsuarioService usuarioService;
  @Autowired RolService rolService;
  @Autowired UsuarioRepository usuarioRepository;
  @Autowired RolRepository rolRepository;

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
  void testUsuarioRolManyToMany() {
    String suffix = UUID.randomUUID().toString().substring(0, 8);

    // 1. Crear roles personalizados
    var rolVeterinario =
        rolService.crear(
            RolRequest.builder()
                .nombre("VETERINARIO_" + suffix)
                .descripcion("Atención médica")
                .build());
    var rolCajero =
        rolService.crear(
            RolRequest.builder()
                .nombre("CAJERO_" + suffix)
                .descripcion("Gestión de cobros")
                .build());

    // 2. Crear usuario asignándole múltiples roles
    UsuarioRequest request = new UsuarioRequest();
    request.setNombre("Carlos Gomez " + suffix);
    request.setEmail("carlos." + suffix + "@garritas.pe");
    request.setTelefono("987654321");
    request.setDireccion("Av. Las Flores 123");
    request.setRoleIds(Set.of(rolVeterinario.getId(), rolCajero.getId()));

    UsuarioResponse creado = usuarioService.crear(request);
    assertNotNull(creado.getId());
    assertEquals(2, creado.getRoles().size());

    // 3. Obtener y verificar relación muchos a muchos
    UsuarioResponse obtenido = usuarioService.obtener(creado.getId());
    assertTrue(
        obtenido.getRoles().stream()
            .anyMatch(r -> r.getNombre().equals(rolVeterinario.getNombre())));
    assertTrue(
        obtenido.getRoles().stream().anyMatch(r -> r.getNombre().equals(rolCajero.getNombre())));

    // 4. Remover un rol
    UsuarioResponse sinCajero = usuarioService.removerRol(creado.getId(), rolCajero.getId());
    assertEquals(1, sinCajero.getRoles().size());
    assertEquals(rolVeterinario.getNombre(), sinCajero.getRoles().get(0).getNombre());

    // 5. Asignar rol nuevamente
    UsuarioResponse conCajero = usuarioService.asignarRol(creado.getId(), rolCajero.getId());
    assertEquals(2, conCajero.getRoles().size());
  }
}
