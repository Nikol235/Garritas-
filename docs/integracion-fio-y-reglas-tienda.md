# Integración de Catálogo y Usuario y reglas de la tienda

Se integran los aportes de Fio desde `Garritas_Store`, rama
`catalogo-ms-y-usuario-ms` (commit `5d9c754`), conservando la historia de ambas
ramas. El repositorio del equipo no se modifica. La rama de trabajo sigue siendo
`feat/garritas-store` de `Nikol235/Garritas-`.

## Qué se conserva y qué se ajusta

- Productos con varias categorías, búsqueda, filtros y paginación.
- Clientes, mascotas, DNI y formularios en ventanas de diálogo.
- Catálogo de roles internos y asignación usuario–rol de muchos a muchos.
- Guardado confirmado del perfil y edad de mascotas en días o meses, también
  desde el mantenimiento administrativo.
- Los permisos **CLIENTE/ADMIN del JWT siguen siendo responsabilidad de
  Keycloak**. Un rol interno como COMPRAS o SECRETARIA clasifica al personal;
  asignarlo no concede privilegios en las APIs. Las pantallas lo explican.
- Las consultas y modificaciones del catálogo de roles exigen administrador.
  No se permite borrar roles base o eliminar un rol todavía asignado.
- Se elimina el parche que modificaba internamente la comprobación de Node de
  Angular. Debe utilizarse una versión de Node compatible con el proyecto.
- Los lanzadores conservan la comprobación de identidad de los procesos antes
  de detenerlos, para no terminar un proceso ajeno cuyo PID se haya reutilizado.

## Administrador y cliente

El administrador mantiene productos, categorías, sedes, servicios, paquetes,
logística, clientes y roles internos. Puede consultar y gestionar pedidos de
clientes. No tiene carrito ni puede crear una venta propia: la API y el servicio
rechazan la compra, incluso mediante una petición directa. Para comprar se usa
una cuenta de cliente. La contratación personal de planes también exige cliente.

## Delivery cobrado antes de generar el despacho

1. El cliente añade productos, selecciona sede y elige **recojo** o **delivery**.
2. Si elige delivery, indica cobertura y dirección. El carrito muestra subtotal,
   costo de envío y total. Recojo cuesta cero.
3. Venta consulta la cobertura por Feign usando el nombre lógico
   `garritas-envio-ms`, descubierto mediante Eureka. La consulta tiene timeout y
   Circuit Breaker, como la consulta a Catálogo enseñada en S6 de Pagatu.
4. El servidor obtiene la tarifa real. Si cambió desde la selección del cliente,
   devuelve `409`: el cliente debe revisar la tarifa y confirmar nuevamente.
   Si no puede validarse, responde de manera controlada y no crea la compra.
5. El total del evento de venta incluye productos más envío. Pago procesa ese
   mismo total mediante la Saga de Kafka.
6. Al aprobarse el pago, Venta genera automáticamente un único despacho en la
   misma transacción local que registra el evento recibido y el estado PAGADA.
7. Si el pago se rechaza, se compensa el inventario y no se genera despacho.

No se permite añadir un delivery sin cobrar después de pagar un pedido con
recojo. El endpoint anterior de creación solo puede devolver el despacho ya
pagado si sus datos coinciden. Los despachos históricos se conservan: una tarifa
antigua registrada no se convierte retroactivamente en un cobro confirmado.

Los reintentos reutilizan `Idempotency-Key`. El borrador de dirección y su clave
se conservan en `sessionStorage` de la pestaña; los tokens continúan en memoria.
Los precios siempre se obtienen del servidor. El pago sigue siendo una
simulación, sin cargo bancario real. No existe un proceso automático de reembolso
de un envío pagado: su cancelación no puede fingir que devolvió dinero.

## Paquetes de servicios por sede

En **Sedes → Ver servicios y paquetes** se consulta la oferta de esa sede.
Un paquete es una prestación compuesta por entre dos y ocho servicios
individuales. Por ejemplo, **Paquete Baño + Corte** contiene baño higiénico y
corte de pelo. La asociación vive en Institución, tabla `prestacion_componentes`.

El administrador define los componentes y asigna precio, duración y estado del
paquete en cada sede. La duración se expresa en bloques de 30 minutos. No hay
paquetes dentro de paquetes, autorreferencias ni componentes inactivos. Si un
componente se desactiva, el paquete deja de estar disponible para reservar.

El cliente reserva el paquete desde **Servicios y paquetes por sede** o desde
**Citas**. No puede añadir además un servicio que el paquete ya incluya. Citas
guarda nombre, componentes, precio y duración como una fotografía del acuerdo:
cambiar la oferta posteriormente no modifica una reserva anterior. Continúan
vigentes la propiedad de la mascota, la sede del profesional y la prohibición
de cruzar horarios. La reserva de servicios informa su precio, pero no realiza
un cobro bancario desde Citas.

## Validaciones

- Celular peruano opcional: si se informa, exactamente nueve dígitos y comienza
  con `9`, sin `+51`, espacios ni letras. Se valida en Angular y en el backend.
- DNI opcional: exactamente ocho dígitos cuando se informa.
- Paginación: página desde cero y tamaño entre 1 y 100.
- Categorías y roles referenciados deben existir; no se ignoran IDs inválidos.
- No se vincula un perfil a otro `sub` solo porque coincida su correo.
- Los conflictos de registros duplicados o relacionados se comunican como
  `409`, sin exponer mensajes internos de PostgreSQL.

## Actualizar una copia de nuestro repositorio

Detener primero Java y Angular, ejecutar `git pull` en `feat/garritas-store`,
compilar y arrancar nuevamente con los comandos habituales de `uso-rapido`.
Flyway aplica nuevas migraciones. **No borrar volúmenes ni ejecutar `repair`**
para actualizar una copia normal de este repositorio.

Las migraciones V3 y V4 originales de Usuario no se modifican. Los aportes de
roles y DNI se incorporan como V5, V6 y V7. Una base que ya haya ejecutado las
migraciones diferentes de la rama independiente de Fio requiere una migración
específica; no debe conectarse automáticamente a esta versión.

## Dónde revisar el código

| Capacidad | Archivo (desde la raíz del repositorio) |
|---|---|
| Cobro de envío y prohibición de compra administrativa | `services/garritas-venta-ms/src/main/java/pe/edu/upeu/garritas/venta/service/VentaService.java` |
| Feign y Circuit Breaker logístico | `services/garritas-venta-ms/src/main/java/pe/edu/upeu/garritas/venta/client/LogisticaClient.java` y `LogisticaConsulta.java` |
| Generación idempotente del despacho pagado | `services/garritas-venta-ms/src/main/java/pe/edu/upeu/garritas/venta/messaging/VentaEvents.java` |
| Componentes de paquetes | `services/garritas-institucion-ms/src/main/java/pe/edu/upeu/garritas/institucion/entity/Prestacion.java` |
| Reglas de paquetes y oferta por sede | `services/garritas-institucion-ms/src/main/java/pe/edu/upeu/garritas/institucion/service/PrestacionService.java` |
| Reserva, componentes repetidos e historial | `services/garritas-citas-ms/src/main/java/pe/edu/upeu/garritas/citas/service/CitaService.java` |
| N:M producto–categoría | `services/garritas-catalogo-ms/src/main/java/pe/edu/upeu/garritas/catalogo/entity/Producto.java` |
| N:M usuario–rol interno | `services/garritas-usuario-ms/src/main/java/pe/edu/upeu/garritas/usuario/entity/Usuario.java` |
| Seguridad común | `infra/garritas-common/src/main/java/pe/edu/upeu/garritas/common/SecurityConfiguration.java` |
| Prueba integrada reproducible | `uso-rapido/scripts/integracion_fio_smoke.py` |

La guía PDF anterior conserva enlaces a su revisión histórica. Este documento
describe los cambios posteriores y debe acompañarla para sustentar la versión
actual.
