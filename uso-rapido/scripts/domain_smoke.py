"""Real browser/API review for every business microservice and CLIENTE/ADMIN permissions.
Uses only the local demonstration identities and identifiable test records.
"""
import json
import os
import re
import uuid
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright, expect
from smoke import API, WEB, login, request, wait_state
TOKENS = {}


def prepare_second_client():
    body = urllib.parse.urlencode({'grant_type': 'password', 'client_id': 'admin-cli',
        'username': 'admin', 'password': os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'local-admin-change-me')}).encode()
    with urllib.request.urlopen(urllib.request.Request('http://localhost:18180/realms/master/protocol/openid-connect/token', data=body)) as response:
        token = json.load(response)['access_token']
    base = 'http://localhost:18180/admin/realms/garritas'
    def admin(path, method='GET', data=None):
        req = urllib.request.Request(base+path, method=method, data=None if data is None else json.dumps(data).encode(),
            headers={'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    found = admin('/users?username=cliente-dos&exact=true')
    if not found:
        admin('/users', 'POST', {'username': 'cliente-dos', 'firstName': 'Cliente', 'lastName': 'Dos',
            'email': 'cliente-dos@example.test', 'emailVerified': True, 'enabled': True,
            'credentials': [{'type': 'password', 'value': 'ClienteDos123!', 'temporary': False}]})
        found = admin('/users?username=cliente-dos&exact=true')
    role = admin('/roles/CLIENTE')
    admin('/users/'+found[0]['id']+'/role-mappings/realm', 'POST', [role])


def submit(page, label, method, suffix, expected=200):
    print('CHECK:', label, method, suffix, flush=True)
    with page.expect_response(lambda r: r.request.method == method and r.url.endswith('/api/v1'+suffix)) as pending:
        page.get_by_role('button', name=label, exact=True).click()
    response = pending.value
    assert response.status == expected, f'{method} {suffix}: {response.status}: {response.text()[:300]}'
    if expected==204:return None
    # Read persisted state through a fresh authenticated GET. System Chromium may
    # discard CDP response bodies when several isolated contexts are in use.
    expect(page.locator('main .notice').first).to_be_visible()
    data=request(suffix,TOKENS[page])
    if not isinstance(data,list):return data
    body=response.request.post_data_json
    fields=[k for k in ['nombre','idVenta','motivo'] if k in body]
    matches=[row for row in data if all(row.get(k)==body[k] for k in fields)]
    assert len(matches)==1,(suffix,len(matches))
    return matches[0]


def choose_id(page, label, value):
    select=page.get_by_role('combobox', name=label, exact=True)
    option=select.locator(f'option[value="{value}"], option[value$=": {value}"]')
    expect(option).to_have_count(1)
    select.select_option(value=option.get_attribute('value'))


def main():
    prepare_second_client()
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_PATH')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path': executable} if executable else {}))
        ac, admin_page, admin = login(browser, 'admin-store', 'Admin123!')
        cc, page, cliente = login(browser, 'cliente', 'Cliente123!')
        oc, _, other = login(browser, 'cliente-dos', 'ClienteDos123!')
        TOKENS[admin_page]=admin;TOKENS[page]=cliente
        key = str(uuid.uuid4())[:8]
        request('/usuarios/me', other, 'PUT', {'nombre': 'Cliente dos', 'email': 'otro-'+key+'@example.test'})
        sedes = request('/sedes')
        assert len(sedes) >= 6 and {'Lima','Arequipa','Trujillo','Cusco','Huancayo'} <= {s['ciudad'] for s in sedes}
        request('/sedes', cliente, 'POST', {}, expected=403)
        request('/especialistas', cliente, 'POST', {}, expected=403)
        request('/usuarios', cliente, expected=403)

        admin_page.get_by_role('button', name='Sedes', exact=True).click()
        for label, value in [('Nombre de sede','Sede prueba '+key),('Ciudad','Lima'),('Dirección','Av. de ejemplo 123, Lima'),('Teléfono','999300001')]:
            admin_page.get_by_label(label, exact=True).fill(value)
        sede = submit(admin_page, 'Guardar sede', 'POST', '/sedes', 201)
        admin_page.get_by_role('button', name='Editar '+sede['nombre'], exact=True).click()
        expect(admin_page.get_by_label('Ciudad', exact=True)).to_have_value('Lima')
        admin_page.get_by_label('Ciudad', exact=True).fill('Piura')
        submit(admin_page, 'Guardar sede', 'PUT', '/sedes/'+str(sede['id']))
        page.get_by_role('button', name='Sedes', exact=True).click()
        card = page.locator('article.location-card').filter(has=page.get_by_role('heading', name=sede['nombre'], exact=True))
        expect(card).to_contain_text('Piura')
        expect(card.get_by_role('button', name='Editar', exact=True)).to_have_count(0)
        page.get_by_role('button', name='Seleccionar '+sede['nombre'], exact=True).click()
        expect(page.get_by_role('heading', name='Nueva orden', exact=True)).to_be_visible()
        expect(page.get_by_role('combobox', name='Sede de la compra', exact=True)).to_have_value(re.compile(r'(?:^|: )'+str(sede['id'])+r'$'))
        print('PASS: sedes del Perú, ADMIN crea/edita y CLIENTE solo consulta/selecciona', flush=True)

        page.get_by_role('button', name='Mi cuenta y mascotas', exact=True).click()
        for label, value in [('Nombre completo','Cliente prueba'),('Correo de contacto','cliente-'+key+'@example.test'),('Teléfono de contacto','999300002'),('Dirección de contacto','Av. Arequipa 100, Lima')]:
            page.get_by_label(label, exact=True).fill(value)
        profile = submit(page, 'Guardar perfil', 'PUT', '/usuarios/me')
        assert profile['email'] == 'cliente-'+key+'@example.test', 'El perfil no persistió el correo introducido'
        page.get_by_label('Nombre de mascota', exact=True).fill('Luna '+key)
        page.get_by_role('combobox', name='Especie', exact=True).select_option(label='Gato')
        page.get_by_label('Raza', exact=True).fill('Criolla')
        page.get_by_label('Edad en años', exact=True).fill('3')
        pet = submit(page, 'Guardar mascota', 'POST', '/usuarios/me/mascotas', 201)
        request('/usuarios/me/mascotas/'+str(pet['id']), other, expected=403)
        request('/usuarios/'+str(profile['id'])+'/mascotas', other, expected=403)
        print('PASS: perfil y mascotas persistidos; un segundo cliente no puede acceder a ellas', flush=True)

        admin_page.get_by_role('button', name='Especialistas', exact=True).click()
        admin_page.get_by_label('Nombre de especialidad', exact=True).fill('Especialidad prueba '+key)
        admin_page.get_by_label('Descripción de especialidad', exact=True).fill('Ejemplo de relación muchos a muchos')
        specialty = submit(admin_page, 'Guardar especialidad', 'POST', '/especialidades', 201)
        for label,value in [('Nombre del profesional','Profesional '+key),('Correo del profesional',key+'@example.test'),('Teléfono del profesional','999300003')]:
            admin_page.get_by_label(label, exact=True).fill(value)
        choose_id(admin_page,'Sede de atención',sede['id'])
        admin_page.get_by_role('checkbox', name='Medicina general', exact=True).check()
        admin_page.get_by_role('checkbox', name=specialty['nombre'], exact=True).check()
        professional = submit(admin_page, 'Guardar profesional', 'POST', '/especialistas', 201)
        assert len(professional['especialidades']) == 2
        ids = [e['id'] for e in professional['especialidades']]
        second = request('/especialistas', admin, 'POST', {'nombre':'Segundo '+key,'email':'segundo-'+key+'@example.test','sedeId':sede['id'],'activo':True,'especialidadIds':ids+ids}, expected=201)
        assert len(second['especialidades']) == 2
        assert sum(specialty['id'] in [e['id'] for e in item['especialidades']] for item in request('/especialistas')) == 2
        request('/especialidades/'+str(specialty['id']), admin, 'DELETE', expected=409)
        print('PASS: Bienestar muchos a muchos real, especialidades compartidas y asociación sin duplicados', flush=True)

        page.get_by_role('button', name='Citas', exact=True).click()
        choose_id(page,'Mascota para la cita',pet['id'])
        choose_id(page,'Sede para la cita',sede['id'])
        choose_id(page,'Profesional',professional['id'])
        date = (datetime.now(timezone.utc)+timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0)
        page.get_by_label('Fecha y hora de la cita', exact=True).fill(date.strftime('%Y-%m-%dT%H:%M'))
        page.get_by_label('Motivo de la cita', exact=True).fill('Revisión de Luna '+key)
        cita = submit(page, 'Reservar cita', 'POST', '/citas', 201)
        request('/citas', cliente, 'POST', {'idMascota':pet['id'],'idSede':sede['id'],'profesionalId':professional['id'],'fechaHora':date.isoformat(),'motivo':'Duplicada'}, expected=409)
        request('/citas/'+str(cita['id']), other, expected=403)
        request('/citas/'+str(cita['id'])+'/confirmar', cliente, 'POST', expected=403)
        admin_page.get_by_role('button', name='Citas', exact=True).click()
        row = admin_page.get_by_role('row').filter(has_text='Revisión de Luna '+key)
        with admin_page.expect_response(lambda r: r.request.method=='POST' and r.url.endswith('/citas/'+str(cita['id'])+'/confirmar')) as res:
            row.get_by_role('button', name='Confirmar', exact=True).click()
        assert res.value.status == 200
        with admin_page.expect_response(lambda r: r.request.method=='POST' and r.url.endswith('/citas/'+str(cita['id'])+'/atender')) as res:
            row.get_by_role('button', name='Marcar atendida', exact=True).click()
        assert res.value.status == 200
        request('/citas/'+str(cita['id'])+'/cancelar', cliente, 'POST', expected=409)
        print('PASS: cita desde Angular con mascota/sede/profesional, sin doble reserva y con permisos de estado', flush=True)

        admin_page.get_by_role('button', name='Productos', exact=True).click()
        category = next(c for c in request('/categorias') if c['nombre']=='Alimentos')
        for label,value in [('Nombre del producto','Alimento prueba '+key),('Precio en soles','12.50'),('Stock disponible','8')]:
            admin_page.get_by_label(label, exact=True).fill(value)
        choose_id(admin_page,'Categoría del producto',category['id'])
        product = submit(admin_page, 'Guardar producto', 'POST', '/productos', 201)
        page.get_by_role('button', name='Nueva orden', exact=True).click()
        page.get_by_role('button', name='Actualizar catálogo', exact=True).click()
        page.get_by_role('button', name='Añadir '+product['nombre']+' al carrito', exact=True).click()
        with page.expect_response(lambda r: r.request.method=='POST' and r.url.endswith('/api/v1/ventas')) as response:
            page.get_by_role('button', name='Confirmar compra', exact=True).click()
        assert response.value.status == 201, response.value.text()
        venta = next(v for v in request('/ventas',cliente) if v['sedeId']==sede['id'] and any(d['idProducto']==product['id'] for d in v['detalles']))
        assert venta['sedeId'] == sede['id']
        wait_state(venta['id'], cliente, 'PAGADA')
        assert request('/productos/'+str(product['id']))['stock'] == 7
        request('/ventas/'+str(venta['id']), other, expected=403)
        print('PASS: producto gestionado en Angular, compra por sede, Kafka, pago y stock correctos', flush=True)

        page.get_by_role('button', name='Envíos', exact=True).click()
        choose_id(page,'Pedido pagado',venta['id'])
        page.get_by_label('Dirección de entrega', exact=True).fill('Av. de ejemplo 456, Miraflores, Lima')
        envio = submit(page, 'Solicitar envío', 'POST', '/envios', 201)
        request('/envios/'+str(envio['id']), other, expected=403)
        request('/envios/'+str(envio['id'])+'/en-transito', cliente, 'POST', expected=403)
        request('/envios', cliente, 'POST', {'idVenta':venta['id'],'direccionEntrega':'Duplicado'}, expected=409)
        admin_page.get_by_role('button', name='Envíos', exact=True).click()
        shipping = admin_page.locator('article').filter(has=admin_page.get_by_role('heading', name='Envío #'+str(envio['id']), exact=True))
        with admin_page.expect_response(lambda r: r.request.method=='POST' and r.url.endswith('/envios/'+str(envio['id'])+'/en-transito')) as res:
            shipping.get_by_role('button', name='Marcar en tránsito', exact=True).click()
        assert res.value.status==200
        with admin_page.expect_response(lambda r: r.request.method=='POST' and r.url.endswith('/envios/'+str(envio['id'])+'/entregado')) as res:
            shipping.get_by_role('button', name='Marcar entregado', exact=True).click()
        assert res.value.status==200
        assert request('/envios/'+str(envio['id']), cliente)['estado']=='ENTREGADO'
        request('/pagos/venta/'+str(venta['id']), other, expected=403)
        page.get_by_role('button', name='Pagos', exact=True).click()
        expect(page.get_by_role('row').filter(has_text='#'+str(venta['id'])).first).to_be_visible()
        admin_page.get_by_role('button', name='Clientes', exact=True).click()
        expect(admin_page.get_by_role('row').filter(has_text='cliente-'+key+'@example.test')).to_be_visible()
        print('PASS: envío entregado desde Angular, pagos y clientes visibles con separación por propietario', flush=True)

        request('/productos/'+str(product['id']), admin, 'DELETE', expected=204)
        request('/especialistas/'+str(professional['id']), admin, 'DELETE', expected=204)
        request('/especialistas/'+str(second['id']), admin, 'DELETE', expected=204)
        request('/sedes/'+str(sede['id']), admin, 'DELETE', expected=204)
        ac.close();cc.close();oc.close();browser.close()


if __name__ == '__main__':
    main()
