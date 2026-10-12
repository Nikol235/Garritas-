# garritas-pago-ms

Pasarela de pagos. Microservicio Spring Boot 4 / Java 21, registrado en Eureka y configurado via Config Server.

## Correr en local
```
docker compose -f compose-dev.yml up -d
./mvnw spring-boot:run
```
API: http://localhost:8087/api/v1
Swagger: http://localhost:8087/swagger-ui.html
