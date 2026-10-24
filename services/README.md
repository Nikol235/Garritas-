# Microservicios de negocio

| Carpeta | Responsabilidad | Angular |
|---|---|---|
| garritas-catalogo-ms | Categorías, productos y stock | Catálogo, productos y categorías |
| garritas-venta-ms | Pedidos por sede y Saga | Nueva orden, carrito y mis pedidos |
| garritas-pago-ms | Pago simulado e idempotencia | Pagos |
| garritas-institucion-ms | Sedes del Perú | Sedes |
| garritas-usuario-ms | Perfil y mascotas por identidad | Mi cuenta y mascotas, clientes |
| garritas-citas-ms | Reservas con control de horario | Citas |
| garritas-envio-ms | Entrega de pedidos pagados | Envíos |
| garritas-bienestar-ms | Profesionales y especialidades M:N | Especialistas |

Cada uno tiene base PostgreSQL, Flyway, configuración, endpoint de readiness y métricas propios. Las referencias entre servicios se consultan por HTTP con Eureka y JWT, no por joins SQL entre bases.
