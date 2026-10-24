package pe.edu.upeu.garritas.bienestar;

@org.springframework.boot.autoconfigure.SpringBootApplication
@org.springframework.context.annotation.Import(
    pe.edu.upeu.garritas.common.SecurityConfiguration.class)
public class GarritasBienestarMsApplication {
  public static void main(String[] args) {
    org.springframework.boot.SpringApplication.run(GarritasBienestarMsApplication.class, args);
  }
}
