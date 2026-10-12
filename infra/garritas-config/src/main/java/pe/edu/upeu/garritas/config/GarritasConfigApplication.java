package pe.edu.upeu.garritas.config;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

@SpringBootApplication
@EnableConfigServer
public class GarritasConfigApplication {
    public static void main(String[] args) {
        SpringApplication.run(GarritasConfigApplication.class, args);
    }
}
