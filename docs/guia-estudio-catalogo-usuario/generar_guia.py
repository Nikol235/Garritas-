"""Generate a self-contained HTML study guide, vector C4 diagrams and printable PDF.
Run from any directory: python docs/guia-estudio-catalogo-usuario/generar_guia.py
Requires Graphviz and Playwright with Chromium; no external web assets are loaded.
"""

from pathlib import Path
import html, json, re, subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
COMMIT = "cf3cedec51da578248ce840fe03c4600bb7af593"
BASE = f"https://github.com/Nikol235/Garritas-/blob/{COMMIT}/"
C = "services/garritas-catalogo-ms/src/main/java/pe/edu/upeu/garritas/catalogo/"
U = "services/garritas-usuario-ms/src/main/java/pe/edu/upeu/garritas/usuario/"
V = "services/garritas-venta-ms/src/main/java/pe/edu/upeu/garritas/venta/"
P = "services/garritas-pago-ms/src/main/java/pe/edu/upeu/garritas/pago/"
COMMON = "infra/garritas-common/src/main/java/pe/edu/upeu/garritas/common/"
REFS = {}


def ref(key, path, needle, label=None):
    text = (ROOT / path).read_text()
    assert (
        text
        == subprocess.check_output(
            ["git", "show", f"{COMMIT}:{path}"], cwd=ROOT
        ).decode()
    ), path
    hits = [i for i, line in enumerate(text.splitlines(), 1) if needle in line]
    assert hits, (path, needle)
    line = hits[0]
    REFS[key] = {
        "path": path,
        "line": line,
        "needle": needle,
        "label": label or key,
        "url": f"{BASE}{path}#L{line}",
    }


def a(key):
    r = REFS[key]
    return f'<a href="{r["url"]}">{html.escape(r["label"])}</a>'


def code(key, before=0, after=9):
    r = REFS[key]
    lines = (ROOT / r["path"]).read_text().splitlines()
    lo = max(0, r["line"] - 1 - before)
    hi = min(len(lines), r["line"] + after)
    return (
        '<div class="source">'
        + a(key)
        + f' · línea {r["line"]}</div><pre>'
        + html.escape("\n".join(f"{i+1:3}  {lines[i]}" for i in range(lo, hi)))
        + "</pre>"
    )


def table(headers, rows):
    return (
        "<table><thead><tr>"
        + "".join("<th>" + x + "</th>" for x in headers)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join("<td>" + str(x) + "</td>" for x in row) + "</tr>"
            for row in rows
        )
        + "</tbody></table>"
    )


def box(text):
    return '<aside class="note">' + text + "</aside>"


def section(id, title, body):
    return f'<section class="chapter" id="{id}"><p class="eyebrow">GUÍA DE ESTUDIO · GARRITAS STORE</p><h1>{title}</h1>{body}</section>'


for key, path, needle, label in [
    (
        "prod_controller",
        C + "controller/ProductoController.java",
        "public class ProductoController",
        "ProductoController: endpoints de productos",
    ),
    (
        "prod_create",
        C + "service/ProductoService.java",
        "public ProductoResponse crear",
        "ProductoService.crear(): alta de productos",
    ),
    (
        "prod_update",
        C + "service/ProductoService.java",
        "public ProductoResponse actualizar",
        "ProductoService.actualizar(): edición y categorías",
    ),
    (
        "prod_delete",
        C + "service/ProductoService.java",
        "public void eliminar",
        "ProductoService.eliminar(): baja lógica",
    ),
    (
        "prod_query",
        C + "repository/ProductoRepository.java",
        "Page<Producto> buscar",
        "ProductoRepository.buscar(): filtros y paginación",
    ),
    (
        "prod_entity",
        C + "entity/Producto.java",
        "@ManyToMany",
        "Producto: relación N:M con categorías",
    ),
    (
        "prod_mapper",
        C + "mapper/ProductoMapper.java",
        "public ProductoResponse toResponse",
        "ProductoMapper: entidad a respuesta",
    ),
    (
        "cat_controller",
        C + "controller/CategoriaController.java",
        "public class CategoriaController",
        "CategoriaController: CRUD de categorías",
    ),
    (
        "cat_service",
        C + "service/CategoriaService.java",
        "public class CategoriaService",
        "CategoriaService: reglas y persistencia",
    ),
    (
        "inv_consume",
        C + "messaging/InventarioEvents.java",
        "public void consume",
        "InventarioEvents.consume(): entrada de Kafka",
    ),
    (
        "inv_reserve",
        C + "messaging/InventarioEvents.java",
        "private void reservar",
        "InventarioEvents.reservar(): reserva e idempotencia",
    ),
    (
        "inv_lock",
        C + "messaging/InventarioEvents.java",
        "SELECT stock,activo,precio",
        "Bloqueo de filas antes de cambiar stock",
    ),
    (
        "inv_release",
        C + "messaging/InventarioEvents.java",
        "private void liberar",
        "InventarioEvents.liberar(): compensación",
    ),
    (
        "user_controller",
        U + "controller/UsuarioController.java",
        "public class UsuarioController",
        "UsuarioController: gestión administrativa de usuarios",
    ),
    (
        "me_controller",
        U + "controller/MiCuentaController.java",
        "public class MiCuentaController",
        "MiCuentaController: perfil y mascotas propias",
    ),
    (
        "profile_save",
        U + "service/UsuarioService.java",
        "public UsuarioResponse guardarMe",
        "UsuarioService.guardarMe(): persistencia por sub",
    ),
    (
        "profile_lookup",
        U + "service/UsuarioService.java",
        "public Usuario miUsuario",
        "UsuarioService.miUsuario(): identidad y perfil",
    ),
    (
        "user_roles",
        U + "entity/Usuario.java",
        "@ManyToMany",
        "Usuario: relación N:M con Rol",
    ),
    (
        "user_pets",
        U + "entity/Usuario.java",
        "@OneToMany",
        "Usuario: relación 1:N con Mascota",
    ),
    (
        "role_controller",
        U + "controller/RolController.java",
        "public class RolController",
        "RolController: catálogo de roles internos",
    ),
    (
        "role_service",
        U + "service/RolService.java",
        "public void eliminar",
        "RolService.eliminar(): protección de roles usados",
    ),
    (
        "role_assign",
        U + "controller/UsuarioController.java",
        "public UsuarioResponse asignarRol",
        "UsuarioController.asignarRol(): asociación usuario–rol",
    ),
    (
        "pet_controller",
        U + "controller/MascotaController.java",
        "public class MascotaController",
        "MascotaController: mascotas por usuario",
    ),
    (
        "pet_service",
        U + "service/MascotaService.java",
        "public MascotaResponse crear",
        "MascotaService.crear(): alta y propiedad",
    ),
    (
        "phone",
        U + "dto/UsuarioRequest.java",
        "El celular peruano",
        "UsuarioRequest: validación del celular y DNI",
    ),
    (
        "pet_age",
        U + "dto/MascotaRequest.java",
        "edadUnidad",
        "MascotaRequest: edad y unidad explícita",
    ),
    (
        "sub_controller",
        U + "controller/SuscripcionController.java",
        "public class SuscripcionController",
        "SuscripcionController: planes y ciclo de suscripciones",
    ),
    (
        "sub_contract",
        U + "service/SuscripcionService.java",
        "public SuscripcionResponse contratar",
        "SuscripcionService.contratar(): proceso transaccional",
    ),
    (
        "sub_renew",
        U + "service/SuscripcionService.java",
        "public SuscripcionResponse renovar",
        "SuscripcionService.renovar(): período e idempotencia",
    ),
    (
        "sub_cancel",
        U + "service/SuscripcionService.java",
        "public SuscripcionResponse cancelar",
        "SuscripcionService.cancelar(): transición local",
    ),
    (
        "sub_lock",
        U + "service/SuscripcionService.java",
        "private void lock",
        "Bloqueos de suscripción y clave de reintento",
    ),
    (
        "sub_entity",
        U + "entity/Suscripcion.java",
        "@ManyToOne",
        "Suscripcion: entidad de asociación Usuario–Plan",
    ),
    (
        "sub_period",
        U + "entity/PeriodoSuscripcion.java",
        "private UUID idempotencyKey",
        "PeriodoSuscripcion: clave y precio histórico",
    ),
    (
        "user_repo",
        U + "repository/UsuarioRepository.java",
        "Page<Usuario> buscarConRol",
        "UsuarioRepository: búsqueda por rol y DNI/nombre",
    ),
    (
        "security",
        COMMON + "SecurityConfiguration.java",
        "SecurityFilterChain",
        "SecurityConfiguration: protección de rutas",
    ),
    (
        "jwt_roles",
        COMMON + "SecurityConfiguration.java",
        "realm_access",
        "Conversión de roles reales del JWT",
    ),
    (
        "identity",
        COMMON + "CurrentUser.java",
        "public static void requireOwner",
        "CurrentUser.requireOwner(): propiedad de recursos",
    ),
    (
        "outbox",
        COMMON + "Outbox.java",
        "public void append",
        "Outbox.append(): cambio y evento en una transacción",
    ),
    (
        "outbox_send",
        COMMON + "Outbox.java",
        "public void publish",
        "Outbox.publish(): publicación posterior a Kafka",
    ),
    (
        "inbox",
        COMMON + "Inbox.java",
        "public boolean claim",
        "Inbox.claim(): deduplicación por eventId",
    ),
    (
        "event_contract",
        COMMON + "SagaEvent.java",
        "public record SagaEvent",
        "SagaEvent: contrato del evento",
    ),
    (
        "messaging",
        COMMON + "MessagingConfiguration.java",
        "NewTopic sagaTopic",
        "MessagingConfiguration: topic y particiones",
    ),
    (
        "dlt",
        COMMON + "MessagingConfiguration.java",
        "DefaultErrorHandler kafkaErrorHandler",
        "Reintentos y topic DLT",
    ),
    (
        "sale_create",
        V + "service/VentaService.java",
        "public VentaResponse crear",
        "VentaService.crear(): validación, total y outbox",
    ),
    (
        "sale_events",
        V + "messaging/VentaEvents.java",
        "public void consume",
        "VentaEvents: estados de Saga y despacho pagado",
    ),
    (
        "feign",
        V + "client/ProductoClient.java",
        "@FeignClient",
        "ProductoClient: Feign por nombre lógico",
    ),
    (
        "breaker",
        V + "client/CatalogoConsulta.java",
        '.create("catalogo")',
        "CatalogoConsulta: Circuit Breaker y respuesta controlada",
    ),
    (
        "pago",
        P + "messaging/PagoEvents.java",
        "boolean aprobado",
        "PagoEvents: pago simulado y rechazo",
    ),
    (
        "gateway",
        "infra/garritas-config/config-repo/garritas-gateway-dev.yml",
        "uri: lb://garritas-catalogo-ms",
        "Rutas del Gateway hacia Catálogo y Usuario",
    ),
    (
        "eureka",
        "infra/garritas-config/config-repo/garritas-eureka-dev.yml",
        "port:",
        "Configuración de Eureka DEV",
    ),
    (
        "catalog_config",
        "infra/garritas-config/config-repo/garritas-catalogo-ms-dev.yml",
        "defaultZone:",
        "Registro de Catálogo en Eureka",
    ),
    (
        "user_config",
        "infra/garritas-config/config-repo/garritas-usuario-ms-dev.yml",
        "defaultZone:",
        "Registro de Usuario en Eureka",
    ),
    (
        "jwt_config",
        "infra/garritas-config/config-repo/garritas-usuario-ms-dev.yml",
        "jwk-set-uri:",
        "Emisor, claves públicas y audiencia del JWT",
    ),
    (
        "timeout",
        "infra/garritas-config/config-repo/garritas-venta-ms-dev.yml",
        "connectTimeout:",
        "Timeouts Feign y configuración de los circuitos",
    ),
    (
        "kafka_config",
        "kafka/compose-dev.yml",
        "KAFKA_ADVERTISED_LISTENERS",
        "Kafka: direcciones internas y externas",
    ),
    (
        "kafka_groups",
        "infra/garritas-config/config-repo/garritas-catalogo-ms-dev.yml",
        "group-id:",
        "Grupo consumidor propio de Catálogo",
    ),
    (
        "db_catalog",
        "services/garritas-catalogo-ms/compose-dev.yml",
        "POSTGRES_PASSWORD:",
        "PostgreSQL de Catálogo: credenciales DEV",
    ),
    (
        "db_user",
        "services/garritas-usuario-ms/compose-dev.yml",
        "POSTGRES_PASSWORD:",
        "PostgreSQL de Usuario: credenciales DEV",
    ),
    (
        "kc_users",
        "keycloak/garritas-realm.json",
        '"username": "cliente"',
        "Usuario cliente de demostración en Keycloak",
    ),
    (
        "kc_adminstore",
        "keycloak/garritas-realm.json",
        '"username": "admin-store"',
        "Usuario administrador de la tienda",
    ),
    (
        "kc_password",
        "keycloak/compose-dev.yml",
        "KC_BOOTSTRAP_ADMIN_PASSWORD",
        "Contraseña de administración inicial de Keycloak",
    ),
    (
        "grafana_password",
        "obs/compose-dev.yml",
        "GF_SECURITY_ADMIN_PASSWORD",
        "Contraseña inicial de Grafana DEV",
    ),
    (
        "pkce",
        "clients/garritas-frontend/src/app/core/auth.ts",
        "pkceMethod:",
        "Auth de Angular: PKCE y sesión",
    ),
    (
        "frontend_api",
        "clients/garritas-frontend/public/config.json",
        "apiUrl",
        "Angular: dirección de la API del Gateway",
    ),
    (
        "frontend_prod",
        "clients/garritas-frontend/src/app/features/admin/productos.component.ts",
        "  save()",
        "Angular: formulario de producto y categorías",
    ),
    (
        "frontend_profile",
        "clients/garritas-frontend/src/app/features/cuenta/cuenta.component.ts",
        "  save()",
        "Angular: guardar y volver a consultar el perfil",
    ),
    (
        "frontend_roles",
        "clients/garritas-frontend/src/app/features/admin/usuarios-roles.component.ts",
        "export class",
        "Angular: asignación de roles internos",
    ),
    (
        "frontend_sub",
        "clients/garritas-frontend/src/app/features/planes/planes.component.ts",
        "  contratar(",
        "Angular: contratación de planes",
    ),
    (
        "flyway_cat",
        "services/garritas-catalogo-ms/src/main/resources/db/migration/V5__producto_categorias_many_to_many.sql",
        "CREATE TABLE",
        "Migración producto_categoria",
    ),
    (
        "flyway_user",
        "services/garritas-usuario-ms/src/main/resources/db/migration/V5__create_roles_tables.sql",
        "CREATE TABLE",
        "Migración rol y usuario_rol",
    ),
    (
        "flyway_sub",
        "services/garritas-usuario-ms/src/main/resources/db/migration/V4__suscripciones_periodos.sql",
        "CREATE TABLE suscripciones",
        "Migración de suscripciones y períodos",
    ),
]:
    ref(key, path, needle, label)

DIAGRAMS = {
    "c1-contexto": (
        "C4 · Nivel 1 — Contexto del sistema",
        """
cliente [label="Cliente\n[Persona]\nCompra y gestiona sus mascotas",fillcolor="#155e75",fontcolor="white"];
admin [label="Administrador\n[Persona]\nMantiene productos y usuarios",fillcolor="#155e75",fontcolor="white"];
sys [label="Garritas Store\n[Sistema de software]\nTienda y servicios para mascotas",fillcolor="#176b4d",fontcolor="white"];
idp [label="Keycloak\n[Sistema externo al negocio]\nIdentidad y roles de acceso",fillcolor="#e2e8f0"];
cliente -> sys [label="Compra, consulta y reserva"];
admin -> sys [label="Administra"];
sys -> idp [label="Integra OIDC y valida JWT"];
cliente -> idp [label="Inicia sesión",style=dashed];
admin -> idp [label="Inicia sesión",style=dashed];
""",
    ),
    "c2-contenedores": (
        "C4 · Nivel 2 — Contenedores: foco en Catálogo y Usuario",
        """
angular [label="Angular :4200\n[SPA]\nInterfaz de la tienda"];
kc [label="Keycloak :18180\n[Servidor OIDC]\nAutenticación",fillcolor="#e2e8f0"];
gateway [label="Gateway :18080\n[Spring Cloud Gateway MVC]\nEnrutamiento y seguridad"];
eureka [label="Eureka :18761\n[Registro de servicios]\nDescubrimiento",fillcolor="#e2e8f0"];
cat [label="Catálogo :8085\n[Spring Boot]\nProductos e inventario",fillcolor="#176b4d",fontcolor="white"];
usr [label="Usuario :8086\n[Spring Boot]\nPerfiles y suscripciones",fillcolor="#176b4d",fontcolor="white"];
venta [label="Venta :8081\n[Spring Boot]\nÓrdenes y Saga",fillcolor="#e2e8f0"];
pago [label="Pago :8087\n[Spring Boot]\nPago simulado",fillcolor="#e2e8f0"];
citas [label="Citas :8084\n[Spring Boot]\nReservas",fillcolor="#e2e8f0"];
kafka [label="Kafka :19092 (host)\n[Broker de eventos]\nTopic de ventas",fillcolor="#fff1cc"];
dbc [label="PostgreSQL Catálogo\n:15445 → :5432\n[Base de datos]",shape=cylinder];
dbu [label="PostgreSQL Usuario\n:15446 → :5432\n[Base de datos]",shape=cylinder];
angular -> gateway [label="REST + JWT"];
angular -> kc [label="Login PKCE",style=dashed];
gateway -> cat [label="/productos, /categorias"];
gateway -> usr [label="/usuarios, /planes, etc."];
gateway -> venta [label="/ventas"];
gateway -> citas [label="/citas"];
venta -> cat [label="Feign: precio y stock"];
citas -> usr [label="HTTP: mascota propia"];
cat -> dbc [label="JPA / JDBC"];
usr -> dbu [label="JPA / JDBC"];
venta -> kafka [label="Produce / consume",color="#b7791f"];
cat -> kafka [label="Consume / produce",color="#b7791f"];
pago -> kafka [label="Consume / produce",color="#b7791f"];
gateway -> eureka [label="Descubre instancias",style=dashed];
cat -> eureka [label="Se registra",style=dashed];
usr -> eureka [label="Se registra",style=dashed];
{rank=same; cat; usr;}
""",
    ),
    "c3-catalogo": (
        "C4 · Nivel 3 — Componentes dentro de Catálogo",
        """
rest [label="ProductoController\nCategoriaController\n[Componentes REST]"];
security [label="SecurityConfiguration\nCurrentUser\n[Seguridad compartida]",fillcolor="#e2e8f0"];
service [label="ProductoService\nCategoriaService\n[Reglas y transacciones]"];
mapper [label="ProductoMapper\nCategoriaMapper + DTO\n[Conversión]"];
repo [label="ProductoRepository\nCategoriaRepository\n[JPA y consultas]"];
consumer [label="InventarioEvents\n[Consumidor Kafka]\nReserva / libera stock",fillcolor="#fff1cc"];
inbox [label="Inbox\n[Deduplicación]"];
outbox [label="Outbox\n[Publicación durable]"];
db [label="PostgreSQL Catálogo\nProductos, categorías,\nreservas, inbox y outbox",shape=cylinder];
rest -> security [label="Petición protegida",style=dashed];
rest -> service [label="Delega"];
service -> repo [label="Consulta / guarda"];
service -> mapper [label="Construye respuesta"];
repo -> db [label="SQL vía JPA"];
consumer -> inbox [label="claim(eventId)"];
consumer -> db [label="JDBC + bloqueos de fila"];
consumer -> outbox [label="Resultado de reserva / liberación"];
inbox -> db [label="Misma transacción"];
outbox -> db [label="Guarda evento"];
""",
    ),
    "c3-usuario": (
        "C4 · Nivel 3 — Componentes dentro de Usuario",
        """
controllers [label="Usuario / MiCuenta / Mascota /\nRol / SuscripcionController\n[Componentes REST]"];
services [label="Usuario / Mascota / Rol /\nSuscripcionService\n[Reglas de negocio]"];
security [label="SecurityConfiguration\nCurrentUser.requireOwner\n[JWT y propiedad]",fillcolor="#e2e8f0"];
repos [label="Usuario, Mascota, Rol, Plan,\nSuscripcion y PeriodoRepository\n[Persistencia JPA]"];
mappers [label="Mappers y DTO\n[Validación de entrada\ny respuestas sin entidades]"];
lock [label="JdbcTemplate + EntityManager\n[Bloqueos de suscripción\ny actualización segura]"];
db [label="PostgreSQL Usuario\nPerfiles, mascotas, roles,\nplanes, suscripciones y períodos",shape=cylinder];
controllers -> services [label="Invoca operación"];
controllers -> mappers [label="Request validado",style=dashed];
services -> security [label="Comprueba propietario",style=dashed];
services -> repos [label="Consulta / guarda"];
services -> mappers [label="Genera DTO"];
services -> lock [label="Contratar / renovar"];
repos -> db [label="JPA"];
lock -> db [label="Misma transacción local"];
""",
    ),
    "c4-catalogo": (
        "C4 · Nivel 4 — Código: clases y persistencia de Catálogo",
        """
p [label="Producto\n[Clase JPA]\nid, nombre, precio, stock\nactivo, version"];
c [label="Categoria\n[Clase JPA]\nid, nombre, descripcion"];
j [label="producto_categoria\n[Tabla de unión]\nid_producto + id_categoria",shape=cylinder];
r [label="reservas_stock\n[Tabla SQL]\nid_venta único\nNUEVA / RESERVADA /\nRECHAZADA / LIBERADA",shape=cylinder];
i [label="InventarioEvents\n[Clase]\nconsume()\nreservar()\nliberar()",fillcolor="#fff1cc"];
p -> c [label="N:M · categorias\n@ManyToMany",dir=both];
p -> c [label="N:1 · categoria\nCompatibilidad histórica",style=dashed];
p -> j [label="@JoinTable"];
c -> j [label="FK de categoría"];
i -> p [label="JDBC modifica stock\ny aumenta version"];
i -> r [label="Deduplicación por venta"];
""",
    ),
    "c4-usuario": (
        "C4 · Nivel 4 — Código: asociaciones de Usuario",
        """
u [label="Usuario\n[Clase JPA]\nid Long + subject String\nDatos de contacto"];
m [label="Mascota\n[Clase JPA]\nEdad + DIAS/MESES"];
r [label="Rol\n[Clase JPA]\nClasificación interna"];
s [label="Suscripcion\n[Entidad de asociación]\nEstado y vigencia"];
p [label="Plan\n[Clase JPA]\nPrecio y duración"];
period [label="PeriodoSuscripcion\n[Clase JPA]\nALTA / RENOVACION\nPrecio histórico + clave"];
u -> m [label="1:N · mascotas"];
u -> r [label="N:M vía usuario_rol",dir=both];
u -> s [label="1:N (por id_usuario)"];
p -> s [label="1:N (por id_plan)"];
s -> period [label="1:N · periodos"];
u -> period [label="1:N (por id_usuario)",style=dashed];
""",
    ),
    "saga-compensacion": (
        "Diagrama dinámico — Saga y compensación de inventario",
        """
a [label="1. Venta crea orden pendiente\nGuarda venta + outbox\nEvento: venta.creada"];
b [label="2. Catálogo reserva stock\n10 → 8 unidades\nEvento: inventario.reservado"];
c [label="3. Pago procesa el total\nTRANSFERENCIA simula rechazo\nEvento: pago.fallido"];
d [label="4. Catálogo compensa\n8 → 10 unidades\nEvento: inventario.liberado",fillcolor="#fff1cc"];
e [label="5. Venta termina CANCELADA\nSin despacho"];
ok [label="Pago aprobado\npago.validado → PAGADA\nDespacho si incluyó delivery",fillcolor="#dcfce7"];
a -> b [label="Kafka"];
b -> c [label="Kafka"];
c -> d [label="Rechazo",color="#b45309"];
d -> e [label="Kafka"];
c -> ok [label="Alternativa exitosa",style=dashed];
""",
    ),
    "jwt": (
        "Diagrama dinámico — Identidad y protección del perfil",
        """
a [label="Cliente en Angular\nInicia sesión"];
b [label="Keycloak\nAuthorization Code + PKCE\nEmite JWT firmado"];
c [label="Gateway\nValida JWT y enruta"];
d [label="Usuario MS\nValida JWT nuevamente\nCurrentUser.subject()"];
e [label="Perfil propio\nBusca usuarios.subject = sub\nValida propiedad de mascotas"];
a -> b [label="Redirección OIDC"];
b -> a [label="Código y canje PKCE"];
a -> c [label="Authorization: Bearer JWT"];
c -> d [label="HTTP con el token"];
d -> e [label="Control de propiedad"];
""",
    ),
}

# Focused C2 view: keep discovery and authentication in their own explanations to avoid crossing labels.
DIAGRAMS["c2-contenedores"] = (
    DIAGRAMS["c2-contenedores"][0],
    r"""subgraph cluster_store {
 label="Garritas Store · aplicaciones y bases enfocadas"; color="#9db8a6"; style="rounded,dashed";
 angular [label="Angular :4200\n[SPA]\nCliente web"];
 gateway [label="Gateway :18080\n[Spring Cloud Gateway MVC]\nEntrada de las APIs"];
 venta [label="Venta :8081\n[Spring Boot]\nProceso de compra",fillcolor="#e2e8f0"];
 citas [label="Citas :8084\n[Spring Boot]\nReservas",fillcolor="#e2e8f0"];
 cat [label="Catálogo :8085\n[Spring Boot]\nProductos e inventario",fillcolor="#176b4d",fontcolor="white"];
 usr [label="Usuario :8086\n[Spring Boot]\nPerfiles y suscripciones",fillcolor="#176b4d",fontcolor="white"];
 dbc [label="PostgreSQL Catálogo\n:15445 → :5432\n[Base de datos]",shape=cylinder];
 dbu [label="PostgreSQL Usuario\n:15446 → :5432\n[Base de datos]",shape=cylinder];
 kafka [label="Kafka :19092 (host)\n[Broker]\nEventos de ventas",fillcolor="#fff1cc"];
 angular -> gateway [label="REST + JWT"];
 gateway -> cat [label="/productos y /categorias"];
 gateway -> usr [label="/usuarios, /planes, etc."];
 venta -> cat [label="Feign: precio y stock"];
 citas -> usr [label="HTTP: mascota propia"];
 cat -> dbc [label="JPA / JDBC"];
 usr -> dbu [label="JPA / JDBC"];
 cat -> kafka [label="Consume / produce",color="#b7791f"];
 {rank=same;venta;gateway;citas;}
 {rank=same;cat;usr;}
 {rank=same;dbc;kafka;dbu;}
}""",
)
for key, nodes, label in [
    (
        "c3-catalogo",
        "rest security service mapper repo consumer inbox outbox",
        "Límite del contenedor: garritas-catalogo-ms",
    ),
    (
        "c3-usuario",
        "controllers services security repos mappers lock",
        "Límite del contenedor: garritas-usuario-ms",
    ),
]:
    title, body = DIAGRAMS[key]
    body += (
        '\nsubgraph cluster_boundary {label="'
        + label
        + '"; color="#9db8a6"; style="rounded,dashed"; fontname="DejaVu Sans"; fontsize=12; '
        + "; ".join(nodes.split())
        + ";}\n"
    )
    DIAGRAMS[key] = (title, body)

DOTHEAD = """digraph G { graph [rankdir=TB,bgcolor="transparent",pad="0.18",nodesep="0.35",ranksep="0.48",fontname="DejaVu Sans",fontsize=12]; node [shape=box,style="rounded,filled",fillcolor="#eef7f0",color="#729b84",fontname="DejaVu Sans",fontsize=12,margin="0.16,0.12"]; edge [color="#526777",fontname="DejaVu Sans",fontsize=10,arrowsize=0.7];"""


def diagram(key):
    title, body = DIAGRAMS[key]
    p = OUT / "diagramas" / key
    p.with_suffix(".dot").write_text(DOTHEAD + body + "\n}")
    subprocess.run(
        ["dot", "-Tsvg", str(p.with_suffix(".dot")), "-o", str(p.with_suffix(".svg"))],
        check=True,
    )
    subprocess.run(
        [
            "dot",
            "-Tpng",
            "-Gdpi=150",
            str(p.with_suffix(".dot")),
            "-o",
            str(p.with_suffix(".png")),
        ],
        check=True,
    )
    svg = p.with_suffix(".svg").read_text()
    svg = svg[svg.index("<svg") :]
    svg = re.sub(
        r"<svg\b", f'<svg role="img" aria-label="{html.escape(title)}"', svg, count=1
    )
    return (
        "<figure>"
        + svg
        + "<figcaption>"
        + html.escape(title)
        + "</figcaption></figure>"
    )


parts = []
parts.append(
    """<section class="cover"><p class="eyebrow">ESTUDIAR · ENTENDER · SUSTENTAR</p><h1>Catálogo y Usuario<br><span>Garritas Store</span></h1><p class="lead">Guía explicada con C4 Model, código real y ejemplos para la exposición.</p><div class="cover-tags">C1 Contexto · C2 Contenedores · C3 Componentes · C4 Código</div><p>Incluye Eureka, Gateway, Keycloak, Kafka, Saga, compensación y ubicaciones de credenciales de demostración.</p><p><strong>Responsable de estos servicios: Fio.</strong><br>El contenido también permite explicar cómo colaboran con Venta, Pago y Citas.</p><p class="revision">Código revisado: <code>cf3cede</code> · Rama <code>feat/garritas-store</code><br>Los enlaces de código fijan esta revisión para conservar sus líneas exactas.</p><p><a href="#indice">Ir al índice</a> · <button onclick="window.print()">Imprimir / guardar como PDF</button></p></section>"""
)
chapters = [
    ("rapido", "1. Lo esencial para explicar en un minuto"),
    ("c4", "2. Cómo leer C4 Model"),
    ("contexto", "3. C1: contexto de Garritas"),
    ("contenedores", "4. C2: conexiones reales"),
    ("catalogo", "5. Qué administra Catálogo"),
    ("cat-componentes", "6. C3: componentes de Catálogo"),
    ("cat-codigo", "7. C4: clases y muchos a muchos de Catálogo"),
    ("usuario", "8. Qué administra Usuario"),
    ("usr-componentes", "9. C3: componentes de Usuario"),
    ("usr-codigo", "10. C4: clases y relaciones de Usuario"),
    ("crud", "11. Dónde están los CRUD y reglas"),
    ("infra", "12. Eureka, Gateway y comunicación resiliente"),
    ("seguridad", "13. Keycloak, JWT y perfil propio"),
    ("mensajes", "14. Kafka, Outbox e Inbox"),
    ("saga", "15. Saga: fallos y compensación"),
    ("claves", "16. Credenciales, claves e identificadores"),
    ("demo", "17. Cómo exponerlo desde Angular"),
    ("preguntas", "18. Preguntas y respuestas rápidas"),
    ("mapa", "19. Mapa completo del código"),
]
parts.append(
    '<section class="chapter" id="indice"><h1>Índice</h1><ol class="toc">'
    + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in chapters)
    + "</ol>"
    + box(
        "Los diagramas se pueden ampliar en el HTML. El PDF contiene texto seleccionable y enlaces al código. Las imágenes PNG y SVG también están en la carpeta <code>diagramas</code>."
    )
    + "</section>"
)
parts.append(
    section(
        "rapido",
        chapters[0][1],
        table(
            ["Servicio", "Qué administra", "Cómo lo explicas"],
            [
                [
                    "Catálogo",
                    "Productos, categorías, stock y reservas de inventario.",
                    "“Dice qué vendemos, cuánto cuesta y qué unidades podemos reservar”.",
                ],
                [
                    "Usuario",
                    "Perfiles, mascotas, roles internos, planes, suscripciones y períodos.",
                    "“Organiza al cliente y registra su vínculo con los planes, conservando su historial”.",
                ],
            ],
        )
        + """<h2>Clasificación para la sustentación</h2><p><strong>Catálogo es principalmente un servicio de datos maestros</strong>, aunque también participa transaccionalmente en la reserva y compensación del stock. No significa que carezca de transacciones.</p><p><strong>Usuario tiene una capacidad transaccional verificable en las suscripciones</strong>: contratar, renovar y cancelar con estados e historial. El CRUD de perfiles por sí solo no explica esa capacidad.</p><p>Fio puede demostrar muchos a muchos tanto en <strong>Producto–Categoría</strong> como en <strong>Usuario–Rol</strong>. También existe Usuario–Plan mediante Suscripcion.</p>"""
        + box(
            "No atribuyas a Usuario la emisión de tokens: el proveedor de identidad es Keycloak. No atribuyas a Usuario una Saga de Kafka: la Saga implementada de compra involucra Venta, Catálogo y Pago."
        ),
    )
)
parts.append(
    section(
        "c4",
        chapters[1][1],
        """<p>C4 es una forma de explicar una arquitectura con cuatro acercamientos. Cada nivel responde una pregunta distinta.</p>"""
        + table(
            ["Nivel", "Pregunta", "En esta guía"],
            [
                [
                    "C1 · Contexto",
                    "¿Quién usa el sistema y con qué sistema externo se relaciona?",
                    "Clientes, administradores, Garritas y Keycloak.",
                ],
                [
                    "C2 · Contenedores",
                    "¿Qué aplicaciones y almacenes ejecutables lo componen?",
                    "Angular, Gateway, microservicios, Kafka y PostgreSQL.",
                ],
                [
                    "C3 · Componentes",
                    "¿Cómo se organiza por dentro una aplicación?",
                    "Controllers, services, repositorios y mensajería.",
                ],
                [
                    "C4 · Código",
                    "¿Qué clases y relaciones implementan un componente?",
                    "Entidades, asociaciones y métodos reales de Catálogo y Usuario.",
                ],
            ],
        )
        + """<p><strong>“Contenedor” en C4 no significa obligatoriamente contenedor Docker.</strong> Un microservicio ejecutado como proceso Java sigue siendo un contenedor de software en el modelo C4.</p><p>Los diagramas de nivel 4 usan clases reales y anotaciones JPA. Cuando aparece una tabla SQL como apoyo, se identifica explícitamente como tabla, no como clase Java.</p>""",
    )
)
parts.append(
    section(
        "contexto",
        chapters[2][1],
        diagram("c1-contexto")
        + """<p>El cliente compra y gestiona a sus mascotas. El administrador mantiene información y opera la tienda. Keycloak proporciona autenticación y roles de acceso; forma parte de la solución desplegada, pero está fuera de la lógica propia del negocio.</p>""",
    )
)
parts.append(
    section(
        "contenedores",
        chapters[3][1],
        diagram("c2-contenedores")
        + """<p>Esta es una vista enfocada: también existen Pago, Institución, Envío y Bienestar, además de Eureka, Keycloak, Config Server y observabilidad. Venta y Pago también intercambian eventos con Kafka, como muestra el diagrama de Saga. No se dibujan todos sus enlaces para mantener legible el acercamiento a los dos servicios estudiados.</p><p>Catálogo y Usuario <strong>no comparten base de datos ni necesitan llamarse directamente</strong> para sus CRUD. Venta consulta Catálogo por Feign. Citas consulta Usuario para verificar la mascota del cliente. Las llamadas del navegador a las APIs de negocio pasan por Gateway; el login se comunica con Keycloak.</p>"""
        + table(
            ["Componente DEV", "Puerto de tu PC", "Función"],
            [
                ["Angular", "4200", "Interfaz"],
                ["Gateway", "18080", "Entrada de APIs"],
                ["Catálogo / PostgreSQL", "8085 / 15445", "Productos e inventario"],
                ["Usuario / PostgreSQL", "8086 / 15446", "Perfiles y suscripciones"],
                [
                    "Eureka / Config Server",
                    "18761 / 18888",
                    "Descubrimiento / configuración",
                ],
                [
                    "Keycloak / Kafka UI",
                    "18180 / 18085",
                    "Identidad / inspección de eventos",
                ],
                [
                    "Kafka / Grafana / Prometheus",
                    "19092 / 13000 / 19090",
                    "Mensajería / visualización / métricas",
                ],
            ],
        ),
    )
)
parts.append(
    section(
        "catalogo",
        chapters[4][1],
        """<h2>Responsabilidades</h2><ul><li><strong>Producto:</strong> nombre, descripción, precio, stock, estado y categorías.</li><li><strong>Categoría:</strong> clasificación reutilizable: alimentos, higiene, juguetes, etc.</li><li><strong>Reserva de inventario:</strong> descontar disponibilidad de manera controlada para una venta.</li><li><strong>Compensación:</strong> liberar la reserva si el pago es rechazado.</li></ul><h2>Reglas que debes poder explicar</h2><p>Se rechazan cantidades inválidas y stock insuficiente. Los IDs de categorías deben existir. La búsqueda admite filtros y paginación. La eliminación de un producto es <strong>baja lógica</strong>: lo deja inactivo para conservar historial y reservas. La reserva Kafka bloquea filas en orden y verifica todos los productos antes de descontar stock.</p>"""
        + table(
            ["Qué mostrar en Angular", "Qué código lo respalda"],
            [
                [
                    "Productos: crear y editar",
                    a("prod_controller") + " → " + a("prod_create"),
                ],
                [
                    "Dos categorías para el mismo producto",
                    a("prod_entity") + " y " + a("flyway_cat"),
                ],
                ["Filtros y paginación", a("prod_query")],
                ["Desactivar producto", a("prod_delete")],
                ["Pago rechazado y stock recuperado", a("inv_release")],
            ],
        )
        + box(
            "El precio que envía o muestra el navegador no se acepta como verdad para crear la venta. Venta obtiene el precio real desde Catálogo y la reserva vuelve a verificarlo."
        ),
    )
)
parts.append(
    section(
        "cat-componentes",
        chapters[5][1],
        diagram("c3-catalogo")
        + """<p><strong>Flujo REST:</strong> Controller recibe la petición y valida el DTO; Service aplica reglas; Repository accede a PostgreSQL; Mapper prepara el DTO de salida.</p><p><strong>Flujo Kafka:</strong> InventarioEvents recibe un contrato de evento, reclama su eventId en Inbox y reserva o libera stock mediante JDBC. Guarda el resultado en Outbox dentro de la misma transacción local. El publicador de Outbox lo envía después a Kafka.</p>"""
        + code("prod_create", after=8),
    )
)
parts.append(
    section(
        "cat-codigo",
        chapters[6][1],
        diagram("c4-catalogo")
        + """<h2>Muchos a muchos que puedes demostrar</h2><p>Un champú puede pertenecer a <strong>Higiene</strong> y <strong>Cuidado</strong>. A su vez, Higiene agrupa champú, cepillos y otros productos. La tabla <code>producto_categoria</code> guarda cada par de IDs.</p>"""
        + code("prod_entity", after=8)
        + """<p>Existe además el campo antiguo <code>categoria</code> con @ManyToOne para compatibilidad. No debes usarlo para explicar toda la relación actual: las múltiples categorías viven en <code>categorias</code> y en la tabla de unión.</p><h2>Concurrencia e inventario</h2><p><code>@Version</code> protege actualizaciones JPA. Las operaciones JDBC de reserva/liberación aumentan también <code>version</code>. <code>reservas_stock.id_venta</code> identifica el efecto de negocio, incluso si llega otro eventId para la misma venta.</p>""",
    )
)
parts.append(
    section(
        "usuario",
        chapters[7][1],
        """<h2>Responsabilidades</h2>"""
        + table(
            ["Capacidad", "Qué conserva", "Regla importante"],
            [
                [
                    "Perfil",
                    "Nombre, correo, teléfono, dirección, DNI y subject.",
                    "El perfil propio se identifica con el sub del JWT; guardar comprueba persistencia.",
                ],
                [
                    "Mascotas",
                    "Nombre, especie, raza, edad y DIAS/MESES.",
                    "Pertenecen a un usuario; se controla propiedad.",
                ],
                [
                    "Roles internos",
                    "Clasificaciones como VENTAS o SECRETARIA.",
                    "No conceden permisos ADMIN en el JWT.",
                ],
                [
                    "Planes",
                    "Nombre, precio, duración y estado.",
                    "Se desactivan sin borrar el historial contratado.",
                ],
                [
                    "Suscripciones",
                    "Usuario, plan, estado y vigencia.",
                    "No duplicar una suscripción activa del mismo plan.",
                ],
                [
                    "Períodos",
                    "ALTA o RENOVACION, precio y fechas acordados.",
                    "La misma clave de reintento no agrega otro período.",
                ],
            ],
        )
        + """<p>Teléfono opcional: si se informa, celular peruano de nueve dígitos y empieza con 9. DNI opcional: ocho dígitos. La edad de mascota se expresa como entero con unidad explícita.</p>"""
        + box(
            "Keycloak guarda y verifica las credenciales de acceso. La tabla usuarios de este microservicio guarda el perfil del negocio; no contiene un campo de contraseña de login."
        ),
    )
)
parts.append(
    section(
        "usr-componentes",
        chapters[8][1],
        diagram("c3-usuario")
        + """<p>MiCuentaController expone <code>/usuarios/me</code>: usa el token para operar sobre el perfil propio. UsuarioController permite el mantenimiento administrativo. MascotaService comprueba que la mascota corresponde al usuario. RolService valida el catálogo de clasificaciones.</p><p>SuscripcionService administra planes y el ciclo de contratación. Sus repositorios conservan cabecera e historial. Los bloqueos PostgreSQL serializan operaciones del usuario y la clave de idempotencia. Todo esto es una transacción local de Usuario, no una transacción distribuida entre bases.</p>""",
    )
)
parts.append(
    section(
        "usr-codigo",
        chapters[9][1],
        diagram("c4-usuario")
        + """<h2>Tres relaciones que puedes señalar</h2><ul><li><strong>Usuario 1:N Mascota:</strong> una familia registra varias mascotas; cada mascota tiene su propietario.</li><li><strong>Usuario N:M Rol:</strong> varios roles por usuario y varios usuarios por rol; unión <code>usuario_rol</code>.</li><li><strong>Usuario N:M Plan mediante Suscripcion:</strong> la asociación tiene estado, fechas y períodos; por eso es una entidad de negocio y no solamente @ManyToMany.</li></ul>"""
        + code("user_roles", after=7)
        + code("sub_entity", after=8)
        + """<p>Los IDs de estas asociaciones pertenecen a la misma base de Usuario. Una referencia entre microservicios, como el id de mascota que guarda Citas, no se convierte en una FK entre bases independientes.</p>""",
    )
)
parts.append(
    section(
        "crud",
        chapters[10][1],
        """<p>CRUD significa crear, consultar, actualizar y eliminar. En este dominio algunas eliminaciones son desactivaciones; las suscripciones usan operaciones de negocio, no una edición arbitraria de todos sus campos.</p>"""
        + table(
            ["Recurso y ruta por Gateway", "Operaciones", "Código"],
            [
                [
                    "/api/v1/productos",
                    "GET lista/detalle; POST alta; PUT /{id}; DELETE /{id} desactiva.",
                    a("prod_controller"),
                ],
                [
                    "/api/v1/categorias",
                    "GET lista/detalle; POST; PUT /{id}; DELETE /{id}.",
                    a("cat_controller"),
                ],
                [
                    "/api/v1/usuarios",
                    "Administración: GET, POST, PUT /{id}, DELETE /{id} con restricciones de historial.",
                    a("user_controller"),
                ],
                [
                    "/api/v1/usuarios/me",
                    "GET y PUT del perfil autenticado.",
                    a("me_controller"),
                ],
                [
                    "/api/v1/usuarios/me/mascotas",
                    "GET, POST; GET/PUT/DELETE /{id}, con propiedad.",
                    a("me_controller"),
                ],
                [
                    "/api/v1/usuarios/{id}/mascotas",
                    "Mantenimiento de mascotas del usuario autorizado.",
                    a("pet_controller"),
                ],
                [
                    "/api/v1/roles o /api/v1/usuarios/roles",
                    "CRUD administrativo del catálogo interno.",
                    a("role_controller"),
                ],
                [
                    "/api/v1/usuarios/{id}/roles/{idRol}",
                    "POST asigna; DELETE retira la asociación.",
                    a("role_assign"),
                ],
                [
                    "/api/v1/planes",
                    "GET público; POST, PUT /{id} y DELETE /{id} administrativos.",
                    a("sub_controller"),
                ],
                [
                    "/api/v1/suscripciones",
                    "GET y POST contratar; POST /{id}/renovar o /cancelar.",
                    a("sub_controller"),
                ],
            ],
        )
        + """<h2>Cómo encontrar cualquier clase</h2><p>Abre la raíz del proyecto en VS Code. Pulsa <strong>Ctrl+P</strong>, pega la ruta completa del mapa final y presiona Enter. Con <strong>Ctrl+G</strong> salta a la línea indicada. Los enlaces azules abren la misma ubicación en GitHub.</p>""",
    )
)
parts.append(
    section(
        "infra",
        chapters[11][1],
        """<h2>Eureka: la agenda de direcciones</h2><p>Cada servicio registra nombre, instancia y puerto, y mantiene su presencia con renovaciones. Eureka permite descubrir dónde está un servicio. No almacena productos ni transporta los eventos de Kafka. La detección de una caída no es instantánea.</p><p>Configuración: """
        + a("eureka")
        + "; registro de "
        + a("catalog_config")
        + " y "
        + a("user_config")
        + """.</p><h2>Gateway: la entrada de las APIs</h2><p>Angular llama a <code>http://localhost:18080/api/v1</code>. Gateway aplica seguridad y enruta <code>/productos</code> a <code>lb://garritas-catalogo-ms</code> y <code>/usuarios</code> a <code>lb://garritas-usuario-ms</code>. El prefijo lb indica resolución y balanceo por nombre lógico.</p><p>Rutas reales: """
        + a("gateway")
        + "; dirección que usa Angular: "
        + a("frontend_api")
        + """.</p><h2>Feign y resiliencia: S6</h2><p>Venta necesita consultar precio y disponibilidad antes de aceptar una orden. Feign expresa esa consulta como una interfaz Java con nombre lógico. El timeout limita una espera; el Circuit Breaker evita seguir insistiendo sobre una dependencia que falla; su fallback devuelve una respuesta controlada, sin inventar stock ni precio.</p>"""
        + code("feign", after=7)
        + """<p>Consulta protegida: """
        + a("breaker")
        + "; límites: "
        + a("timeout")
        + """. En DEV hay connectTimeout de 2 segundos y readTimeout de 3 segundos; el circuito de Catálogo tiene ventana 10, mínimo 5 llamadas, umbral 50% y apertura de 10 segundos.</p>"""
        + box(
            "No toda llamada interna usa Feign. Citas utiliza ServiceClient con descubrimiento y tiempos acotados para consultar Usuario. No dibujes un Circuit Breaker que no exista en esa llamada."
        ),
    )
)
parts.append(
    section(
        "seguridad",
        chapters[12][1],
        diagram("jwt")
        + """<p><strong>Autenticación:</strong> Keycloak identifica al usuario. <strong>Autorización:</strong> Gateway y cada servicio deciden qué puede hacer según el JWT y el recurso.</p><p>El token contiene <code>sub</code> (identidad de tipo String) y <code>realm_access.roles</code>. La conversión añade el prefijo ROLE_ para Spring Security. El id local de la fila de usuario sigue siendo Long; no debe confundirse con sub.</p><p>El servicio valida firma, emisor y audiencia configurada. Las claves públicas se consultan en el endpoint JWKS; la clave privada de firma permanece en Keycloak. Para el perfil propio se compara subject con la identidad autenticada.</p>"""
        + code("identity", before=0, after=5)
        + """<p>Ubicaciones: """
        + a("security")
        + ", "
        + a("jwt_roles")
        + ", "
        + a("jwt_config")
        + " y "
        + a("pkce")
        + """.</p>"""
        + box(
            "El cliente Angular usa Authorization Code + PKCE y administra tokens en memoria; no guarda access_token en localStorage. Las guardas o botones ocultos no sustituyen la autorización del backend. Los roles internos de PostgreSQL no cambian el rol firmado por Keycloak."
        ),
    )
)
parts.append(
    section(
        "mensajes",
        chapters[13][1],
        """<h2>Kafka: comunicar hechos de negocio</h2><p>Un productor publica un evento y cada grupo consumidor procesa los eventos que le corresponden. Garritas utiliza <code>garritas.ventas.v1</code>, con tres particiones y un grupo independiente para Venta, Catálogo y Pago. La clave de publicación es la venta, para distribuir sus eventos de forma coherente por partición.</p><p><strong>REST/Feign:</strong> el llamador espera una respuesta ahora. <strong>Kafka:</strong> se informa un hecho y el resultado final puede conocerse después. Hay desacople temporal y consistencia eventual; deben manejarse duplicados.</p>"""
        + table(
            ["Pieza", "Qué problema resuelve", "Código"],
            [
                [
                    "SagaEvent",
                    "Contrato con eventId, tipo, ventaId, cliente, total, items y traceId.",
                    a("event_contract"),
                ],
                [
                    "Outbox",
                    "Guarda el evento junto con el cambio de base; lo publica después.",
                    a("outbox") + " y " + a("outbox_send"),
                ],
                [
                    "Inbox",
                    "Deduplica por eventId dentro de la transacción del consumidor.",
                    a("inbox"),
                ],
                [
                    "reserva por venta",
                    "Evita repetir el efecto aunque llegue otro eventId para la misma venta.",
                    a("inv_reserve"),
                ],
                [
                    "Reintentos y DLT",
                    "El manejador aplica reintentos finitos y deriva errores no resueltos a .DLT.",
                    a("dlt"),
                ],
            ],
        )
        + """<p>La entrega puede repetirse: si el proceso cae después del ACK de Kafka y antes de marcar publicado el outbox, el evento podría volver a salir. Por eso no prometemos “exactamente una vez” global; construimos efectos idempotentes.</p><p>Un mensaje que acaba en DLT requiere diagnóstico y reprocesamiento controlado; no se recupera por arte de magia. Usuario no implementa un consumidor de esta Saga. Su idempotencia de suscripciones se basa en la clave de petición y los períodos guardados en su propia base.</p>""",
    )
)
parts.append(
    section(
        "saga",
        chapters[14][1],
        diagram("saga-compensacion")
        + """<h2>Compensación real</h2><p>Es una operación nueva que revierte un efecto de negocio ya confirmado. Catálogo pasó de stock 10 a 8 al reservar dos unidades. Ante pago.fallido, <code>liberar()</code> recupera las cantidades de la reserva original, pasa de 8 a 10 y marca la reserva LIBERADA. Si el evento vuelve a llegar, no debe liberar nuevamente.</p>"""
        + code("inv_release", after=17)
        + table(
            ["Situación", "Qué hace Garritas", "Clasificación"],
            [
                [
                    "Falla una validación previa",
                    "No se crea la venta.",
                    "Validación / resiliencia",
                ],
                [
                    "Falla la reserva asíncrona",
                    "Venta existente termina cancelada sin pago.",
                    "Rechazo del proceso",
                ],
                [
                    "Pago rechaza tras reservar",
                    "Catálogo devuelve stock; Venta COMPENSANDO → CANCELADA.",
                    "Compensación",
                ],
                [
                    "Pago/Kafka temporalmente detenido",
                    "El proceso puede continuar tras recuperarse; revisar reintentos y DLT ante errores persistentes.",
                    "Recuperación",
                ],
                ["Evento repetido", "No se repite el efecto.", "Idempotencia"],
                [
                    "Error antes del commit de una base",
                    "Se deshacen cambios de esa transacción.",
                    "Rollback local",
                ],
            ],
        )
        + box(
            "No existe compensación universal de todos los módulos ni una transacción ACID que abarque sus bases. El pago de Garritas es simulado. Cancelar una suscripción es una transición local; no equivale a un reembolso bancario."
        ),
    )
)
parts.append(
    section(
        "claves",
        chapters[15][1],
        """<p>“Claves” puede referirse a contraseñas, identificadores o claves de seguridad. Aquí se separan para no confundirlos.</p><h2>Credenciales de demostración de la configuración DEV</h2>"""
        + table(
            ["Acceso", "Usuario / contraseña inicial", "Dónde está"],
            [
                ["Angular cliente", "cliente / Cliente123!", a("kc_users")],
                [
                    "Angular administrador",
                    "admin-store / Admin123!",
                    a("kc_adminstore"),
                ],
                [
                    "Keycloak, consola de administración",
                    "admin / local-admin-change-me",
                    a("kc_password"),
                ],
                ["Grafana", "admin / local-grafana", a("grafana_password")],
                [
                    "PostgreSQL Catálogo",
                    "garritas / garritas · DB garritas_catalogo_db",
                    a("db_catalog"),
                ],
                [
                    "PostgreSQL Usuario",
                    "garritas / garritas · DB garritas_usuario_db",
                    a("db_user"),
                ],
            ],
        )
        + """<p>Son valores de desarrollo publicados en el repositorio. Si cambiaste la contraseña en una instalación o definiste la variable de entorno correspondiente, prevalece ese valor. Editar el archivo de importación del realm no restablece automáticamente la contraseña de un usuario existente.</p><h2>Claves de firma y claves de idempotencia</h2>"""
        + table(
            ["Término", "Significado y ubicación"],
            [
                [
                    "Clave privada JWT",
                    "Keycloak la administra. No se pega una clave privada en Angular ni en Usuario MS.",
                ],
                [
                    "Claves públicas JWKS",
                    "http://localhost:18180/realms/garritas/protocol/openid-connect/certs · "
                    + a("jwt_config"),
                ],
                [
                    "sub",
                    "Identificador del usuario autenticado; se guarda como subject. "
                    + a("profile_lookup"),
                ],
                [
                    "Idempotency-Key",
                    "UUID enviado para reintentar una operación sin duplicarla. "
                    + a("sub_controller"),
                ],
                [
                    "eventId",
                    "Identificador de un evento; Inbox lo usa para deduplicar. "
                    + a("inbox"),
                ],
                [
                    "idVenta",
                    "Clave de negocio de la reserva; protege también contra duplicados semánticos. "
                    + a("inv_reserve"),
                ],
            ],
        )
        + box(
            "La SPA es un cliente público (publicClient=true): no tiene client_secret. Su protección de login se basa en PKCE."
        ),
    )
)
parts.append(
    section(
        "demo",
        chapters[16][1],
        """<h2>Guion para Fio: tres minutos, con datos preparados</h2>"""
        + table(
            ["Tiempo", "Acción visible", "Frase para explicar"],
            [
                [
                    "0:00–0:40",
                    "Administrador → Productos. Muestra un producto con dos categorías y usa un filtro.",
                    "“Catálogo mantiene productos y la relación muchos a muchos Producto–Categoría”.",
                ],
                [
                    "0:40–1:15",
                    "Cliente → Mi cuenta y mascotas. Guarda un dato y recarga; muestra edad con unidad.",
                    "“El perfil se vincula al sub del token; la mascota pertenece a este cliente”.",
                ],
                [
                    "1:15–1:50",
                    "Planes y suscripciones. Muestra un contrato y sus períodos; utiliza un cliente preparado.",
                    "“Usuario registra una operación con estado e historial. Un reintento con la misma clave no agrega otro período”.",
                ],
                [
                    "1:50–3:00",
                    "Anota stock; compra con TRANSFERENCIA; espera cancelación y comprueba stock recuperado. Apoya con logs/eventos.",
                    "“La reserva se confirmó, el pago falló y Catálogo compensó liberando las unidades”.",
                ],
            ],
        )
        + """<h2>Pestañas listas antes de empezar</h2><p>Angular en una ventana de cliente y otra de administrador; Kafka UI en :18085; Grafana en :13000; mapa de código abierto. No uses la cuenta administradora para comprar. Preparar datos evita dedicar la demo a escribir formularios largos.</p><h2>Qué observar en las herramientas</h2><p>En Kafka UI selecciona el topic de ventas y localiza venta.creada, inventario.reservado, pago.fallido e inventario.liberado por ventaId. En Grafana, Explore → Loki permite buscar el traceId y comparar servicios. Para disponibilidad de Keycloak usa Prometheus: <code>up{job="keycloak"}</code>; esto demuestra scrape correcto, no por sí solo un login exitoso.</p>"""
        + box(
            "Presionar Renovar dos veces con claves nuevas son dos operaciones distintas. Para demostrar idempotencia, hay que repetir la misma petición con el mismo propietario y la misma Idempotency-Key."
        ),
    )
)
parts.append(
    section(
        "preguntas",
        chapters[17][1],
        """<dl>
<dt>¿Qué diferencia hay entre Catálogo y Usuario?</dt><dd>Catálogo administra lo que se vende y su inventario; Usuario administra perfiles, mascotas y el ciclo de suscripciones.</dd>
<dt>¿Dónde está mi muchos a muchos?</dt><dd>En Producto.categorias → producto_categoria y Usuario.roles → usuario_rol. Usuario–Plan se representa mediante Suscripcion porque la asociación tiene datos de negocio.</dd>
<dt>¿Usuario autentica con contraseña?</dt><dd>No. Keycloak autentica; Usuario conserva el perfil asociado al sub y valida el JWT para sus rutas protegidas.</dd>
<dt>¿Para qué Eureka si ya existe Gateway?</dt><dd>Gateway es la entrada y enruta; Eureka permite descubrir las instancias a las que enruta y a las que otros servicios consultan.</dd>
<dt>¿Kafka reemplaza Feign?</dt><dd>No. Feign consulta datos que se necesitan inmediatamente; Kafka desacopla pasos que pueden completarse después.</dd>
<dt>¿Qué compensación implementaste?</dt><dd>Liberar stock reservado cuando el pago es rechazado. El efecto confirmado se revierte mediante otra transacción y otro evento.</dd>
<dt>¿Cancelar un estado basta para compensar?</dt><dd>No. Hay que deshacer el efecto correspondiente: por ejemplo, recuperar las unidades reservadas.</dd>
<dt>¿Por qué el duplicado no libera dos veces?</dt><dd>Inbox detecta el eventId y la reserva por venta solo se libera si sigue RESERVADA. Una reserva LIBERADA no vuelve a sumar stock.</dd>
<dt>¿Todo queda consistente de inmediato?</dt><dd>No. Hay estados intermedios y consistencia eventual. Se recupera el proceso y se diagnostican mensajes fallidos con logs, métricas y DLT.</dd>
<dt>¿Qué demuestran los tests existentes?</dt><dd>La revisión cf3cede documenta 30 pruebas Java y 15 Angular más verificaciones de flujos y fallos. Esta entrega es documental: no vuelve a ejecutar ni certifica tu instalación Windows.</dd>
</dl>""",
    )
)
rows = []
for k, r in REFS.items():
    rows.append(
        [
            html.escape(r["label"]),
            '<a href="'
            + r["url"]
            + '"><code class="path">'
            + html.escape(r["path"])
            + "</code></a>",
            str(r["line"]),
        ]
    )
parts.append(
    section(
        "mapa",
        chapters[18][1],
        "<p>Rutas relativas a la raíz <code>Garritas-actualizado</code>. En Windows puedes usar Ctrl+P y pegar la ruta con las barras tal como aparece. La línea corresponde al commit <code>cf3cede</code>.</p>"
        + table(["Qué buscar", "Archivo exacto", "Línea"], rows),
    )
)
CSS = """
:root{--green:#195c47;--ink:#20342e;--muted:#52645d;--border:#d5e1da}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eef3ef;color:var(--ink);font:16px/1.58 Arial,"DejaVu Sans",sans-serif}main{max-width:1040px;margin:auto;background:white;padding:48px 64px}h1,h2{color:var(--green);line-height:1.2}h1{font-size:31px;margin:12px 0 24px}h2{font-size:21px;margin:25px 0 12px}p{margin:12px 0}a{color:#145a78;text-decoration:underline;text-underline-offset:2px}code,pre{font-family:"DejaVu Sans Mono",monospace;font-size:.84em}code{overflow-wrap:anywhere}.path{word-break:break-all}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6f4;border:1px solid var(--border);padding:14px;border-radius:8px;line-height:1.45;break-inside:avoid}.source{font-size:13px;margin-top:16px}.eyebrow{letter-spacing:2px;font-weight:bold;font-size:11px;color:var(--green)}.cover{min-height:82vh;padding-top:65px}.cover h1{font-size:48px}.cover h1 span{color:#36748a}.cover .lead{font-size:23px}.cover-tags{border-top:3px solid var(--green);padding-top:18px;margin:35px 0}.revision{font-size:13px;color:var(--muted);margin-top:35px}.chapter{margin:50px 0;padding-top:24px;border-top:2px solid var(--border)}table{width:100%;border-collapse:collapse;font-size:14px;margin:18px 0;table-layout:fixed}th,td{padding:10px;border:1px solid var(--border);text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#e6f0e8;color:var(--green)}tr{break-inside:avoid}.note{background:#eef5e9;border-left:4px solid #6b8e49;padding:14px 18px;margin:20px 0;break-inside:avoid}.toc{columns:2;padding-left:0;list-style:none}.toc li{margin-bottom:12px;break-inside:avoid}.toc a{font-size:15px}figure{margin:20px 0;break-inside:avoid;text-align:center}figure svg{max-width:100%;width:auto;height:auto;max-height:690px}figcaption{font-size:12px;color:var(--muted);margin-top:10px}dt{font-weight:bold;color:var(--green);margin-top:17px;break-after:avoid}dd{margin:5px 0 12px}button{background:var(--green);color:white;padding:10px;border:0;border-radius:5px;cursor:pointer}li{margin-bottom:7px}
@media(max-width:700px){main{padding:20px}.cover h1{font-size:35px}.toc{columns:1}table{font-size:12px}th,td{padding:6px}figure svg{width:100%}}
@page{size:A4;margin:17mm 15mm 18mm}
@media print{html{scroll-behavior:auto}body{background:white;font-size:10.5pt;line-height:1.45}main{max-width:none;padding:0}.cover{min-height:240mm;padding-top:35mm}.cover h1{font-size:35pt}.cover .lead{font-size:19pt}.chapter{break-before:page;margin:0;padding:0;border:0}h1{font-size:22pt;margin:10px 0 18px}h2{font-size:15pt}table{font-size:8.5pt}th,td{padding:7px}pre{font-size:8pt}figure svg{max-height:172mm;max-width:100%}.toc a{font-size:10pt}button{display:none}a{color:#145a78}thead{display:table-header-group}.source{font-size:9pt}.note{padding:10px 13px}#contenedores figure svg{max-height:100mm}#claves table{font-size:8pt}#claves td,#claves th{padding:5px}#seguridad figure svg{max-height:115mm}#cat-codigo figure svg{max-height:100mm}#usr-codigo figure svg{max-height:95mm}#mapa table{font-size:7.5pt}#mapa th:nth-child(1){width:28%}#mapa th:nth-child(2){width:65%}#mapa th:nth-child(3){width:7%}.eyebrow{font-size:8pt}}
"""
html_doc = (
    '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Guía de estudio C4 · Catálogo y Usuario · Garritas Store</title><style>'
    + CSS
    + "</style></head><body><main>"
    + "".join(parts)
    + "</main></body></html>"
)
(OUT / "Guia-estudio-C4-Catalogo-Usuario.html").write_text(html_doc)
(OUT / "referencias.json").write_text(
    json.dumps({"commit": COMMIT, "references": REFS}, ensure_ascii=False, indent=2)
    + "\n"
)
(OUT / "Mapa-de-codigo.txt").write_text(
    "GARRITAS STORE · CATÁLOGO Y USUARIO\nCódigo: "
    + COMMIT
    + "\n\n"
    + "\n\n".join(
        f'{r["label"]}\n{r["path"]}:{r["line"]}\n{r["url"]}' for r in REFS.values()
    )
    + "\n"
)
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"]
    )
    page = browser.new_page(viewport={"width": 1100, "height": 900})
    page.set_content(html_doc, wait_until="networkidle")
    assert page.locator("svg").count() == len(DIAGRAMS)
    assert page.locator("svg").evaluate_all(
        "(items)=>items.every(x=>x.getBoundingClientRect().width>100)"
    )
    page.pdf(
        path=str(OUT / "Guia-estudio-C4-Catalogo-Usuario.pdf"),
        format="A4",
        print_background=True,
        prefer_css_page_size=True,
        outline=True,
        tagged=True,
        display_header_footer=True,
        header_template="<div></div>",
        footer_template='<div style="font-size:8px;width:100%;padding:0 15mm;color:#52645d;display:flex;justify-content:space-between"><span>Garritas Store · Catálogo y Usuario · C4</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    )
    page.screenshot(path="/tmp/guia-c4-portada.png", full_page=False)
    page.locator("#cat-codigo").screenshot(path="/tmp/guia-c4-catalogo.png")
    browser.close()
print(
    json.dumps(
        {
            "references": len(REFS),
            "diagrams": len(DIAGRAMS),
            "html": str(OUT / "Guia-estudio-C4-Catalogo-Usuario.html"),
            "pdf": str(OUT / "Guia-estudio-C4-Catalogo-Usuario.pdf"),
        },
        ensure_ascii=False,
    )
)
