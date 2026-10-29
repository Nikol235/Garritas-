#!/usr/bin/env python3
"""Comprueba legibilidad, cobertura de rutas y hashes del material entregado."""
from pathlib import Path
import hashlib, json, re, zipfile
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/manuales'
manifest=json.loads((OUT/'MANIFIESTO-CODIGO.json').read_text())
expected={x['ruta']:x for x in manifest['archivos']}
with zipfile.ZipFile(OUT/'Garritas-Store-codigo-base.zip') as z:
 assert z.testzip() is None
 for path,item in expected.items():
  content=z.read('Garritas-Store/'+path)
  assert hashlib.sha256(content).hexdigest()==item['sha256'],path
  assert not path.endswith('.env'),path
 print('ZIP:',len(expected),'archivos con SHA-256 correcto')
texts={};summary=[]
for p in sorted(OUT.glob('*.pdf')):
 reader=PdfReader(p)
 assert not reader.is_encrypted,p
 pages=[page.extract_text() for page in reader.pages]
 assert all(len(t.strip())>20 for t in pages),'Página vacía en '+p.name
 if not p.name.startswith('04-'):
  assert reader.outline,'Falta índice de marcadores'
  assert 'Índice' in pages[1]
 else:
  for command in ['git clone --branch feat/garritas-store https://github.com/Nikol235/Garritas-.git', r'.\uso-rapido\garritas.ps1 -Accion build', r'.\uso-rapido\garritas.ps1 -Accion iniciar']:
   assert command in '\n'.join(pages), 'Comando cortado: '+command
 assert not any('Placeholder for table of contents' in t for t in pages)
 texts[p.name]=re.sub(r'\s+','', ''.join(pages))
 summary.append({'archivo':p.name,'paginas':len(pages),'bytes':p.stat().st_size})
 print(p.name,len(pages),'páginas; texto, índice y marcadores OK')
tech=texts['03-Arquitectura-clases-y-conexiones.pdf']
for p in expected:
 if p.endswith(('.java','.ts')):
  assert re.sub(r'\s+','',p) in tech, 'Falta ficha técnica de '+p
construction=texts['02-Construccion-desde-cero-con-codigo.pdf']
for p in expected:
 if p.endswith(('.java','.ts','.sql')):
  assert re.sub(r'\s+','',p) in construction, 'Falta código de '+p
for p in OUT.joinpath('diagramas').glob('*.svg'):
 assert p.with_suffix('.png').exists()
print('Cobertura de Java/TypeScript/SQL y diagramas: OK')
(OUT/'verificacion-documental.json').write_text(json.dumps({'pdfs':summary,'archivos_zip':len(expected),'hashes_zip':'OK','cobertura_clases_y_sql':'OK','paginas_sin_vacios':'OK'},ensure_ascii=False,indent=2))
