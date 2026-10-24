"""Destructive-to-processes DEV checks: pause the local payment JVM and Kafka, then recover.
Run only against uso-rapido/scripts/dev.sh's disposable development stack, after smoke.py.
"""
from pathlib import Path
import json
import os
import signal
import subprocess
import time
import uuid
from playwright.sync_api import sync_playwright
from smoke import login, request, wait_state

ROOT = Path(__file__).resolve().parents[2]


def command(*args, data=None):
    return subprocess.run(args, cwd=ROOT, input=data, text=True, capture_output=True, check=True).stdout


def main():
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_PATH')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        admin_context, _, admin = login(browser, 'admin-store', 'Admin123!')
        customer_context, _, customer = login(browser, 'cliente', 'Cliente123!')
        suffix = str(uuid.uuid4())[:8]
        category = request('/categorias', admin, 'POST', {'nombre': 'Faults ' + suffix}, expected=201)
        product = request('/productos', admin, 'POST', {'nombre': 'Faults ' + suffix, 'precio': 5, 'stock': 10, 'activo': True, 'categoriaId': category['id']}, expected=201)
        def buy(method):
            return request('/ventas', customer, 'POST', {'sedeId': request('/sedes')[0]['id'], 'metodoPago': method, 'detalles': [{'idProducto': product['id'], 'cantidad': 1}]}, str(uuid.uuid4()), expected=201)
        try:
            rejected = buy('TRANSFERENCIA')
            wait_state(rejected['id'], customer, 'CANCELADA')
            assert request('/productos/' + str(product['id']))['stock'] == 10
            payload = command('docker', 'exec', 'garritas-postgres-pago-dev', 'psql', '-U', 'garritas', '-d', 'garritas_pago_db', '-Atc',
                f"SELECT payload FROM outbox_event WHERE aggregate_id='{rejected['id']}' AND payload::jsonb->>'type'='pago.fallido'").strip()
            assert payload
            # Same event, then a semantic duplicate with a new event identity.
            semantic = json.loads(payload)
            semantic['eventId'] = str(uuid.uuid4())
            data = f"{rejected['id']}\t{payload}\n{rejected['id']}\t{json.dumps(semantic)}\n"
            command('docker', 'compose', '-f', 'kafka/compose-dev.yml', 'exec', '-T', 'kafka', '/opt/kafka/bin/kafka-console-producer.sh', '--bootstrap-server', 'localhost:9092', '--topic', 'garritas.ventas.v1', '--property', 'parse.key=true', '--property', 'key.separator=\t', data=data)
            time.sleep(3)
            assert request('/productos/' + str(product['id']))['stock'] == 10
            assert request('/ventas/' + str(rejected['id']), customer)['estado'] == 'CANCELADA'
            print('PASS: replay Kafka y duplicado semántico no restauran stock dos veces', flush=True)

            pid = int((ROOT / '.runtime/garritas-pago-ms.pid').read_text())
            cmdline = Path(f'/proc/{pid}/cmdline').read_bytes()
            assert b'.runtime/garritas-pago-ms/app.jar' in cmdline
            os.kill(pid, signal.SIGTERM)
            time.sleep(3)
            delayed = buy('YAPE')
            wait_state(delayed['id'], customer, 'PENDIENTE_PAGO')
            assert request('/productos/' + str(product['id']))['stock'] == 9
            # Remove the exited process PID file so zombie PIDs cannot mask startup.
            (ROOT / '.runtime/garritas-pago-ms.pid').unlink(missing_ok=True)
            command('bash', 'uso-rapido/scripts/dev.sh', 'up')
            wait_state(delayed['id'], customer, 'PAGADA')
            print('PASS: Pago detenido, venta pendiente y recuperación sin perder el evento', flush=True)

            command('docker', 'compose', '-f', 'kafka/compose-dev.yml', 'stop', 'kafka')
            try:
                queued = buy('PLIN')
                assert queued['estado'] == 'PENDIENTE_STOCK'
                count = command('docker', 'exec', 'garritas-postgres-venta-dev', 'psql', '-U', 'garritas', '-d', 'garritas_venta_db', '-Atc',
                    f"SELECT count(*) FROM outbox_event WHERE aggregate_id='{queued['id']}' AND published_at IS NULL").strip()
                assert count == '1'
            finally:
                command('docker', 'compose', '-f', 'kafka/compose-dev.yml', 'up', '-d', '--wait', '--wait-timeout', '120', 'kafka')
            wait_state(queued['id'], customer, 'PAGADA')
            assert request('/productos/' + str(product['id']))['stock'] == 8
            print('PASS: Kafka detenido, outbox duradero y recuperación del pago', flush=True)
        finally:
            # Ensure a failed assertion cannot leave the broker stopped.
            command('docker', 'compose', '-f', 'kafka/compose-dev.yml', 'up', '-d', '--wait', '--wait-timeout', '120', 'kafka')
            request('/productos/' + str(product['id']), admin, 'DELETE', expected=204)
            customer_context.close()
            admin_context.close()
            browser.close()


if __name__ == '__main__':
    main()
