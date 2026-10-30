"""Idempotent DEV migration between databases. Never deletes the source archive."""
from pathlib import Path
import argparse,json,subprocess

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--origen',default='garritas-postgres-envio-dev')
    parser.add_argument('--destino',default='garritas-postgres-venta-dev')
    args=parser.parse_args()
    query="SELECT COALESCE(json_agg(row_to_json(e)),'[]'::json) FROM envios e"
    result=subprocess.run(['docker','exec',args.origen,'psql','-U','garritas','-d','garritas_envio_db','-Atc',query],check=True,capture_output=True,text=True).stdout.strip()
    rows=json.loads(result)
    if not rows:
        print('Despachos: no hay registros históricos para migrar.');return
    # ASCII JSON and SQL-literal escaping preserve accents/quotes across PowerShell/PTY encodings.
    payload=json.dumps(rows,ensure_ascii=True).replace("'","''")
    sql=Path(__file__).with_name('migrar-despachos.sql').read_text().replace('__LEGACY_JSON__',payload)
    inserted=subprocess.run(['docker','exec','-i',args.destino,'psql','-v','ON_ERROR_STOP=1','-U','garritas','-d','garritas_venta_db'],input=sql,text=True,capture_output=True)
    if inserted.returncode:
        detail=inserted.stderr.splitlines()[0] if inserted.stderr else 'psql no completó la transacción'
        raise SystemExit('No se migraron despachos; el origen se conserva. '+detail)
    print(f'Despachos: {len(rows)} históricos comprobados; origen conservado, destino sin duplicados.')

if __name__=='__main__':main()
