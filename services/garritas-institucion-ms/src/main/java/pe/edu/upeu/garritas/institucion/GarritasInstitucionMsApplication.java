package pe.edu.upeu.garritas.institucion;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@org.springframework.context.annotation.Import(
    pe.edu.upeu.garritas.common.SecurityConfiguration.class)
@io.swagger.v3.oas.annotations.OpenAPIDefinition(
    security = @io.swagger.v3.oas.annotations.security.SecurityRequirement(name = "bearerAuth"))
@io.swagger.v3.oas.annotations.security.SecurityScheme(
    name = "bearerAuth",
    type = io.swagger.v3.oas.annotations.enums.SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT")
@SpringBootApplication
public class GarritasInstitucionMsApplication {

  public static void main(String[] args) {
    SpringApplication.run(GarritasInstitucionMsApplication.class, args);
  }
}
