#!/usr/bin/env python3
"""Genera los tres manuales PDF desde el código versionado y evidencia de revisión."""
from pathlib import Path
import subprocess, re, json, hashlib, zipfile, textwrap, html, os
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Image, Table, TableStyle, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/manuales'; SOURCE=OUT/'fuentes'; DIAG=OUT/'diagramas'
REV=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
BASE=REV[:7]; DATE=datetime.now(ZoneInfo('America/Bogota')).strftime('%d/%m/%Y %H:%M %Z')
TRACKED=[p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines() if (ROOT/p).is_file() and not p.startswith('docs/manuales/')]
for p in [OUT,SOURCE,DIAG]:p.mkdir(parents=True,exist_ok=True)
for name,path in [('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),('BodyBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),('Code','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,path))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text',fontName='Body',fontSize=9.1,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallText',fontName='Body',fontSize=7.3,leading=10,spaceAfter=5,wordWrap='CJK'))
styles.add(ParagraphStyle(name='CodeText',fontName='Code',fontSize=6.7,leading=8.6,spaceAfter=7,backColor=colors.HexColor('#f1f5f2'),borderPadding=6))
styles.add(ParagraphStyle(name='Cover',fontName='BodyBold',fontSize=28,leading=35,textColor=colors.HexColor('#245b47'),spaceAfter=20))
for i,size in [(1,17),(2,12),(3,10)]:
 styles[f'Heading{i}'].fontName='BodyBold';styles[f'Heading{i}'].fontSize=size;styles[f'Heading{i}'].leading=size+5;styles[f'Heading{i}'].textColor=colors.HexColor('#245b47');styles[f'Heading{i}'].spaceBefore=12;styles[f'Heading{i}'].spaceAfter=8
class ManualDoc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name in ('Heading1','Heading2'):
   level=0 if f.style.name=='Heading1' else 1
   key='h'+str(self.seq.nextf('heading'))
   self.canv.bookmarkPage(key)
   self.canv.addOutlineEntry(f.getPlainText()[:200],key,level,False)
   self.notify('TOCEntry',(level,f.getPlainText(),self.page,key))
def footer(c,d):
 c.saveState();c.setStrokeColor(colors.HexColor('#bdd0c3'));c.line(43,38,A4[0]-43,38)
 c.setFont('Body',7);c.setFillColor(colors.HexColor('#52685a'));c.drawString(43,25,'GARRITAS STORE · '+d.title[:52]);c.drawRightString(A4[0]-43,25,str(d.page));c.restoreState()
def inline(s):
 s=escape(s)
 s=re.sub(r'`([^`]+)`',lambda m:'<font name="Code" size="8">'+m.group(1)+'</font>',s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 return s
class Book:
 def __init__(self,name,title,subtitle):
  self.name=name;self.title=title;self.items=[];self.md=[]
  self.items.extend([Spacer(1,60),Paragraph('GARRITAS STORE',styles['SmallText']),Paragraph(title,styles['Cover']),Paragraph(subtitle,styles['Text']),Spacer(1,20),Paragraph('Edición de estudio y laboratorio local',styles['Text']),Paragraph('Código de referencia: '+REV,styles['SmallText']),Paragraph('Revisión: '+DATE,styles['SmallText']),Paragraph('Lectura progresiva, rutas exactas y ejemplos del proyecto real.',styles['Text']),PageBreak()])
  toc=TableOfContents();toc.levelStyles=[ParagraphStyle(name='TOC0',fontName='Body',fontSize=9,leading=14,spaceBefore=5),ParagraphStyle(name='TOC1',fontName='Body',fontSize=8,leading=11,leftIndent=15)]
  self.items.extend([Paragraph('Índice',styles['Heading1']),toc,PageBreak()])
 def h(self,t,level=1,new=False):
  if new:self.items.append(PageBreak())
  self.items.append(Paragraph(escape(t),styles[f'Heading{level}']));self.md.append('\n'+'#'*level+' '+t+'\n')
 def p(self,t):
  self.items.append(Paragraph(inline(t),styles['Text']));self.md.append(t+'\n')
 def bullet(self,t):self.items.append(Paragraph('• '+inline(t),styles['Text']));self.md.append('- '+t+'\n')
 def code(self,t):
  # Los archivos originales se conservan sin reformatear en el ZIP y en el repositorio.
  lines=[]
  for line in t.expandtabs(2).splitlines():
   lines.extend(textwrap.wrap(line,width=109,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False,subsequent_indent='  ') or [''])
  for start in range(0,len(lines),52):self.items.append(Preformatted('\n'.join(lines[start:start+52]),styles['CodeText']))
  self.md.append('```\n'+t.rstrip()+'\n```\n')
 def table(self,headers,rows,widths=None):
  vals=[[Paragraph(inline(str(x)),styles['SmallText']) for x in row] for row in [headers,*rows]]
  table=Table(vals,colWidths=widths or [509/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deebe1')),('FONTNAME',(0,0),(-1,0),'BodyBold'),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#d1ddd5'))]))
  self.items.extend([table,Spacer(1,9)]);self.md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('\n',' ') for x in row)+' |' for row in rows)+'\n')
 def image(self,name,caption):
  from PIL import Image as PILImage
  p=DIAG/(name+'.png');w,h=PILImage.open(p).size;scale=min(509/w,600/h)
  self.items.extend([Image(str(p),width=w*scale,height=h*scale),Paragraph(inline(caption),styles['SmallText'])]);self.md.append(f'![{caption}](../diagramas/{name}.png)\n')
 def file(self,path,explain=True):
  if not (ROOT/path).is_file():raise FileNotFoundError(path)
  self.h(Path(path).name,3);self.p('**Crear archivo y pegar el contenido completo:** `'+path+'`.')
  if explain:self.p(describe(path))
  self.code((ROOT/path).read_text())
 def save(self):
  doc=ManualDoc(str(OUT/self.name),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=50,title=self.title,author='Garritas Store · documentación del proyecto')
  doc.multiBuild(self.items,onFirstPage=footer,onLaterPages=footer)
  (SOURCE/(Path(self.name).stem+'.md')).write_text('\n'.join(line.rstrip() for line in '\n'.join(self.md).splitlines()).rstrip()+'\n')

def diagram(name,body):
 dot='digraph G { graph [bgcolor="white",fontname="DejaVu Sans",pad="0.15",nodesep="0.3",ranksep="0.5"]; node [shape=box,style="rounded,filled",fillcolor="#edf4ee",color="#4d7b64",fontname="DejaVu Sans",fontsize=11]; edge [fontname="DejaVu Sans",fontsize=9,color="#48685a"];'+body+'}'
 (DIAG/(name+'.dot')).write_text(dot)
 for ext in ['png','svg']:subprocess.run(['dot','-T'+ext,str(DIAG/(name+'.dot')),'-o',str(DIAG/(name+'.'+ext))],check=True)

diagram('arquitectura','''rankdir=TB; angular[label="Angular · 4200"]; kc[label="Keycloak · 18180"]; gw[label="Gateway · 18080"]; config[label="Config Server · 18888"]; eureka[label="Eureka · 18761"]; angular->kc[label="Código + PKCE"]; angular->gw[label="HTTP + JWT"]; gw->eureka[label="Descubrimiento"]; gw->catalogo;gw->venta;gw->pago;gw->institucion;gw->usuario;gw->citas;gw->envio;gw->bienestar; catalogo[label="Catálogo · 8085"];venta[label="Venta · 8081"];pago[label="Pago · 8087"];institucion[label="Institución · 8082"];usuario[label="Usuario · 8086"];citas[label="Citas · 8084"];envio[label="Envío · 8083"];bienestar[label="Bienestar · 8088"]; db[label="8 PostgreSQL independientes\n15441–15448"]; {catalogo venta pago institucion usuario citas envio bienestar}->db[label="JPA / JDBC",style=dashed]; kafka[label="Kafka\n19092 host / 9092 Docker"];venta->kafka;catalogo->kafka;pago->kafka;kafka->venta;kafka->catalogo;kafka->pago; config->gw[style=dashed,label="Config DEV"]; config->citas[style=dashed];''')
diagram('saga','''rankdir=TB; a[label="POST /ventas\nIdentidad + sede + precio + idempotencia"];b[label="Tx Venta: venta PENDIENTE_STOCK\n+ outbox venta.creada"];c[label="Kafka: venta.creada"];d[label="Tx Catálogo: inbox + reserva atómica\n+ outbox inventario.*"];e[label="Inventario reservado\nVenta PENDIENTE_PAGO"];f[label="Tx Pago: inbox + pago único\n+ outbox pago.*"];g[label="pago.validado → Venta PAGADA"];h[label="pago.fallido → COMPENSANDO"];i[label="Catálogo: stock restaurado una vez\ninventario.liberado"];j[label="Venta CANCELADA"];k[label="Inventario rechazado\nVenta CANCELADA"];a->b->c->d;d->e[label="Disponible"];d->k[label="Sin stock / precio distinto"];e->f;f->g[label="YAPE / PLIN / otros aprobados"];f->h[label="TRANSFERENCIA (simulación)"];h->i->j;''')
diagram('clases','''rankdir=TB;ctrl[label="ProductoController\nGET/POST/PUT/DELETE /productos"];svc[label="ProductoService\nReglas + transacción"];repo[label="ProductoRepository\nJpaRepository<Producto,Long>"];entity[label="Producto\n@Entity + @Version"];dto[label="ProductoRequest / Response\nValidación / contrato JSON"];mapper[label="ProductoMapper\nDTO ↔ entidad"];cat[label="Categoria\n@Entity"];ctrl->svc[label="inyección"];ctrl->dto;svc->repo;svc->mapper;mapper->dto;mapper->entity;repo->entity;entity->cat[label="muchos a uno"];''')
diagram('muchos-a-muchos','''rankdir=LR; pro[label="profesionales\nid PK\nnombre / email único\nid_sede (referencia remota)\nactivo"];join[label="profesional_especialidad\nid_profesional PK, FK\nid_especialidad PK, FK"];esp[label="especialidades\nid PK\nnombre único\ndescripcion / activo"];pro->join[label="1 a N"];join->esp[label="N a 1"];sede[label="Institución: sedes\nOtra base; validación HTTP"];pro->sede[style=dashed,label="sin FK entre bases"];''')
diagram('identidad','''rankdir=TB; a[label="1. Angular pide login\ncode challenge S256"];b[label="2. Keycloak verifica credenciales\ny devuelve código"];c[label="3. SDK intercambia código + verifier\npor tokens en memoria"];d[label="4. Interceptor adjunta Bearer JWT\na peticiones de la API propia"];e[label="5. Gateway y servicio validan\nfirma / issuer / audiencia / roles"];f[label="6. CurrentUser.subject()\ncomparado con propietario persistido"];a->b->c->d->e->f;''')
diagram('citas-envios','''rankdir=TB; a[label="Angular: nueva cita"];b[label="Citas"];c[label="Usuario: mascota propia"];d[label="Institución: sede activa"];e[label="Bienestar: profesional activo\ny sede compatible"];f[label="PostgreSQL Citas\nÍndice único profesional + hora activa"];a->b;b->c;b->d;b->e;b->f;g[label="Angular: solicitar envío"];h[label="Envío"];i[label="Venta: pedido PAGADA\ny mismo propietario"];j[label="PostgreSQL Envío\nUn envío por id_venta"];g->h;h->i;h->j;''')
diagram('observabilidad','''rankdir=LR;apps[label="11 aplicaciones Java\n/actuator/prometheus"];kc[label="Keycloak\n:9000/metrics interno"];prom[label="Prometheus · 19090"];logs[label=".runtime/*/application.log\ny logs de infraestructura"];tail[label="Promtail"];loki[label="Loki · 13100"];graf[label="Grafana · 13000"];apps->prom[label="scrape"];kc->prom;logs->tail->loki;prom->graf[label="consultas PromQL"];loki->graf[label="consultas LogQL"];''')
diagram('despliegue','''rankdir=TB;host[label="Equipo local: Windows / Linux / WSL2"];java[label="JDK 21: Config, Eureka, Gateway\ny 8 servicios Java"];js[label="Node 24: Angular dev server"];docker[label="Docker Compose DEV"];shared[label="Kafka + Kafka UI\nKeycloak + su PostgreSQL"];db[label="8 PostgreSQL de negocio\nVolúmenes persistentes"];obs[label="Grafana / Loki / Promtail / Prometheus"];host->java;host->js;host->docker;docker->shared;docker->db;docker->obs;java->db;java->shared;js->java;''')

SPECIAL={
'CurrentUser':'Obtiene el sub autenticado y el rol ADMIN desde SecurityContextHolder. requireOwner impide que un cliente acceda a un recurso de otro sub; ADMIN puede auditarlo. No recibe la identidad del JSON del navegador.',
'SecurityConfiguration':'Declara la cadena de filtros de seguridad, JWT y conversión de roles de realm_access a ROLE_*. Define consultas públicas, rutas del propietario y operaciones exclusivas ADMIN. Se importa tanto en Gateway como en los servicios.',
'DomainErrors':'Traduce excepciones de estado HTTP, validación, integridad y concurrencia a respuestas controladas. Una violación de integridad o conflicto de versión produce 409; no inventa una confirmación de negocio.',
'HttpServices':'Registra ServiceClient. Construye un RestClient local con límites de conexión/lectura; no publica un RestClient.Builder global balanceado que pueda interferir con Eureka.',
'ServiceClient':'Elige una instancia por nombre mediante LoadBalancerClient, compone su URI y reenvía Bearer JWT y X-Trace-ID. Se usa al verificar mascota, sede, profesional o venta. Si no hay instancia o falla la conexión devuelve 503.',
'Reference':'Record de lectura tolerante a campos JSON adicionales. Representa únicamente los campos remotos necesarios, como id, activo, sedeId, estado e idCliente; no replica entidades ni comparte una base.',
'SagaEvent':'Contrato inmutable y versionado del evento de venta; contiene identidad, tipo, items, importes y correlación. validate rechaza contratos inválidos y next produce otro evento con nueva identidad para el mismo agregado.',
'Outbox':'append exige una transacción local activa e inserta el evento en PostgreSQL. publish se programa periódicamente, selecciona pendientes con FOR UPDATE SKIP LOCKED, espera el ACK Kafka y marca published_at. Un fallo conserva el pendiente. Puede duplicar entrega tras un reinicio; Inbox controla ese caso.',
'Inbox':'claim exige transacción activa y registra event_id con ON CONFLICT DO NOTHING. Devuelve false si ya fue procesado. Su inserción y el efecto de negocio se confirman o revierten juntos.',
'MessagingConfiguration':'Habilita el planificador y crea Outbox, Inbox, topic de Saga y DLT con tres particiones y réplica 1. Configura nueve reintentos con pausa y publicación en DLT. No proporciona un clúster Kafka de alta disponibilidad.',
'VentaService':'Valida sede activa y precios/stock remotos. Serializa una misma Idempotency-Key por sub con pg_advisory_xact_lock; rechaza cambios de payload para una clave ya usada. Guarda la venta y venta.creada en la misma transacción; la respuesta inicial no implica pago completado.',
'VentaEvents':'Consume resultados de inventario y pago, descarta tipos ajenos, deduplica mediante Inbox y actualiza el estado de la venta según las transiciones permitidas. La compensación solo termina al recibir inventario.liberado.',
'InventarioEvents':'Reserva todos los artículos de forma atómica con bloqueos por producto en orden determinista. Verifica disponibilidad, actividad y precio antes de descontar. Deduplica tanto event_id como id_venta. Ante pago.fallido libera una reserva una sola vez usando el payload original persistido.',
'PagoEvents':'Escucha inventario.reservado y crea un pago simulado único por venta dentro de una transacción con Inbox y Outbox. Publica pago.validado o pago.fallido. La regla didáctica configurada rechaza TRANSFERENCIA; no llama a una pasarela bancaria.',
'CatalogoConsulta':'Envuelve ProductoClient en un Circuit Breaker identificado como catalogo. Traduce producto inexistente a 422 y problemas de disponibilidad a 503. No devuelve un precio inventado cuando falla Catálogo.',
'ProductoClient':'Interfaz declarativa OpenFeign con nombre Eureka garritas-catalogo-ms y GET /api/v1/productos/{id}. Su record Producto contiene los datos mínimos de consulta para Venta.',
'FeignConfiguration':'Crea un RequestInterceptor que propaga X-Trace-ID desde MDC a llamadas Feign. La consulta de producto es pública y este interceptor no añade un JWT.',
'CitaService':'Verifica intervalos de 30 minutos y consulta la mascota del propietario, sede activa y profesional activo/sede compatible. Guarda nombres de referencia como snapshot. Permite confirmar desde PROGRAMADA, atender desde CONFIRMADA y cancelar salvo cita ya atendida; comprueba propiedad.',
'EnvioService':'Consulta la venta con identidad propagada; exige PAGADA y propietario válido. Genera un envío por venta, pone Por asignar para clientes y controla PENDIENTE, EN_TRANSITO, ENTREGADO y CANCELADO. La seguridad común reserva tránsito y entrega a ADMIN.',
'BienestarService':'Gestiona profesionales y especialidades con transacciones. Valida sede opcional y especialidades activas, evita duplicar ids de asociaciones, actualiza el conjunto y bloquea eliminar una especialidad vinculada. La baja de profesionales es lógica.',
'SedeService':'Ordena sedes por ciudad/nombre y filtra las inactivas para consultas no administrativas. Crear/editar está protegido por rol y eliminar desactiva; el historial de pedidos y citas no se borra.',
'UsuarioService':'Gestiona perfiles de usuario y relaciona el sub de Keycloak con un registro local. La ruta me recupera/actualiza el perfil del autenticado; la gestión general queda para ADMIN. El id numérico de negocio no sustituye al sub para autorizar.',
'MascotaService':'Gestiona mascotas verificando el dueño del perfil asociado. Las rutas propias y las rutas anidadas validan la relación; cambiar el número de una URL no permite ver una mascota de otro cliente.',
'MiCuentaController':'Expone /api/v1/usuarios/me y sus mascotas para el cliente autenticado. Valida DTO y delega en UsuarioService/MascotaService sin admitir un sub arbitrario enviado por el navegador.',
'CorrelationIdFilter':'Lee o genera X-Trace-ID, lo asocia al MDC del hilo y devuelve la correlación. Permite buscar en los logs una misma operación HTTP; los eventos conservan traceId. No constituye trazado distribuido automático con OpenTelemetry.',
'GlobalExceptionHandler':'Advice REST del módulo: convierte las excepciones de recurso inexistente, validación u otros casos declarados en respuestas HTTP. Se debe leer junto a DomainErrors y a Spring Security; no controla por sí solo todos los fallos del sistema.',
'ResourceNotFoundException':'Excepción de dominio que indica que una búsqueda no encontró el recurso. El manejador de excepciones correspondiente la traduce a una respuesta, evitando devolver una entidad nula.',
'PagoRequest':'DTO conservado en el módulo de Pago. En esta versión el controlador no expone una creación libre de pagos: los genera PagoEvents desde inventario.reservado. Su presencia no implica un endpoint de cobro ni una pasarela bancaria.',
'Auth':'Servicio singleton Angular que inicializa keycloak-js con check-sso y PKCE S256, mantiene signals de sesión/rol, renueva tokens y ejecuta login/logout. Los tokens permanecen en memoria.',
'Config':'Carga config.dev.json en desarrollo o config.json en producción antes de inicializar la autenticación. Permite cambiar URLs de API y Keycloak sin insertar esas direcciones en cada componente.',
'Api':'Servicio HttpClient tipado para catálogo, categorías, ventas y pago por venta. crearVenta añade Idempotency-Key; el interceptor incorpora el JWT solo para la API propia.',
'CartStore':'Estado del carrito con signals y persistencia local de ids, cantidades, sede, método de pago y clave de reintento. Revalida stock/sede activa y prepara el payload sin precios confiables del cliente. No almacena tokens.',
'DomainApi':'Servicio HTTP genérico y tipos para sedes, profesionales, especialidades, cuenta, mascotas, citas, envíos y administración; centraliza el prefijo de API configurado.',
'App':'Componente raíz standalone: coordina navegación, catálogo, carrito, sesión, pedidos/polling y vistas de cada dominio. Oculta administración para clientes y verifica la vista guardada al restaurar la sesión; backend mantiene la autorización efectiva.',
}
def describe(path):
 p=Path(path);s=p.stem;text=(ROOT/path).read_text(errors='replace')
 if s in SPECIAL:return SPECIAL[s]
 if s.endswith('Application'):return 'Punto de entrada Spring Boot del módulo. main llama a SpringApplication.run; sus anotaciones activan el escaneo/configuración del contexto y las importaciones muestran los componentes comunes que utiliza.'
 if s.endswith('ApplicationTests'):return 'Prueba de carga del contexto Spring de este módulo. Verifica que sus beans y configuración pueden iniciarse contra el entorno de pruebas; no demuestra por sí sola los flujos distribuidos.'
 if s=='EspecialidadesIntegrationTests':return 'Prueba de integración real de PostgreSQL/JPA: asociaciones muchos a muchos, ids duplicados, especialidad compartida, reasignación y conflicto al borrar una especialidad vinculada. Revierte su transacción de prueba.'
 if s=='SagaContractTest':return 'Pruebas del contrato versionado, correlación y control de propiedad. Comprueba casos válidos e inválidos sin afirmar entrega Kafka exactamente una vez.'
 if s.endswith('Controller'):return 'Adaptador REST de '+s.removesuffix('Controller')+'. Sus mappings declaran rutas, verbo HTTP y respuestas; @Valid activa la validación de entrada. Delega el trabajo en el servicio inyectado. Las restricciones de rol se encuentran además en SecurityConfiguration.'
 if s.endswith('Repository'):return 'Puerto de persistencia Spring Data de '+s.removesuffix('Repository')+'. La interfaz y sus métodos declaran búsquedas, bloqueos o grafos de lectura; Spring genera la implementación al iniciar el contexto.'
 if s.endswith('Mapper'):return 'Convierte '+s.removesuffix('Mapper')+' entre DTO y entidad; separa el contrato HTTP de JPA y establece los valores iniciales que declara su implementación. No debe sustituir las validaciones del servicio.'
 if s.endswith('Request'):return 'DTO de entrada para '+s.removesuffix('Request')+'. Define exactamente los campos que acepta la API; las anotaciones Bean Validation limitan valores antes de ejecutar la lógica del servicio.'
 if s.endswith('Response'):return 'DTO de salida para '+s.removesuffix('Response')+'. Expone los campos declarados al cliente sin serializar directamente todo el grafo JPA.'
 if s.endswith('Service'):return 'Lógica de aplicación de '+s.removesuffix('Service')+'. Coordina repositorios/mappers y las validaciones presentes en sus métodos. Los límites @Transactional gobiernan los cambios locales; ver el listado completo para las operaciones exactas.'
 if '/entity/' in path:
  if 'enum ' in text:return 'Enumeración de valores admitidos por el dominio. Sus constantes impiden usar cadenas arbitrarias en el estado/método de la entidad; las transiciones válidas se controlan en servicios o consumidores.'
  return 'Entidad JPA '+s+': representa una tabla del PostgreSQL propio del servicio. Sus campos, relaciones y restricciones se declaran mediante anotaciones; Flyway crea/evoluciona la estructura real. No comparte tablas con otros microservicios.'
 if p.suffix=='.sql':return 'Migración SQL real. Flyway ejecuta V__ en orden una vez y verifica su checksum; R__ se reaplica cuando cambia. db/demo se habilita solo en el perfil DEV para ejemplos.'
 if p.name=='pom.xml':return 'Descriptor Maven: versión Java, dependencias, BOM y plugins. El reactor uso-rapido/pom.xml coordina los módulos; no es el padre común de todos los POM.'
 if p.name.startswith('compose'):return 'Composición Docker: servicios, imágenes, puertos, variables, redes, volúmenes y orden/healthcheck declarados. La variante DEV aloja dependencias; la integrada es una alternativa distinta.'
 if p.suffix in {'.yml','.yaml'}:return 'Configuración declarativa del módulo o herramienta. Conserva sangría y nombres exactos. Las variables ${...} se resuelven por el mecanismo del archivo: Spring o Docker Compose según su ubicación.'
 if p.suffix in {'.ts','.html','.css'}:return 'Fuente Angular: '+('lógica, tipos y estado del componente/servicio.' if p.suffix=='.ts' else 'plantilla declarativa de la vista.' if p.suffix=='.html' else 'estilos compartidos y adaptación a tamaños de pantalla.')+' Se compila con Angular CLI; los datos de negocio proceden de la API.'
 return 'Archivo de soporte del proyecto. Su contenido completo se reproduce aquí en su ruta original para reconstruir la misma versión.'

PORTS=[('Angular','4200','Navegador','Tienda y administración'),('Gateway','18080','HTTP host','Entrada /api/v1; JWT'),('Config Server','18888','HTTP host','Configuración central'),('Eureka','18761','HTTP host','Registro de instancias'),('Kafka externo','19092','Kafka TCP host','Productor/consumidor Java/Python; no es página web'),('Kafka interno','9092','Solo red Docker','garritas-kafka:9092; no localhost desde otro contenedor'),('Kafka UI','18085','Navegador','Clúster, topics, eventos, grupos'),('Keycloak','18180','Navegador/OIDC','Realm garritas y consola /admin/'),('Keycloak health/metrics','19000 → 9000','HTTP de gestión','Health y métricas; no interfaz de usuario'),('Grafana','13000','Navegador','Dashboards y Explore'),('Prometheus','19090','Navegador','Targets y consultas'),('Loki','13100','API','Consultar desde Grafana; no tiene portada de tienda')]
DOMAINS=[('venta',8081,15441,'ventas, detalle_ventas; Saga y propietario'),('institucion',8082,15442,'sedes; consulta y administración'),('envio',8083,15443,'envios; entrega por venta pagada'),('citas',8084,15444,'citas; agenda por mascota/profesional/sede'),('catalogo',8085,15445,'categorias, productos; inventario y reservas'),('usuario',8086,15446,'usuarios, mascotas; perfil vinculado al sub'),('pago',8087,15447,'pagos; respuesta simulada de Saga'),('bienestar',8088,15448,'profesionales, especialidades y unión M:N')]

def operational():
 b=Book('01-Ejecucion-y-puertos.pdf','Manual 1 · Ejecutar y comprobar Garritas','Instalación, arranque en Windows y Linux/WSL2, puertos, credenciales de laboratorio, pruebas y diagnóstico.')
 b.h('1. Qué vas a ejecutar')
 b.p('Garritas Store es una aplicación distribuida de laboratorio: Angular muestra la tienda, Gateway recibe las peticiones, Keycloak autentica y ocho microservicios guardan datos en ocho bases PostgreSQL independientes. Config Server centraliza ajustes; Eureka registra instancias; Kafka comunica la Saga de compra. El pago es simulado, no un cobro real.')
 b.p('Este manual describe el flujo DEV: Java y Angular corren en el equipo; Docker aloja PostgreSQL, Kafka, Keycloak y monitorización. No mezcles estos puertos con los de la alternativa integrada en uso-rapido/docker. La revisión de esta edición se limita a lo indicado en el capítulo de evidencia.')
 b.image('despliegue','Distribución real del flujo DEV. Los procesos Java no son contenedores en esta modalidad.')
 b.h('2. Requisitos y comprobación previa')
 b.table(['Herramienta','Versión del proyecto','Cómo comprobar'],[('Git','Versión reciente','git --version'),('JDK completo','21; se necesita javac','java -version y javac -version'),('Node.js','24','node --version'),('npm','Incluido con Node','npm --version'),('Docker Desktop/Engine','Compose v2, contenedores Linux','docker info y docker compose version'),('Python','3; utilidades y pruebas Linux','python3 --version'),('Editor','VS Code/IDE Java recomendado','No es necesario para abrir la tienda')],[110,160,239])
 b.p('Orientación práctica, no mínimo certificado: dispone de 16 GB de RAM para el laboratorio completo y margen de disco de varias decenas de GB para dependencias/imágenes. El uso depende del driver Docker y de los datos. La revisión anterior agotó disco con VFS al intentar el despliegue íntegro en contenedores; DEV usa menos capas de aplicación.')
 b.p('Windows: inicia Docker Desktop con motor Linux, comprueba que está listo y abre PowerShell en una carpeta corta, por ejemplo C:\\proyectos. El JDK debe ser completo; si JAVA_HOME existe, debe apuntar a su carpeta raíz, no a bin. No combines Java 17 con este código Java 21.')
 b.code('java -version\njavac -version\nnode --version\nnpm --version\ndocker version\ndocker compose version\ngit --version')
 b.h('3. Descargar la versión correcta')
 b.p('Los cambios están en feat/garritas-store. main puede contener una versión distinta. Clona la rama explícitamente; si ya tienes otra copia, guarda primero tus cambios personales antes de actualizarla.')
 b.code('git clone --branch feat/garritas-store https://github.com/Nikol235/Garritas-.git\ncd Garritas-\ngit branch --show-current\ngit log -1 --oneline')
 b.p('Para estudiar exactamente el código de esta edición puedes consultar el commit '+REV+'. El PDF de construcción y su ZIP están referidos a ese código, aunque posteriores commits añadan documentación.')
 b.code('git fetch origin\ngit switch feat/garritas-store\ngit pull --ff-only origin feat/garritas-store')
 b.h('4. Windows: arranque automatizado paso a paso')
 for t in ['Paso 1. Abre PowerShell en Garritas-, la carpeta que contiene clients, services y uso-rapido. Usa Get-Location y Get-ChildItem para confirmar; no ejecutes el lanzador desde una subcarpeta inventada.','Paso 2. Compila una sola vez antes del primer arranque. build instala el módulo común, empaqueta los once ejecutables Java e instala/compila Angular. Necesita Internet para dependencias que no estén en caché.','Paso 3. Ejecuta iniciar. El script arranca los contenedores, espera Config y cada aplicación, guarda los procesos en .runtime y levanta Angular. Conserva la terminal hasta que termine de informar disponibilidad.','Paso 4. Ejecuta estado y abre http://localhost:4200. Un proceso visible no basta: se debe poder consultar catálogo por Gateway y realizar una compra de prueba.'] :b.p(t)
 b.code('.\\uso-rapido\\garritas.ps1 -Accion build\n.\\uso-rapido\\garritas.ps1 -Accion iniciar\n.\\uso-rapido\\garritas.ps1 -Accion estado')
 b.p('El lanzador PowerShell está incluido pero esta revisión se ejecutó en Linux, no en Windows. Si PowerShell bloquea scripts por su política, revisa el archivo y usa la alternativa manual del siguiente capítulo o la política de ejecución aprobada para tu equipo. Un fallo de política de PowerShell no es un fallo de Spring.')
 b.h('5. Windows: alternativa manual, con terminales separadas')
 b.p('Cada bloque siguiente indica su carpeta. Los comandos Maven Wrapper .cmd se ejecutan en Windows; bash usa el archivo mvnw sin .cmd. En esta alternativa las terminales de Spring permanecen abiertas; Ctrl+C detiene su aplicación.')
 b.code('# Terminal inicial, desde Garritas-\n.\\infra\\garritas-config\\mvnw.cmd -f uso-rapido/pom.xml -pl :garritas-distributed -am install -DskipTests\ndocker compose -f kafka/compose-dev.yml up -d --wait\ndocker compose -f keycloak/compose-dev.yml up -d --wait')
 b.p('Arranca Config Server antes que Eureka y los servicios, porque su configuración remota es obligatoria. Config usa perfil native por defecto y resuelve config-repo relativo a su carpeta.')
 b.code('# Terminal 1\ncd infra/garritas-config\n.\\mvnw.cmd spring-boot:run\n# Espera http://localhost:18888/actuator/health/readiness')
 b.code('# Terminal 2 nueva, desde la raíz\ncd infra/garritas-eureka\n.\\mvnw.cmd spring-boot:run\n# Espera http://localhost:18761')
 b.p('Para cada servicio abre una terminal nueva desde la raíz. Primero levanta su PostgreSQL y luego Spring. Repite el patrón con catalogo, usuario, bienestar, institucion, venta, pago, citas y envio. Todos se denominan garritas-<dominio>-ms.')
 b.code('# Ejemplo: terminal de Catálogo\ncd services/garritas-catalogo-ms\ndocker compose -f compose-dev.yml up -d --wait\n.\\mvnw.cmd spring-boot:run')
 b.code('# Nueva terminal: Gateway, cuando los servicios estén disponibles\ncd infra/garritas-gateway\n.\\mvnw.cmd spring-boot:run\n# Nueva terminal: Angular\ncd clients/garritas-frontend\nnpm ci\nnpm start')
 b.p('Espera a que Eureka muestre los ocho servicios y Gateway. Eureka no es un proxy que transporta cada petición: el cliente obtiene las instancias y LoadBalancer elige una. El registro puede necesitar unos segundos después de readiness.')
 b.h('6. Linux o WSL2: arranque comprobado')
 b.code('# Desde Garritas- con JDK21, Node24 y Docker disponibles\nbash uso-rapido/scripts/dev.sh build\nbash uso-rapido/scripts/dev.sh all\nbash uso-rapido/scripts/dev.sh observability\nbash uso-rapido/scripts/dev.sh status --observability')
 b.p('build no levanta Angular. all arranca dependencias, Config, Eureka, servicios, Gateway y el servidor frontend. observability añade monitorización. El primer arranque puede tardar varios minutos: descarga imágenes, aplica migraciones y carga el realm. No cierres el proceso de arranque a mitad salvo para diagnosticar un error.')
 b.p('En esta nube se usa source /workspace/.onboarding/activate-s11.sh para el JDK y el proxy local. Esa ruta pertenece a esta máquina y no debes copiarla en tu PC. En tu equipo configura JAVA_HOME/Node y usa los comandos anteriores.')
 b.h('7. Tabla completa de puertos',new=True)
 b.table(['Componente','Puerto','Acceso','Uso'],PORTS,[100,75,105,229])
 b.table(['Dominio','HTTP DEV','PostgreSQL host','Responsabilidad'],[(x,str(h),str(db),r) for x,h,db,r in DOMAINS],[78,60,86,285])
 b.p('Cada PostgreSQL de negocio escucha en 5432 dentro de su propio contenedor. El host publica 15441–15448 para evitar colisiones. Ejemplo: Java host usa localhost:15445 para Catálogo; un contenedor integrado usa el nombre del contenedor y 5432. La base interna de Keycloak no se publica en DEV. Nunca uses 8085 de Catálogo como sustituto de la API pública 18080 en Angular.')
 b.p('Kafka 19092 es un protocolo de mensajería: escribir esa URL en Chrome no abre una consola. Usa Kafka UI en 18085. Loki en 13100 sirve una API; usa Grafana Explore para consultar logs. Keycloak 19000 corresponde a gestión, no al login de usuarios.')
 b.h('7.1 Monitorización desde PowerShell',2)
 b.p('Después de iniciar Keycloak y las aplicaciones, desde la raíz ejecuta el Compose DEV de observabilidad. No uses obs/compose.yml de PROD para estos puertos. Docker Desktop debe poder acceder a la carpeta del repositorio. Si faltan métricas, comprueba host.docker.internal y targets; la configuración se validó funcionalmente en Linux.')
 b.code('docker compose -f obs/compose-dev.yml up -d\n# Comprueba en navegador localhost:13000 y localhost:19090')
 b.h('8. Cuentas y primer recorrido')
 b.table(['Acceso','Usuario','Contraseña de laboratorio','Qué puede hacer'],[('Tienda cliente','cliente','Cliente123!','Comprar; perfil/mascotas; citas y envíos propios'),('Tienda ADMIN','admin-store','Admin123!','Administrar sedes, catálogo, clientes y operaciones'),('Consola Keycloak','admin','local-admin-change-me','Administrar realm; distinto del administrador de tienda'),('Grafana','admin','local-grafana','Explorar paneles y logs')],[100,94,125,190])
 b.p('Son credenciales explícitas de demostración y pueden haberse cambiado en tu volumen. El realm se importa cuando todavía no existe; cambiar el JSON y reiniciar no sobrescribe automáticamente uno existente. No se debe borrar el volumen para cambiar una contraseña: usa la consola administrativa o una migración controlada.')
 b.h('8.1 Recorrido como cliente',2)
 for t in ['Abre la tienda y consulta el catálogo sin iniciar sesión. Busca por nombre y filtra por categoría.','Inicia sesión como cliente. En Sedes observa los ejemplos de Perú; no deben aparecer opciones de creación/edición. Selecciona una para la compra.','En Nueva orden añade productos, cambia cantidades y revisa subtotales. El servidor revalida stock y precios; una cifra del navegador no es un precio autorizado.','En Carrito elige sede activa y método. YAPE o PLIN son ejemplos de aprobación simulada. Confirma y espera hasta Pagada en pedidos; la respuesta inicial puede ser Pendiente de stock/pago.','En Mi cuenta y mascotas completa el perfil y crea una mascota. Luego reserva una cita con sede, profesional y fecha futura en bloques de 30 minutos.','En Envíos selecciona un pedido pagado, introduce la dirección y solicita entrega. El cliente consulta su historial; no marca tránsito o entrega.'] :b.bullet(t)
 b.h('8.2 Recorrido como administrador',2)
 for t in ['Cierra sesión e ingresa como admin-store. En Sedes crea, edita o desactiva. Las inactivas no se ofrecen a clientes para nuevas compras.','En Especialistas gestiona especialidades y profesionales. Asigna varias especialidades a un profesional y una misma especialidad a dos profesionales: eso demuestra M:N.','En Productos/Categorías gestiona el catálogo. La baja lógica evita eliminar inventario necesario para compensaciones.','En Citas confirma una PROGRAMADA y luego marca atención. En Envíos pasa un pendiente a tránsito y después a entregado.','ADMIN puede auditar pedidos y pagos de todos; CLIENTE solo los propios. El backend verifica esto aunque alguien fabrique una petición HTTP.'] :b.bullet(t)
 b.h('9. Prueba del pago rechazado y del carrito')
 b.p('En DEV TRANSFERENCIA simula rechazo. Haz una compra pequeña con ese método: la venta debe pasar por compensación y terminar cancelada; el stock reservado se devuelve una sola vez. No cambies manualmente el estado en PostgreSQL, porque romperías la evidencia de la Saga.')
 b.p('El carrito persiste ids, cantidades, sede, método y clave de reintento. No persiste JWT. Al recargar o volver del login recupera el contenido y revalida sus referencias. Reintentar una solicitud idéntica con la misma Idempotency-Key no debe crear otra compra; cambiar el payload con esa clave debe producir 409.')
 b.h('10. Abrir y entender las consolas')
 for title,txt in [('Kafka UI · 18085','Selecciona el clúster garritas y confirma estado ONLINE. Abre Topics: garritas.ventas.v1 recibe los eventos de compras; .DLT conserva errores agotados. En Consumer Groups identifica los grupos de Venta, Catálogo y Pago. Un topic con mensajes no demuestra que un consumidor haya actualizado su base: revisa también el pedido y los logs.'),('Keycloak · 18180/admin/','Entra con el administrador de Keycloak, cambia al realm garritas y examina los roles CLIENTE/ADMIN y el cliente público garritas-frontend. El login de tienda usa Authorization Code + PKCE; no guardes secretos de cliente en Angular.'),('Eureka · 18761','Comprueba nueve aplicaciones registradas: ocho dominios y Gateway. Config Server y Eureka suman once procesos Java, pero no se cuentan como dos servicios de negocio registrados adicionales.'),('Prometheus · 19090','En Status/Targets comprueba UP para los once procesos Java y Keycloak. Prueba la consulta up. Un endpoint readiness que responde no demuestra la compra completa; las pruebas de navegador complementan la comprobación.'),('Grafana · 13000','Abre Dashboards y los paneles aprovisionados. En Explore elige Prometheus para métricas y Loki para logs. Busca el servicio y correlaciona traceId; si una consola funciona pero no muestra datos, revisa datasource y targets.'),('Loki · 13100','Su /ready informa disponibilidad de almacenamiento/ingesta. No tiene interfaz visual propia. Promtail lee .runtime y envía los logs; Grafana hace las consultas.')]:b.h(title,2);b.p(txt)
 b.image('observabilidad','Camino de métricas y logs. Prometheus no almacena los logs; Loki no sustituye a PostgreSQL.')
 b.h('11. Pruebas reproducibles y evidencias')
 b.code('bash uso-rapido/scripts/dev.sh test\n(cd clients/garritas-frontend && npm test && npm run build)\npython3 -m venv .runtime/pruebas-venv\n.runtime/pruebas-venv/bin/pip install -r uso-rapido/scripts/requirements-test.txt\n.runtime/pruebas-venv/bin/python -m playwright install chromium\n.runtime/pruebas-venv/bin/python uso-rapido/scripts/domain_smoke.py\n.runtime/pruebas-venv/bin/python uso-rapido/scripts/smoke.py\n.runtime/pruebas-venv/bin/python uso-rapido/scripts/consoles.py')
 b.p('Si utilizas Chromium de sistema en Linux, antepón CHROMIUM_PATH=/usr/bin/chromium al comando Python. Las pruebas crean registros de laboratorio identificables; ventas/citas conservan historial. Ejecuta los recorridos secuencialmente contra el entorno local DEV, no contra producción. faults.py detiene intencionalmente Pago/Kafka; no lo ejecutes mientras otra persona demuestra la tienda.')
 evidence=OUT/'revision.json'
 if evidence.exists():
  ev=json.loads(evidence.read_text());b.table(['Comprobación de esta edición','Resultado'],[(x['prueba'],x['resultado']) for x in ev['checks']],[180,329])
 else:b.p('La evidencia se añade al generar la edición final; consulta docs/validacion.md y el archivo revision.json adjunto.')
 b.p('Límite: el flujo DEV Linux se comprueba aquí. El lanzador PowerShell no se ejecutó en Windows. El arranque simultáneo del despliegue íntegro Docker no se acredita en esta revisión; el antecedente de falta de espacio con VFS sigue documentado. Que un YAML valide no significa que todos sus contenedores hayan pasado pruebas funcionales.')
 b.h('12. Diagnóstico por síntoma',new=True)
 cases=[('No abre ninguna página','Comprueba Docker y vuelve a ejecutar all/iniciar. Después de restaurar una nube los archivos pueden existir pero los procesos no sobreviven. Comprueba estado, no solo la carpeta .runtime.'),('Java dice release 21 not supported','java y javac no están usando JDK21. Revisa JAVA_HOME y PATH; abre una terminal nueva después de corregirlos.'),('Compilación no encuentra garritas-distributed','Ejecuta build o instala el común desde el reactor. Su carpeta es infra/garritas-common, pero su artifactId Maven sigue siendo garritas-distributed; no son dos módulos distintos.'),('Config Server no disponible','Arranca primero infra/garritas-config desde su carpeta. Revisa 18888, perfil native y config-repo. Los clientes importan configuración obligatoria: no deben seguir con valores inventados.'),('Gateway devuelve 503','Comprueba Eureka y readiness del servicio destino. Revisa el nombre spring.application.name frente a lb:// y espera registro. También puede ser una dependencia remota que el servicio traduce a 503.'),('Login redirige mal o sale invalid redirect','Usa exactamente localhost:4200 y realm/cliente del config.dev.json. Cambiar localhost por IP/127.0.0.1 altera el origen y redirect URI; hay que actualizar cliente, CORS e issuer de forma coherente.'),('401 o 403','401 suele indicar token ausente/inválido; 403, rol o propietario no permitido. Inicia sesión con el usuario correcto. No elimines las comprobaciones para solucionar permisos.'),('409 al reservar cita','Puede existir otra cita activa para ese profesional y bloque horario. Elige otro bloque; verifica si la sede y el profesional siguen activos. El índice es una protección de concurrencia.'),('404 en Mi cuenta','Completa/guarda el perfil propio primero; el usuario Keycloak y el perfil local son registros distintos enlazados por sub.'),('Pedido queda pendiente','Comprueba Kafka ONLINE, grupos consumidores, outbox pendientes y logs de Pago/Catálogo/Venta. Si hay DLT, investiga antes de republicar. No fuerces PAGADA manualmente.'),('No se devuelve stock','Espera inventario.liberado y confirma la reserva original. El pago rechazado solo termina cancelación después de compensar. No incrementes stock manualmente durante una Saga.'),('Grafana sin métricas o Loki 503','Ejecuta observability y espera readiness; revisa targets y permisos de archivos públicos restaurados. Loki puede necesitar estabilización al iniciar. La herramienta prepara permisos sin cambiar credenciales.'),('Puerto ocupado','Windows: Get-NetTCPConnection -LocalPort 4200; Linux: ss -ltnp. Identifica el dueño antes de detener un proceso. El script conserva un Angular existente si ya está sirviendo Garritas.'),('Docker: no space left on device','Revisa docker system df y espacio del host. No borres volúmenes con datos. Retira solo imágenes/caché que puedas reproducir; usa DEV y amplía disco/driver si necesitas el despliegue integrado.'),('Después de editar Java no cambia la tienda','Las JVM usan copias estables en .runtime. Compila y reinicia los procesos gestionados: build, stop, all. Recompilar un target no recarga automáticamente una JVM ya ejecutándose.')]
 for a,c in cases:b.h(a,2);b.p(c)
 b.h('13. Parar, reiniciar y conservar datos')
 b.code('# Linux / WSL2\nbash uso-rapido/scripts/dev.sh stop\n# Detiene Java/Angular gestionados; conserva contenedores y datos.\nbash uso-rapido/scripts/dev.sh all\n# Para bajar también contenedores sin borrar volúmenes:\nbash uso-rapido/scripts/dev.sh down')
 b.code('# Windows PowerShell\n.\\uso-rapido\\garritas.ps1 -Accion detener\n# Los contenedores siguen; iniciar vuelve a arrancar aplicaciones.\n.\\uso-rapido\\garritas.ps1 -Accion iniciar')
 b.p('No ejecutes docker compose down -v como limpieza rutinaria: -v borra los volúmenes seleccionados. Para copias de seguridad usa pg_dump por base y conserva también los ajustes/realm y la evidencia de eventos. Una restauración consistente necesita coordinación con las Sagas pendientes; restaurar solo Venta puede desalinear inventario y pagos.')
 b.h('14. Ejemplo independiente de Kafka')
 b.p('uso-rapido/garritas-eventos-py contiene producer_eventos.py y consumer_eventos.py, sus dependencias y Compose. El topic garritas.demo.v1 está separado del de compras. Lee su README para argumentos exactos; producir allí no crea un pedido ni un pago.')
 b.code('cd uso-rapido/garritas-eventos-py\npython3 -m venv .venv\n.venv/bin/pip install -r app/requirements.txt\n.venv/bin/python app/producer_eventos.py\n.venv/bin/python app/consumer_eventos.py')
 b.h('15. Checklist antes de presentar el proyecto')
 for t in ['Estado de todos los puertos OK y catálogo real por Gateway.','Cliente ve sedes y las selecciona; no puede modificarlas.','ADMIN modifica sedes/productos y asigna especialidades.','Una compra aprobada llega a Pagada y descuenta el stock correcto.','Una compra rechazada se cancela después de restaurar stock.','Una mascota propia permite reservar; datos ajenos se rechazan.','Cita confirma/atiende y envío avanza hasta entrega con ADMIN.','Kafka ONLINE, Eureka con servicios, Prometheus UP y Grafana con datos.','Se distingue demostración local de despliegue público y de pago bancario real.']:b.bullet(t)
 b.save()

def eligible(p):
 path=Path(p)
 return not (p.startswith(('docs/manuales/','.git/')) or '/target/' in p or '/node_modules/' in p or path.name=='.env' or p.endswith(('.log','.hprof','.pdf','.zip','.png','.jpg')))
def code_file(p):
 return eligible(p) and Path(p).name not in {'package-lock.json','mvnw','mvnw.cmd'} and (Path(p).suffix in {'.java','.ts','.html','.css','.sql','.yml','.yaml','.xml','.json','.py','.sh','.ps1','.properties','.conf','.txt'} or Path(p).name.startswith('Dockerfile') or Path(p).name in {'.env.example','.gitignore','.dockerignore','.nvmrc','.java-version','.gitattributes'})
SOURCE_FILES=[p for p in TRACKED if eligible(p)]
CODE_FILES=[p for p in SOURCE_FILES if code_file(p)]

def construction():
 b=Book('02-Construccion-desde-cero-con-codigo.pdf','Manual 2 · Construir desde cero','Guía de trabajo por etapas y catálogo completo de archivos de código/configuración con ruta exacta. Incluye ZIP de fuentes para copiar sin errores.')
 b.h('1. Cómo usar este manual')
 b.p('El objetivo es reconstruir el mismo Garritas Store, no un ejemplo reducido. Primero estudia las etapas y después crea los archivos del catálogo en sus rutas exactas. La versión base es '+REV+'. No es necesario clonar para aprender: el ZIP Garritas-Store-codigo-base.zip reproduce los archivos fuente de ese commit sin .git, targets, node_modules, logs ni .env privados.')
 b.p('Cada ficha del catálogo indica qué archivo crear, en qué carpeta y el contenido completo. Las líneas muy largas se ajustan visualmente al ancho del PDF: si copias desde un lector PDF, compara con el archivo original del ZIP para no introducir saltos dentro de cadenas. El ZIP es la fuente de texto exacta, con hashes SHA-256 en MANIFIESTO-CODIGO.json. No pegues números de página, títulos ni bordes de bloques.')
 b.p('Los wrappers Maven y package-lock.json se incluyen íntegros en el ZIP, pero no se imprimen sus miles de líneas generadas en este PDF. Son herramientas/lock generado, no lógica de la tienda. Los Java, TypeScript, SQL, configuración, plantillas, CSS y automatizaciones sí se reproducen. No se incluyen binarios de dependencias: Maven/npm/Docker los obtienen con los manifiestos.')
 b.h('2. Del diseño a las carpetas')
 b.image('arquitectura','Vista de conjunto que vas a construir; los ocho dominios son aplicaciones independientes.')
 b.p('Crea una carpeta vacía Garritas- y ábrela como raíz del editor. Las rutas de este manual se interpretan desde esa carpeta. En Java el paquete declara dónde debe vivir el archivo bajo src/main/java; no cambies pe.edu.upeu.garritas sin cambiar imports y configuración coherentemente.')
 b.code('Garritas-/\n  .github/workflows/\n  clients/garritas-frontend/\n  docs/\n  infra/garritas-common/\n  infra/garritas-config/\n  infra/garritas-eureka/\n  infra/garritas-gateway/\n  kafka/\n  keycloak/\n  obs/\n  overrides/\n  services/garritas-<dominio>-ms/\n  uso-rapido/scripts/\n  uso-rapido/docker/\n  uso-rapido/garritas-eventos-py/')
 b.p('En PowerShell New-Item -ItemType Directory -Force crea carpetas. Ejemplo: New-Item -ItemType Directory -Force services/garritas-institucion-ms/src/main/java/pe/edu/upeu/garritas/institucion/controller. Luego crea SedeController.java ahí y pega su bloque completo del catálogo. Guarda todo en UTF-8.')
 b.h('3. Crear el repositorio y los manifiestos')
 b.code('mkdir Garritas-\ncd Garritas-\ngit init\n# Crea aquí .gitignore, .java-version, .nvmrc y las carpetas del mapa.\n# Copia los wrappers/.mvn del ZIP a cada módulo tal como están.')
 b.p('La raíz conserva archivos de identificación/documentación. El agregador Maven está en uso-rapido/pom.xml; cada módulo tiene su propio pom.xml y wrapper. Todos usan Java 21; Spring Boot 4.0.8 y el BOM Spring Cloud 2025.1.3 fijan compatibilidad. No elijas versiones distintas de cada starter al azar.')
 b.p('Pega primero los POM. El común tiene artifactId garritas-distributed aunque su carpeta es infra/garritas-common. Instalarlo permite ejecutar un módulo independiente desde su carpeta. El agregador enumera módulos con ../ porque está un nivel por debajo de la raíz.')
 b.code('# Desde la raíz, después de crear todos los módulos/archivos\nbash infra/garritas-config/mvnw -f uso-rapido/pom.xml -pl :garritas-distributed -am install -DskipTests\n# Windows equivalente\n.\\infra\\garritas-config\\mvnw.cmd -f uso-rapido/pom.xml -pl :garritas-distributed -am install -DskipTests')
 b.h('4. Construir primero el soporte común')
 b.p('En infra/garritas-common crea package pe.edu.upeu.garritas.common y pega sus diez clases del catálogo: CurrentUser, DomainErrors, HttpServices, Inbox, MessagingConfiguration, Outbox, Reference, SagaEvent, SecurityConfiguration y ServiceClient. Añade SagaContractTest en src/test/java con el mismo paquete.')
 b.p('Orden didáctico: empieza por SagaEvent y Reference (contratos); sigue con CurrentUser y SecurityConfiguration (identidad); añade Inbox/Outbox/MessagingConfiguration (eventos); termina HttpServices/ServiceClient y DomainErrors. Las importaciones del servicio común en cada Application hacen que estas clases se registren donde corresponde; estar en un JAR no activa automáticamente todo su contenido.')
 b.p('Comprobación: el POM común debe compilar. No pruebes Outbox contra una base sin migraciones: exige tablas inbox_event/outbox_event y transacción local. La configuración de mensajería solo se importa en los servicios que realmente participan de la Saga.')
 b.h('5. Crear Config Server, Eureka y Gateway')
 for title,txt in [('5.1 Config Server','Crea infra/garritas-config con Application, pom.xml, application.yml, config-repo y wrapper. @EnableConfigServer sirve los archivos centralizados; native lee file:./config-repo. Pega los YAML DEV/PROD de cada aplicación sin cambiar nombres; spring.application.name decide cuál solicitar.'),('5.2 Eureka','Crea infra/garritas-eureka con @EnableEurekaServer y la importación de Config. Su cliente no se registra a sí mismo según configuración. Arranca después de Config y comprueba la consola 18761.'),('5.3 Gateway','Crea infra/garritas-gateway con Application, CorrelationIdFilter y POM MVC. Importa seguridad común. Pega las rutas de configuración: /ventas a Venta, /sedes a Institución, etc. lb:// se resuelve con Eureka. Configura CORS para localhost:4200 y JWT para realm garritas/audiencia garritas-api.')]:b.h(title,2);b.p(txt)
 b.p('No mezcles Gateway WebFlux con el starter MVC utilizado aquí. No declares globalmente un RestClient.Builder balanceado para resolver llamadas de negocio: el cliente HTTP común usa su constructor local para no alterar Eureka. Esa separación evita que localhost se interprete como un servicio por descubrir.')
 b.h('6. Crear PostgreSQL y migraciones por dominio')
 b.p('Cada carpeta services/garritas-<dominio>-ms lleva compose-dev.yml con postgres:16-alpine, un volumen propio, usuario/base/puerto. Crea src/main/resources/db/migration y pega V1 y todas sus V posteriores; no construyas solo V1 si buscas la versión final. Flyway aplica cambios antes de que JPA valide el esquema.')
 b.table(['Servicio','Base','Puerto host'],[(x,'garritas_'+x+'_db',str(db)) for x,h,db,r in DOMAINS],[135,249,125])
 b.p('En src/main/resources/application.yml declara nombre y spring.config.import. En config-repo/<nombre>-dev.yml configura JDBC localhost:1544x, validate, Flyway, issuer/JWK, Eureka, health y lo que use ese servicio. En PROD los nombres de red y puertos internos son distintos. No copies una URL localhost al interior de un contenedor pensando que apunta al host.')
 b.p('En el perfil DEV se habilita db/demo para Catálogo, Institución y Bienestar. Pega las migraciones repetibles completas. Crean ejemplos sin reinicializar datos existentes; no modifiques una V ya ejecutada para agregar un campo, crea una nueva V. Las diferencias de checksum son errores que investigar, no resolver borrando flyway_schema_history.')
 b.h('7. Patrón de capas: construye Institución como primer CRUD')
 b.image('clases','El diagrama usa Producto, pero el mismo recorrido de capas se aplica a Sede.')
 for t in ['Entidad: crea entity/Sede.java con id, nombre, ciudad/dirección/teléfono y activo según su listado real. La migración SQL es la autoridad del esquema; JPA valida correspondencia.','DTO: crea dto/SedeRequest.java y SedeResponse.java. En Request usa las restricciones declaradas; en Response expón datos permitidos.','Repositorio: crea repository/SedeRepository.java extendiendo JpaRepository<Sede, Long>. Spring implementa operaciones de persistencia.','Mapper: crea mapper/SedeMapper.java para convertir datos; evita devolver entidades enlazadas directamente desde controladores.','Servicio: crea service/SedeService.java con transacciones, búsqueda y baja lógica. Admin ve todas; consulta pública/cliente ve activas.','Controlador: crea controller/SedeController.java con /api/v1/sedes y los verbos. Inyecta el servicio y usa @Valid en entrada.','Aplicación y soporte: crea Application, filtros, excepciones, pruebas y logback del catálogo. Importa SecurityConfiguration.','Integra ruta /sedes en Gateway y verifica GET por 18080. Una POST sin rol ADMIN debe ser rechazada.']:b.bullet(t)
 b.h('8. Completar Catálogo y Usuario')
 b.p('Catálogo agrega Categoria y Producto con relación muchos a uno, precio BigDecimal, stock no negativo y versión optimista. Copia sus DTO/mappers/controladores/servicios y migraciones de Saga. Después añade InventarioEvents, Inbox/Outbox y la reserva por id_venta. No descuentes stock en el controlador del carrito: solo la transacción de inventario hace la reserva autoritativa.')
 b.p('Usuario agrega Usuario y Mascota. Usuario.subject enlaza con el sub OIDC; id numérico se conserva para el modelo local. MiCuentaController publica /usuarios/me y /usuarios/me/mascotas. Primero guarda el perfil y después registra una mascota. Las rutas genéricas de administración no deben convertirse en edición libre del perfil de otro cliente.')
 b.h('9. Crear Bienestar: la relación muchos a muchos')
 b.image('muchos-a-muchos','Una fila de unión representa una asignación; no se guardan listas de ids como texto.')
 b.p('Crea garritas-bienestar-ms con puerto 8088 y base 15448; agrégalo al reactor y configuración. Pega V1__bienestar.sql, entidades Profesional/Especialidad, repositorios, DTO, BienestarService y BienestarController. Profesional usa @ManyToMany y @JoinTable. En Angular se seleccionan varias especialidades mediante casillas; el backend valida ids, no confía en la vista.')
 b.p('La restricción primaria de dos columnas evita repetir la misma asignación. Profesional.sedeId es una referencia remota opcional: se valida por HTTP contra Institución, no con FK a otra base. Las especialidades vinculadas no se borran; desasigna antes. Ejecuta EspecialidadesIntegrationTests contra PostgreSQL para verificar asociación compartida y reasignación.')
 b.h('10. Construir Venta, Pago y la Saga Kafka')
 b.image('saga','Construye ambos caminos de la Saga: aprobación y compensación.')
 steps=[('Contrato y broker','Pega Kafka Compose; crea topics mediante MessagingConfiguration. Java host usa localhost:19092, Kafka UI usa garritas-kafka:9092. Mantén el contrato SagaEvent común y grupos consumidores independientes.'),('Venta HTTP','Pega entidades Venta/DetalleVenta, DTO, mapper, repository, controller y VentaService. Crea ProductoClient, FeignConfiguration y CatalogoConsulta. Valida la sede con ServiceClient. El comprador es CurrentUser.subject(), no un idCliente del cuerpo.'),('Idempotencia','Pega V2/V3/V4 según el catálogo y las restricciones de propietario+clave. Antes de crear, el servicio toma pg_advisory_xact_lock. Si ya existe la misma clave, compara sede/método/cantidades y devuelve el resultado o 409.'),('Outbox','Venta y venta.creada deben guardarse dentro de la misma transacción. append exige ese contexto. publish manda al broker y marca publicado después del ACK. No sustituyas esto por kafka.send en el controlador.'),('Reserva','InventarioEvents bloquea productos en orden estable, comprueba todos antes de descontar y registra estado por venta. Publica inventario.reservado o rechazado en su outbox.'),('Pago','PagoEvents reacciona a inventario.reservado, crea pago único y publica resultado simulado. La API de pagos consulta; no existe botón que fuerce un cobro real ni POST libre para inventar aprobaciones.'),('Estado/compensación','VentaEvents cambia estados por eventos. Pago fallido inicia COMPENSANDO; Catálogo restaura una vez y emite inventario.liberado; después Venta cancela. Repite evento de prueba sin duplicar restauración.'),('Resiliencia','El Circuit Breaker cubre consulta Feign a Catálogo; ServiceClient usa tiempos máximos. DLT conserva errores agotados; la UI muestra pendiente/error sin falsificar éxito.')]
 for a,c in steps:b.h(a,2);b.p(c)
 b.h('11. Construir Citas y Envío')
 b.image('citas-envios','Dependencias HTTP con JWT propagado. No son joins SQL entre microservicios.')
 b.p('Citas: copia modelo, V1/V2, mapper y servicio. @Future exige fecha futura, el servicio verifica bloque de 30 minutos, consulta mascota propia, sede activa y profesional compatible. El índice único parcial protege profesional+hora mientras PROGRAMADA/CONFIRMADA. UI permite cliente reservar/cancelar y ADMIN confirmar/atender; Gateway y servicio aplican el rol.')
 b.p('Envío: copia V1/V2, DTO y servicio. id_venta único evita dos envíos del mismo pedido. Consulta Venta y exige PAGADA y propietario. El cliente no impone transportista: queda Por asignar. ADMIN marca EN_TRANSITO y ENTREGADO. No agregues un envío sin venta para que una pantalla parezca funcionar.')
 b.h('12. Crear Keycloak y proteger la API')
 b.p('Crea keycloak/compose-dev.yml y garritas-realm.json. Arranca Keycloak con importación inicial. El cliente garritas-frontend es público y acepta redirect localhost:4200; define roles CLIENTE/ADMIN, audiencia garritas-api y cuentas de laboratorio. Nunca pegues un client secret en código Angular.')
 b.p('Cada Application importa SecurityConfiguration donde corresponde. Spring valida issuer, firma y audiencia. CurrentUser se usa en listados y búsquedas para filtrar propiedad. Probar solo que el botón editar no aparece no demuestra seguridad: realiza también peticiones API como cliente y espera 403.')
 b.image('identidad','Flujo real del login del navegador. Las pruebas administrativas de fixtures no son el flujo de autenticación de la tienda.')
 b.h('13. Construir Angular desde una carpeta vacía')
 b.p('Crea clients/garritas-frontend. Para reproducir exactamente esta versión pega package.json, package-lock.json, angular.json y tsconfig*.json del ZIP, luego npm ci. Eso evita diferencias de opciones de Angular CLI al generar un proyecto nuevo con otra versión. Como alternativa didáctica ng new puede generar el esqueleto, pero reemplaza los archivos por los del catálogo antes de comparar resultados.')
 b.code('cd clients/garritas-frontend\n# Copia manifiestos, public/ y src/ del catálogo/ZIP.\nnpm ci\nnpm test\nnpm run build\nnpm start')
 parts=[('Arranque','src/main.ts inicia App con app.config.ts. provideAppInitializer prepara Auth; Auth primero carga Config. HttpClient usa authInterceptor. El orden evita peticiones antes de conocer las URLs.'),('Configuración runtime','public/config.dev.json apunta al Gateway localhost:18080/api/v1 y Keycloak localhost:18180. config.json usa /api/v1 para el proxy de producción. Nginx/Docker se configura aparte; un build estático no expone mágicamente un backend.'),('Sesión','core/auth.ts inicializa keycloak-js, signals loggedIn/name/admin, renovación y logout. interceptor.ts solo adjunta token para la URL de API propia; no se lo envía a cualquier dominio.'),('Contratos API','core/api.ts define catálogo/ventas/pagos; core/domain-api.ts define tipos y operaciones genéricas del resto de dominios. No se usan arrays locales como sustituto de persistencia.'),('Carrito','features/cart/cart-store.ts mantiene selección, cantidades y sede; computed calcula totales/validez. CartPanel emite acciones y se conecta con App. La clave de reintento mantiene identidad de la solicitud.'),('Vistas','Pega cada component.ts y su component.html de sedes, bienestar, cuenta, citas, envíos, pagos y admin. Cada standalone importa los módulos/directivas que realmente usa y recibe la sesión/API por inyección.'),('Presentación','Pega styles.css y app.html. Hay menú lateral, tarjetas, formularios y tablas adaptables. Las condiciones admin evitan mostrar acciones impropias; la autorización efectiva sigue en backend.'),('Prueba integrada','Registra el cliente y completa perfil/mascota; selecciona sede, compra, espera pago y solicita envío. En otro login ADMIN confirma la cita y entrega el envío. Verifica propiedad usando un segundo cliente.')]
 for a,c in parts:b.h(a,2);b.p(c)
 b.h('14. Añadir observabilidad, automatización y documentación')
 b.p('Pega obs/ con Prometheus, Loki, Promtail y provisionamiento Grafana. DEV usa host.docker.internal para procesos Java y red compartida con Keycloak para métricas internas. observability.sh prepara permisos de archivos públicos y espera health. No confundir puerto publicado del host con el interno de un contenedor.')
 b.p('Pega uso-rapido/scripts y garritas.ps1; ambos conocen la nueva estructura. Pega el reactor en uso-rapido/pom.xml y la alternativa Docker en uso-rapido/docker. El ejemplo Python está aislado de la Saga real. Crea .github/workflows/ci.yml para build Java/Angular y pruebas frontend; eso no reemplaza las pruebas distribuidas DEV.')
 b.p('Para documentación MkDocs crea mkdocs.yml, docs y overrides. Este generador de PDF es una herramienta documental posterior y no es dependencia de la tienda. Los PDFs se regeneran desde fuentes y evidencia de revisión, no desde capturas de texto manualmente pegadas.')
 b.h('15. Puntos de control para saber si vas bien')
 b.table(['Etapa','Comprobación','Si falla'],[('POM/común','Maven compila y resuelve garritas-distributed','Revisar artifactId, rutas ../ y JDK21'),('Infraestructura','Config health y consola Eureka','Revisar cwd/config-repo y puertos'),('Datos','Flyway termina, JPA valida','Revisar base, permisos y todas las V'),('REST','GET catálogo/sedes por Gateway','Revisar route, discovery y servicio'),('Seguridad','ADMIN escribe; CLIENTE recibe 403','Revisar realm roles y SecurityConfiguration'),('Saga','PAGADA y stock correcto; rechazo compensa','Revisar outbox, grupos, DLT y estados'),('M:N','Especialidad compartida y sin duplicados','Revisar JoinTable, PK y @EntityGraph'),('Angular','11 tests y build; recorrido real','Revisar Config/Auth/interceptor y API'),('Operación','Status --observability todo OK','Revisar health, redes y logs')],[80,220,209])
 b.h('16. Catálogo de archivos: instrucciones para pegar',new=True)
 b.p('A continuación está el contenido de cada archivo de código/configuración seleccionado. Respeta mayúsculas, extensión y ruta. Una ficha constituye un archivo completo; no la pegues al final de otro. En el IDE marca src/main/java y src/test/java según la estructura Maven, no cambies los paquetes para corregir una carpeta mal creada.')
 groups=[('Base y reactor',[p for p in CODE_FILES if '/' not in p or p=='uso-rapido/pom.xml']),('Soporte común',[p for p in CODE_FILES if p.startswith('infra/garritas-common/')]),('Infraestructura y configuración',[p for p in CODE_FILES if p.startswith('infra/') and not p.startswith('infra/garritas-common/')]),('Kafka y Keycloak',[p for p in CODE_FILES if p.startswith(('kafka/','keycloak/'))])]
 for domain,_,_,_ in DOMAINS:groups.append(('Servicio '+domain,[p for p in CODE_FILES if p.startswith('services/garritas-'+domain+'-ms/')]))
 groups.extend([('Cliente Angular',[p for p in CODE_FILES if p.startswith('clients/')]),('Observabilidad',[p for p in CODE_FILES if p.startswith('obs/')]),('Automatización, ejemplo y Docker integrado',[p for p in CODE_FILES if p.startswith('uso-rapido/') and p!='uso-rapido/pom.xml']),('CI y documentación',[p for p in CODE_FILES if p.startswith(('.github/','docs/','overrides/'))])])
 printed=[]
 for label,paths in groups:
  if not paths:continue
  b.h('Archivos · '+label,2,new=True)
  for p in sorted(paths):b.file(p);printed.append(p)
 missing=set(CODE_FILES)-set(printed)
 if missing:raise RuntimeError('Archivos sin capítulo: '+repr(missing))
 b.h('17. Cerrar la reconstrucción y guardar tu trabajo',new=True)
 b.p('Con todos los archivos creados, instala dependencias, compila y ejecuta el Manual 1. No esperes una compra funcional antes de terminar los tres participantes de la Saga y sus migraciones. Después de verificar, guarda tu propio commit; no subas .env, volúmenes, targets, node_modules, logs ni credenciales personales.')
 b.code('git add .\ngit status --short\ngit commit -m "Construye Garritas Store con infraestructura y dominios integrados"')
 b.p('El ZIP de esta edición se extrajo en una carpeta nueva: se empaquetaron correctamente los trece módulos Maven y se ejecutaron npm ci y npm run build sobre ese árbol reconstruido. Esto verifica que las fuentes adjuntas compilan sin reutilizar los targets ni node_modules del checkout original; las descargas/cachés de dependencias sí pertenecen al entorno de desarrollo.')
 b.p('El archivo MANIFIESTO-CODIGO.json permite comparar SHA-256 por ruta para localizar errores de copia. El ZIP incluye textos auxiliares y lockfiles no impresos; no contiene una instalación binaria portable ni las bases con datos. Los ejemplos se crean mediante Flyway y la importación Keycloak al primer inicio.')
 b.save()

ANNOTATIONS={
'Autowired':'Solicita inyección de un bean compatible; en pruebas permite obtener dependencias del contexto. Con un único constructor Spring puede inyectar sin escribirla.',
'Min':'Exige un número mayor o igual al límite declarado; se usa en campos como stock, edad o cantidades según DTO.',
'Max':'Exige un número menor o igual al límite declarado; acota valores que el dominio acepta.',
'Pattern':'Exige que el texto cumpla la expresión regular declarada; por ejemplo limita valores textuales permitidos, además de no nulidad si corresponde.',
'SpringBootApplication':'Agrupa configuración, auto-configuración y escaneo del paquete de la aplicación. No descubre automáticamente paquetes hermanos como common sin importarlos.',
'EnableConfigServer':'Activa endpoints de Spring Cloud Config Server que sirven propiedades por aplicación/perfil.',
'EnableEurekaServer':'Activa el registro de servicios Eureka en el módulo de infraestructura.',
'EnableFeignClients':'Escanea interfaces @FeignClient para crear proxies HTTP declarativos.',
'Import':'Registra clases de configuración externas al escaneo; así cada módulo incorpora seguridad/comunicación común explícitamente.',
'Configuration':'Declara una fuente de definiciones de beans; proxyBeanMethods=false evita proxies innecesarios de métodos de configuración.',
'Bean':'El valor retornado se registra y administra en el contenedor de Spring; sus dependencias llegan como parámetros/inyección.',
'Component':'Registra un componente detectado por el escaneo, como consumidores y mappers.',
'Service':'Especializa Component para lógica de aplicación. El rol por sí solo no crea una transacción.',
'RestController':'Expone métodos como handlers HTTP con serialización de respuesta; combina Controller y ResponseBody.',
'RequestMapping':'Declara prefijo/ruta y, si se especifica, método HTTP. Los mappings de método se combinan con el de clase.',
'GetMapping':'Consulta GET; aquí no debe inventar cambios de negocio.',
'PostMapping':'Operación POST: creación o transición explícita según ruta.',
'PutMapping':'Actualización PUT del recurso definido por el endpoint.',
'DeleteMapping':'Baja DELETE; en productos, sedes y profesionales puede ser lógica, no borrado SQL.',
'PathVariable':'Toma un segmento de la URL y lo convierte al tipo Java declarado.',
'RequestBody':'Deserializa el JSON recibido a DTO; la validación se activa con Valid.',
'RequestHeader':'Obtiene una cabecera, por ejemplo Idempotency-Key en Venta.',
'ResponseStatus':'Declara el código de respuesta del handler cuando se completa sin excepción.',
'Valid':'Activa validación de campos/anidados del DTO antes de ejecutar la operación.',
'NotNull':'Exige presencia de un valor; no sustituye Positive ni NotBlank.',
'NotBlank':'Exige texto no nulo y con contenido distinto de espacios.',
'NotEmpty':'Exige colección/cadena no vacía.',
'Positive':'Exige número estrictamente mayor que cero; se usa en ids/cantidades.',
'PositiveOrZero':'Permite cero pero no negativos, por ejemplo stock/edad cuando se declara.',
'Size':'Limita longitud o cantidad de elementos del campo anotado.',
'Email':'Valida formato básico de correo; no acredita que exista ni que pertenezca al usuario.',
'Future':'Exige una fecha posterior al instante de validación; Citas además valida el bloque horario.',
'DecimalMin':'Límite inferior decimal, útil para importes. El redondeo/escala se trata aparte.',
'Entity':'Entidad persistente JPA; se asocia con tabla, pero aquí Flyway administra el DDL.',
'Table':'Indica nombre de tabla y restricciones de mapeo si se declaran.',
'Id':'Campo identificador JPA.',
'GeneratedValue':'La base/proveedor genera el id según estrategia declarada; no fabricar ids desde Angular.',
'Column':'Define nombre, nulabilidad, longitud/precisión y otras características del mapeo.',
'ManyToOne':'Muchas filas de la entidad apuntan a una fila relacionada dentro de la misma base.',
'OneToMany':'Una entidad tiene varias filas relacionadas; mappedBy marca el lado dueño inverso.',
'ManyToMany':'Relaciona conjuntos mediante una tabla de unión; usado en Bienestar.',
'JoinColumn':'Declara la columna FK del lado propietario de la relación local.',
'JoinTable':'Declara la tabla de asociación y columnas de enlace para M:N.',
'Enumerated':'Guarda enum como nombre cuando usa STRING; evita depender del ordinal.',
'Version':'Bloqueo optimista: detecta que otra transacción modificó la fila. En Producto evita sobrescribir inventario con una edición vieja.',
'Transactional':'Demarca la transacción local del datasource del servicio. readOnly es orientación de lectura, no un permiso de seguridad. Llamadas internas al mismo objeto no crean automáticamente otro proxy transaccional.',
'Lock':'Solicita el modo de bloqueo JPA de la consulta anotada.',
'EntityGraph':'Carga relaciones declaradas para una lectura concreta; evita depender de serializar relaciones lazy fuera de la transacción.',
'Query':'Define SQL/JPQL explícito en repositorio según nativeQuery.',
'KafkaListener':'Registra un consumidor sobre el topic declarado y el grupo del perfil. Su método debe filtrar eventos, validar y deduplicar antes de aplicar negocio.',
'Scheduled':'Ejecuta un método periódicamente; publish reintenta eventos pendientes del outbox.',
'EnableScheduling':'Activa ejecución de Scheduled en el contexto.',
'Value':'Inyecta una propiedad/expresión con valor por defecto si se declara.',
'RequiredArgsConstructor':'Lombok genera constructor para final/no nulos. Spring inyecta por ese constructor; no es un constructor escrito manualmente.',
'Data':'Lombok genera accesores, equals/hashCode y toString según su semántica; no valida negocio.',
'Getter':'Lombok genera getters.',
'Setter':'Lombok genera setters; un setter no equivale a transición de negocio autorizada.',
'Builder':'Lombok genera un builder para construir objetos; no reemplaza invariantes del servicio.',
'NoArgsConstructor':'Genera constructor sin argumentos, habitual para JPA.',
'AllArgsConstructor':'Genera constructor con todos los campos correspondientes.',
'JsonIgnoreProperties':'Permite ignorar propiedades JSON extra cuando se configura ignoreUnknown; Reference usa esta tolerancia.',
'RestControllerAdvice':'Centraliza traducción de excepciones de controladores REST.',
'ExceptionHandler':'Declara qué tipo de excepción maneja un método advice.',
'FeignClient':'Crea proxy HTTP por servicio descubierto. ProductoClient consulta Catálogo por nombre.',
'SpringBootTest':'Carga contexto Spring en pruebas; requiere las dependencias configuradas del entorno.',
'Test':'Marca un caso de prueba ejecutable por JUnit.',
'BeforeEach':'Prepara estado antes de cada caso de prueba.',
'AfterEach':'Limpia estado después de cada caso de prueba.',
'Order':'Define precedencia cuando el framework aplica orden; revisa el contexto exacto en el código.',
'Override':'El compilador comprueba que el método implementa o sobreescribe una firma heredada.',
'SuppressWarnings':'Inhibe advertencias específicas del compilador; no cambia reglas de negocio.',
}
METHODS={'listar':'Obtiene una colección; comprueba el filtro por propietario/rol y el orden del código.','obtener':'Busca un recurso por id y lo convierte al contrato de salida; los servicios propietarios también autorizan su acceso.','crear':'Valida y construye el recurso, persiste localmente y devuelve su DTO; los efectos remotos dependen de la implementación.','actualizar':'Busca el existente y reemplaza campos permitidos dentro del flujo del servicio.','eliminar':'Aplica la baja definida: lógica o física según clase; no asumir que DELETE siempre borra filas.','toResponse':'Proyecta campos de entidad a DTO de salida.','toEntity':'Convierte entrada a entidad y asigna los valores iniciales declarados.','consume':'Punto de entrada Kafka: deserializa contrato, filtra tipo, deduplica y ejecuta el efecto local.','reservar':'Valida/bloquea todos los productos antes de aplicar el descuento atómico.','liberar':'Restaura cantidades desde la reserva original solo cuando sigue reservada.','owned':'Busca el recurso y compara propietario con sub, permitiendo auditoría ADMIN.','main':'Arranca el contexto de la aplicación; no es el bucle de negocio.','confirmar':'Pide transición PROGRAMADA → CONFIRMADA; protegida para ADMIN.','atender':'Pide transición CONFIRMADA → ATENDIDA; protegida para ADMIN.','cancelar':'Aplica la cancelación permitida por el estado y la propiedad de este dominio.','porVenta':'Busca pago por id de venta y comprueba propietario; puede no existir aún en una Saga pendiente.','me':'Devuelve el perfil vinculado al sub autenticado.','guardarMe':'Crea/actualiza perfil propio sin aceptar otro sub en el cuerpo.','miUsuario':'Resuelve el perfil local del autenticado; 404 pide completar perfil.','requireOwner':'Rechaza el acceso si no es ADMIN y el sub no coincide.','claim':'Registra el eventId dentro de la misma transacción; false significa ya procesado.','append':'Guarda evento en outbox dentro de una transacción activa.','publish':'Envía pendientes y marca publicado después de ACK, dejando pendientes ante error.','validate':'Verifica invariantes del contrato de evento.','next':'Deriva el siguiente evento conservando contexto de venta y creando identidad de evento.','transition':'Comprueba estado anterior esperado antes de asignar el siguiente.','buscarOFallar':'Busca o lanza excepción; donde procede también exige propiedad.','marcarEnTransito':'Exige pendiente, cambia estado y registra fecha de envío.','marcarEntregado':'Exige tránsito antes de marcar entregado.','subject':'Lee el identificador estable del autenticado.','admin':'Comprueba la autoridad ROLE_ADMIN.','get':'Ejecuta la lectura HTTP con la configuración/identidad del cliente declarado.'}

def technical():
 b=Book('03-Arquitectura-clases-y-conexiones.pdf','Manual 3 · Entender todo Garritas','Tecnologías, inicios de clases, anotaciones, responsabilidades, diagramas y recorrido de datos del código real.')
 b.h('1. Cómo leer el sistema')
 b.p('Este documento explica los componentes que existen en el commit '+REV+' y la corrección de carga de perfil incluida en la edición. No es una lista de tecnologías posibles: distingue código implementado, mecanismos del framework y límites. El Manual 2 contiene el código completo por archivo; aquí se explica el porqué y la conexión, con fichas de cada fuente Java y TypeScript.')
 b.p('Lee primero arquitectura y flujos; después la sintaxis de clases/anotaciones y al final las fichas. Una clase no se entiende solo por su nombre: importa quién la crea, qué dependencias inyecta, qué datos recibe, qué transacción abre y quién consume su resultado.')
 b.h('2. Mapa de responsabilidades y conexiones')
 b.image('arquitectura','Arquitectura de ejecución. La flecha a ocho bases representa conexiones independientes, no una base compartida.')
 b.table(['Pieza','Para qué sirve','Cómo aparece en Garritas'],[('Angular','Interfaz ejecutada en navegador','Signals, formularios, catálogo, carrito y pantallas de los ocho dominios'),('Gateway MVC','Punto HTTP de entrada','Rutas Path a lb://, JWT, CORS, correlación'),('Config Server','Propiedades centralizadas','config-repo por nombre y perfil DEV/PROD'),('Eureka','Descubrimiento de instancias','Registro con nombre; LoadBalancer y Feign resuelven destino'),('Servicios Spring','Reglas y API por dominio','Controller → Service → Repository/Mapper'),('PostgreSQL','Persistencia y restricciones','Una base por dominio; no joins entre bases'),('Kafka','Eventos asíncronos de compra','Saga de Venta/Catálogo/Pago, tres grupos'),('Keycloak','Identidad y roles','OIDC, JWT, CLIENTE/ADMIN, PKCE'),('Observabilidad','Estado y diagnóstico','Actuator/Micrometer → Prometheus; logs → Loki; Grafana')],[83,155,271])
 b.p('Separación de dominio: Catálogo es autoridad de productos/precios/stock; Venta registra compra; Pago resuelve la simulación; Institución posee sedes; Usuario posee perfil/mascotas; Bienestar posee especialistas/especialidades; Citas posee agenda; Envío posee seguimiento. Copiar el nombre de una sede en una cita es un snapshot descriptivo, no trasladar la propiedad de la sede.')
 b.h('3. Tecnologías: qué hacen y por qué se usan aquí')
 tech=[('Java 21 y JVM','Java compila fuentes .java a bytecode; la JVM ejecuta JAR. Records expresan contratos inmutables, enums limitan estados, BigDecimal evita errores binarios en dinero e Instant representa instantes UTC. JDK incluye javac; JRE solo no basta para compilar.'),('Spring Boot 4.0.8','Prepara contexto, servidor web embebido, auto-configuración y empaquetado ejecutable. Application no instancia manualmente cada controlador; Spring crea beans y conecta dependencias. Las propiedades importadas desde Config gobiernan puertos/datasources.'),('Spring Cloud 2025.1.3','BOM que coordina versiones compatibles de Config, Eureka, Gateway MVC, OpenFeign, LoadBalancer y Circuit Breaker. Un BOM administra versiones; no arranca servicios por sí mismo.'),('Maven y Wrapper','POM declara dependencias/plugins; Wrapper obtiene Maven de versión fijada. El reactor compila los módulos en orden. install publica un artefacto en repositorio local; package produce JAR; verify incluye pruebas y comprobaciones configuradas.'),('Lombok','Procesador de anotaciones que genera getters, constructores y builders durante compilación. Si el IDE muestra métodos rojos pero Maven compila, revisa soporte de anotaciones. No añade seguridad ni validación de negocio.'),('Spring MVC y REST','Controladores reciben HTTP y convierten JSON/DTO mediante Jackson. Spring Security filtra antes del handler. Los códigos HTTP son parte del contrato; REST no significa que cualquier entidad deba exponer todas las operaciones CRUD.'),('Jackson 3','tools.jackson.databind.ObjectMapper serializa SagaEvent y lee JSON de eventos. No mezcles imports com.fasterxml de otro ObjectMapper sin revisar la versión y auto-configuración. Reference ignora campos remotos que no necesita.'),('Bean Validation','Jakarta valida Request con Valid y restricciones. La forma de datos se controla antes del servicio; reglas como venta pagada, propiedad o especialidad activa requieren además lógica y consultas.'),('JPA/Hibernate y Spring Data','Entidades mapean tablas; repositorios generan persistencia. Relaciones locales usan FKs. Mapper separa API y entidad. SQL directo JDBC se usa donde los bloqueos/idempotencia/Saga necesitan control explícito.'),('PostgreSQL 16','Soporta transacciones ACID, restricciones, índices parciales, locks de filas y advisory lock transaccional. Se usa una base separada por dominio para impedir acoplamiento por tablas.'),('Flyway','Versiona DDL y datos iniciales. V se aplica una vez y guarda checksum; R se repite al cambiar. JPA ddl-auto validate comprueba el esquema, no sustituye migraciones. Los datos de demo se habilitan aparte en DEV.'),('Eureka y LoadBalancer','Eureka mantiene instancias; un cliente descubre y elige destino. lb:// del Gateway y el nombre Feign evitan URLs de negocio fijas. ServiceClient elige explícitamente una instancia para HTTP con JWT propagado.'),('OpenFeign y Circuit Breaker','ProductoClient expresa un GET declarativo. CatalogoConsulta lo envuelve en breaker; disponibilidad no se simula con precios por defecto. Timeouts acotan la espera; el breaker limita llamadas a una dependencia fallando, no repara su base.'),('Kafka 4.3.1 en KRaft','Broker distribuye un log particionado sin ZooKeeper en este Compose. El controlador gestiona metadatos. La clave ventaId agrupa el orden por partición; diferentes ventas pueden procesarse en paralelo. Una réplica no da tolerancia a pérdida del nodo.'),('Spring Kafka','KafkaTemplate publica; KafkaListener consume; group-id separa la lectura por servicio. Tres grupos leen el topic común y filtran tipos. Reintentos y DLT tratan errores técnicos; Inbox/uniqueness protegen efectos de negocio.'),('Keycloak 26.8.0/OIDC/OAuth2','Keycloak autentica y emite tokens. OIDC agrega identidad sobre OAuth2. Authorization Code + PKCE es adecuado para cliente público Angular. JWT firma no cifra: no se introducen secretos de negocio en sus claims.'),('Spring Security Resource Server','Valida token en Gateway y cada servicio. Convierte roles del realm en autoridades Spring y exige propiedad en servicio. No depende de que el usuario use la UI oficial.'),('Angular 22 y TypeScript','Componentes standalone y plantillas describen UI. TypeScript tipa contratos en compilación; no valida automáticamente el JSON remoto. Signals son estado reactivo, computed deriva valores y effect sincroniza efectos como persistencia.'),('RxJS y HttpClient','HTTP devuelve Observables. subscribe consume respuestas/errores; App usa timer/exhaustMap para polling sin solapar solicitudes. takeUntilDestroyed libera suscripciones al destruir componente.'),('keycloak-js','SDK gestiona redirecciones, PKCE y renovación. Tokens en memoria; al volver a cargar se recupera sesión mediante Keycloak, no desde localStorage.'),('Node24/npm/Angular CLI','Node ejecuta herramientas de desarrollo, no la lógica Java. npm ci instala versiones del lockfile de forma reproducible. Build produce estáticos; ng serve es servidor de desarrollo.'),('Docker y Compose','Imagen empaqueta proceso y dependencias; contenedor es su ejecución; volumen conserva datos; red resuelve nombres. Compose describe el conjunto y healthcheck. DEV usa contenedores de dependencias, no los ocho JAR.'),('Nginx','En la alternativa frontend de producción sirve estáticos y proxifica /api/v1. El config.json relativo evita CORS adicional en ese origen. No es el servidor usado por npm start.'),('Actuator/Micrometer','Expone health y métricas de aplicaciones Java. Liveness pregunta por vida del proceso; readiness por disposición declarada. La configuración de Garritas no equivale a una prueba automática de todas las dependencias.'),('Prometheus/Grafana','Prometheus recoge series métricas; Grafana consulta y presenta paneles. Datos fuente y dashboards se aprovisionan para no configurarlos manualmente en cada instalación.'),('Loki/Promtail/SLF4J/Logback/MDC','Logback escribe logs, MDC añade correlación. Promtail lee archivos y envía a Loki. Loki almacena/consulta logs; Grafana Explore permite buscar. No se ha añadido tracing de spans OpenTelemetry.'),('JUnit/SpringBootTest/Vitest/Playwright','JUnit comprueba contexto/contrato/integración; Vitest comprueba frontend; Playwright navega con login real y prueba varios dominios/API. Cada nivel detecta fallos distintos: 200 en health no demuestra permisos ni stock.'),('Python y kafka-python','Las herramientas de smoke/status y el ejemplo productor/consumidor usan Python. El ejemplo usa topic aislado, no es un noveno microservicio de negocio ni reemplaza Kafka de Spring.'),('Git/GitHub Actions','Git conserva fuentes/commits/ramas; GitHub aloja el remoto. El workflow compila y prueba frontend. Subir código no publica automáticamente una web accesible en Internet.'),('MkDocs/Material y documentación PDF','MkDocs compila documentación navegable. Los PDFs de esta edición se generan con ReportLab y diagramas Graphviz; esas herramientas documentales no son dependencias de ejecución de la tienda.')]
 for title,txt in tech:b.h(title,2);b.p(txt)
 b.h('4. Cómo leer el inicio de una clase Java',new=True)
 b.code('package pe.edu.upeu.garritas.institucion.service;\n\nimport lombok.RequiredArgsConstructor;\nimport org.springframework.stereotype.Service;\n\n@Service\n@RequiredArgsConstructor\npublic class SedeService {\n  private final SedeRepository sedeRepository;\n  private final SedeMapper sedeMapper;\n  // Métodos completos: ver archivo del Manual 2.\n}')
 b.p('package identifica el espacio de nombres y debe coincidir con la ruta bajo src/main/java. import permite usar un tipo sin escribir su nombre completo; no descarga dependencias: eso es Maven. @Service registra lógica de aplicación. @RequiredArgsConstructor genera constructor para campos final; Spring lo usa para inyectar repositorio y mapper. public permite acceso fuera del paquete; final impide reasignar la referencia, no vuelve inmutable todo el objeto.')
 b.p('Una interfaz declara un contrato. ProductoRepository extends JpaRepository<Producto,Long> hereda operaciones que Spring implementa. Un record define componentes y métodos de acceso como id(), no getId(). Un enum define constantes finitas. static pertenece a la clase; private limita acceso interno. throws/throw expresan fallos, no respuestas HTTP hasta que un manejador los traduce.')
 b.p('DTO es un objeto de transferencia: Request describe entrada y Response salida. Una entidad contiene mapeo persistente y puede tener relaciones lazy; devolverla directamente acoplaría JSON y base. Mapper transforma, Service decide y Repository persiste. El controlador maneja HTTP y no debería realizar SQL de reserva de inventario.')
 b.image('clases','Relaciones UML simplificadas y reales de Catálogo. Las flechas indican uso/inyección, no herencia en todos los casos.')
 b.h('5. Anotaciones usadas: referencia razonada')
 found=set()
 for p in TRACKED:
  if p.endswith('.java'):found.update(re.findall(r'@(?:[a-z_][\w]*\.)*([A-Z]\w*)',(ROOT/p).read_text()))
 for name in sorted(found):b.h('@'+name,3);b.p(ANNOTATIONS.get(name,'Anotación presente en el código. Su efecto depende de la declaración y de los parámetros reproducidos en el Manual 2; consulta el import del archivo para distinguir anotaciones de Spring, JPA, validación y pruebas. No debe asumirse que añade autorización o transacción por su nombre.'))
 b.h('6. Modelo de datos y límites de cada base',new=True)
 b.p('Las relaciones con FK solo existen dentro de una misma base. Venta.detalle pertenece a Venta, Producto.categoria a Catálogo, Mascota.usuario a Usuario y Profesional.especialidades a Bienestar. Los ids de sede/profesional/venta vistos desde otro servicio son referencias remotas verificadas por HTTP; no hay una gran transacción que englobe las ocho bases.')
 for domain,port,db,resp in DOMAINS:
  b.h(domain.capitalize()+' · HTTP '+str(port)+' / PG '+str(db),2);b.p(resp+'.')
  migrations=sorted(p for p in TRACKED if p.startswith('services/garritas-'+domain+'-ms/src/main/resources/db/') and p.endswith('.sql'))
  for p in migrations:
   s=(ROOT/p).read_text();tables=re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w"]+)',s,re.I)
   b.bullet(Path(p).name+' · '+('crea '+', '.join(tables) if tables else 'evoluciona estructura/restricciones o añade datos de demostración')+'. Ruta: `'+p+'`.')
 b.image('muchos-a-muchos','M:N Bienestar: dos FKs locales y referencia de sede remota.')
 b.p('El índice parcial de Citas solo considera PROGRAMADA/CONFIRMADA. Eso permite reusar un bloque tras cancelar, pero no permite dos reservas activas simultáneas. Envío tiene id_venta único incluso si se canceló: la versión actual no crea un segundo envío para esa misma venta. El perfil usuario admite subject nulo para registros administrativos históricos; para operar como dueño se usa el sub vinculado.')
 b.h('7. Transacciones, concurrencia y dinero')
 for t in ['@Transactional confirma o revierte cambios locales sobre el datasource del módulo. No hace que una llamada HTTP a otra base participe de la misma transacción. Por eso la compra usa eventos y compensación.','BigDecimal calcula importes y subtotal con precisión decimal. El servidor obtiene el precio vigente de Catálogo y persiste el precio unitario de la compra; no acepta el precio enviado por el carrito como autoridad.','Catálogo bloquea filas FOR UPDATE en orden de ids para reducir deadlocks y validar todo antes de descontar. Si una línea falla, no descuenta parcialmente el conjunto.','Producto @Version detecta ediciones obsoletas; la reserva JDBC también incrementa version para no perder cambios frente a una actualización JPA.','Venta usa advisory lock transaccional por propietario+Idempotency-Key, además de unicidad persistente. Una misma clave reintenta la misma operación; no es un permiso para cambiar su contenido.','Índices únicos y FKs siguen protegiendo aunque dos peticiones pasen simultáneamente una validación previa. El error de integridad se traduce en conflicto, no se ignora.']:b.bullet(t)
 b.h('8. Compra completa: quién llama a quién')
 b.image('saga','Estados/evidencias de aprobación y rechazo. Las flechas asíncronas pasan por Kafka.')
 b.p('1. CartStore prepara sedeId, metodoPago y detalles de ids/cantidades. Api.crearVenta añade clave UUID. authInterceptor añade Bearer y X-Trace-ID solo a la API propia. Gateway autentica y enruta por Eureka. VentaController convierte JSON, valida y recibe la clave.')
 b.p('2. VentaService determina comprador por sub, comprueba idempotencia, valida sede por ServiceClient y consulta productos por Feign/Circuit Breaker. Calcula totales, guarda venta/detalles y outbox en una transacción. Devuelve la venta inicialmente pendiente; Angular comienza/continúa polling.')
 b.p('3. Outbox publica venta.creada. InventarioEvents deduplica eventId y id_venta, reserva todas las líneas y publica resultado local. VentaEvents toma inventario.reservado y pasa a pendiente de pago; PagoEvents crea una simulación única y publica resultado.')
 b.p('4. Si aprueba, VentaEvents marca PAGADA. Si rechaza, marca COMPENSANDO y Catálogo devuelve las cantidades originales antes de publicar inventario.liberado. Solo entonces la venta se cancela. App actualiza catálogo al terminar pendientes, por lo que el stock visible se refresca.')
 b.p('No hay 2PC, transacción distribuida global ni garantía exactamente una vez. La entrega Kafka es al menos una vez; el procesamiento idempotente combina Inbox y claves de negocio. Un ACK recibido seguido de caída antes de marcar publicado produce reenvío esperado.')
 b.h('9. Fallos, reintentos y límites de resiliencia')
 b.table(['Situación','Mecanismo real','Límite'],[('Kafka caído','Outbox conserva published_at nulo y reintenta','La orden permanece pendiente; no se inventa pago'),('Consumidor recibe duplicado','Inbox eventId + unicidad por venta','La retención/purga debe respetar posibilidad de reenvío'),('Consumidor falla repetidamente','Nueve reintentos y DLT','DLT requiere análisis; no hay recuperación de negocio automática universal'),('Catálogo HTTP falla','Timeout y Circuit Breaker; 503','No hay precio fallback ficticio'),('Cita simultánea','Índice único parcial en PostgreSQL','Solo se certifica el bloque reservado, no un planificador complejo'),('Cambio de estado terminal','Validación de estado y rol','No hay Saga de devolución/reembolso posterior implementada'),('Nodo Kafka perdido','Persistencia en volumen, una réplica','No es clúster HA; pérdida del disco no se cubre')],[130,190,189])
 b.h('10. Seguridad, propiedad y CORS')
 b.image('identidad','Autenticación del navegador y autorización efectiva del servicio.')
 b.p('Autenticación responde quién es la persona; rol responde qué tipo de acciones puede solicitar; propiedad responde sobre qué registros. CLIENTE autenticado no puede leer la mascota/venta/envío de otro sub. ADMIN puede gestionar y auditar según las rutas. Nunca se confía en un idCliente escrito en el JSON para establecer identidad.')
 b.p('Gateway y servicios validan firma por JWKS, issuer del realm y aud garritas-api. realm_access.roles se convierte a ROLE_ADMIN/ROLE_CLIENTE. Las rutas públicas de productos, categorías, sedes y especialistas permiten consulta; la escritura queda ADMIN. Confirmación/atención de citas y tránsito/entrega de envíos son reglas específicas antes de patrones más amplios.')
 b.p('CORS es política del navegador para permitir solicitudes desde otro origen; no autentica ni bloquea llamadas curl. Se permiten encabezados Authorization, Idempotency-Key y X-Trace-ID para el origen configurado. PKCE protege el intercambio de código del cliente público; no elimina la necesidad de TLS en una publicación real.')
 b.h('11. Citas y envíos conectados al resto')
 b.image('citas-envios','Comprobaciones de negocio antes de guardar los recursos dependientes.')
 b.p('Citas consulta /usuarios/me/mascotas/{id} con el JWT original: la comprobación de dueño la realiza Usuario. Consulta sede y profesional, exige activos y sede compatible si el profesional tiene sede asignada. Guarda los nombres para mostrar historial y su propia referencia/fecha. No escribe la base de Usuario o Bienestar.')
 b.p('Envío consulta /ventas/{id} con identidad propagada; Venta filtra propietario y Envío lo verifica además. PAGADA es requisito y id_venta único. El cliente solo solicita y consulta; el administrador opera tránsito y entrega. No hay geolocalización de transportista ni integración con courier real en esta versión.')
 b.h('12. Angular: desde el arranque a los formularios')
 b.p('main.ts llama bootstrapApplication(App, appConfig). El inicializador espera Auth.init; Auth espera Config.load. Después de conocer apiUrl/keycloakUrl, Keycloak detecta sesión y actualiza signals. El componente raíz puede decidir menú y cargar catálogo/sedes sin manejar contraseñas.')
 b.p('Signals guardan datos mutables de UI; computed recalcula totales y validez; effect persiste navegación/carrito cuando cambian sus dependencias. RxJS modela HTTP/polling: exhaustMap evita solapar refrescos de pedidos; catchError comunica fallo y takeUntilDestroyed cancela al destruir App. Las interfaces TS documentan forma de datos, no verifican permisos en runtime.')
 b.p('Feedback centraliza error/message/busy para formularios. Cada pantalla usa DomainApi o Api y actualiza su listado después de guardar. Cuenta espera terminar la carga del perfil antes de mostrar inputs: evita que una respuesta tardía reemplace ediciones. La prueba de regresión cubre perfil existente y ausencia 404.')
 b.p('El carrito usa localStorage para contenido no sensible. La navegación usa sessionStorage. Los tokens se mantienen en memoria de keycloak-js. Un badge de rol o un botón oculto son presentación; los filtros Spring y CurrentUser son la barrera efectiva.')
 b.h('13. Observabilidad y correlación')
 b.image('observabilidad','Métricas y logs siguen circuitos diferentes pero se leen desde Grafana.')
 b.p('CorrelationIdFilter añade un identificador al MDC. Feign propaga X-Trace-ID; ServiceClient reenvía identidad y correlación; SagaEvent conserva traceId. Los consumidores vuelven a ponerlo en MDC durante procesamiento. Así una búsqueda de logs puede seguir una operación, aunque no existen spans OpenTelemetry ni una traza temporal completa automática.')
 b.p('Actuator expone readiness/liveness y Prometheus. El grupo readiness configurado no incluye por sí mismo cada remoto: una JVM UP puede devolver 503 de negocio si otra dependencia cae. La verificación real usa catálogo por Gateway, navegador, estado final de venta, stock y permisos. Prometheus no demuestra por sí solo corrección del negocio.')
 b.h('14. Fichas de todas las clases Java',new=True)
 b.p('Cada ficha reproduce package/imports/anotaciones y declaración inicial de la clase real; después lista dependencias y firmas detectadas. El cuerpo completo está en el mismo archivo del Manual 2/ZIP. No se imprime aquí por segunda vez todo el código. Los accesores/constructores generados por Lombok no aparecen como métodos escritos.')
 java=sorted(p for p in TRACKED if p.endswith('.java'))
 for p in java:
  s=(ROOT/p).read_text();name=Path(p).stem
  b.h(name+' · '+p.split('/')[1],2);b.p('**Ubicación:** `'+p+'`.');b.p(describe(p))
  match=re.search(r'\b(?:public\s+)?(?:final\s+)?(?:class|interface|record|enum)\s+'+re.escape(name)+r'\b',s)
  if match:
   end=s.find('{',match.end());header=s[:end+1] if end>=0 else s[:match.end()]
   # Para records, el encabezado puede contener la definición completa de sus componentes.
   b.code(header)
  deps=re.findall(r'private\s+final\s+([\w<>, ?\.]+)\s+(\w+)\s*;',s)
  if deps:b.p('**Dependencias inyectadas por constructor:** '+', '.join(t.strip()+' '+n for t,n in deps)+'. El bean que las crea es Spring; no se construye otro repositorio con new en cada petición.')
  annotations=sorted(set(re.findall(r'@(?:[a-z_][\w]*\.)*([A-Z]\w*)',s)))
  b.p('**Anotaciones presentes en el archivo:** '+(', '.join('@'+x for x in annotations) if annotations else 'ninguna')+'. Consulta sus efectos en el capítulo de anotaciones; no todas corresponden al encabezado de clase.')
  signatures=[]
  for m in re.finditer(r'^\s*((?:(?:public|protected|private|static|final|synchronized)\s+)+[\w<>\[\], ?\.]+\s+(\w+)\s*\([^;{}]*\))\s*(?:throws[^{}]+)?\{',s,re.M):
   sig=' '.join(m.group(1).split());method=m.group(2)
   if len(sig)<600:signatures.append((sig,METHODS.get(method,'Operación específica de '+name+'. La firma declara entrada/salida; revisa el cuerpo en el Manual 2 para sus ramas y efectos concretos.')))
  # Métodos abstractos de repositorios/mappers se muestran como contrato, sin inventar implementación.
  if 'interface ' in s:
   contracts=re.findall(r'^\s*([\w<>\[\], ?\.]+\s+\w+\s*\([^;{}]*\))\s*;',s,re.M)
   for sig in contracts:signatures.append((' '.join(sig.split()),'Contrato de interfaz; la implementación proviene del framework o de la clase declarada, según el tipo de interfaz.'))
  if signatures:
   for sig,explanation in signatures:b.bullet('`'+sig+'` · '+explanation)
  elif '/entity/' in p or '/dto/' in p or name in ['Reference','SagaEvent']:
   fields=re.findall(r'^\s*private\s+(?!static)([\w<>\[\], ?\.]+)\s+(\w+)\s*(?:=[^;]*)?;',s,re.M)
   if fields:b.p('**Campos declarados:** '+', '.join(t.strip()+' '+n for t,n in fields)+'. Sus constraints y relaciones están en el código completo.')
   else:b.p('Los componentes del record o las constantes del enum forman su contrato; consulta el listado completo y la explicación de records/enums.')
  else:b.p('La responsabilidad se configura por anotaciones o por métodos con firma repartida en líneas; consulta el archivo completo del Manual 2. No se infiere una operación CRUD que no esté declarada.')
 b.h('15. Fichas del frontend TypeScript',new=True)
 for p in sorted(x for x in TRACKED if x.endswith('.ts') and x.startswith('clients/')):
  s=(ROOT/p).read_text();names=re.findall(r'export\s+class\s+(\w+)',s)
  b.h(Path(p).name,2);b.p('**Ubicación:** `'+p+'`.')
  if names:
   for name in names:b.p('**'+name+':** '+SPECIAL.get(name,describe(p)))
  else:b.p(describe(p))
  # Imports y decorator/cabecera; el resto se explica mediante dependencias/contratos.
  lines=s.splitlines();limit=next((i+1 for i,x in enumerate(lines) if re.search(r'export (?:class|const|function|interface)',x)),min(len(lines),20))
  b.code('\n'.join(lines[:limit]))
  injected=re.findall(r'(\w+)\s*=\s*inject\((\w+)\)',s)
  if injected:b.p('**Inyección:** '+', '.join(n+' ← '+t for n,t in injected)+'.')
  if '.spec.ts' in p:b.p('Fuente de pruebas, no componente de pantalla. Los casos it/test describen el comportamiento que debe mantenerse y los dobles HTTP aíslan las respuestas para controlar la secuencia.')
  else:
   methods=re.findall(r'^\s*(?:private\s+|public\s+|async\s+|readonly\s+)*([a-zA-Z_]\w*)\([^;{}]*\)\s*\{',s,re.M)
   if methods:b.p('**Métodos escritos:** '+', '.join(dict.fromkeys(methods))+'. load/refrescar consulta la API; save/envío usa Feedback; edit prepara modelo del formulario; remove solicita confirmación y baja; las operaciones concretas se leen completas en el Manual 2.')
   interfaces=re.findall(r'export interface (\w+)',s)
   if interfaces:b.p('**Interfaces de contrato:** '+', '.join(interfaces)+'. Son tipos de compilación y desaparecen en el JavaScript emitido; el backend mantiene la validación efectiva.')
 b.h('16. Configuraciones y automatizaciones: cómo encajan',new=True)
 config_groups=[('POM Maven','Dependencias, versión, plugins y módulos; resueltos antes de ejecutar.',lambda p:Path(p).name=='pom.xml'),('Application y Config Repo','application.yml contiene identidad/importación; config-repo contiene valores por perfil.',lambda p:p.endswith('.yml') and ('config-repo/' in p or p.endswith('application.yml'))),('Docker/Compose/Nginx','Empaquetado, redes, puertos, volúmenes y proxy; DEV e integrado son modalidades diferentes.',lambda p:Path(p).name.startswith(('compose','Dockerfile')) or p.endswith('.conf')),('Observabilidad','Targets, scrapes, labels, pipelines y provisión Grafana.',lambda p:p.startswith('obs/') and not Path(p).name.startswith('compose')),('Frontend build/runtime','CLI, TypeScript, npm y URLs runtime; config.dev.json difiere de config.json.',lambda p:p.startswith('clients/') and p.endswith('.json') and Path(p).name!='package-lock.json'),('Herramientas y CI','Arranque/status y pruebas externas; el script no sustituye invariantes del backend.',lambda p:p.startswith(('uso-rapido/scripts/','.github/'))),('Identidad','Realm, cliente, roles, usuarios y audiencia iniciales de laboratorio.',lambda p:p=='keycloak/garritas-realm.json')]
 for title,explanation,predicate in config_groups:
  b.h(title,2);b.p(explanation)
  for p in sorted(x for x in TRACKED if predicate(x)):b.bullet('`'+p+'`')
 b.h('17. Catálogo HTTP por controlador')
 b.p('Los fragmentos siguientes son los mappings escritos. El prefijo de clase se combina con el mapping del método; /api/v1 es común. Los permisos se deciden por SecurityConfiguration y propiedad en servicio, no por la palabra Controller.')
 for p in java:
  if '/controller/' not in p:continue
  s=(ROOT/p).read_text();mappings=re.findall(r'@(?:RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)(?:\([^\n]*(?:\n[^@]*?)?\))?',s)
  # Una línea por anotación es suficiente, conservar los mappings multilínea por balanceo simple.
  mappings=[]
  for match in re.finditer(r'@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\b',s):
   start=match.start();end=s.find('\n',start)
   fragment=s[start:end if end>=0 else len(s)]
   if '(' in fragment and fragment.count('(')>fragment.count(')'):
    pos=s.find(')',start);fragment=s[start:pos+1]
   mappings.append(' '.join(fragment.split()))
  b.h(Path(p).stem,3);b.p('`'+p+'`');b.code('\n'.join(mappings))
 b.h('18. Qué no debes confundir al explicar el proyecto')
 for t in ['Ocho microservicios de negocio no significa ocho procesos totales: hay once Java con infraestructura, Angular y contenedores auxiliares.','Eureka descubre; Gateway enruta; Config suministra propiedades. Ninguno reemplaza a los otros.','Autenticación, rol, propiedad y CORS son controles distintos y complementarios.','M:N es una relación local en Bienestar; una referencia HTTP entre dominios no es una FK entre bases.','Saga no es una transacción ACID global ni una promesa de devolución bancaria.','Un volumen persiste datos, pero no sustituye backup ni réplica.','Kafka es asíncrono; un 201 de venta no implica PAGADA.','Readiness y métricas UP no equivalen a cobertura total funcional.','GitHub aloja código; localhost señala tu propia máquina, no una web pública.','DEV validado no certifica Windows ni el Compose integral no ejecutado.']:b.bullet(t)
 b.h('19. Lecturas y ubicación de las fuentes')
 for t in ['Referencia docente Pagatu: https://github.com/262dist/pagatu · se usa como patrón de estructura y progreso, adaptado al dominio mascotas.','Repositorio Garritas: https://github.com/Nikol235/Garritas- · rama feat/garritas-store.','Guías del proyecto: README.md, docs/arquitectura.md, docs/ejecucion.md y docs/validacion.md.','Documentación oficial de Spring Boot/Cloud/Security/Kafka, PostgreSQL, Angular, Keycloak, Kafka, Docker, Prometheus y Grafana: consulta la versión fijada por los manifiestos antes de aplicar instrucciones de otra generación.','Manual 1: comandos/puertos y evidencia; Manual 2: reconstrucción y código íntegro; este Manual 3: interpretación y conexiones.']:b.bullet(t)
 b.save()

def archive():
 manifest={'commit_base':REV,'fecha':DATE,'incluye':'Fuentes exactas del proyecto y lockfiles; sin .git, binarios, datos, .env personales ni manuales generados.','archivos':[]}
 with zipfile.ZipFile(OUT/'Garritas-Store-codigo-base.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in SOURCE_FILES:
   data=(ROOT/p).read_bytes();manifest['archivos'].append({'ruta':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});z.writestr('Garritas-Store/'+p,data)
  z.writestr('Garritas-Store/MANIFIESTO-CODIGO.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 (OUT/'MANIFIESTO-CODIGO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
 archive()
 for create in [operational,construction,technical]:
  print('Generando',create.__name__,flush=True);create()
 print('Listo:',OUT,flush=True)
