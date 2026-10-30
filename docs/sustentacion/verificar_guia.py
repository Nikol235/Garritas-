from pathlib import Path
import json,re,subprocess
from pypdf import PdfReader
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
index=json.loads((OUT/'mapa-codigo.json').read_text());commit=index['commit']
for path in {r['ruta'] for r in index['referencias']}:
    expected=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
    assert (ROOT/path).read_bytes()==expected,'Fuente distinta de la revisión enlazada: '+path
for r in index['referencias']:
    lines=(ROOT/r['ruta']).read_text().splitlines();assert 1<=r['linea']<=len(lines)
    if r['simbolo']:assert r['simbolo'] in lines[r['linea']-1]
summary=[]
for filename in ['Guia-de-sustentacion-Garritas.pdf','Resumen-para-exponer.pdf']:
    reader=PdfReader(OUT/filename);texts=[page.extract_text() for page in reader.pages]
    assert all(len(t.strip())>80 for t in texts)
    assert reader.outline
    joined='\n'.join(texts);normalized=re.sub(r'\s+','',joined)
    if filename.startswith('Guia'):
        assert 'Índice' in texts[1]
        for r in index['referencias']:assert re.sub(r'\s+','',r['ruta']) in normalized,r['ruta']
        assert all(t in joined for t in ['preguntas 1–3','preguntas 4–5','preguntas 6–7','Circuit Breaker','PKCE','Idempotency-Key'])
    else:assert len(reader.pages)==2
    links=sum(1 for page in reader.pages for a in page.get('/Annots',[]) if a.get_object().get('/A',{}).get('/URI'))
    assert links>0
    summary.append({'archivo':filename,'paginas':len(reader.pages),'enlaces':links})
    print(filename,len(reader.pages),'páginas;',links,'enlaces; texto y marcadores correctos')
assert len(list((OUT/'diagramas').glob('*.svg')))==11
print('Referencias con ruta, línea y símbolo correctos:',len(index['referencias']))
(OUT/'verificacion.json').write_text(json.dumps({'commit_codigo':commit,'pdfs':summary,'referencias_verificadas':len(index['referencias']),'diagramas':11,'fuentes_iguales_al_commit':True},ensure_ascii=False,indent=2)+'\n')
