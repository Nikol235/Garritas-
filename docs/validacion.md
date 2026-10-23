# Evidencia de validación

Las comprobaciones se ejecutaron en la máquina de nube de esta tarea. Esto no acredita publicación del entorno ni restauración en una tarea nueva.

| Comprobación | Resultado observado |
|---|---|
| Reactor Maven: librería común, tres aplicaciones de infraestructura y siete servicios | Compilación correcta |
| `bash scripts/dev.sh test` | **13 pruebas, 0 fallos, 0 errores, 0 omitidas**: diez contextos Spring y tres pruebas de contrato/correlación/propiedad |
| Angular `npm test` | **8 pruebas correctas**, estados y carrito: cantidades, totales, persistencia, cambios de stock e idempotencia |
| Angular `npm run build` | Compilación de producción correcta |
| Arranque DEV | Config Server, Eureka, Gateway y los siete servicios con readiness, siete PostgreSQL, Kafka y Keycloak |
| Readiness y exportación Prometheus | HTTP 200 y métricas JVM verificadas en los diez componentes Java; exportadores añadidos también a Config Server y Eureka |
| `scripts/smoke.py` con Chromium | Nueva orden con catálogo de mascotas, filtros, cantidades, subtotales, eliminación de líneas, carrito conservado tras login y recarga, login real Authorization Code + PKCE, roles, catálogo público, compra Angular a través de Gateway, polling hasta PAGADA, pago rechazado, stock restaurado, idempotencia HTTP, validación de cantidades y CORS |
| `scripts/faults.py` | Replay del mismo evento y de un duplicado semántico sin duplicar compensación; Pago detenido y recuperado; Kafka detenido, evento retenido en outbox y compra completada al recuperar Kafka |
| Configuración Compose raíz, prebuilt y observabilidad | Validación sintáctica de Compose correcta |
| Construcción Docker con artefactos precompilados | Las once imágenes se construyeron correctamente |
| Dockerfile con compilación Maven dentro del builder | Bloqueado por falta de salida de red del builder; se añadió la alternativa `compose.prebuilt.yml` |
| Arranque simultáneo de todo el Compose raíz | **Pendiente**: `no space left on device` con el driver VFS de esta nube, incluso después de compactar las imágenes. No se da por validado el funcionamiento conjunto en contenedores |
| Grafana/Loki/Prometheus completos | Configuración ajustada y validada por Compose; stack DEV ejecutado: consolas, dashboards, fuentes de datos y métricas verificadas con `scripts/consoles.py` |

Para recuperar espacio se retiraron los contenedores de prueba, las imágenes generadas y su caché. Se conservaron los volúmenes PostgreSQL y los artefactos de compilación; el flujo DEV se restauró. Las imágenes pueden reproducirse desde las instrucciones del README. Para cerrar la validación Docker pendiente se necesita más disco o un driver que comparta capas, como overlay2, y repetir el smoke contra el Gateway de Compose en el puerto 28080.

La aplicación de pagos es una simulación didáctica; las pruebas no representan cobros bancarios reales. Las cuentas de prueba y el realm son exclusivamente de desarrollo.

## Revisión de arranque y consolas

Se añadió Kafka UI (18085) y se verificó su clúster ONLINE. Se probaron los logins de las consolas de Keycloak y Grafana, el registro de Eureka, los dashboards aprovisionados y las conexiones de Grafana con Prometheus y Loki. Prometheus consulta los diez componentes Java y Keycloak; Loki recibe los logs de Catálogo.

Se corrigieron permisos de lectura para configuraciones de monitorización restauradas como 0600 y la conexión interna que el proxy externo impedía. Keycloak se monitoriza por la red interna Docker. `scripts/observability.sh` reproduce la preparación de permisos, sin tocar archivos de credenciales. `scripts/status.py` comprueba cada endpoint y la conexión de Kafka con su topic de ventas.

El catálogo inicial de demostración se ejecutó nuevamente y se comprobó que no duplica productos ni altera stock o precios existentes. El frontend se revisó en escritorio y móvil sin desbordamiento horizontal. El Compose completo sigue con la limitación de disco documentada; esta revisión acredita el flujo DEV con las consolas, no un despliegue público.
