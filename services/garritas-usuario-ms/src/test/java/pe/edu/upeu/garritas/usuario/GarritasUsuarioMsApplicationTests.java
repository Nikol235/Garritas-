package pe.edu.upeu.garritas.usuario;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

@SpringBootTest
@Import(UsuarioRolIntegrationTests.TestSecurityConfig.class)
class GarritasUsuarioMsApplicationTests {

	@Test
	void contextLoads() {
	}

}
