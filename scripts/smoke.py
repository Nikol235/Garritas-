"""Real PKCE browser + Gateway + PostgreSQL + Kafka integration checks.
Requires DEV stack, Angular at :4200, and playwright (Chromium or CHROMIUM_PATH).
Fixture products are deactivated; categories and sale/payment audit history are retained.
"""
import json
import os
import time
import uuid
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright, expect

API = os.environ.get('API_URL', 'http://localhost:18080/api/v1')
WEB = os.environ.get('WEB_URL', 'http://localhost:4200')


def request(path, token=None, method='GET', body=None, key=None, expected=200):
    headers = {'Content-Type': 'application/json', 'X-Trace-ID': 'smoke-garritas'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if key:
        headers['Idempotency-Key'] = key
    req = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(), headers=headers, method=method)
    try:
        response = urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    data = response.read()
    assert response.status == expected, f'{method} {path}: expected {expected}, got {response.status}: {data[:250]!r}'
    return json.loads(data) if data else None


def login(browser, username, password):
    context = browser.new_context()
    page = context.new_page()
    page.goto(WEB)
    page.get_by_role('button', name='Iniciar sesión', exact=True).click()
    page.locator('#username').fill(username)
    page.locator('#password').fill(password)
    with page.expect_response(lambda response: '/protocol/openid-connect/token' in response.url and response.status == 200) as exchange:
        page.locator('#kc-login').click()
    session = exchange.value.json()
    expect(page.get_by_role('button', name='Salir', exact=True)).to_be_visible(timeout=30000)
    assert session.get('access_token'), 'PKCE did not return an access token'
    assert page.evaluate('Object.values(localStorage).every(v=>!v.includes("access_token")&&!v.startsWith("eyJ"))')
    return context, page, session['access_token']


def wait_state(venta_id, token, wanted):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        venta = request('/ventas/' + str(venta_id), token)
        if venta['estado'] == wanted:
            return venta
        time.sleep(.5)
    raise AssertionError(f'Venta {venta_id}: expected {wanted}, got {venta["estado"]}')


def main():
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_PATH')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        admin_context, _, admin = login(browser, 'admin-store', 'Admin123!')
        context, page, cliente = login(browser, 'cliente', 'Cliente123!')
        print('PASS: login real PKCE con Keycloak, sesión Angular sin tokens persistidos')
        suffix = str(uuid.uuid4())[:8]
        categoria = request('/categorias', admin, 'POST', {'nombre': 'Smoke ' + suffix, 'descripcion': 'Prueba de integración'}, expected=201)
        producto = request('/productos', admin, 'POST', {'nombre': 'Alimento ' + suffix, 'descripcion': 'Prueba de integración', 'precio': 12.5, 'stock': 10, 'activo': True, 'categoriaId': categoria['id']}, expected=201)
        try:
            request('/ventas', expected=401)
            request('/productos', cliente, 'POST', {}, expected=403)
            request('/productos/' + str(producto['id']))
            print('PASS: catálogo público, ventas protegidas y escritura solo ADMIN')
            # Browser CORS request, real purchase, and eventual state rendering.
            page.get_by_role('button', name='Actualizar catálogo').click()
            quantity = page.get_by_label('Cantidad de ' + producto['nombre'], exact=True)
            expect(quantity).to_be_visible()
            quantity.fill('1')
            page.get_by_role('button', name='Comprar', exact=True).click()
            expect(page.get_by_role('heading', name='Mis pedidos', exact=True)).to_be_visible()
            expect(page.locator('.order').first.locator('.badge')).to_have_text('PAGADA', timeout=45000)
            assert request('/productos/' + str(producto['id']))['stock'] == 9
            print('PASS: compra desde Angular, CORS, reserva, pago Kafka y polling hasta PAGADA')
            body = {'metodoPago': 'TRANSFERENCIA', 'detalles': [{'idProducto': producto['id'], 'cantidad': 2}]}
            key = str(uuid.uuid4())
            venta = request('/ventas', cliente, 'POST', body, key, expected=201)
            assert request('/ventas', cliente, 'POST', body, key, expected=201)['id'] == venta['id']
            modified = {**body, 'metodoPago': 'YAPE'}
            request('/ventas', cliente, 'POST', modified, key, expected=409)
            wait_state(venta['id'], cliente, 'CANCELADA')
            assert request('/productos/' + str(producto['id']))['stock'] == 9
            assert request('/pagos/venta/' + str(venta['id']), cliente)['estado'] == 'RECHAZADO'
            print('PASS: rechazo, compensación de stock e idempotencia HTTP con conflicto de payload')
            request('/ventas', cliente, 'POST', {'metodoPago': 'YAPE', 'detalles': [{'idProducto': producto['id'], 'cantidad': 999}]}, str(uuid.uuid4()), expected=409)
            request('/ventas', cliente, 'POST', {'metodoPago': 'YAPE', 'detalles': [{'idProducto': producto['id'], 'cantidad': 0}]}, str(uuid.uuid4()), expected=400)
            request('/ventas', cliente, 'POST', body, expected=400)
            print('PASS: sin sobreventa, cantidad inválida y clave obligatoria')
            preflight = urllib.request.urlopen(urllib.request.Request(API + '/ventas', method='OPTIONS', headers={'Origin': WEB, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'authorization,content-type,idempotency-key'}))
            assert preflight.headers['Access-Control-Allow-Origin'] == WEB
            print('PASS: preflight CORS con Authorization e Idempotency-Key')
        finally:
            request('/productos/' + str(producto['id']), admin, 'DELETE', expected=204)
            # Category remains associated with the deactivated product for audit.
            context.close()
            admin_context.close()
            browser.close()


if __name__ == '__main__':
    main()
