# Evidencia de validación

Las comprobaciones se ejecutaron en la máquina de nube de esta tarea. Esto no acredita publicación del entorno ni restauración en una tarea nueva.

| Comprobación | Resultado observado |
|---|---|
| Reactor Maven: librería común, tres aplicaciones de infraestructura y ocho servicios | Compilación correcta |
| `bash uso-rapido/scripts/dev.sh test` | **15 pruebas, 0 fallos, 0 errores, 0 omitidas**: once contextos Spring, tres pruebas de contrato/correlación/propiedad y una integración de muchos a muchos |
| Angular `npm test` | **9 pruebas correctas**, estados y carrito: cantidades, totales, persistencia, cambios de stock e idempotencia |
| Angular `npm run build` | Compilación de producción correcta |
| Arranque DEV | Config Server, Eureka, Gateway y los ocho servicios con readiness, ocho PostgreSQL, Kafka y Keycloak |
| Readiness y exportación Prometheus | HTTP 200 y métricas JVM verificadas en los once componentes Java; exportadores añadidos también a Config Server y Eureka |
| `uso-rapido/scripts/smoke.py` con Chromium | Nueva orden con catálogo de mascotas, filtros, cantidades, subtotales, eliminación de líneas, carrito conservado tras login y recarga, login real Authorization Code + PKCE, roles, catálogo público, compra Angular a través de Gateway, polling hasta PAGADA, pago rechazado, stock restaurado, idempotencia HTTP, validación de cantidades y CORS |
| `uso-rapido/scripts/faults.py` | Replay del mismo evento y de un duplicado semántico sin duplicar compensación; Pago detenido y recuperado; Kafka detenido, evento retenido en outbox y compra completada al recuperar Kafka |
| Configuración Compose integrado, prebuilt y observabilidad | Validación sintáctica de Compose correcta |
| Construcción Docker con artefactos precompilados | Revisión anterior: once imágenes construidas; no se ha reconstruido el conjunto ampliado con Bienestar |
| Dockerfile con compilación Maven dentro del builder | Bloqueado por falta de salida de red del builder; se añadió la alternativa `compose.prebuilt.yml` |
| Arranque simultáneo de todo el Compose integrado | **Pendiente**: `no space left on device` con el driver VFS de esta nube, incluso después de compactar las imágenes. No se da por validado el funcionamiento conjunto en contenedores |
| Grafana/Loki/Prometheus completos | Configuración ajustada y validada por Compose; stack DEV ejecutado: consolas, dashboards, fuentes de datos y métricas verificadas con `uso-rapido/scripts/consoles.py` |

Para recuperar espacio se retiraron los contenedores de prueba, las imágenes generadas y su caché. Se conservaron los volúmenes PostgreSQL y los artefactos de compilación; el flujo DEV se restauró. Las imágenes pueden reproducirse desde las instrucciones del README. Para cerrar la validación Docker pendiente se necesita más disco o un driver que comparta capas, como overlay2, y repetir el smoke contra el Gateway de Compose en el puerto 28080.

La aplicación de pagos es una simulación didáctica; las pruebas no representan cobros bancarios reales. Las cuentas de prueba y el realm son exclusivamente de desarrollo.

## Revisión de arranque y consolas

Se añadió Kafka UI (18085) y se verificó su clúster ONLINE. Se probaron los logins de las consolas de Keycloak y Grafana, el registro de Eureka, los dashboards aprovisionados y las conexiones de Grafana con Prometheus y Loki. Prometheus consulta los once componentes Java y Keycloak; Loki recibe los logs de Catálogo.

Se corrigieron permisos de lectura para configuraciones de monitorización restauradas como 0600 y la conexión interna que el proxy externo impedía. Keycloak se monitoriza por la red interna Docker. `uso-rapido/scripts/observability.sh` reproduce la preparación de permisos, sin tocar archivos de credenciales. `uso-rapido/scripts/status.py` comprueba cada endpoint y la conexión de Kafka con su topic de ventas.

El catálogo inicial de demostración se ejecutó nuevamente y se comprobó que no duplica productos ni altera stock o precios existentes. El frontend se revisó en escritorio y móvil sin desbordamiento horizontal. El Compose completo sigue con la limitación de disco documentada; esta revisión acredita el flujo DEV con las consolas, no un despliegue público.

## Revisión integral de estructura y módulos

La estructura se alineó con Pagatu: `clients`, `docs`, `infra`, `kafka`, `keycloak`, `obs`, `overrides`, `services` y `uso-rapido`. El reactor Maven y la alternativa Docker integrada están en `uso-rapido`. Se retiraron del versionado logs generados, conservándolos localmente.

`uso-rapido/scripts/domain_smoke.py` pasó con Chromium real y cuentas ADMIN, CLIENTE y un segundo cliente: creación/edición de sedes desde Angular, selección de sede, perfil/mascota, aislamiento entre clientes, especialidades compartidas por profesionales mediante tabla de unión, bloqueo de borrado de especialidad vinculada, cita con bloqueo de horario duplicado, confirmación/atención, compra pagada con descuento de stock y solicitud/entrega de envío. Se verificaron permisos en API, no solo botones ocultos.

Se revisaron las vistas de sedes, especialistas y citas en escritorio y móvil, sin desbordamiento horizontal. El cliente ve seis sedes ficticias de Perú; solo ADMIN las modifica. Las pruebas de consola comprobaron nueve aplicaciones registradas en Eureka y al menos doce targets activos en Prometheus. El ejemplo Python de Kafka publicó y consumió tres mensajes reales en un topic aislado. `mkdocs build --strict` pasó.

El lanzador PowerShell se incluye para Windows, pero no se ejecutó en una máquina Windows. La validación funcional acreditada corresponde al flujo DEV de Linux/nube; el arranque simultáneo de todos los servicios en Docker continúa pendiente por la limitación descrita arriba. CI se añadió al repositorio; su ejecución en GitHub requiere que corra el workflow tras el push.
