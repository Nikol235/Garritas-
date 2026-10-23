# Garritas Store

Tienda de mascotas con Java 21, Spring Boot 4, Spring Cloud, PostgreSQL/Flyway, Kafka, Keycloak y Angular 22. La arquitectura del proyecto y las decisiones de consistencia están en [el análisis arquitectónico](docs/arquitectura.md).

## Desarrollo local

Requisitos: JDK 21 completo (`java` y `javac`), Docker Compose, Node 24, Python 3 y Git. Maven se descarga con el wrapper incluido.

Desde la raíz del repositorio:

```bash
bash scripts/dev.sh build
bash scripts/dev.sh all
bash scripts/dev.sh observability
bash scripts/dev.sh status --observability
```

`all` inicia Kafka, Kafka UI, Keycloak, siete PostgreSQL, Config Server, Eureka, los siete servicios, Gateway y Angular. Instala las dependencias frontend con `npm ci` si faltan. `observability` añade Grafana, Prometheus, Loki y Promtail; `status --observability` comprueba respuestas HTTP y conexión real con el broker. Comprueba readiness; guarda PIDs, copias estables de los JAR y logs en `.runtime/`. No elimina volúmenes ni datos. `bash scripts/dev.sh stop` detiene las aplicaciones Java y Angular; `down` también baja los contenedores de desarrollo, conservando sus volúmenes.

En una nube con proxy Maven, `MAVEN_SETTINGS` puede apuntar a un `settings.xml` externo y `MAVEN_USER_HOME` a un directorio escribible. Se mantiene la validación TLS. Cada tarea de nube está aislada: usar el checkout existente, sin crear un worktree salvo petición explícita.

| Componente DEV | Puerto |
|---|---|
| Angular / Gateway | 4200 / 18080 |
| Config / Eureka | 18888 / 18761 |
| Venta / Institución / Envío / Citas | 8081 / 8082 / 8083 / 8084 |
| Catálogo / Usuario / Pago | 8085 / 8086 / 8087 |
| Keycloak / health y métricas | 18180 / 19000 |
| Kafka broker / Kafka UI | 19092 / 18085 |
| Grafana / Prometheus / Loki | 13000 / 19090 / 13100 |

Fixtures locales: `cliente` / `Cliente123!` (CLIENTE), `admin-store` / `Admin123!` (ADMIN). Consola Keycloak: `admin` / `local-admin-change-me`, configurable con `KEYCLOAK_ADMIN_PASSWORD`. El realm se importa automáticamente **solo si no existe**: editar el JSON no modifica un realm ya creado. No publicar estas cuentas ni los valores de `.env.example` en un servicio accesible por Internet.

## Compose integrado

```bash
docker compose up -d --build --wait --wait-timeout 300
```

El Compose raíz es el punto de entrada para el sistema completo: redes compartidas, dependencias con salud, bases privadas y volúmenes persistentes. Angular se sirve en 4200 con proxy `/api` al Gateway; Gateway se publica en 28080, Config en 28888 y Eureka en 28761. Keycloak mantiene el emisor público de desarrollo `http://localhost:18180/realms/garritas`, mientras los servicios consultan su JWKS por el nombre interno Docker. No ejecutar al mismo tiempo DEV y este stack: comparten los puertos de Keycloak, Kafka y Angular.

Si el builder Docker no puede descargar dependencias, compilar primero en el host:

```bash
bash scripts/dev.sh build
(cd clients/garritas-frontend && npm ci && npm run build)
docker compose -f compose.yml -f compose.prebuilt.yml up -d --build --wait --wait-timeout 300
```

Esta alternativa usa los mismos JAR y el mismo frontend compilados; conserva las comprobaciones de salud. Los Dockerfile de cada módulo también se construyen desde la **raíz** del repositorio, porque necesitan la librería común. Los Compose por servicio se conservan para trabajo manual con infraestructura externa; no sustituyen al Compose raíz.

Observabilidad opcional:

```bash
# Aplicaciones ejecutadas en el host
bash scripts/dev.sh observability
# Aplicaciones en el Compose integrado
docker compose -f compose.yml -f compose.observability.yml up -d
```

Prometheus descubre servicios por Eureka; Grafana tiene los dashboards existentes y Loki recibe los logs. El overlay raíz monta los volúmenes reales de logs; DEV lee `.runtime/`. Esta observabilidad no bloquea una compra.

## API de compra y seguridad

Catálogo GET público; modificaciones y dominios secundarios requieren ADMIN. Ventas y pagos se filtran por el `sub` del cliente; ADMIN puede auditar.

```http
POST /api/v1/ventas
Authorization: Bearer <access_token de Keycloak>
Idempotency-Key: <UUID nuevo para cada compra; conservar al reintentar>
Content-Type: application/json

{"metodoPago":"TARJETA","detalles":[{"idProducto":1,"cantidad":2}]}
```

El servidor determina cliente y precios. La respuesta inicial es pendiente; consultar `GET /api/v1/ventas/{id}` hasta `PAGADA` o `CANCELADA`. `GET /api/v1/pagos/venta/{id}` muestra el pago cuando exista. TRANSFERENCIA simula rechazo y devolución de stock; no hay cobros reales. El catálogo DEV incluye 16 productos para mascotas en cinco categorías. El frontend permite buscar, filtrar, preparar una nueva orden, editar cantidades, quitar artículos y confirmar el carrito. Los precios y el stock de compra siempre se validan en los servicios. El catálogo se gestiona con APIs ADMIN; el frontend permite CRUD de categorías.

## Pruebas

Con el stack DEV iniciado:

```bash
bash scripts/dev.sh test
(cd clients/garritas-frontend && npm test && npm run build)
python3 -m pip install -r scripts/requirements-test.txt
python3 -m playwright install chromium
python3 scripts/smoke.py
python3 scripts/consoles.py
```

Si ya hay Chromium instalado, se puede ejecutar `CHROMIUM_PATH=/usr/bin/chromium python3 scripts/smoke.py`. El smoke utiliza las cuentas de demostración, crea fixtures identificables y desactiva los productos usados. Conserva ventas, pagos, categorías y reservas como historial. No ejecutar contra datos de producción.

Para probar duplicados y recuperaciones con caída deliberada de Pago y Kafka, ejecutar `python3 scripts/faults.py` únicamente contra el stack DEV desechable. El script detiene procesos propios y recupera el broker; no usar contra producción.

Consulta [la arquitectura](docs/arquitectura.md) para contratos de eventos, manejo de duplicados, recuperación de DLT, cambios incompatibles de API y límites del despliegue local. Los resultados y el bloqueo de disco del Compose completo están en [la evidencia de validación](docs/validacion.md).

## Abrir las aplicaciones

Después de `bash scripts/dev.sh all` y `bash scripts/dev.sh observability`, estas direcciones se usan en el navegador **de la máquina donde ejecutas el proyecto**:

| Aplicación | Dirección local | Acceso de demostración |
|---|---|---|
| Garritas Store | `http://localhost:4200` | `cliente` / `Cliente123!` |
| Kafka UI | `http://localhost:18085` | Sin login; clúster `garritas` |
| Keycloak | `http://localhost:18180/admin/` | `admin` / `local-admin-change-me` |
| Eureka | `http://localhost:18761` | Sin login |
| Grafana | `http://localhost:13000` | `admin` / `local-grafana` |
| Prometheus | `http://localhost:19090` | Sin login |

Loki tiene una API en el puerto 13100; sus logs se consultan desde Grafana. En una nube, `localhost` corresponde al entorno remoto; estas direcciones no publican una web ni un acceso externo.

En **Nueva orden**, elige productos y revisa el panel **Tu carrito**. También puedes abrir **Carrito** desde la navegación. El carrito se conserva al recargar y durante el login; solo guarda identificadores, cantidades y la clave de reintento, nunca tokens ni precios confiables. Un stock cambiado bloquea la confirmación hasta corregir o quitar la línea. Al registrar el pedido, el carrito se vacía y **Mis pedidos** sigue el pago.

El catálogo inicial contiene alimentos para perros, gatos, aves y conejos, arena sanitaria, champú, bolsas de paseo, juguetes, correa, plato, cama, rascador y bebedero. La migración repetible de `db/demo` no modifica precios ni stock de productos existentes. Solo se activa en DEV y en el Compose de integración local; para excluirla de este último, definir `CATALOGO_MIGRATION_LOCATIONS=classpath:db/migration`.
