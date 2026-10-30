# Ejecución y diagnóstico

## Separación como en Pagatu

Kafka y Kafka UI están en `kafka/compose-dev.yml`; Keycloak y su base en `keycloak/compose-dev.yml`. Cada microservicio conserva su `compose-dev.yml` para PostgreSQL y su Maven Wrapper. `infra/` contiene Config Server, Eureka y Gateway. Las automatizaciones y el agregador Maven se ubican en `uso-rapido/`.

## Arranque manual con PowerShell

Antes de arrancar por módulo, instala el soporte común desde la raíz:

```powershell
.\infra\garritas-config\mvnw.cmd -f uso-rapido/pom.xml -pl :garritas-distributed -am install -DskipTests
```

Primero los contenedores compartidos:

```powershell
docker compose -f kafka/compose-dev.yml up -d
docker compose -f keycloak/compose-dev.yml up -d
```

En terminales independientes y desde cada carpeta:

```powershell
cd infra/garritas-config
.\mvnw.cmd spring-boot:run
```

```powershell
cd infra/garritas-eureka
.\mvnw.cmd spring-boot:run
```

Repite para `infra/garritas-gateway`. Cada servicio se inicia como en el modelo:

```powershell
cd services/garritas-institucion-ms
docker compose -f compose-dev.yml up -d
.\mvnw.cmd spring-boot:run
```

Repite para Catálogo, Usuario, Bienestar, Venta, Pago, Citas y Envío. Cuando haya una dependencia de negocio, espera a que sus servicios aparezcan en Eureka antes de utilizar el formulario. Angular se inicia desde `clients/garritas-frontend` con `npm ci` y `npm start`.

El lanzador `uso-rapido/garritas.ps1` automatiza el proceso en Windows. El script Bash `uso-rapido/scripts/dev.sh all` automatiza el equivalente en Linux/WSL2 y comprueba también una petición funcional a través del Gateway.

## Puertos de negocio DEV

| Servicio | Aplicación | PostgreSQL |
|---|---|---|
| Venta | 8081 | 15441 |
| Institución | 8082 | 15442 |
| Envío | 8083 | 15443 |
| Citas | 8084 | 15444 |
| Catálogo | 8085 | 15445 |
| Usuario | 8086 | 15446 |
| Pago | 8087 | 15447 |
| Bienestar | 8088 | 15448 |

## Operación

- `bash uso-rapido/scripts/dev.sh status --observability` comprueba endpoints y conexión Kafka. No considera un PID como prueba suficiente de funcionamiento.
- Los procesos y logs gestionados están en `.runtime/`; cada JVM ejecuta una copia de su JAR para que una compilación posterior no modifique un archivo en uso.
- Después de cambiar Java: `build`, `stop`, `all`. No ejecutes dos compilaciones Maven sobre las mismas carpetas al mismo tiempo.
- `stop` detiene los procesos gestionados; `down` baja además los contenedores y conserva los volúmenes. No eliminar volúmenes para solucionar un error de arranque sin preservar los datos.
- Si 4200 ya sirve Garritas, se conserva ese proceso existente. El lanzador no intenta apropiarse de otro servidor; para actualizarlo, detén su terminal original.
- En la nube se puede indicar `MAVEN_SETTINGS` para el proxy y `MAVEN_USER_HOME` para una caché escribible. Nunca desactivar TLS ni firmas para descargar dependencias.
- La monitorización prepara permisos de archivos públicos de `obs/` y comunica los contenedores por sus nombres internos, sin pasar por el proxy externo.

## Roles y datos

Las sedes tienen baja lógica: desactivarlas impide nuevas selecciones sin borrar el historial de pedidos. Las citas verifican que la mascota pertenezca al cliente y que la sede/profesional estén activos. La clave única de profesional y hora evita reservas concurrentes para el mismo bloque. No se permiten confirmar citas canceladas ni atender citas sin confirmar.

Los envíos se crean solo para ventas pagadas y pertenecen al mismo cliente de la venta; hay un envío por pedido. Solo ADMIN puede marcar tránsito/entrega. Un cliente no puede cancelar un envío en tránsito o ya entregado.

Una especialidad utilizada no se elimina: primero se desasigna de sus profesionales. Cambiar las asociaciones se confirma en una única transacción de la base de Bienestar.

## Actualización académica y recuperación de arranque

[Asignación y migraciones](asignacion-y-sustentacion.md) explica el traslado de despachos a Venta, las nuevas relaciones y las edades en días/meses. Los puertos no cambian. `build` utiliza `clean package` para evitar que un JAR conserve una copia anterior de la librería común.

En Windows las consolas nuevas se ocultan y los logs se conservan en `.runtime`. No ejecutes dos arranques simultáneamente ni alternes copias en C: y D: que comparten puertos y contenedores. `detener` comprueba id y hora del proceso antes de detenerlo. Un registro sin procesos vivos se retira al iniciar.

Swagger de cada servicio está en `http://localhost:PUERTO/swagger-ui/index.html`; la documentación es consultable y las operaciones protegidas requieren un JWT Bearer mediante Authorize. No se incluyen tokens en esta documentación.
