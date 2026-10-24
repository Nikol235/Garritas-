# Kafka y Kafka UI

Desde la raíz: `docker compose -f kafka/compose-dev.yml up -d --wait`.

- Broker para aplicaciones en el host: `localhost:19092`.
- Broker dentro de Docker: `garritas-kafka:9092`.
- Kafka UI: puerto **18085**, clúster `garritas`.
- Red: `garritas-kafka-dev-net`.
- Topic de negocio: `garritas.ventas.v1`; errores recuperados: `garritas.ventas.v1.DLT`.
- Ejemplo Python aislado: `garritas.demo.v1`.

Cada servicio de la Saga tiene un grupo consumidor propio. No uses el productor de demostración para inventar ventas en el topic de negocio. Los volúmenes conservan sus nombres anteriores para preservar los datos al reorganizar el proyecto.
