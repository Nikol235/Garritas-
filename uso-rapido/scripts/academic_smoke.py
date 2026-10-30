"""PKCE browser and API evidence for the three assigned pairs. Run after domain_smoke.py in DEV."""
import os,re,uuid
from playwright.sync_api import sync_playwright,expect
from smoke import login,request
from domain_smoke import submit,choose_id,TOKENS

def fill(page,values):
    for label,value in values.items():page.get_by_label(label,exact=True).fill(str(value))

def main():
    with sync_playwright() as p:
        executable=os.environ.get('CHROMIUM_PATH')
        b=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':executable} if executable else {}))
        ac,ap,admin=login(b,'admin-store','Admin123!');cc,cp,client=login(b,'cliente','Cliente123!');oc,_,other=login(b,'cliente-dos','ClienteDos123!')
        TOKENS[ap]=admin;TOKENS[cp]=client;key=str(uuid.uuid4())[:8]
        ap.get_by_role('button',name='Servicios por sede',exact=True).click()
        name='Prestación demo '+key
        fill(ap,{'Nombre de prestación':name,'Descripción de prestación':'Asociación N:M demostrable'})
        prestation=submit(ap,'Guardar prestación','POST','/prestaciones',201)
        sedes=[s for s in request('/sedes') if s['activo']][:2]
        for sede in sedes:
            choose_id(ap,'Sede de atención',sede['id']);choose_id(ap,'Prestación para la sede',prestation['id'])
            fill(ap,{'Precio de la prestación':70,'Duración en minutos':60})
            submit(ap,'Guardar oferta','PUT','/sedes/'+str(sede['id'])+'/prestaciones')
        assert all(any(o['prestacionId']==prestation['id'] and o['precio']==70 for o in request('/sedes/'+str(s['id'])+'/prestaciones')) for s in sedes)
        request('/sedes/'+str(sedes[0]['id'])+'/prestaciones',client,'PUT',{},expected=403)
        cp.get_by_role('button',name='Servicios por sede',exact=True).click();choose_id(cp,'Sede de atención',sedes[0]['id'])
        expect(cp.locator('article').filter(has=cp.get_by_role('heading',name=name,exact=True))).to_contain_text('60 minutos')
        expect(cp.get_by_role('button',name='Guardar oferta',exact=True)).to_have_count(0)
        print('PASS: Institución maestro, prestación compartida por dos sedes y escritura solo ADMIN',flush=True)
        ap.get_by_role('button',name='Logística',exact=True).click()
        fill(ap,{'Nombre del transportista':'Courier demo '+key,'Teléfono del transportista':'999400001'})
        carrier=submit(ap,'Guardar transportista','POST','/transportistas',201)
        fill(ap,{'Nombre de zona':'Zona demo '+key,'Ciudad de zona':'Lima'})
        zone=submit(ap,'Guardar zona','POST','/zonas',201)
        choose_id(ap,'Transportista de cobertura',carrier['id']);choose_id(ap,'Zona de cobertura',zone['id'])
        fill(ap,{'Tarifa de entrega':12.5});submit(ap,'Guardar cobertura','PUT','/coberturas')
        second=request('/transportistas',admin,'POST',{'nombre':'Courier dos '+key,'telefono':'999400002','activo':True},expected=201)
        known=next(z for z in request('/zonas') if z['id']!=zone['id'])
        for t,z in [(second['id'],zone['id']),(carrier['id'],known['id'])]:request('/coberturas',admin,'PUT',{'transportistaId':t,'zonaId':z,'tarifa':15,'diasEstimados':2,'activo':True})
        covers=request('/coberturas');assert sum(c['zonaId']==zone['id'] for c in covers)==2;assert sum(c['transportistaId']==carrier['id'] for c in covers)==2
        request('/coberturas',client,'PUT',{},expected=403);expect(cp.get_by_role('button',name='Logística',exact=True)).to_have_count(0)
        print('PASS: Envío maestro, transportistas y zonas N:M con tarifa/plazo y roles',flush=True)
        ap.get_by_role('button',name='Planes y suscripciones',exact=True).click()
        plan_name='Plan demo '+key
        fill(ap,{'Nombre del plan':plan_name,'Descripción del plan':'Contratación con períodos','Precio del plan':30,'Duración del plan en días':30})
        plan=submit(ap,'Guardar plan','POST','/planes',201)
        cp.get_by_role('button',name='Planes y suscripciones',exact=True).click();cp.once('dialog',lambda d:d.accept())
        with cp.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/suscripciones')) as pending:cp.get_by_role('button',name='Contratar '+plan_name,exact=True).click()
        response=pending.value;assert response.status==201
        first=next(s for s in request('/suscripciones',client) if s['planId']==plan['id'])
        retry=request('/suscripciones',client,'POST',{'planId':plan['id']},response.request.headers['idempotency-key'],expected=201)
        assert retry['id']==first['id'] and len(retry['periodos'])==1
        other_plan=next(x for x in request('/planes') if x['id']!=plan['id'])
        request('/suscripciones',client,'POST',{'planId':other_plan['id']},response.request.headers['idempotency-key'],expected=409)
        request('/suscripciones/'+str(first['id']),other,expected=403);request('/planes',client,'POST',{},expected=403)
        request('/planes/'+str(plan['id']),admin,'PUT',{'nombre':plan_name,'descripcion':'Nuevo precio','precio':40,'duracionDias':30,'activo':True})
        cp.once('dialog',lambda d:d.accept())
        with cp.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/suscripciones/'+str(first['id'])+'/renovar')) as pending:cp.get_by_role('button',name='Renovar suscripción #'+str(first['id']),exact=True).click()
        response=pending.value;assert response.status==200
        renewed=request('/suscripciones/'+str(first['id'])+'/renovar',client,'POST',{},response.request.headers['idempotency-key'])
        assert len(renewed['periodos'])==2 and renewed['totalContratado']==70
        assert [x['precio'] for x in renewed['periodos']]==[30,40]
        cp.get_by_text('Ver períodos de la suscripción #'+str(first['id']),exact=True).click();expect(cp.get_by_role('row').filter(has_text='Renovación')).to_be_visible()
        shared=request('/suscripciones',other,'POST',{'planId':plan['id']},str(uuid.uuid4()),expected=201)
        assert first['usuarioId']!=shared['usuarioId'];assert sum(s['planId']==plan['id'] for s in request('/suscripciones',admin))==2
        cp.once('dialog',lambda d:d.accept())
        with cp.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/suscripciones/'+str(first['id'])+'/cancelar')) as pending:cp.get_by_role('button',name='Cancelar suscripción #'+str(first['id']),exact=True).click()
        assert pending.value.status==200
        request('/suscripciones/'+str(first['id'])+'/renovar',client,'POST',{},str(uuid.uuid4()),expected=409)
        print('PASS: Usuario transaccional, clientes y planes N:M, períodos históricos, renovación/cancelación e idempotencia',flush=True)
        request('/suscripciones/'+str(shared['id'])+'/cancelar',other,'POST')
        for path in ['/planes/'+str(plan['id']),'/prestaciones/'+str(prestation['id']),'/transportistas/'+str(carrier['id']),'/transportistas/'+str(second['id']),'/zonas/'+str(zone['id'])]:request(path,admin,'DELETE',expected=204)
        ac.close();cc.close();oc.close();b.close()

if __name__=='__main__':main()
