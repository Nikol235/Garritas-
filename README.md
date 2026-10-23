# Garritas Store

Tienda de mascotas con Java 21, Spring Boot 4, Spring Cloud, PostgreSQL/Flyway, Kafka, Keycloak y Angular 22. La adaptación de Pagatu hasta S11 y las decisiones de consistencia están en [el análisis arquitectónico](docs/arquitectura-s11.md).

## Desarrollo local

Requisitos: JDK 21 completo (`java` y `javac`), Docker Compose, Node 24, Python 3 y Git. Maven se descarga con el wrapper incluido.

Desde la raíz del repositorio:

```bash
bash scripts/dev.sh build
bash scripts/dev.sh up
cd clients/garritas-frontend
npm ci
npm start
```

El script inicia Kafka, Keycloak, siete PostgreSQL, Config Server, Eureka, los siete servicios y Gateway. Comprueba readiness; guarda PIDs, copias estables de los JAR y logs en `.runtime/`. No elimina volúmenes ni datos. `bash scripts/dev.sh stop` detiene las aplicaciones Java; `down` también baja los contenedores de desarrollo, conservando sus volúmenes.

En una nube con proxy Maven, `MAVEN_SETTINGS` puede apuntar a un `settings.xml` externo y `MAVEN_USER_HOME` a un directorio escribible. Se mantiene la validación TLS. Cada tarea de nube está aislada: usar el checkout existente, sin crear un worktree salvo petición explícita.

| Componente DEV | Puerto |
|---|---|
| Angular / Gateway | 4200 / 18080 |
| Config / Eureka | 18888 / 18761 |
| Venta / Institución / Envío / Citas | 8081 / 8082 / 8083 / 8084 |
| Catálogo / Usuario / Pago | 8085 / 8086 / 8087 |
| Keycloak / health y métricas | 18180 / 19000 |
| Kafka | 19092 |

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
docker compose -f obs/compose-dev.yml up -d
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

El servidor determina cliente y precios. La respuesta inicial es pendiente; consultar `GET /api/v1/ventas/{id}` hasta `PAGADA` o `CANCELADA`. `GET /api/v1/pagos/venta/{id}` muestra el pago cuando exista. TRANSFERENCIA simula rechazo y devolución de stock; no hay cobros reales. El catálogo se carga con APIs ADMIN; el frontend permite CRUD de categorías.

## Pruebas

Con el stack DEV iniciado:

```bash
bash scripts/dev.sh test
(cd clients/garritas-frontend && npm test && npm run build)
python3 -m pip install -r scripts/requirements-test.txt
python3 -m playwright install chromium
python3 scripts/smoke.py
```

Si ya hay Chromium instalado, se puede ejecutar `CHROMIUM_PATH=/usr/bin/chromium python3 scripts/smoke.py`. El smoke utiliza las cuentas de demostración, crea fixtures identificables y desactiva los productos usados. Conserva ventas, pagos, categorías y reservas como historial. No ejecutar contra datos de producción.

Para probar duplicados y recuperaciones con caída deliberada de Pago y Kafka, ejecutar `python3 scripts/faults.py` únicamente contra el stack DEV desechable. El script detiene procesos propios y recupera el broker; no usar contra producción.

Consulta [la arquitectura](docs/arquitectura-s11.md) para contratos de eventos, manejo de duplicados, recuperación de DLT, cambios incompatibles de API y límites del despliegue local. Los resultados y el bloqueo de disco del Compose completo están en [la evidencia de validación](docs/validacion-s11.md).
