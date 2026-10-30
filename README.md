# Garritas Store

Tienda y bienestar para mascotas en el Perú. Microservicios con **Java 21 / Spring Boot 4**, PostgreSQL/Flyway, Config Server, Eureka, Gateway, Kafka, Keycloak y un cliente **Angular 22**.

La organización sigue el [proyecto de referencia Pagatu](https://github.com/262dist/pagatu): infraestructura, servicios, Kafka, identidad, observabilidad, clientes y casos de uso rápido tienen sus propias carpetas.

## Estructura

```text
Garritas-/
├── .github/          # CI: compilación Java y pruebas/build de Angular
├── clients/          # garritas-frontend
├── docs/             # Arquitectura, ejecución y evidencia de validación
├── infra/            # Config Server, Eureka, Gateway y soporte técnico común
├── kafka/            # Broker Kafka y Kafka UI
├── keycloak/         # Keycloak, su PostgreSQL y el realm de demostración
├── obs/              # Prometheus, Loki, Promtail y Grafana
├── overrides/        # Personalización del sitio de documentación
├── services/         # Ocho microservicios de negocio, cada uno con PostgreSQL propio
└── uso-rapido/       # Ejemplo Python Kafka, arranque, pruebas y Compose integrado opcional
```

Los Compose y Dockerfiles de integración que estaban en la raíz se movieron a `uso-rapido/docker/`. Las herramientas están en `uso-rapido/scripts/`; el soporte común está en `infra/garritas-common/`. Las rutas de compilación y ejecución ya usan esta organización.

## Qué se puede hacer en Angular

| Pantalla | Cliente | Administrador |
|---|---|---|
| Catálogo, nueva orden y carrito | Buscar, filtrar, seleccionar sede y comprar | Igual; además gestionar productos y categorías |
| Sedes | Consultar sedes activas del Perú y seleccionar una | Crear, editar, activar y desactivar sedes |
| Especialistas | Consultar profesionales y sus especialidades; reservar cita | Gestionar profesionales y asignar varias especialidades |
| Mi cuenta y mascotas | Editar su perfil y gestionar sus propias mascotas | Perfil propio y administración de clientes |
| Citas | Reservar una o varias prestaciones para sus mascotas | Ver todas, confirmar y marcar atención; revisar detalle, total y duración |
| Envíos de pedidos (Venta) | Seleccionar cobertura y solicitar entrega de un pedido pagado | Gestionar tránsito y entrega |
| Servicios por sede (Institución) | Consultar prestaciones, precios y duración | Gestionar prestaciones y ofertas por sede |
| Logística (Envío) | Consultar coberturas durante una solicitud de entrega | Gestionar transportistas, zonas y coberturas |
| Planes y suscripciones (Usuario) | Contratar, renovar, cancelar y consultar períodos propios | Administrar planes y auditar suscripciones |
| Pagos y pedidos | Ver únicamente los suyos | Consultar todos |

Los permisos se verifican también en el Gateway y los microservicios. Ocultar botones no es la protección: una petición directa de un cliente intentando editar sedes o acceder a datos ajenos se rechaza.

**Bienestar** conserva otra relación **muchos a muchos**: un profesional tiene varias especialidades y una especialidad pertenece a varios profesionales. La tabla de asociación tiene clave primaria compuesta y claves foráneas. Citas valida las referencias de mascota, sede y profesional mediante llamadas HTTP con identidad propagada y límites de tiempo.

## Parejas para la sustentación

| Pareja original | Transaccional (cabecera/detalle) | Maestro | N:M |
|---|---|---|---|
| Venta–Institución | Venta / DetalleVenta | Institución | Sedes ↔ prestaciones |
| Envío–Citas | Cita / DetalleCita | Envío: logística | Transportistas ↔ zonas |
| Catálogo–Usuario (Fio) | Suscripcion / PeriodoSuscripcion en Usuario | Catálogo | Clientes ↔ planes |

[Asignación, reglas, migración y demo por integrante](docs/asignacion-y-sustentacion.md). [Contraste con las sesiones 1–11 del ingeniero](docs/alineacion-pagatu.md).

El perfil confirma su guardado leyendo nuevamente la API. La edad de mascotas se registra en **días o meses**, con unidad explícita; las edades históricas en años se convierten a meses mediante migración. El despacho operativo pasa a Venta; el archivo histórico de Envío se conserva y el lanzador DEV lo migra sin duplicar ventas. Las N:M con atributos se implementan con entidades de asociación y claves foráneas locales.

## Inicio rápido

Requisitos: **JDK 21 completo, Node 24, Docker Compose, Git** y Python 3 para las herramientas Linux/pruebas. Los ejemplos son locales; no se hacen cobros bancarios reales.

### Linux o WSL2

Desde la raíz:

```bash
bash uso-rapido/scripts/dev.sh build
bash uso-rapido/scripts/dev.sh all
bash uso-rapido/scripts/dev.sh status
```

`build` hace una compilación limpia para empaquetar también los cambios del soporte común; compila todos los servicios e instala el soporte común para permitir también arranques manuales por módulo. `all` inicia Kafka, Keycloak, las ocho bases de negocio, Config Server, Eureka, los ocho servicios, Gateway y Angular. Si faltan dependencias frontend, ejecuta `npm ci` antes de iniciar su servidor.

Observabilidad opcional:

```bash
bash uso-rapido/scripts/dev.sh observability
bash uso-rapido/scripts/dev.sh status --observability
```

### Windows con PowerShell

Con Docker Desktop iniciado, JDK 21 y Node 24 en PATH:

```powershell
.\uso-rapido\garritas.ps1 -Accion build
.\uso-rapido\garritas.ps1 -Accion iniciar
.\uso-rapido\garritas.ps1 -Accion estado
```

Las nuevas consolas Java/Node se ejecutan ocultas y sus logs quedan en `.runtime/`. Un registro de procesos ya finalizados se recupera automáticamente; si siguen activos, usa `estado` o `detener` antes de reiniciar. Para detener Java y Angular: `-Accion detener`. Este lanzador conserva los volúmenes y verifica los procesos registrados antes de detenerlos. También se pueden seguir los comandos manuales de cada módulo como en Pagatu; consulta [la guía de ejecución](docs/ejecucion.md).

## Abrir las aplicaciones

Las direcciones se abren **en la máquina donde ejecutas el proyecto**; no constituyen una publicación web de GitHub ni una URL externa de la nube.

| Aplicación | Dirección local | Acceso de demostración |
|---|---|---|
| Garritas Store | `http://localhost:4200` | `cliente` / `Cliente123!` |
| Kafka UI | `http://localhost:18085` | Clúster `garritas` |
| Keycloak | `http://localhost:18180/admin/` | `admin` / `local-admin-change-me` |
| Eureka | `http://localhost:18761` | Sin login |
| Gateway | `http://localhost:18080` | API con JWT |
| Grafana | `http://localhost:13000` | `admin` / `local-grafana` |
| Prometheus | `http://localhost:19090` | Sin login |

Administrador de la tienda: **`admin-store` / `Admin123!`**. Es distinto del administrador de Keycloak. Loki expone su API en 13100 y se consulta desde Grafana.

DEV incluye 16 productos para mascotas, seis sedes ficticias de Lima, Arequipa, Trujillo, Cusco y Huancayo, y profesionales/especialidades de ejemplo. Las migraciones repetibles de `db/demo` no sobrescriben datos existentes. El realm solo se importa cuando aún no existe. No uses estas identidades ni contraseñas de demostración para exponer el sistema en Internet.

El carrito conserva identificadores, cantidades, sede y clave de reintento, nunca tokens. El servidor determina precios, identidad y stock. La Saga reserva inventario, procesa un pago simulado y confirma o compensa. **TRANSFERENCIA** simula rechazo; el stock se devuelve antes de cancelar la venta.

## Uso rápido de Kafka

El ejemplo equivalente al de Pagatu está en [`uso-rapido/garritas-eventos-py`](uso-rapido/garritas-eventos-py/README.md). Tiene productor, consumidor, requisitos y Compose. Usa un topic de demostración separado para no crear compras ficticias en la Saga real.

## Pruebas y documentación

Con DEV iniciado:

```bash
bash uso-rapido/scripts/dev.sh test
(cd clients/garritas-frontend && npm test && npm run build)
python3 -m pip install -r uso-rapido/scripts/requirements-test.txt
CHROMIUM_PATH=/usr/bin/chromium python3 uso-rapido/scripts/domain_smoke.py
CHROMIUM_PATH=/usr/bin/chromium python3 uso-rapido/scripts/academic_smoke.py
CHROMIUM_PATH=/usr/bin/chromium python3 uso-rapido/scripts/smoke.py
CHROMIUM_PATH=/usr/bin/chromium python3 uso-rapido/scripts/consoles.py
```

Si no usas Chromium del sistema, instala el navegador de Playwright con `python3 -m playwright install chromium` y omite `CHROMIUM_PATH`. `domain_smoke.py` prueba todos los dominios con ADMIN y dos CLIENTE: propiedad, permisos, asociación muchos a muchos, cita, compra y entrega. Los registros de prueba se identifican como tales; los historiales de ventas y citas se conservan.

- [Guía de ejecución y diagnóstico](docs/ejecucion.md)
- [Arquitectura y decisiones](docs/arquitectura.md)
- [Resultados y límites de validación](docs/validacion.md)
- [Compose integrado opcional](uso-rapido/docker/README.md)

La documentación puede construirse con `pip install -r docs/requirements.txt` y `mkdocs build --strict`.

## Manuales en PDF

1. [Ejecutar Garritas: instalación, puertos y diagnóstico](docs/manuales/01-Ejecucion-y-puertos.pdf).
2. [Construir desde cero: pasos, rutas y código completo](docs/manuales/02-Construccion-desde-cero-con-codigo.pdf).
3. [Entender arquitectura, clases, tecnologías y conexiones](docs/manuales/03-Arquitectura-clases-y-conexiones.pdf).

[Índice y evidencias de los manuales](docs/manuales/README.md). Se incluye un ZIP de fuentes sin dependencias/binarios, con manifiesto SHA-256; fue extraído y compilado en una carpeta nueva.

## Guía para la sustentación

[Guía completa en PDF](docs/sustentacion/Guia-de-sustentacion-Garritas.pdf), [resumen oral de dos páginas](docs/sustentacion/Resumen-para-exponer.pdf) y [mapa de código con rutas/líneas exactas](docs/sustentacion/Mapa-de-codigo.txt). Incluye once diagramas, fichas de los ocho servicios y respuestas a las siete preguntas S6–S11. [Índice y verificación](docs/sustentacion/README.md).
