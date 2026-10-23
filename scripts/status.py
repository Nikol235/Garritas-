"""Check useful application responses, including Kafka's actual cluster connection."""
import concurrent.futures
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ('Tienda Angular', 4200, '/'),
    ('Kafka UI', 18085, '/api/clusters'),
    ('Keycloak', 18180, '/realms/garritas/.well-known/openid-configuration'),
    ('Eureka', 18761, '/actuator/health/readiness'),
    ('Config Server', 18888, '/actuator/health/readiness'),
    ('Gateway', 18080, '/actuator/health/readiness'),
    ('Catálogo por Gateway', 18080, '/api/v1/productos'),
    *[(name, port, '/actuator/health/readiness') for name, port in [
        ('Venta', 8081), ('Institución', 8082), ('Envío', 8083), ('Citas', 8084),
        ('Catálogo', 8085), ('Usuario', 8086), ('Pago', 8087)]],
]
if '--observability' in sys.argv:
    TARGETS += [('Grafana', 13000, '/api/health'), ('Prometheus', 19090, '/-/ready'), ('Loki', 13100, '/ready')]


def check(target):
    name, port, path = target
    try:
        with urllib.request.urlopen(f'http://localhost:{port}{path}', timeout=5) as response:
            body = response.read()
            if name == 'Kafka UI':
                clusters = json.loads(body)
                assert clusters and all(str(c.get('status')).upper() == 'ONLINE' for c in clusters), 'Kafka no está conectado'
            elif name == 'Catálogo por Gateway':
                assert isinstance(json.loads(body), list)
            elif name == 'Keycloak':
                assert '/realms/garritas' in json.loads(body)['issuer']
            elif name == 'Tienda Angular':
                assert b'<app-root' in body
        return name, port, 'OK', True
    except Exception as error:
        return name, port, str(error), False


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(check, TARGETS))
    for name, port, detail, ok in results:
        print(f'{"OK" if ok else "FALLO":5} {name:24} puerto {port:<5} {"" if ok else detail}')
    broker = subprocess.run(['docker', 'compose', '-f', 'compose-dev.yml', 'exec', '-T', 'kafka', '/opt/kafka/bin/kafka-topics.sh', '--bootstrap-server', 'localhost:9092', '--list'], cwd=ROOT, capture_output=True, text=True, timeout=20)
    topics_ok = broker.returncode == 0 and 'garritas.ventas.v1' in broker.stdout
    print(f'{"OK" if topics_ok else "FALLO":5} Kafka broker y topic de ventas')
    return 0 if all(ok for *_, ok in results) and topics_ok else 1


if __name__ == '__main__':
    sys.exit(main())
