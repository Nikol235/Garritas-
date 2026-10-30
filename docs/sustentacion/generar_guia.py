"""Guía de defensa verificada contra rutas y símbolos reales, sin modificar la aplicación."""
from pathlib import Path
import subprocess,re,json,html,textwrap
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,Table,TableStyle,Image
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
REV=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
GH='https://github.com/Nikol235/Garritas-/blob/'+REV+'/'
COMMON='infra/garritas-common/src/main/java/pe/edu/upeu/garritas/common/'
CONFIG='infra/garritas-config/config-repo/'
FRONT='clients/garritas-frontend/src/app/'
def src(d,f):return f'services/garritas-{d}-ms/src/main/java/pe/edu/upeu/garritas/{d}/'+f
for name,file in [('Text','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='Bold',italic='Text',boldItalic='Bold')
S={
'p':ParagraphStyle('body',fontName='Text',fontSize=9.2,leading=14,spaceAfter=8),
'small':ParagraphStyle('small',fontName='Text',fontSize=7.3,leading=10,spaceAfter=5),
'path':ParagraphStyle('path',fontName='Mono',fontSize=6.5,leading=9,spaceAfter=6,wordWrap='CJK'),
'h1':ParagraphStyle('h1',fontName='Bold',fontSize=17,leading=23,textColor=colors.HexColor('#245b47'),spaceAfter=12),
'h2':ParagraphStyle('h2',fontName='Bold',fontSize=11,leading=16,textColor=colors.HexColor('#245b47'),spaceBefore=7,spaceAfter=6),
'code':ParagraphStyle('code',fontName='Mono',fontSize=7,leading=10,spaceAfter=8),
'cover':ParagraphStyle('cover',fontName='Bold',fontSize=27,leading=34,textColor=colors.HexColor('#245b47'),spaceAfter=20)
}
class Doc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name=='h1':
   key='sec-'+str(self.seq.nextf('section'));self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,0);self.notify('TOCEntry',(0,f.getPlainText(),self.page,key))
story=[];md=[];refs=[];chapters=[]
def p(t):story.append(Paragraph(t,S['p']));md.append(t.replace('<b>','**').replace('</b>','**')+'\n')
def h(t):story.append(Paragraph(escape(t),S['h2']));md.append('### '+t+'\n')
def chapter(t,new=True):
 if new:story.append(PageBreak())
 story.append(Paragraph(escape(t),S['h1']));md.append('\n## '+t+'\n');chapters.append(t)
def code(t):
 lines=[]
 for line in t.splitlines():lines+=textwrap.wrap(line,113,replace_whitespace=False,drop_whitespace=False,break_on_hyphens=False) or ['']
 story.append(Preformatted('\n'.join(lines),S['code']));md.append('```\n'+t+'\n```\n')
def table(headers,rows,widths=None):
 data=[[Paragraph(escape(str(c)),S['small']) for c in row] for row in [headers,*rows]]
 t=Table(data,colWidths=widths or [509/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deebe1')),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#ccd9d1')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([t,Spacer(1,7)])
 md.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('\n',' ') for c in r)+' |' for r in rows)+'\n')
def ref(path,label,needle=None):
 f=ROOT/path;assert f.is_file(),path;lines=f.read_text().splitlines()
 if needle:
  found=[i+1 for i,line in enumerate(lines) if needle in line];assert found,(path,needle);line=found[0]
 else:line=1
 url=GH+path+'#L'+str(line)
 story.append(Paragraph('<b>'+escape(label)+'</b> · línea '+str(line),S['small']))
 story.append(Paragraph('<link href="'+escape(url)+'" color="#245b47">'+escape(path)+'</link>',S['path']))
 md.append('**'+label+'**: ['+path+':'+str(line)+']('+url+')\n');refs.append({'seccion':chapters[-1] if chapters else 'Portada','ruta':path,'linea':line,'simbolo':needle,'explicacion':label,'url':url})
def excerpt(path,needle,count=10):
 lines=(ROOT/path).read_text().splitlines();start=next(i for i,l in enumerate(lines) if needle in l);code('\n'.join(lines[start:start+count]))
def diagram(name,body):
 dot='digraph G {graph [fontname="DejaVu Sans",bgcolor="white",pad="0.15",ranksep="0.35"];node [fontname="DejaVu Sans",fontsize=11,shape=box,style="rounded,filled",fillcolor="#edf4ee",color="#47735e"];edge [fontname="DejaVu Sans",fontsize=9,color="#48685a"];'+body+'}'
 file=OUT/'diagramas'/name;file.with_suffix('.dot').write_text(dot)
 for ext in ['png','svg']:subprocess.run(['dot','-T'+ext,str(file.with_suffix('.dot')),'-o',str(file.with_suffix('.'+ext))],check=True,capture_output=True)
 w,h=PILImage.open(file.with_suffix('.png')).size;scale=min(509/w,440/h);story.append(Image(str(file.with_suffix('.png')),width=w*scale,height=h*scale));story.append(Spacer(1,8));md.append('!['+name+'](diagramas/'+name+'.png)\n')
def footer(c,d):
 c.setStrokeColor(colors.HexColor('#c2d5c7'));c.line(43,36,A4[0]-43,36);c.setFillColor(colors.HexColor('#52685a'));c.setFont('Text',7);c.drawString(43,23,'Garritas Store · Guía de sustentación · Código '+REV[:7]);c.drawRightString(A4[0]-43,23,str(d.page))

story.extend([Spacer(1,55),Paragraph('Garritas Store',S['cover']),Paragraph('Guía para explicar y sustentar el proyecto',S['h1'])])
p('Funcionamiento, conexiones, CRUD, relaciones muchos a muchos y respuestas a las preguntas de S6–S11. Explicación corta primero; código exacto después.')
p('Basada en el código <b>'+REV[:7]+'</b> de <b>feat/garritas-store</b>. Las rutas y líneas se comprueban al generar esta guía. No se atribuye al proyecto una función que todavía no implementa.')
p('Las rutas del PDF son enlaces a GitHub fijados a esta revisión. En VS Code usa <b>Ctrl+P</b> y pega la ruta relativa; <b>Ctrl+G</b> permite saltar a la línea. Todas parten de la carpeta Garritas-, sea que tu copia esté en C: o D:. El archivo Mapa-de-codigo.txt facilita copiarlas sin saltos.')
p('Ruta rápida: lee el resumen, el flujo de compra, tu ficha de microservicios y las siete respuestas. Para una exposición individual usa el guion de tres minutos del final.')
story.append(PageBreak());story.append(Paragraph('Índice',S['h1']));toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Text',fontSize=9,leading=14,spaceBefore=4)];story.append(toc)
chapter('1. Explicación del proyecto en un minuto')
p('<b>Qué decir:</b> “Garritas Store es una tienda y plataforma de cuidado de mascotas. Angular presenta la aplicación; Gateway es la entrada de negocio; Keycloak identifica al usuario. Cada microservicio administra su propia base. Las consultas que necesitan respuesta inmediata usan HTTP; la compra se completa por eventos Kafka con consistencia eventual”.')
table(['Pareja','Transaccional','Maestro','N:M'],[('Tú','Venta + DetalleVenta','Institución','Sedes ↔ prestaciones'),('Compañera','Cita + DetalleCita','Envío: logística','Transportistas ↔ zonas'),('Fio','Suscripcion + PeriodoSuscripcion, en Usuario','Catálogo','Clientes ↔ planes')],[65,165,100,179])
p('Pago y Bienestar son complementarios. Bienestar también tiene Profesional ↔ Especialidad. Un maestro puede usar @Transactional para guardar datos: “no transaccional” aquí describe su función principal, no la ausencia de transacciones SQL.')
h('Cinco ideas que debes recordar')
for t in ['Controller recibe HTTP; Service aplica reglas; Repository accede a PostgreSQL; DTO define entrada/salida y Mapper convierte.','Cada base tiene transacciones ACID locales. No hay una transacción ACID única que abarque ocho bases y Kafka.','Un 201 al crear una venta significa que se registró: el pago puede continuar pendiente.','Ocultar botones por rol es presentación; Gateway y cada backend verifican el JWT y la propiedad.','No todos los servicios tienen CRUD libre: Venta y Pago conservan historial y sus estados cambian por el proceso de negocio.']:p('• '+t)
h('No afirmar en la sustentación')
p('No hay un garritas-auth-ms propio en esta versión; se usa Keycloak. El pago es simulado, no bancario. No se garantiza entrega “exactamente una vez”. Las pruebas DEV Linux no certifican todas las instalaciones Windows ni el arranque integral Docker.')
chapter('2. Quién se conecta con quién')
diagram('arquitectura','''rankdir=TB;a[label="Angular :4200"];g[label="Gateway :18080"];k[label="Keycloak :18180"];e[label="Eureka :18761"];c[label="Config :18888"];s[label="8 microservicios\n:8081–8088"];db[label="8 PostgreSQL independientes\n:15441–15448 en host"];a->g[label="API HTTP + JWT"];a->k[label="Login PKCE"];g->e[label="consulta instancias"];g->s[label="lb://nombre lógico"];s->db[label="JPA/JDBC local"];c->s[style=dashed,label="propiedades por perfil"];c->g[style=dashed];s->e[style=dashed,label="registro"];''')
table(['Origen','Destino','Por qué / dónde'],[('Venta','Catálogo','Feign: ProductoClient / CatalogoConsulta; precio y disponibilidad'),('Venta','Institución','ServiceClient en VentaService; sede activa'),('Venta: despacho','Envío','ServiceClient en DespachoService; cobertura/tarifa'),('Citas','Usuario, Institución, Bienestar','ServiceClient en CitaService; mascota propia, sede/ofertas y profesional'),('Bienestar','Institución','ServiceClient en BienestarService; sede opcional válida'),('Venta, Catálogo, Pago','Kafka','Outbox publica; listeners reciben por grupos distintos'),('Institución, Envío, Usuario, Pago','Su base propia','Sus CRUD/operaciones no tienen que llamar a otro servicio para cada consulta')],[93,123,293])
p('Config no transporta las compras y Eureka no es un proxy: suministran configuración y descubrimiento. Angular conoce Gateway y Keycloak; no usa direcciones de instancias de negocio.')
ref(CONFIG+'garritas-gateway-dev.yml','Rutas Path y destinos lb://','routes:')
ref(COMMON+'ServiceClient.java','Selección de instancia, JWT y correlación','public <T> T get')
h('Referencias HTTP internas: flecha desde quien consulta')
diagram('referencias-http','''rankdir=LR;v[label="Venta :8081"];ca[label="Catálogo :8085"];i[label="Institución :8082"];e[label="Envío :8083"];ci[label="Citas :8084"];u[label="Usuario :8086"];b[label="Bienestar :8088"];p[label="Pago :8087\nintercambia eventos; no consulta HTTP interno"];v->ca[label="Feign / producto"];v->i[label="sede"];v->e[label="despacho / cobertura"];ci->u[label="mascota propia"];ci->i[label="sede / prestaciones"];ci->b[label="profesional"];b->i[label="sede opcional"];''')
p('Las flechas de este mapa son consultas HTTP de negocio; Kafka se muestra en el siguiente flujo. Los clientes de Config y Eureka son infraestructura común a los servicios, no joins entre bases.')
chapter('3. Flujo de una compra y su compensación')
diagram('saga','''rankdir=TB;a[label="Angular → POST /ventas\nJWT + Idempotency-Key"];v[label="Venta valida sede/precios\nTx: venta PENDIENTE_STOCK + outbox"];c[label="Kafka: venta.creada\nCatálogo reserva todo el stock"];p[label="inventario.reservado\nVenta: PENDIENTE_PAGO\nPago procesa simulación"];ok[label="pago.validado\nVenta: PAGADA"];fail[label="pago.fallido\nVenta: COMPENSANDO"];restore[label="Catálogo restaura reserva una vez\ninventario.liberado"];cancel[label="Venta: CANCELADA"];no[label="inventario.rechazado\nVenta: CANCELADA"];a->v->c;c->p[label="stock válido"];c->no[label="sin stock / precio distinto"];p->ok[label="aprobado"];p->fail[label="rechazado"];fail->restore->cancel;''')
p('<b>Cómo contarlo:</b> Venta no descuenta stock ni aprueba pagos por su cuenta. Guarda su venta y un evento pendiente. Catálogo confirma o rechaza la reserva; Pago publica el resultado; Venta observa esos hechos y cambia de estado. Si el pago falla, se devuelve inventario antes de terminar la cancelación.')
table(['Productor','Tipos publicados','Consumidor interesado'],[('Venta','venta.creada','Catálogo'),('Catálogo','inventario.reservado / rechazado','Pago y/o Venta según tipo'),('Pago','pago.validado / fallido','Venta; Catálogo escucha el fallo'),('Catálogo','inventario.liberado','Venta')],[80,245,184])
p('El topic compartido es garritas.ventas.v1; cada servicio tiene su propio grupo y filtra tipos. La clave Kafka es ventaId. Hay orden dentro de una partición, no un orden global de todas las compras. TRANSFERENCIA simula rechazo; YAPE/PLIN son ejemplos de aprobación.')
chapter('4. Dónde demostrar los muchos a muchos')
diagram('nm-institucion','''rankdir=LR;s[label="Sede"];sp[label="SedePrestacion\nprecio / duración / activo"];p[label="Prestacion"];s->sp[label="1:N"];sp->p[label="N:1"];''')
diagram('nm-envio','''rankdir=LR;t[label="Transportista"];c[label="Cobertura\ntarifa / días / activo"];z[label="Zona"];t->c[label="1:N"];c->z[label="N:1"];''')
diagram('nm-usuario','''rankdir=LR;u[label="Usuario"];s[label="Suscripcion\nestado / fechas"];p[label="Plan"];d[label="PeriodoSuscripcion\nalta / renovación / precio"];u->s[label="1:N"];s->p[label="N:1"];s->d[label="1:N"];''')
p('Una N:M significa que ambos extremos pueden relacionarse con varios registros del otro. Como la relación tiene datos propios, se usa una entidad de asociación con dos @ManyToOne. No es una N:M falsa: es el modelo relacional correcto para conservar precio, tarifa o historial.')
ref(src('institucion','entity/SedePrestacion.java'),'Tu N:M: observa los dos @ManyToOne','@ManyToOne')
ref(src('envio','entity/Cobertura.java'),'N:M de tu compañera: transportista y zona','@ManyToOne')
ref(src('usuario','entity/Suscripcion.java'),'N:M de Fio: usuario y plan; además sus períodos','@ManyToOne')
ref(src('bienestar','entity/Profesional.java'),'Ejemplo adicional con @ManyToMany literal','@ManyToMany')
p('<b>Demo rápida:</b> ofrece la misma prestación en dos sedes; asigna un transportista a dos zonas y dos transportistas a una zona; contrata el mismo plan con dos clientes y dos planes con un cliente. Una sola fila no demuestra por sí sola ambas cardinalidades.')
p('Las claves foráneas solo unen tablas de la misma base. En Citas, prestacionId es una referencia remota validada por HTTP; no una FK a la base de Institución.')

cards=[
 dict(d='venta',title='5. Venta · compra y despacho',port=8081,ui='Nueva orden, Carrito, Mis pedidos y Envíos',role='CLIENTE crea/consulta sus pedidos; ADMIN audita todos y opera tránsito/entrega.',crud='Venta no tiene PUT/DELETE libre. El despacho tiene creación, lectura y transiciones; conserva historial.',links=[('controller/VentaController.java','Entrada HTTP de la compra y clave de reintento','@RequestMapping'),('service/VentaService.java','Reglas, precios, propietario e idempotencia','public VentaResponse crear'),('repository/VentaRepository.java','Persistencia de cabecera y consulta por propietario/clave',None),('entity/Venta.java','Cabecera y relación con DetalleVenta',None),('messaging/VentaEvents.java','Consumo y transiciones protegidas por estado previo','public void consume'),('despacho/controller/DespachoController.java','API de entrega; /envios es alias de /despachos','@RequestMapping'),('despacho/service/DespachoService.java','Venta pagada, propietario y cobertura logística','public DespachoResponse crear')],rule='Crear una venta calcula el total en servidor, valida sede y consulta Catálogo. En el mismo commit guarda venta.creada en Outbox. El despacho ahora está aquí, no en el servicio maestro Envío.',connection='Feign → Catálogo; ServiceClient → Institución; despacho → Envío; Kafka ↔ Catálogo/Pago.',api=[('GET /ventas y /ventas/{id}','Consultar, filtrado por propietario'),('POST /ventas','Crear con Idempotency-Key'),('POST /despachos; GET /despachos','Solicitar/consultar entrega'),('POST /despachos/{id}/en-transito, /entregado, /cancelar','Transiciones controladas')]),
 dict(d='institucion',title='6. Institución · sedes y prestaciones',port=8082,ui='Sedes y Servicios por sede',role='Consulta pública/CLIENTE; crear, editar y desactivar requiere ADMIN.',crud='Aquí sí existe CRUD de maestros. DELETE desactiva sedes/prestaciones; no borra referencias históricas.',links=[('controller/SedeController.java','CRUD de sedes: GET/POST/PUT/DELETE','@RequestMapping'),('service/SedeService.java','Filtro de activas, validación y baja lógica',None),('controller/PrestacionController.java','CRUD de prestaciones y asignación por sede','@RequestMapping'),('service/PrestacionService.java','guardarOferta y precio/duración por asociación','guardarOferta('),('entity/SedePrestacion.java','N:M real: sede + prestación + atributos','@ManyToOne'),('repository/SedePrestacionRepository.java','Buscar/reutilizar la pareja, evitando duplicados',None)],rule='Una oferta activa requiere sede y prestación activas; duración de 30 a 240 minutos en múltiplos de 30. Citas usa esa oferta para validar y copiar precio/duración.',connection='Tiene su propia base. Venta, Citas y Bienestar lo consultan por HTTP; no necesita llamarles para guardar su maestro.',api=[('GET/POST /sedes; GET/PUT/DELETE /sedes/{id}','CRUD de sedes'),('GET/POST /prestaciones; PUT/DELETE /prestaciones/{id}','Maestro de prestaciones'),('GET/PUT /sedes/{id}/prestaciones','Consultar/asignar oferta por sede')],sql='V2__prestaciones_sede.sql'),
 dict(d='envio',title='7. Envío · maestro logístico',port=8083,ui='Logística (ADMIN); coberturas disponibles al solicitar Envíos',role='Lecturas de cobertura disponibles; modificaciones solo ADMIN.',crud='CRUD de transportistas y zonas; PUT de cobertura crea o actualiza la pareja. Las bajas son lógicas.',links=[('controller/LogisticaController.java','Todos los endpoints de los maestros','@RequestMapping'),('service/LogisticaService.java','Reglas de actividad y mantenimiento de coberturas','guardarCobertura('),('entity/Cobertura.java','N:M: transportista ↔ zona con tarifa y plazo','@ManyToOne'),('entity/Transportista.java','Maestro transportista',None),('entity/Zona.java','Maestro zona',None),('repository/CoberturaRepository.java','Lectura de una pareja transportista/zona',None)],rule='Un transportista atiende varias zonas y una zona admite varios transportistas. La tarifa no puede ser negativa y el plazo es de 1 a 30 días. Si alguno está inactivo, la cobertura no está disponible.',connection='Venta/Despacho consulta /transportistas/{t}/zonas/{z}. Envío ya no guarda el seguimiento operativo nuevo; la tabla antigua se conserva como archivo migrado.',api=[('GET/POST /transportistas; PUT/DELETE /transportistas/{id}','Maestro transportistas'),('GET/POST /zonas; PUT/DELETE /zonas/{id}','Maestro zonas'),('GET/PUT /coberturas; DELETE /coberturas/{id}','N:M y atributos'),('GET /transportistas/{t}/zonas/{z}','Validar cobertura para un despacho')],sql='V3__maestros_logisticos.sql'),
 dict(d='citas',title='8. Citas · reserva con cabecera y detalle',port=8084,ui='Citas; acceso desde Especialistas o Servicios por sede',role='CLIENTE opera sus citas. ADMIN consulta todas, confirma y marca atención.',crud='Es una operación transaccional: crear, consultar y cancelar; no ofrece edición libre ni borrado histórico.',links=[('controller/CitaController.java','Entrada y acciones de estado','@RequestMapping'),('service/CitaService.java','Validaciones remotas, total y detección de cruces','public CitaResponse crear'),('entity/Cita.java','Cabecera: dueño, mascota, sede, profesional y estado',None),('entity/DetalleCita.java','Detalle: snapshot de prestación/precio/duración',None),('mapper/CitaMapper.java','Identidad del JWT y proyección del detalle',None),('repository/CitaRepository.java','Lecturas por cliente y persistencia',None)],rule='Fecha futura a las :00/:30; mascota propia; sede/profesional activos y compatibles; prestaciones ofrecidas allí. Se suma duración/precio en backend y se bloquea por profesional para rechazar cruces, no solo inicios iguales.',connection='ServiceClient → Usuario para mascota propia; → Institución para sede/ofertas; → Bienestar para profesional. La cabecera y sus detalles se guardan en una transacción local.',api=[('POST /citas; GET /citas y /citas/{id}','Reservar/consultar'),('POST /citas/{id}/confirmar y /atender','ADMIN: PROGRAMADA → CONFIRMADA → ATENDIDA'),('POST /citas/{id}/cancelar','Cancelación permitida; no después de atender')],sql='V3__cita_cabecera_detalle.sql'),
 dict(d='catalogo',title='9. Catálogo · productos, categorías e inventario',port=8085,ui='Catálogo; Productos y Categorías para ADMIN',role='GET público; escritura ADMIN. El consumidor de inventario aplica eventos internos del proceso.',crud='CRUD de categorías y productos. Producto se desactiva; categoría utilizada puede producir conflicto por integridad.',links=[('controller/ProductoController.java','CRUD HTTP de productos','@RequestMapping'),('controller/CategoriaController.java','CRUD HTTP de categorías','@RequestMapping'),('service/ProductoService.java','Reglas de producto y métricas de negocio',None),('repository/ProductoRepository.java','Persistencia y relación con categoría',None),('entity/Producto.java','Entidad y versión para detectar edición obsoleta','@Version'),('messaging/InventarioEvents.java','Reservar/liberar; Inbox y reserva única por venta','private void reservar')],rule='El precio y stock válidos proceden de Catálogo. Al reservar, ordena ids, bloquea filas y valida todas antes de descontar. Si falla una línea, no deja una reserva parcial. La liberación usa el payload original y ocurre una sola vez.',connection='Venta lo consulta por Feign. Kafka entrega venta.creada y pago.fallido; Catálogo publica inventario.reservado/rechazado/liberado.',api=[('GET/POST /productos; GET/PUT/DELETE /productos/{id}','CRUD productos'),('GET/POST /categorias; GET/PUT/DELETE /categorias/{id}','CRUD categorías'),('InventarioEvents.consume → reservar / liberar','Reserva operativa por eventos; no un botón de stock arbitrario')]),
 dict(d='usuario',title='10. Usuario · perfil, mascotas y suscripciones',port=8086,ui='Mi cuenta y mascotas, Clientes y Planes y suscripciones',role='Perfil/mascotas/suscripciones del propietario; ADMIN administra perfiles/planes y audita.',crud='CRUD de perfil/mascotas y planes; suscripciones usan alta, renovación y cancelación con historial.',links=[('controller/UsuarioController.java','CRUD administrativo de perfiles','@RequestMapping'),('controller/MiCuentaController.java','Perfil propio y CRUD de mascotas propias','@RequestMapping'),('service/UsuarioService.java','Guardar mi perfil, vínculo sub y conflictos de correo','guardarMe('),('controller/SuscripcionController.java','CRUD de planes y operaciones de suscripción','@RequestMapping'),('service/SuscripcionService.java','Idempotencia y reglas de contratación/renovación','contratar('),('entity/Suscripcion.java','N:M cliente ↔ plan; cabecera con períodos','@ManyToOne'),('entity/PeriodoSuscripcion.java','Detalle con precio, fechas y clave por operación',None)],rule='Solo un plan vigente activo por cliente; un reintento no agrega otro período; cancelar no borra historia ni simula reembolso. Mascotas exigen edad entera y unidad DIAS/MESES. DELETE de un perfil vinculado devuelve 409 para conservar historia; demuestra borrado con un perfil administrativo sin cuenta vinculada.',connection='Sus operaciones principales son locales; Citas consulta la mascota usando el JWT del cliente. No se añade un evento Kafka ficticio para cada CRUD.',api=[('GET/PUT /usuarios/me; CRUD /usuarios/me/mascotas','Cuenta propia'),('CRUD /usuarios; GET/POST/PUT/DELETE de planes según ruta','Administración'),('POST /suscripciones; POST /suscripciones/{id}/renovar o /cancelar','Operación con períodos; alta/renovación exige clave'),('GET /suscripciones y /suscripciones/{id}','Solo dueño o auditor ADMIN')],sql='V4__suscripciones_periodos.sql'),
 dict(d='pago',title='11. Pago · resultado simulado de la compra',port=8087,ui='Pagos y resultado en Mis pedidos',role='CLIENTE consulta los suyos; ADMIN consulta todos.',crud='No hay CRUD de escritura público. El pago se genera por evento y se consulta por HTTP.',links=[('controller/PagoController.java','API de lectura de pagos','@RequestMapping'),('service/PagoService.java','Filtrado por sub y comprobación de propietario',None),('messaging/PagoEvents.java','Consumir inventario.reservado y emitir resultado','public void consume'),('entity/Pago.java','Registro del pago simulado',None),('repository/PagoRepository.java','Consulta por venta/cliente',None)],rule='Un pago por venta: UNIQUE(id_venta) y ON CONFLICT evitan efectos repetidos. Pago, Inbox y Outbox se confirman juntos. El resultado es APROBADO/RECHAZADO en Pago; la venta usa PAGADA/CANCELADA tras completar su proceso.',connection='Kafka desde Catálogo; publica pago.validado o pago.fallido para Venta y compensación de inventario. No llama a una pasarela externa real.',api=[('GET /pagos; GET /pagos/{id}','Consulta protegida'),('GET /pagos/venta/{id}','Pago de una compra; puede ser 404 si aún no existe'),('PagoEvents.consume','Creación interna por evento, no POST abierto')]),
 dict(d='bienestar',title='12. Bienestar · profesionales y especialidades',port=8088,ui='Especialistas',role='Lecturas públicas; altas/cambios/bajas ADMIN.',crud='CRUD de maestros. Baja lógica de profesional; especialidad vinculada no se elimina hasta desasignarla.',links=[('controller/BienestarController.java','CRUD de ambos recursos','@RequestMapping'),('service/BienestarService.java','Validación, asignación y bloqueo de borrado vinculado',None),('entity/Profesional.java','@ManyToMany y @JoinTable profesional_especialidad','@ManyToMany'),('entity/Especialidad.java','Extremo compartido de la asociación',None),('repository/ProfesionalRepository.java','Lectura de profesionales y sus especialidades',None)],rule='Un profesional tiene varias especialidades; una especialidad pertenece a varios profesionales. Los ids se validan y deduplican. Una sede asignada debe estar activa; si no tiene sede asignada puede atender en cualquiera permitida por el flujo.',connection='Consulta Institución al validar sede opcional. Citas lo consulta antes de reservar; no comparte su tabla de profesionales con Citas.',api=[('GET/POST /especialistas; GET/PUT/DELETE /especialistas/{id}','Profesionales y asignación de especialidades'),('GET/POST /especialidades; PUT/DELETE /especialidades/{id}','Especialidades')])
]
for card in cards:
 chapter(card['title']);p('<b>Para qué sirve:</b> '+card['rule']);p('<b>Dónde verlo:</b> '+card['ui']+'. <b>Puerto:</b> '+str(card['port'])+'.');p('<b>Permisos:</b> '+card['role']);p('<b>CRUD:</b> '+card['crud']);p('<b>Conexiones:</b> '+card['connection'])
 table(['Ruta relativa a /api/v1','Operación'],card['api'],[300,209])
 h('Archivos que debes abrir')
 for f,label,needle in card['links']:ref(src(card['d'],f),label,needle)
 ref(CONFIG+'garritas-'+card['d']+'-ms-dev.yml','Conexión JDBC, puerto, Eureka y emisor JWT del servicio')
 frontend_files={'venta':['app.ts','features/envios/envios.component.ts'],'institucion':['features/sedes/sedes.component.ts','features/prestaciones/prestaciones.component.ts'],'envio':['features/logistica/logistica.component.ts'],'citas':['features/citas/citas.component.ts'],'catalogo':['features/admin/productos.component.ts'],'usuario':['features/cuenta/cuenta.component.ts','features/planes/planes.component.ts'],'pago':['features/pagos/pagos.component.ts'],'bienestar':['features/bienestar/especialistas.component.ts']}
 for f in frontend_files[card['d']]:ref(FRONT+f,'Angular: vista y llamadas API relacionadas')
 if card['d']=='usuario':
  ref(src('usuario','dto/MascotaRequest.java'),'Validación de edad entera antes de convertirla','private java.math.BigDecimal edad;')
  ref(src('usuario','entity/UnidadEdad.java'),'Unidades admitidas: DIAS y MESES')
 if card.get('sql'):ref(f"services/garritas-{card['d']}-ms/src/main/resources/db/migration/"+card['sql'],'Migración real: tablas y restricciones')

chapter('13. S6 · comunicación síncrona resiliente')
p('<b>Idea sencilla:</b> necesito una respuesta ahora, pero no puedo esperar indefinidamente. Venta pide a Catálogo el producto y precio mediante Feign; el nombre identifica un servicio, no una IP fija.')
diagram('sincrona','''rankdir=TB;{rank=same;v;cb;f;}{rank=same;fb;e;c;}v[label="VentaService"];cb[label="CatalogoConsulta\nCircuit Breaker catalogo"];f[label="ProductoClient\n@FeignClient(nombre lógico)"];e[label="Eureka + LoadBalancer\neligen instancia"];c[label="Catálogo\nGET /productos/{id}"];fb[label="Fallback: error controlado\n503 si no disponible\nNo inventa precio"];v->cb->f->e->c;cb->fb[label="fallo / circuito abierto",style=dashed];''')
table(['Mecanismo','Qué resuelve','Configuración actual'],[('Timeout','Acota la espera de conexión/lectura','Feign: conexión 2 s; lectura 3 s'),('Circuit Breaker','Tras suficientes fallos deja de insistir temporalmente','Ventana 10; mínimo 5 llamadas; umbral 50%; espera abierto 10 s'),('TimeLimiter','Acota ejecución del flujo protegido donde lo aplica Spring Cloud','4 s para catalogo'),('Fallback','Define qué hacer cuando la llamada falla o no se permite','CatalogoConsulta devuelve error HTTP controlado; no producto ficticio')],[96,220,193])
p('No son sinónimos: el timeout protege una llamada; el breaker evita insistir repetidamente en un destino enfermo. CLOSED permite llamadas, OPEN las rechaza temporalmente y HALF_OPEN prueba recuperación. No sumes estos valores como una promesa exacta de latencia total.')
ref(src('venta','client/ProductoClient.java'),'Declaración Feign por nombre Eureka','@FeignClient')
excerpt(src('venta','client/ProductoClient.java'),'@FeignClient',7)
ref(src('venta','client/CatalogoConsulta.java'),'Breaker y fallback reales','public ProductoClient.Producto obtener')
ref(CONFIG+'garritas-venta-ms-dev.yml','Timeouts Feign y ajustes Resilience4j','openfeign:')
ref(COMMON+'HttpServices.java','Otras referencias HTTP: conexión 2 s y lectura 3 s','ServiceClient serviceClient')
p('ServiceClient también limita la espera y devuelve 503 si no hay instancia, pero no se presenta como otro Feign ni como un breaker que no tiene. El caso protegido con Circuit Breaker aquí es Venta → Catálogo.')
chapter('14. S7 / S07b · identidad y autorización')
p('<b>Autenticar:</b> comprobar quién eres. <b>Autorizar:</b> comprobar qué puedes hacer. <b>Propiedad:</b> comprobar si ese pedido, mascota o suscripción es tuyo. Un CLIENTE autenticado no puede actuar sobre todos los registros.')
diagram('jwt','''rankdir=TB;u[label="Usuario inicia sesión"];kc[label="Keycloak verifica credenciales\nemite JWT firmado"];g[label="Gateway valida JWT\nfirma + issuer + audiencia + roles"];s[label="Servicio destino valida otra vez\nroles + CurrentUser.requireOwner"];db[label="Consulta/cambio autorizado\nen su PostgreSQL"];u->kc;kc->g[label="Angular envía Bearer"];g->s->db;direct[label="Petición directa a :808x"];direct->s[label="también debe validarse"];''')
ref(COMMON+'SecurityConfiguration.java','Cadena de filtros, rutas y roles en Gateway/servicios','SecurityFilterChain security')
ref(COMMON+'CurrentUser.java','sub, rol ADMIN y comprobación de dueño','public static void requireOwner')
ref(src('usuario','GarritasUsuarioMsApplication.java'),'Importación de la seguridad común en un backend','@org.springframework.context.annotation.Import')
ref(CONFIG+'garritas-usuario-ms-dev.yml','issuer-uri, JWK Set y audiencia garritas-api','issuer-uri:')
ref('keycloak/garritas-realm.json','Realm, roles y cliente público de demostración')
p('La firma se valida con claves públicas JWKS: los servicios no necesitan la contraseña del usuario ni firmar nuevos tokens. El JWT no es cifrado por ser JWT; sus claims pueden leerse. Sin token o token inválido: 401. Token válido pero rol/propiedad insuficiente: 403.')
p('<b>Por qué idCliente es String:</b> Keycloak identifica al usuario con sub, normalmente un UUID. Ese dueño se guarda como texto. Usuario.id sigue siendo Long para sus relaciones locales; no se convierte toda la base a String. La migración no asigna automáticamente datos históricos a una cuenta nueva por coincidir nombre o correo.')
ref('services/garritas-venta-ms/src/main/resources/db/migration/V2__saga_identity.sql','Cambio de propietario y unicidad de reintento')
p('Pagatu construyó un auth temporal compatible y después lo reemplazó. Garritas ya usa Keycloak: explica la estrategia del modelo docente sin decir que construiste un auth-ms que no existe en este repositorio.')
chapter('15. S8 · comunicación por eventos')
p('<b>Idea sencilla:</b> no llamo a Pago para que me conteste en el mismo HTTP. Registro un hecho y lo publico; el consumidor lo procesa cuando esté disponible. Eso reduce la dependencia temporal, pero el resultado final ya no es inmediato.')
diagram('eventos','''rankdir=TB;{rank=same;v;o;k;}{rank=same;ca;pa;ve;}v[label="Venta\nTx: venta + outbox"];o[label="Outbox.publish\nKafkaTemplate.send"];k[label="Kafka: garritas.ventas.v1\nclave ventaId / 3 particiones"];ca[label="Grupo Catálogo\nfiltra eventos de inventario"];pa[label="Grupo Pago\nfiltra inventario.reservado"];ve[label="Grupo Venta\nfiltra resultados"];v->o->k;k->ca;k->pa;k->ve;''')
ref(COMMON+'SagaEvent.java','Contrato compartido y versionado','public record SagaEvent')
ref(COMMON+'Outbox.java','Publicador Kafka y confirmación de envío','public void publish')
ref(COMMON+'MessagingConfiguration.java','Topics, DLT y error handler','NewTopic sagaTopic')
ref(src('pago','messaging/PagoEvents.java'),'Listener que escucha el topic y filtra su tipo','@KafkaListener')
ref(CONFIG+'garritas-pago-ms-dev.yml','group-id propio del consumidor','group-id:')
p('Un grupo no es un usuario. Venta, Catálogo y Pago usan grupos distintos para recibir los eventos necesarios; instancias del mismo grupo reparten particiones. Un mensaje tiene eventId para deduplicar y ventaId para enlazar el proceso; no son el mismo identificador.')
p('Si el broker cae, el Outbox conserva pendientes. Si Pago está detenido, Kafka conserva lo publicado y su grupo puede continuar al volver, dentro de la retención configurada. No se promete conservar mensajes para siempre ni que la orden ya esté pagada.')
p('<b>Dónde mostrarlo:</b> Kafka UI → cluster garritas → Topics → garritas.ventas.v1 → Messages. Busca type, ventaId y traceId. En Consumer Groups observa el grupo de Pago y su lag durante una falla ensayada. Un mensaje visible no basta: muestra también el pedido y el registro de pago.')
chapter('16. S9 · consistencia e idempotencia')
p('<b>Idea sencilla:</b> cada servicio confirma su propia operación. Si después falla el proceso completo, se ejecuta una compensación de negocio; no un rollback mágico de bases remotas.')
table(['Protección','Dónde','Qué evita'],[('Idempotency-Key por cliente','VentaService + uk_venta_request','Compras duplicadas por reintentar el mismo HTTP'),('Inbox eventId','Inbox.claim, PK inbox_event','Reprocesar el mismo evento en una transacción local'),('Unicidad por negocio','reservas_stock.id_venta; pagos.id_venta','Repetición semántica con otro eventId'),('Guardia de estado','VentaEvents UPDATE ... AND estado=?','Transiciones que no corresponden al estado actual'),('Compensación','InventarioEvents.liberar','Reserva descontada que debe devolverse una sola vez'),('Clave por período','SuscripcionService / suscripcion_periodos','Una renovación repetida no añade otro período')],[110,200,199])
ref(src('venta','service/VentaService.java'),'Bloqueo por clave y comparación del payload','public VentaResponse crear')
ref(COMMON+'Inbox.java','Evento y efecto se confirman juntos','public boolean claim')
ref(COMMON+'Outbox.java','Negocio y evento pendiente se guardan juntos','public void append')
ref(src('catalogo','messaging/InventarioEvents.java'),'Devolución desde reserva original y guardia RESERVADA','private void liberar')
ref(src('usuario','service/SuscripcionService.java'),'Alta/renovación idempotente e historial de precios','public SuscripcionResponse renovar')
p('<b>Al menos una vez:</b> un fallo después del ACK Kafka y antes de marcar published_at puede provocar reenvío. Por eso no afirmamos “exactamente una vez”. Un consumidor idempotente mantiene el mismo efecto de negocio ante ese reintento.')
p('Una nueva renovación voluntaria usa una clave nueva y sí añade un período. Para probar idempotencia reenvía la misma petición, con el mismo cuerpo, dueño y cabecera; no pulses Renovar dos veces esperando que sean una sola operación. academic_smoke.py conserva esa clave durante el reintento de prueba.')
p('La compensación devuelve inventario; no borra que la venta existió. Cancelar una compra ya pagada con reembolso necesitaría otro proceso: no se inventa cambiando una columna. Si hay un evento en DLT o una Saga pendiente, se investiga; no se fuerza PAGADA en SQL.')
p('Prueba existente: faults.py reproduce el evento y un duplicado semántico sin duplicar devolución; también detiene Pago/Kafka y verifica recuperación. Solo debe ejecutarse en DEV desechable y sin otras demos concurrentes.')
chapter('17. S10 · observar y diagnosticar')
diagram('observabilidad','''rankdir=TB;{rank=same;j;pr;gr;}{rank=same;logs;tail;lo;}j[label="Java /actuator/prometheus\ny Keycloak /metrics"];pr[label="Prometheus :19090\nseries métricas"];logs[label="Archivos .runtime\nMDC traceId"];tail[label="Promtail"];lo[label="Loki :13100\nlogs centralizados"];gr[label="Grafana :13000\npaneles + Explore"];j->pr->gr;logs->tail->lo->gr;''')
p('<b>Liveness:</b> ¿el proceso está vivo? <b>Readiness:</b> ¿está listo según las dependencias incluidas? En los servicios de negocio se incluye db. Un scrape up=1 no demuestra que una compra termine bien: se necesita además revisar el flujo.')
ref(CONFIG+'garritas-venta-ms-dev.yml','Grupos liveness/readiness y exposición de métricas','management:')
ref(src('venta','filter/CorrelationIdFilter.java'),'Lee/genera X-Trace-ID y lo pone en MDC','protected void doFilterInternal')
ref(src('venta','client/FeignConfiguration.java'),'Propaga el identificador en Feign','RequestInterceptor traceInterceptor')
ref(COMMON+'ServiceClient.java','Propaga JWT y X-Trace-ID en otras referencias','String trace =')
ref('obs/prometheus/prometheus-dev.yml','Descubrimiento de servicios y target Keycloak')
ref('obs/promtail/promtail-config-dev.yml','Lectura de logs por application')
ref('obs/grafana/provisioning/dashboards/garritas-infraestructura.json','Panel real: instancias, HTTP, PostgreSQL, Gateway y logs de Catálogo')
p('<b>Demo:</b> en Grafana → Dashboards → Garritas - Infraestructura muestra “Instancias activas”, peticiones por instancia y conexiones PostgreSQL. Si Pago cae, su target puede marcar 0 o desaparecer al darse de baja en Eureka. Observa el rango de tiempo y el registro, no solo un valor instantáneo.')
p('Para errores 5xx utiliza Explore → Prometheus (no es un panel adicional ya creado):')
code('sum by (instance) (\n  rate(http_server_requests_seconds_count{\n    job="garritas-microservicios", status=~"5.."\n  }[1m])\n)')
p('En Explore → Loki reemplaza TU_TRACE_ID por el X-Trace-ID de la petición/evento. Consulta varios servicios de una vez:')
code('{application=~"garritas-(venta|catalogo|pago)-ms"} |= "TU_TRACE_ID"')
p('Esto correlaciona logs, no crea spans OpenTelemetry. El panel actual trae logs de Catálogo; Explore permite seleccionar los otros servicios. No inventes un panel de estado de Saga que no está aprovisionado.')
chapter('18. S11 · Angular, Gateway y PKCE')
diagram('pkce','''rankdir=TB;a[label="Angular genera verifier y challenge S256"];k[label="Redirige a Keycloak\nusuario se autentica allí"];b[label="Keycloak devuelve código\nAngular intercambia código + verifier"];m[label="keycloak-js mantiene tokens en memoria"];i[label="Interceptor pide token vigente\ny adjunta Bearer a API propia"];g[label="Gateway → servicio validan JWT\nAngular refleja pendiente / pagada / cancelada"];a->k->b->m->i->g;''')
ref(FRONT+'app.config.ts','Inicializa Auth y registra interceptor HTTP','provideAppInitializer')
ref(FRONT+'core/auth.ts','Login, PKCE S256, renovación y roles reales','pkceMethod:')
ref(FRONT+'core/interceptor.ts','Bearer solo para la URL de API propia','export const authInterceptor')
ref(FRONT+'core/config.ts','Carga URLs runtime antes de autenticar','async load')
ref('clients/garritas-frontend/public/config.dev.json','En DEV apiUrl apunta a Gateway, no a :8081–8088')
ref(FRONT+'app.ts','Polling con timer/exhaustMap y estados pendientes','timer(3000')
ref(FRONT+'features/cart/cart-store.ts','Persistencia del carrito; no de tokens')
p('Una SPA es pública: cualquier persona puede leer su JavaScript; por eso no guarda client secret. PKCE vincula el código temporal al verifier de ese navegador. La contraseña se introduce en Keycloak, no en un formulario propio enviado al token endpoint.')
p('No digas que password grant es técnicamente imposible: un proveedor podría habilitarlo. Aquí está desactivado y no debe usarse: haría a la SPA manejar contraseñas y perdería las ventajas del login delegado, SSO/MFA. Los tokens viven en memoria de keycloak-js; Keycloak puede mantener sus propias cookies de sesión.')
p('localStorage solo conserva datos no sensibles del carrito y su reintento; no JWT. Angular usa roles para mostrar acciones, pero el backend vuelve a autorizar. El polling evita mostrar “pagado” simplemente porque POST /ventas devolvió 201.')

chapter('19. Respuestas al docente · preguntas 1–3')
h('1. Si el servicio remoto cae, ¿qué evita quedar colgado?')
p('<b>Respuesta para decir:</b> “Limitamos la espera con timeouts y, en Venta → Catálogo, usamos Circuit Breaker. Tras suficientes fallos el circuito abre y evita insistir. El fallback devuelve un error controlado, no un precio inventado”.')
p('En Garritas: ProductoClient usa el nombre garritas-catalogo-ms; CatalogoConsulta crea el breaker catalogo; el perfil DEV fija conexión 2 s, lectura 3 s y TimeLimiter 4 s. Las otras llamadas de ServiceClient también tienen tiempos acotados, pero no afirmo que todas estén envueltas en el mismo breaker.')
p('<b>Qué mostrar:</b> ProductoClient.java → CatalogoConsulta.java → garritas-venta-ms-dev.yml. Si haces una falla real, ensaya antes y conserva evidencia del estado OPEN; un único 503 no demuestra por sí solo que el breaker abrió. No apagues todos los contenedores en plena presentación.')
h('2. ¿Por qué no basta proteger el Gateway?')
p('<b>Respuesta para decir:</b> “El Gateway es la entrada normal, pero un backend puede recibir una petición directa o desde otra aplicación. Cada servicio valida firma, emisor, audiencia y permisos; además compara el sub con el dueño del registro”.')
p('Sin token válido, una ruta protegida responde 401 incluso si llamas directamente a :808x. Con token válido pero rol o dueño incorrecto responde 403. Una consulta intencionalmente pública, como GET de productos, sí puede responder sin token: eso es una decisión de permisos, no una falla.')
p('<b>Qué mostrar:</b> SecurityConfiguration.java, CurrentUser.requireOwner y la importación de seguridad en la Application de un servicio. En Angular compara ADMIN y CLIENTE y demuestra también el rechazo API, no solo que falta un botón.')
h('3. ¿Qué gana y qué pierde usar eventos frente a REST?')
p('<b>Respuesta para decir:</b> “Gano desacople temporal: el productor no necesita que el consumidor esté atendiendo en ese instante. Pierdo la confirmación inmediata del resultado final; el proceso queda pendiente y puede haber reintentos o duplicados”.')
p('En Garritas, crear la venta y su Outbox no equivale a tener un pago. Kafka permite que Pago retome mensajes al recuperarse; Angular consulta el estado hasta que la Saga termina. Debemos resolver consistencia eventual, monitorear lag/DLT e implementar idempotencia. REST sigue siendo útil para validar datos que necesitamos antes de registrar la operación.')
p('<b>Qué mostrar:</b> Outbox.append/publish, PagoEvents.consume, Kafka UI con el mismo ventaId y Mis pedidos cambiando de estado sin recargar.')
chapter('20. Respuestas al docente · preguntas 4–5')
h('4. ¿Cómo evitas inconsistencia si el proceso falla a mitad?')
p('<b>Respuesta para decir:</b> “Usamos una Saga coreografiada: cada servicio confirma su paso local y publica un hecho. Si falla el pago después de reservar stock, Catálogo compensa devolviendo esa reserva. Idempotente significa que repetir la misma operación no repite su efecto de negocio”.')
p('La venta pasa a COMPENSANDO con pago.fallido y solo termina CANCELADA cuando recibe inventario.liberado. Inbox evita repetir un eventId; las reservas y pagos únicos por venta cubren duplicados semánticos con otro eventId. Outbox evita perder el evento entre guardar en SQL y enviar a Kafka. No existe un ACID global que abarque las bases independientes.')
p('Ejemplo numérico: había 10 unidades; se reservan 2 y quedan 8; el pago falla y se restauran 2: vuelven a 10. Si el evento se repite, deben seguir en 10, no 12. La compensación utiliza las cantidades originales persistidas.')
p('<b>Qué mostrar:</b> InventarioEvents.reservar/liberar, Inbox.claim, tabla reservas_stock y la guardia de estado en VentaEvents. Complementa con Idempotency-Key de VentaService. En Usuario, repetir una renovación con la misma clave tampoco agrega otro período.')
h('5. ¿Qué evidencia del panel ubica una falla sin abrir logs uno a uno?')
p('<b>Respuesta para decir:</b> “Identifico la instancia afectada en Grafana con sus métricas y correlaciono la operación por traceId en Loki. Comparo el servicio caído, el Gateway y los servicios que siguen saludables, dentro del mismo rango de tiempo”.')
p('En el dashboard real Garritas - Infraestructura: Instancias activas muestra un target caído o su desaparición; Peticiones HTTP por segundo ayuda a ubicar dónde dejó de atender; Conexiones PostgreSQL aporta contexto de persistencia. En Explore/Prometheus filtro errores 5xx por instancia; esa consulta no debe presentarse como un panel ya creado.')
p('Después obtengo X-Trace-ID desde la respuesta HTTP o el evento y hago una sola búsqueda LogQL sobre Venta, Catálogo y Pago. La ruta HTTP lo propaga por Feign/ServiceClient; los consumidores vuelven a poner el traceId del evento en MDC. Así leo juntos los mensajes de esa operación.')
p('<b>Matiz importante:</b> up significa que Prometheus pudo hacer scrape, no que el negocio terminó. Si un proceso vivo perdió PostgreSQL, su readiness con db puede fallar aunque el scrape siga respondiendo. Si Eureka da de baja la instancia, el target puede desaparecer en vez de permanecer en cero.')
p('<b>Qué mostrar:</b> dashboard, Status/Targets de Prometheus, /actuator/health/readiness y Explore/Loki con el mismo identificador. Los datos deben ser reales; no basta mostrar la configuración del panel.')
chapter('21. Respuestas al docente · preguntas 6–7')
h('6. ¿Por qué Angular no conoce direcciones de instancias?')
p('<b>Respuesta para decir:</b> “Las instancias cambian de puerto o cantidad y pueden fallar. Angular conoce una entrada estable, Gateway; Eureka y LoadBalancer resuelven qué instancia atiende. Así el frontend no depende del despliegue interno”.')
p('En DEV apiUrl apunta a localhost:18080/api/v1, no a localhost:8081. Se centralizan enrutamiento y CORS y se evita duplicar descubrimiento en cada navegador. La seguridad también se mantiene en los servicios. Angular sí conoce la URL de Keycloak para autenticar: ese es el proveedor de identidad, no una instancia de la API de negocio.')
p('<b>Qué mostrar:</b> public/config.dev.json, Config.load, authInterceptor y las rutas lb:// en garritas-gateway-dev.yml. La segunda instancia se puede demostrar con el encabezado X-Service-Instance usando scaling.py o los comandos documentados.')
h('7. Al migrar de auth propio a Keycloak, ¿qué cambió y por qué fue poco?')
p('<b>Respuesta para decir:</b> “La compatibilidad del contrato JWT permitió conservar la validación estándar y las reglas por rol. Cambió quién emite el token y dónde confiamos sus claves. También hubo que migrar la identidad de negocio a sub; esa parte sí afecta código y datos”.')
table(['Cambia','Se conserva'],[('issuer-uri y JWK Set; claves/realm del emisor','Resource Server y validación JWT estándar'),('Cliente OIDC de Angular, redirect URIs y PKCE','Roles esperados si realm_access.roles mantiene el contrato'),('Propietario idCliente: Long → String/sub; columnas y creación desde JWT','Reglas de autorización por rol y operaciones de negocio que no dependían del antiguo identificador'),('Configuración de audiencia si el nuevo proveedor la requiere','Controladores/repositorios ajenos al cambio de identidad; no reescribir todo el sistema')],[255,254])
p('La lista es corta gracias a un contrato compatible, no porque siempre baste cambiar una URL. El sub es un UUID de Keycloak, por eso el dueño deja de ser Long. Los ids numéricos locales de perfil/producto siguen existiendo. Los registros históricos no se reasignan a nuevas cuentas automáticamente.')
p('<b>En Garritas:</b> ya partimos de Keycloak; no existe un auth-ms temporal propio. Demuestra issuer/jwk/audiences en config-repo, el extractor de roles en SecurityConfiguration, CurrentUser.subject y V2__saga_identity.sql. Compara esa implementación con S07b del ingeniero sin atribuirte un módulo inexistente.')
chapter('22. Guion de demo por integrante y lista de apertura')
table(['Integrante','Primer minuto','Segundo minuto','Tercer minuto'],[('Tú: Venta–Institución','Mostrar prestación en dos sedes y su entidad de unión','Crear compra y seguir el mismo ventaId en Kafka/pedido','Rechazo TRANSFERENCIA y stock restaurado; mostrar Inbox/Outbox'),('Compañera: Envío–Citas','Transportista en dos zonas y dos transportistas en una zona','Reservar cita con detalle, total y duración','Intentar un cruce o confirmar como CLIENTE; después ADMIN confirma'),('Fio: Usuario–Catálogo','Guardar perfil, recargar y mostrar mascota con días/meses; producto ADMIN','Contratar y renovar plan; desplegar períodos y precios históricos','Repetir clave sin duplicar o negar acceso a otro cliente; mostrar cabecera y detalle')],[83,142,142,142])
h('Pestañas preparadas antes de iniciar el reloj')
p('Angular :4200; Kafka UI :18085; Eureka :18761; Grafana :13000; Prometheus :19090; Keycloak :18180/admin/. Prepara las cuentas y los datos con tiempo. Para mostrar N:M de clientes/planes necesitas dos cuentas con perfil de negocio: puedes preparar cliente y la cuenta ADMIN con su perfil, o crear un segundo cliente de laboratorio en Keycloak.')
h('Cómo encontrar código rápido en VS Code')
p('1. Abre Garritas- como carpeta raíz. 2. Ctrl+P y pega una ruta del Mapa-de-codigo.txt. 3. Ctrl+G y escribe la línea. 4. Enseña el método y su regla, no solo el nombre del archivo. Si tu código cambió después de esta revisión, usa el símbolo indicado en el mapa.')
h('Qué enseñar para justificar un CRUD')
p('Controller: verbo/ruta y @Valid → Service: regla y @Transactional → Repository: consulta/persistencia → Entity/SQL: relaciones y restricciones → pantalla Angular: llamada a la API. Para una N:M agrega la entidad de unión, su migración y una asignación visible en ambos sentidos.')
h('Pruebas existentes para ensayar')
ref('uso-rapido/scripts/domain_smoke.py','Recorrido de todos los dominios con roles/propiedad')
ref('uso-rapido/scripts/academic_smoke.py','Demos de las tres parejas y sus N:M')
ref('uso-rapido/scripts/frontend_review.py','Perfil, unidades de edad y revisión móvil')
ref('uso-rapido/scripts/faults.py','Fallas controladas en DEV: detiene procesos/broker')
ref('uso-rapido/scripts/scaling.py','Dos instancias y retiro de la secundaria en DEV')
ref('docs/evidencias-actualizacion/resultado.json','Resultados previos publicados: 24 Java y 13 Angular')
p('Esta guía verifica referencias y explica esas evidencias previas; generarla no vuelve a ejecutar los servicios ni prueba el equipo Windows de cada estudiante. La pasarela externa real del brief final sigue fuera del pago simulado de este laboratorio.')

# Persist a fast, unwrapped code map and a Markdown edition with the same explanations.
(OUT/'Guia-de-sustentacion-Garritas.md').write_text('\n'.join(md))
unique=[];seen=set()
for r in refs:
 key=(r['ruta'],r['linea'],r['explicacion'])
 if key not in seen:seen.add(key);unique.append(r)
(OUT/'mapa-codigo.json').write_text(json.dumps({'commit':REV,'referencias':unique},ensure_ascii=False,indent=2)+'\n')
(OUT/'Mapa-de-codigo.txt').write_text('GARRITAS STORE - MAPA EXACTO DE CÓDIGO\nCommit: '+REV+'\nCtrl+P: pegar ruta; Ctrl+G: saltar a la línea.\n\n'+'\n\n'.join(r['seccion']+'\n'+r['explicacion']+'\n'+r['ruta']+'\nLínea: '+str(r['linea'])+'\n'+r['url'] for r in unique)+'\n')
Doc(str(OUT/'Guia-de-sustentacion-Garritas.pdf'),pagesize=A4,leftMargin=43,rightMargin=43,topMargin=40,bottomMargin=48,title='Garritas Store: guía de sustentación, código y preguntas S6–S11',author='Garritas Store').multiBuild(story,onFirstPage=footer,onLaterPages=footer)
print('PDF generado; referencias verificadas:',len(unique))

# Short oral revision: same verified references, two pages instead of the full atlas.
story=[];md=[]
chapter('Resumen para exponer Garritas',new=False)
p('<b>En 45 segundos:</b> “Garritas es una tienda y plataforma de cuidado de mascotas. Angular usa Gateway para la API; Keycloak autentica. Los ocho microservicios tienen bases independientes. Las consultas inmediatas usan HTTP; la compra se resuelve por Kafka con Saga, idempotencia y compensación”.')
table(['Integrante','Transaccional','Maestro y N:M'],[('Tú','Venta / DetalleVenta','Institución: sedes ↔ prestaciones'),('Compañera','Cita / DetalleCita','Envío: transportistas ↔ zonas'),('Fio','Usuario: suscripción / períodos','Catálogo como maestro; N:M cliente ↔ plan en Usuario')],[75,180,254])
h('Flujo que debes poder contar')
code('Angular → Gateway → Venta valida sede y productos\nVenta + Outbox → Kafka → Catálogo reserva stock\nPago aprobado → Kafka → Venta PAGADA\nPago fallido → Catálogo devuelve stock → Venta CANCELADA')
p('Un 201 de creación no significa pago confirmado. Angular hace polling. Compensar devuelve inventario y conserva historia; no borra la operación ni hace un reembolso bancario real.')
h('Los tres archivos N:M para abrir en VS Code')
ref(src('institucion','entity/SedePrestacion.java'),'Tu pareja: dos @ManyToOne con precio/duración','@ManyToOne')
ref(src('envio','entity/Cobertura.java'),'Compañera: dos @ManyToOne con tarifa/plazo','@ManyToOne')
ref(src('usuario','entity/Suscripcion.java'),'Fio: cliente y plan; períodos como detalle','@ManyToOne')
p('Una tabla de asociación con dos N:1 representa N:M cuando ambos extremos pueden repetirse. Bienestar tiene además @ManyToMany explícito en entity/Profesional.java. No existe una FK que una bases distintas.')
h('Para enseñar un CRUD')
p('Controller: ruta/verbo → Service: regla → Repository: persistencia → Entity/migración: restricciones → Angular: resultado. Venta y Pago no exponen edición/borrado libre; sus estados pertenecen al proceso.')
p('El despacho de compras pertenece a Venta. Envío ahora administra logística. Usuario conserva perfil/mascotas e incorpora contratación/renovación/cancelación de planes.')
chapter('Siete respuestas cortas para recordar')
answers=[
('1. Servicio remoto caído','Los timeouts limitan cuánto espero. En Venta → Catálogo, el Circuit Breaker deja de insistir tras suficientes fallos y el fallback responde controladamente. Feign usa nombre Eureka, conexión 2 s y lectura 3 s; el breaker no reemplaza al timeout.'),
('2. Seguridad solo en Gateway','No basta: podrían llamar al backend directamente. Cada servicio valida el JWT y aplica rol y propiedad. En una ruta protegida: sin token válido, 401; con token válido pero sin permiso, 403. Las consultas públicas son excepciones intencionales.'),
('3. Eventos frente a REST','Gano desacople temporal y puedo procesar cuando el consumidor vuelva. Pierdo el resultado final inmediato: aparecen pendientes, reintentos y posibles duplicados. Por eso uso consistencia eventual e idempotencia; no reemplazo todas las consultas REST por eventos.'),
('4. Fallo a mitad del proceso','La Saga confirma pasos locales y compensa lo necesario: si falla el pago, restaura inventario una vez antes de cancelar. Inbox y restricciones únicas evitan duplicar efectos; Outbox conserva el evento. No hay un ACID global ni entrega exactamente una vez.'),
('5. Evidencia de observabilidad','Grafana ubica la instancia con caída o cambios en HTTP/PostgreSQL. Prometheus permite comprobar targets/errores. Con un mismo X-Trace-ID, Loki muestra los mensajes relacionados de varios servicios en una sola consulta. up=1 no demuestra que una compra haya terminado.'),
('6. Frontend sin URL de instancias','Angular usa una entrada estable, Gateway. Eureka y LoadBalancer resuelven instancias y cambios de cantidad/puerto. Así no acoplo el navegador al despliegue interno. La URL de Keycloak sí se conoce para autenticar; no es una instancia de negocio.'),
('7. Reemplazo de auth por Keycloak','Si los claims/roles son compatibles, se conservan Resource Server y reglas. Cambian issuer/JWKS y el cliente OIDC. Además, el dueño idCliente pasa de Long a String/sub y requiere migración de código/datos. Garritas ya usa Keycloak: no afirma tener un auth propio temporal.')]
for label,answer in answers:h(label);p(answer)
p('<b>Recuerda:</b> password grant no es el flujo usado. La SPA es pública, usa Authorization Code + PKCE y mantiene tokens en memoria, no en localStorage. El carrito sí guarda datos no sensibles. El pago del laboratorio sigue siendo simulado.')
Doc(str(OUT/'Resumen-para-exponer.pdf'),pagesize=A4,leftMargin=43,rightMargin=43,topMargin=40,bottomMargin=48,title='Garritas Store: resumen oral y siete respuestas',author='Garritas Store').multiBuild(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'Resumen-para-exponer.md').write_text('\n'.join(md))
print('Resumen oral generado')
