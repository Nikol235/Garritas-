# Bienestar

Microservicio de profesionales y especialidades, con relación JPA muchos a muchos y tabla de unión `profesional_especialidad`. Puerto DEV 8088, PostgreSQL 15448.

Las consultas son públicas; altas, modificaciones y bajas requieren ADMIN. Las bajas de profesionales son lógicas. Una especialidad vinculada no puede eliminarse hasta retirar sus asociaciones. Una sede asignada debe existir y estar activa; Citas valida el profesional y su sede antes de reservar.

Arranque integrado y pruebas: consulta el [manual principal](../../README.md) y [uso rápido](../../uso-rapido/README.md). Los ejemplos de profesionales y especialidades se cargan solo en DEV mediante migración repetible.
