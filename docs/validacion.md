# Evidencia de validación

Las comprobaciones se ejecutaron en la máquina de nube de esta tarea. Esto no acredita publicación del entorno ni restauración en una tarea nueva.

| Comprobación | Resultado observado |
|---|---|
| Reactor Maven: librería común, tres aplicaciones de infraestructura y ocho servicios | Compilación correcta |
| `bash uso-rapido/scripts/dev.sh test` | **15 pruebas, 0 fallos, 0 errores, 0 omitidas**: once contextos Spring, tres pruebas de contrato/correlación/propiedad y una integración de muchos a muchos |
| Angular `npm test` | **11 pruebas correctas**, estados y carrito: cantidades, totales, persistencia, cambios de stock e idempotencia |
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

## Revisión para los manuales PDF — 24/10/2026

Se reinició el flujo DEV y se repitieron compilación Java, 15 pruebas Java, 11 pruebas Angular, build de producción, smoke de compra, recorrido de todos los dominios y consolas. Se corrigió una carrera al cargar el perfil: el formulario espera la respuesta antes de permitir edición; dos pruebas de regresión cubren respuesta tardía y perfil inexistente. El recorrido real comprobó además que se persiste el correo introducido.

Las pruebas de fallo repitieron replay/duplicado Kafka, detención y recuperación de Pago, caída del broker y entrega tras recuperar outbox. El ejemplo Python publicó/consumió tres mensajes. El ZIP de código se extrajo en una carpeta nueva: el reactor Maven y Angular compilaron sin los targets ni node_modules originales.

Los resultados, límites y PDF están en [manuales](manuales/README.md), con `revision.json` y evidencia resumida. Sigue sin acreditarse ejecución PowerShell en Windows ni arranque simultáneo del despliegue integral Docker.

## Actualización de asignaciones y revisión de sesiones 1–11

La [asignación actual](asignacion-y-sustentacion.md) y la [matriz de referencia docente](alineacion-pagatu.md) sustituyen las descripciones anteriores de Envío operativo: ahora es maestro logístico y los despachos están en Venta. Se mantienen los puertos. La documentación extensa PDF anterior identifica su commit histórico; no se presenta como una copia del código actual.

Resultado de la revisión: **24 pruebas Java, sin fallos/errores/omitidas; 13 pruebas Angular y build de producción correctos**. El reactor completo pasó con 22 pruebas; tras dos refuerzos finales se verificaron de nuevo Usuario y Venta, sumando los casos de edad decimal y propiedad de despacho (24 en los reportes finales).

Los recorridos `domain_smoke.py`, `academic_smoke.py` y `smoke.py` pasaron: cada pareja tiene N:M comprobada desde la UI/API, cabecera/detalle y regla de negocio; el perfil persiste tras recargar; la edad admite días/meses y rechaza decimales/negativos/unidad inválida; la Saga y la entrega conservan permisos y stock. `frontend_review.py` revisó seis vistas con datos cargados en escritorio y móvil, sin desbordamiento horizontal.

Se levantó una segunda instancia de Institución: Gateway alternó las respuestas 8082/18082 y continuó con la principal tras retirar la secundaria. Pasaron replay/duplicados, caída y recuperación de Pago, detención de Kafka y recuperación vía outbox. Kafka UI, Keycloak, Eureka, Grafana, Prometheus y Loki se verificaron otra vez.

Se corrigió un fallo de empaquetado incremental: un JAR ya empaquetado conservaba el soporte común anterior. Los lanzadores ahora hacen `clean package`; se inspeccionó el JAR de Gateway para confirmar que incluye las nuevas reglas de seguridad. La documentación Swagger ofrece esquema Bearer y la API sigue aplicando roles/propiedad.

La copia histórica conservó tres registros exactamente y se repitió sin duplicar ni borrar origen; la migración bloquea escrituras durante el ajuste de secuencia. PowerShell conserva UTF-8 y no necesita Python para migrar. Los cambios Windows se revisaron estáticamente; no se afirma ejecución nativa desde Linux.

[Resultados estructurados](evidencias-actualizacion/resultado.json) y resúmenes de evidencia en `docs/evidencias-actualizacion/`. La alternativa Compose integral valida configuración; su arranque simultáneo continúa sin acreditarse. El pago bancario/API externa real del brief global permanece fuera de la simulación didáctica: no se atribuye como cumplido.
