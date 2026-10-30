"""DEV browser review: saved profile, explicit pet age, API validation and mobile layouts.
Requires domain_smoke.py to have prepared client profiles and a cancelled own order.
"""
import os,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from smoke import login,request

def main():
    with sync_playwright() as p:
        executable=os.environ.get('CHROMIUM_PATH')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':executable} if executable else {}))
        ac,ap,admin=login(browser,'admin-store','Admin123!');cc,cp,client=login(browser,'cliente','Cliente123!');oc,_,other=login(browser,'cliente-dos','ClienteDos123!')
        profile=request('/usuarios/me',client);foreign=request('/usuarios/me',other)
        request('/usuarios/me',client,'PUT',{'nombre':'Intento de prueba','email':foreign['email']},expected=409)
        assert request('/usuarios/me',client)==profile
        key=str(uuid.uuid4())[:8]
        base={'nombre':'Edad demo '+key,'especie':'Gato','raza':'Criolla','edad':45,'edadUnidad':'DIAS'}
        for body in [{**base,'edad':-1},{**base,'edad':1.5},{**base,'edadUnidad':'ANIOS'},{**base,'edadUnidad':None}]:request('/usuarios/me/mascotas',client,'POST',body,expected=400)
        pet=request('/usuarios/me/mascotas',client,'POST',base,expected=201)
        assert pet['edad']==45 and pet['edadUnidad']=='DIAS'
        pet=request('/usuarios/me/mascotas/'+str(pet['id']),client,'PUT',{**base,'edad':2,'edadUnidad':'MESES'})
        assert pet['edad']==2 and pet['edadUnidad']=='MESES'
        cp.get_by_role('button',name='Mi cuenta y mascotas',exact=True).click()
        expect(cp.get_by_label('Correo de contacto',exact=True)).to_have_value(profile['email'])
        card=cp.locator('article').filter(has_text=base['nombre']);expect(card).to_contain_text('2 meses')
        cp.reload();expect(cp.get_by_label('Correo de contacto',exact=True)).to_have_value(profile['email']);expect(cp.locator('article').filter(has_text=base['nombre'])).to_contain_text('2 meses')
        print('PASS: perfil confirmado tras recarga, correo ajeno rechazado sin cambios, edad días/meses y valores inválidos rechazados',flush=True)
        cancelled=next(v for v in request('/ventas',client) if v['estado']=='CANCELADA')
        cover=request('/coberturas')[0]
        shipment={'idVenta':cancelled['id'],'direccionEntrega':'Dirección prueba','zonaId':cover['zonaId'],'transportistaId':cover['transportistaId']}
        request('/despachos',other,'POST',shipment,expected=403)
        request('/despachos',client,'POST',shipment,expected=409)
        print('PASS: despacho ajeno rechazado antes de revelar su estado; pedido propio no pagado tampoco admite despacho',flush=True)
        # Remove leftover active demonstration masters from interrupted reviews, preserving history.
        for path,prefix in [('/sedes','Sede prueba '),('/prestaciones','Prestación demo ')]:
            for row in request(path,admin):
                if row['activo'] and row['nombre'].startswith(prefix):request(path+'/'+str(row['id']),admin,'DELETE',expected=204)
        assert len(request('/sedes'))==6
        screens=Path('.runtime/screens');screens.mkdir(parents=True,exist_ok=True)
        for page,views in [(ap,[('Servicios por sede','Servicios por sede'),('Logística','Logística de envíos'),('Planes y suscripciones','Planes y suscripciones')]),(cp,[('Mi cuenta y mascotas','Mi cuenta y mascotas'),('Citas','Citas'),('Envíos','Envíos')])]:
            for nav,title in views:
                page.set_viewport_size({'width':1440,'height':1000});page.get_by_role('button',name=nav,exact=True).click();expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
                if nav=='Servicios por sede':expect(page.get_by_role('heading',name='Consulta veterinaria',exact=True)).to_be_visible()
                elif nav=='Logística':expect(page.get_by_role('row').filter(has_text='Garritas Express').first).to_be_visible()
                elif nav=='Planes y suscripciones':expect(page.get_by_role('heading',name='Cuidado básico',exact=True)).to_be_visible()
                elif nav=='Mi cuenta y mascotas':expect(page.get_by_label('Correo de contacto',exact=True)).to_have_value(profile['email'])
                elif nav=='Citas':expect(page.get_by_role('row').filter(has_text='Revisión de Luna').first).to_be_visible()
                elif nav=='Envíos':expect(page.locator('article').first).to_be_visible()
                page.screenshot(path=str(screens/('academico-'+('admin-' if page==ap else 'cliente-')+nav.replace(' ','-')+'.png')),full_page=True)
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),nav
                page.screenshot(path=str(screens/('academico-movil-'+nav.replace(' ','-')+'.png')),full_page=True)
        print('PASS: seis pantallas revisadas en escritorio y móvil sin desbordamiento horizontal; seis sedes peruanas activas',flush=True)
        request('/usuarios/me/mascotas/'+str(pet['id']),client,'DELETE',expected=204)
        ac.close();cc.close();oc.close();browser.close()

if __name__=='__main__':main()
