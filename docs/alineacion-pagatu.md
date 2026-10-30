# Contraste con Pagatu: sesiones 1 a 11

Referencia revisada: [repositorio Pagatu](https://github.com/262dist/pagatu/tree/9e6fc30a7028c9398641d187b30da98117a5fc76), commit `9e6fc30a7028c9398641d187b30da98117a5fc76`, y [producto del curso publicado](https://262dist.github.io/pagatu/#producto-del-curso). Se revisaron introducciones, producto de sesión y criterios de aceptación; también `docs/proyecto-sello/brief.md`. Se conserva atribución: Garritas adapta el patrón docente al dominio mascotas, no afirma ser una copia literal.

| Sesión | Patrón de la guía | Aplicación verificable en Garritas |
|---|---|---|
| 1 | Capas REST, DTO, PostgreSQL, Flyway, Swagger y Actuator | Cada dominio mantiene controlador, servicio, repositorio, entidad y contratos; migraciones incrementales, UI Swagger con esquema Bearer y health. Las N:M con atributos tienen entidad de asociación local. |
| 2 | Config Server, perfiles DEV/PROD | `infra/garritas-config/config-repo`, importación obligatoria, puertos y datasource por servicio. Las nuevas rutas y perfiles usan el mismo mecanismo. |
| 3 | Eureka y ejecución concurrente | Ocho dominios y Gateway se registran por nombre; una segunda instancia puede usar otro `server.port`. `X-Service-Instance` identifica la instancia real que respondió. |
| 4 | Gateway y balanceo | Angular usa `/api/v1` por Gateway con `lb://`; rutas nuevas para prestaciones, logística, planes y suscripciones. El alias de envíos ahora llega a Venta. |
| 5 | Integración de la base y defensa individual | Arranque, estado, documentación de roles y reparto con capacidad verificable por integrante. La autoría y las capturas individuales corresponden a cada estudiante. |
| 6 | Feign, límites de espera, Circuit Breaker | Venta consulta Catálogo mediante `ProductoClient` y `CatalogoConsulta`. Las referencias protegidas usan `ServiceClient` con descubrimiento, JWT/correlación y tiempos acotados. Este cliente no publica un builder global que interfiera con Eureka. |
| 7 / 7b | Resource Server, roles, JWT, migración a Keycloak | Gateway y los servicios validan issuer, firma y audiencia; el propietario procede de `sub`, nunca del JSON. Maestros ADMIN, operaciones del dueño y transiciones operativas ADMIN. No se reconstruye un auth temporal ya reemplazado en S07b. |
| 8 | Publicación/consumo Kafka por grupos y desacople | Saga Venta–Catálogo–Pago con tipos de eventos de inventario y pago; Python de uso rápido separado. El Outbox publica tras la confirmación local del negocio. |
| 9 | Idempotencia, duplicados, Saga y compensación | Inbox y unicidad por venta; reserva atómica; pago rechazado inicia compensación y solo termina al liberar inventario. Suscripciones añaden clave por operación, períodos únicos y precios históricos; su cancelación es local, no una Saga bancaria. |
| 10 | Readiness/liveness, métricas, logs y correlación | Actuator/Micrometer, Prometheus, Loki/Promtail y Grafana; traceId HTTP y en eventos. Las nuevas clases conservan esos componentes y los puertos existentes. |
| 11 | Angular, PKCE, CORS y consistencia eventual visible | keycloak-js, tokens en memoria, interceptor de API, polling real de pedidos; pantallas de ofertas, logística y suscripciones. El perfil se confirma con GET persistido y la edad tiene unidad explícita. |

## Adaptaciones deliberadas

- La referencia enseña Orden; Garritas utiliza Venta. La reserva de inventario de Garritas se coordina mediante eventos con Outbox/Inbox, no descontando stock remoto dentro de una transacción de Venta que aún pudiera revertirse.
- Los maestros Institución/Envío mantienen transacciones locales para consistencia de sus datos. «No transaccional» en la tabla académica describe su responsabilidad principal, no la ausencia de `@Transactional`.
- En Usuario se amplía el alcance con suscripciones; una renovación crea detalle histórico en la misma transacción que cambia el vencimiento. Los planes no cobran dinero ni ejecutan beneficios automáticamente.
- Una N:M de negocio con precio, tarifa o historial se representa como entidad de unión con dos relaciones N:1. No confundir el patrón relacional con exigir literalmente una anotación `@ManyToMany`.
- No se cambian todas las versiones de Spring solo para igualar números mencionados en el manual: se conserva el conjunto Boot/Cloud que compila y se verifica en el proyecto. La equivalencia se demuestra con código, funcionamiento y decisiones, no renombrando paquetes.

## Qué no acredita esta revisión

El brief general incluye integración con un **servicio externo real**, preferentemente una pasarela. Los pagos de este laboratorio, como la ruta didáctica S8–S9, siguen siendo simulados. No se presenta esa simulación como cumplimiento del requisito global de pasarela/API real del producto final. Esa integración requiere un proveedor y configuración propios.

El arranque integral Docker y el lanzador PowerShell en una máquina Windows no se dan por probados desde Linux. Los YAML se validan y se documentan; la evidencia funcional que se ejecuta aquí corresponde al flujo DEV. Una captura de métricas tampoco sustituye probar permisos, stock, idempotencia y los estados finales.

## Demostrar dos instancias manualmente

Con el entorno principal ya iniciado y la librería común instalada por `build`, abre una terminal adicional en Institución:

```powershell
cd services/garritas-institucion-ms
.\mvnw.cmd spring-boot:run '-Dspring-boot.run.arguments=--server.port=18082'
```

Espera a ver las dos instancias en Eureka y a que se actualice el descubrimiento de Gateway. Desde otra PowerShell consulta repetidamente el encabezado:

```powershell
1..12 | ForEach-Object {
  (Invoke-WebRequest -UseBasicParsing http://localhost:18080/api/v1/sedes).Headers['X-Service-Instance']
}
```

Deben observarse los puertos 8082 y 18082. Detén únicamente la terminal adicional con Ctrl+C al terminar. La propagación de descubrimiento no es instantánea; las peticiones pueden fallar temporalmente durante cambios de registro. No afirmes que esta capacidad fue demostrada si solo se escribió el comando: ejecuta y conserva tu evidencia con reloj/usuario como indica la guía.
