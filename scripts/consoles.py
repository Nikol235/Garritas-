"""Verify that local service consoles can actually be opened and used in a browser."""
import json
import os
import re
import urllib.request
from playwright.sync_api import sync_playwright, expect


def get_json(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=10) as response:
        return json.load(response)


def main():
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_PATH')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        page = browser.new_page()
        page.goto('http://localhost:18085/')
        expect(page.get_by_text('garritas', exact=True).first).to_be_visible(timeout=30000)
        clusters = get_json('http://localhost:18085/api/clusters')
        assert clusters and all(c['status'] == 'ONLINE' for c in clusters)
        print('PASS: Kafka UI abre y muestra el broker conectado', flush=True)

        page.goto('http://localhost:18180/admin/')
        page.locator('#username').fill('admin')
        page.locator('#password').fill(os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'local-admin-change-me'))
        page.locator('#kc-login').click()
        page.wait_for_function("document.body.innerText.includes('Realm settings')", timeout=30000)
        print('PASS: consola administrativa Keycloak permite iniciar sesión', flush=True)

        page.goto('http://localhost:18761/')
        expect(page.get_by_text('GARRITAS-CATALOGO-MS', exact=True).first).to_be_visible()
        apps = get_json('http://localhost:18761/eureka/apps', {'Accept': 'application/json'})['applications']['application']
        assert len(apps) >= 8
        print('PASS: Eureka abre con los siete servicios y Gateway registrados', flush=True)

        page.goto('http://localhost:13000/login')
        page.locator('input[name="user"]').fill('admin')
        password = os.environ.get('GRAFANA_ADMIN_PASSWORD', 'local-grafana')
        page.locator('input[name="password"]').fill(password)
        page.get_by_role('button', name='Log in', exact=True).click()
        page.wait_for_url(lambda url: '/login' not in url, timeout=30000)
        dashboards = page.request.get('http://localhost:13000/api/search?type=dash-db').json()
        assert len(dashboards) >= 2, 'No se cargaron los dashboards aprovisionados'
        for uid in ['garritas-prometheus', 'garritas-loki']:
            response = page.request.get('http://localhost:13000/api/datasources/uid/' + uid + '/health')
            assert response.ok, 'La fuente de datos no responde: ' + uid
            assert response.json().get('status') == 'OK', response.json().get('message')
        print('PASS: Grafana abre, carga dashboards y conecta con Prometheus y Loki', flush=True)

        page.goto('http://localhost:19090/query')
        expect(page).to_have_title(re.compile(r'^Prometheus'))
        targets = get_json('http://localhost:19090/api/v1/targets')['data']['activeTargets']
        assert len(targets) >= 11 and all(t['health'] == 'up' for t in targets), [(t['labels'].get('job'), t['health']) for t in targets]
        logs = get_json('http://localhost:13100/loki/api/v1/label/application/values')['data']
        assert 'garritas-catalogo-ms' in logs
        print('PASS: Prometheus muestra todos los targets UP; Loki recibe logs de Catálogo', flush=True)
        browser.close()


if __name__ == '__main__':
    main()
