from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

base=Path(__file__).resolve().parent
for name,file in [('Text','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='Bold',italic='Text',boldItalic='Bold')
normal=ParagraphStyle('normal',fontName='Text',fontSize=9,leading=12,spaceAfter=5)
heading=ParagraphStyle('heading',fontName='Bold',fontSize=10,leading=13,spaceBefore=7,spaceAfter=4,textColor=colors.HexColor('#245b47'))
code=ParagraphStyle('code',fontName='Mono',fontSize=8.2,leading=11,spaceAfter=5)
title=ParagraphStyle('title',fontName='Bold',fontSize=17,leading=21,spaceAfter=9,textColor=colors.HexColor('#245b47'))
story=[Paragraph('Garritas Store · Comandos rápidos',title),Paragraph('En <b>PowerShell</b>, con <b>Docker Desktop abierto</b>, ejecuten los bloques en orden.',normal)]
def section(label,commands):
    story.append(Paragraph(label,heading))
    for line in commands.splitlines():assert pdfmetrics.stringWidth(line,'Mono',8.2)<A4[0]-72
    story.append(Preformatted(commands,code))
section('1. Clonar y entrar:',r'''cd $HOME
New-Item -ItemType Directory -Force proyectos
cd proyectos
git clone --branch feat/garritas-store https://github.com/Nikol235/Garritas-.git
cd Garritas-''')
section('2. Permitir el script y compilar:',r'''Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion build''')
story.append(Paragraph('Si Angular pregunta (y/N), escriban <b>N</b> y presionen Enter. Esperen a que termine sin errores.',normal))
section('3. Iniciar todo:',r'''.\uso-rapido\garritas.ps1 -Accion iniciar''')
story.append(Paragraph('Se pueden abrir varias consolas: <b>no las cierren ni ejecuten iniciar otra vez</b>.',normal))
section('4. Consultar estado desde otra PowerShell:',r'''cd "$HOME\proyectos\Garritas-"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion estado''')
section('5. Abrir la tienda:',r'''Start-Process "http://localhost:4200"''')
story.append(Paragraph('• Cliente: <b>cliente</b> / <b>Cliente123!</b><br/>• Administrador: <b>admin-store</b> / <b>Admin123!</b>',normal))
section('Opcional: iniciar Grafana y Prometheus:',r'''docker compose -f obs/compose-dev.yml up -d
Start-Process "http://localhost:13000"
Start-Process "http://localhost:19090"''')
section('Para detener Java y Angular al terminar:',r'''.\uso-rapido\garritas.ps1 -Accion detener''')
SimpleDocTemplate(str(base/'Comandos-rapidos-Garritas.pdf'),pagesize=A4,leftMargin=36,rightMargin=36,topMargin=30,bottomMargin=30,title='Garritas Store: comandos rápidos PowerShell',author='Garritas Store').build(story)
