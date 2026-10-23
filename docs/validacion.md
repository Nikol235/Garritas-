# Evidencia de validación

Las comprobaciones se ejecutaron en la máquina de nube de esta tarea. Esto no acredita publicación del entorno ni restauración en una tarea nueva.

| Comprobación | Resultado observado |
|---|---|
| Reactor Maven: librería común, tres aplicaciones de infraestructura y siete servicios | Compilación correcta |
| `bash scripts/dev.sh test` | **13 pruebas, 0 fallos, 0 errores, 0 omitidas**: diez contextos Spring y tres pruebas de contrato/correlación/propiedad |
| Angular `npm test` | **1 prueba correcta**, estados pendientes y terminales |
| Angular `npm run build` | Compilación de producción correcta |
| Arranque DEV | Config Server, Eureka, Gateway y los siete servicios con readiness, siete PostgreSQL, Kafka y Keycloak |
| Readiness y exportación Prometheus | HTTP 200 y métricas JVM verificadas en los diez componentes Java; exportadores añadidos también a Config Server y Eureka |
| `scripts/smoke.py` con Chromium | Login real Authorization Code + PKCE, roles, catálogo público, compra Angular a través de Gateway, polling hasta PAGADA, pago rechazado, stock restaurado, idempotencia HTTP, validación de cantidades y CORS |
| `scripts/faults.py` | Replay del mismo evento y de un duplicado semántico sin duplicar compensación; Pago detenido y recuperado; Kafka detenido, evento retenido en outbox y compra completada al recuperar Kafka |
| Configuración Compose raíz, prebuilt y observabilidad | Validación sintáctica de Compose correcta |
| Construcción Docker con artefactos precompilados | Las once imágenes se construyeron correctamente |
| Dockerfile con compilación Maven dentro del builder | Bloqueado por falta de salida de red del builder; se añadió la alternativa `compose.prebuilt.yml` |
| Arranque simultáneo de todo el Compose raíz | **Pendiente**: `no space left on device` con el driver VFS de esta nube, incluso después de compactar las imágenes. No se da por validado el funcionamiento conjunto en contenedores |
| Grafana/Loki/Prometheus completos | Configuración ajustada y validada por Compose; stack opcional no ejecutado como parte de estas pruebas |

Para recuperar espacio se retiraron los contenedores de prueba, las imágenes generadas y su caché. Se conservaron los volúmenes PostgreSQL y los artefactos de compilación; el flujo DEV se restauró. Las imágenes pueden reproducirse desde las instrucciones del README. Para cerrar la validación Docker pendiente se necesita más disco o un driver que comparta capas, como overlay2, y repetir el smoke contra el Gateway de Compose en el puerto 28080.

La aplicación de pagos es una simulación didáctica; las pruebas no representan cobros bancarios reales. Las cuentas de prueba y el realm son exclusivamente de desarrollo.
