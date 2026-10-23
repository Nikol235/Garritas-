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


def sign_in(page, username, password, button='Iniciar sesión'):
    page.get_by_role('button', name=button, exact=True).click()
    page.locator('#username').fill(username)
    page.locator('#password').fill(password)
    with page.expect_response(lambda response: '/protocol/openid-connect/token' in response.url and response.status == 200) as exchange:
        page.locator('#kc-login').click()
    session = exchange.value.json()
    expect(page.get_by_role('button', name='Salir', exact=True)).to_be_visible(timeout=30000)
    assert session.get('access_token'), 'PKCE did not return an access token'
    assert page.evaluate('Object.values(localStorage).every(v=>!v.includes("access_token")&&!v.startsWith("eyJ"))')
    return session['access_token']


def login(browser, username, password):
    context = browser.new_context()
    page = context.new_page()
    page.goto(WEB)
    token = sign_in(page, username, password)
    return context, page, token


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
        context = browser.new_context()
        page = context.new_page()
        suffix = str(uuid.uuid4())[:8]
        categoria = request('/categorias', admin, 'POST', {'nombre': 'Smoke ' + suffix, 'descripcion': 'Prueba de integración'}, expected=201)
        producto = request('/productos', admin, 'POST', {'nombre': 'Alimento ' + suffix, 'descripcion': 'Prueba de integración', 'precio': 12.5, 'stock': 10, 'activo': True, 'categoriaId': categoria['id']}, expected=201)
        toy = request('/productos', admin, 'POST', {'nombre': 'Juguete ' + suffix, 'descripcion': 'Prueba de carrito', 'precio': 7.99, 'stock': 5, 'activo': True, 'categoriaId': categoria['id']}, expected=201)
        try:
            page.goto(WEB)
            page.get_by_role('button', name='Nueva orden', exact=True).click()
            expect(page.get_by_role('heading', name='Nueva orden', exact=True)).to_be_visible()
            page.get_by_role('combobox', name='Categoría', exact=True).select_option(label='Alimentos')
            expect(page.get_by_role('button', name='Añadir Alimento para gato adulto 1 kg al carrito', exact=True)).to_be_visible()
            page.get_by_role('combobox', name='Categoría', exact=True).select_option(label='Todas las categorías')
            page.get_by_role('searchbox', name='Buscar productos').fill('gato adulto')
            expect(page.locator('.product-card')).to_have_count(1)
            page.get_by_role('searchbox', name='Buscar productos').fill('')
            page.get_by_role('button', name='Añadir ' + producto['nombre'] + ' al carrito', exact=True).click()
            page.get_by_role('button', name='Añadir ' + toy['nombre'] + ' al carrito', exact=True).click()
            quantity = page.get_by_label('Cantidad de ' + producto['nombre'], exact=True)
            quantity.fill('2'); quantity.press('Tab')
            expect(page.get_by_test_id('cart-total')).to_contain_text('32.99')
            page.get_by_role('button', name='Quitar ' + toy['nombre'], exact=True).click()
            expect(page.get_by_test_id('cart-total')).to_contain_text('25.00')
            quantity.fill('1'); quantity.press('Tab')
            expect(page.get_by_test_id('cart-total')).to_contain_text('12.50')
            cliente = sign_in(page, 'cliente', 'Cliente123!', 'Inicia sesión para comprar')
            expect(page.get_by_label('Cantidad de ' + producto['nombre'], exact=True)).to_have_value('1')
            page.reload()
            expect(page.get_by_role('button', name='Salir', exact=True)).to_be_visible(timeout=30000)
            expect(page.get_by_label('Cantidad de ' + producto['nombre'], exact=True)).to_have_value('1')
            print('PASS: Nueva orden, catálogo de mascotas, filtros, cantidades, subtotales y quitar productos')
            print('PASS: carrito conservado al iniciar sesión y recargar, sesión PKCE sin tokens persistidos')
            request('/ventas', expected=401)
            request('/productos', cliente, 'POST', {}, expected=403)
            request('/productos/' + str(producto['id']))
            print('PASS: catálogo público, ventas protegidas y escritura solo ADMIN')
            page.get_by_role('button', name='Confirmar compra', exact=True).click()
            expect(page.get_by_role('heading', name='Mis pedidos', exact=True)).to_be_visible()
            expect(page.locator('.order').first.locator('.badge')).to_have_text('PAGADA', timeout=45000)
            expect(page.get_by_role('button', name='Carrito, 0 unidades', exact=True)).to_be_visible()
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
            request('/productos/' + str(toy['id']), admin, 'DELETE', expected=204)
            # Category remains associated with the deactivated product for audit.
            context.close()
            admin_context.close()
            browser.close()


if __name__ == '__main__':
    main()
