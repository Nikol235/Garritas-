"""Guía breve de ejecución actual para Windows, con texto y comandos copiables."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Preformatted,Spacer,PageBreak,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
base=Path(__file__).resolve().parent
for n,f in [('Text','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='Bold',italic='Text',boldItalic='Bold')
text=ParagraphStyle('text',fontName='Text',fontSize=9,leading=12,spaceAfter=7)
small=ParagraphStyle('small',fontName='Text',fontSize=7.8,leading=10)
head=ParagraphStyle('head',fontName='Bold',fontSize=11,leading=14,spaceBefore=8,spaceAfter=5,textColor=colors.HexColor('#245b47'))
mono=ParagraphStyle('mono',fontName='Mono',fontSize=8.2,leading=11,spaceAfter=8)
title=ParagraphStyle('title',fontName='Bold',fontSize=19,leading=23,spaceAfter=10,textColor=colors.HexColor('#245b47'))
story=[]
def p(t):story.append(Paragraph(t,text))
def h(t):story.append(Paragraph(t,head))
def code(t):
 for line in t.splitlines():assert pdfmetrics.stringWidth(line,'Mono',8.2)<A4[0]-76,line
 story.append(Preformatted(t,mono))
def table(headers,rows,widths):
 cells=[[Paragraph(escape(str(c)),small) for c in row] for row in [headers,*rows]]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deebe1')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#cddbd2')),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.extend([t,Spacer(1,5)])
def footer(c,d):
 c.setFont('Text',7);c.setFillColor(colors.HexColor('#52685a'));c.drawString(38,23,'Garritas Store · Windows / PowerShell · Código base f2420cd');c.drawRightString(A4[0]-38,23,str(d.page))
story.append(Paragraph('Garritas Store · Inicio y puertos',title))
p('Guía breve para <b>Windows con PowerShell</b>. Copia solo los comandos de cada bloque y ejecútalos por orden. Espera a que termine cada paso; si falla, detente antes de continuar.')
h('1. Requisitos')
p('Instala <b>Git, JDK 21 completo, Node.js 24 y Docker Desktop</b>. Mantén Docker Desktop abierto, con motor Linux. Abre una PowerShell nueva después de instalar y comprueba:')
code('git --version\njava -version\njavac -version\nnode --version\ndocker info')
p('Java y javac: versión 21. Node: v24.x.x. Docker info debe mostrar <b>Server</b> sin errores.')
h('2. Clonar y entrar')
code('cd $HOME\nNew-Item -ItemType Directory -Force proyectos\ncd proyectos\ngit clone --branch feat/garritas-store https://github.com/Nikol235/Garritas-.git\ncd Garritas-')
p('Si la carpeta ya existe, no clones encima ni la borres. Trabaja siempre en la misma copia: no alternes entre C: y D:.')
h('3. Permitir el script y compilar')
code(r'''Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion build''')
p('Si Angular pregunta por estadísticas <b>(y/N)</b>, escribe <b>N</b> y pulsa Enter. Espera a que Java y Angular terminen sin errores. El permiso del script dura solo para esta ventana.')
h('4. Iniciar todo')
code(r'.\uso-rapido\garritas.ps1 -Accion iniciar')
p('Inicia bases, Kafka, Keycloak, Config, Eureka, ocho servicios, Gateway y Angular; aplica migraciones y conserva el archivo histórico de despachos. Los procesos nuevos se ejecutan ocultos y dejan logs en <b>.runtime</b>. <b>No ejecutes iniciar dos veces.</b>')
h('5. Añadir monitorización y consultar estado')
code(r'''docker compose -f obs/compose-dev.yml up -d
.\uso-rapido\garritas.ps1 -Accion estado''')
p('Si la terminal sigue ocupada, abre otra PowerShell con Windows + R → powershell y ejecuta:')
code(r'''cd "$HOME\proyectos\Garritas-"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion estado''')
story.append(PageBreak())
h('6. Enlaces de la tienda y las consolas')
p('Abre estos enlaces en el equipo donde ejecutaste el proyecto. <b>localhost no apunta al equipo de otra compañera.</b>')
table(['Aplicación','Dirección'],[
('Angular — tienda','http://localhost:4200'),('Kafka UI','http://localhost:18085'),('Keycloak — administración','http://localhost:18180/admin/'),('Eureka','http://localhost:18761'),('Config — salud','http://localhost:18888/actuator/health'),('Gateway — catálogo API','http://localhost:18080/api/v1/productos'),('Grafana','http://localhost:13000'),('Prometheus','http://localhost:19090'),('Loki — estado de API','http://localhost:13100/ready')],[185,334])
h('Puertos de los ocho microservicios')
table(['Microservicio','HTTP','PostgreSQL'],[('Venta y despachos','8081','15441'),('Institución: sedes/prestaciones','8082','15442'),('Envío: logística','8083','15443'),('Citas','8084','15444'),('Catálogo','8085','15445'),('Usuario: perfil/mascotas/suscripciones','8086','15446'),('Pago','8087','15447'),('Bienestar','8088','15448')],[309,85,125])
p('Salud de ejemplo: <b>http://localhost:8081/actuator/health</b>. Sus pantallas están en Angular; los servicios devuelven JSON y las API protegidas requieren JWT. Kafka usa TCP 19092 en el host: no es una página web.')
h('7. Cuentas de demostración')
table(['Acceso','Usuario','Contraseña'],[('Cliente Angular','cliente','Cliente123!'),('Administrador Angular','admin-store','Admin123!'),('Administrador Keycloak','admin','local-admin-change-me'),('Grafana','admin','local-grafana')],[180,139,200])
h('8. Detener Java y Angular')
code(r'.\uso-rapido\garritas.ps1 -Accion detener')
p('Los contenedores y datos se conservan. No uses <b>down -v</b> como limpieza: elimina volúmenes. Si aparece “arranque registrado”, revisa estado o usa detener antes de reiniciar. No borres manualmente el registro de procesos.')
p('La validación publicada corresponde a DEV Linux; no certifica todas las configuraciones Windows ni el Compose integral. Los pagos son simulados.')
SimpleDocTemplate(str(base/'Inicio-y-puertos-Garritas.pdf'),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=30,bottomMargin=38,title='Garritas Store: desde la clonación hasta los puertos',author='Garritas Store').build(story,onFirstPage=footer,onLaterPages=footer)
