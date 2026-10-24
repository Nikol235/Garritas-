# Infraestructura

- `garritas-config/`: configuración centralizada por aplicación y ambiente.
- `garritas-eureka/`: registro de servicios y descubrimiento.
- `garritas-gateway/`: acceso único, CORS, JWT y enrutamiento por Eureka.
- `garritas-common/`: soporte técnico compartido de JWT, inbox/outbox, referencias HTTP y errores. No comparte entidades de negocio ni bases de datos.

Las configuraciones de negocio viven en `garritas-config/config-repo/`. Los servicios no arrancan con una configuración incompleta si Config Server falta. El agregador `uso-rapido/pom.xml` instala el soporte común antes del arranque manual de un módulo.
