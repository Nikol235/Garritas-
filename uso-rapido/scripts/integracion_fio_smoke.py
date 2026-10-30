import subprocess
import urllib.request
import urllib.error

"""DEV integration: PKCE roles, multicategories, Peru validation, paid shipping and packages.
Creates demo audit history; does not delete sales/payment records or erase databases.
"""

import json, os, time, uuid, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from smoke import request, login, wait_state, WEB

OUT = Path("docs/evidencias-integracion-fio")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
            args=["--no-sandbox"],
        )
        ac, ap, admin = login(browser, "admin-store", "Admin123!")
        cc, cp, client = login(browser, "cliente", "Cliente123!")
        expect(ap.get_by_role("button", name="Nueva orden", exact=True)).to_have_count(
            0
        )
        expect(ap.get_by_role("button", name="Carrito", exact=True)).to_have_count(0)
        expect(
            ap.get_by_role("button", name="Añadir al carrito", exact=False)
        ).to_have_count(0)
        request("/usuarios/roles", client, expected=403)
        request("/usuarios/roles", expected=401)
        plans = request("/planes")
        request(
            "/suscripciones",
            admin,
            "POST",
            {"planId": plans[0]["id"]},
            key=str(uuid.uuid4()),
            expected=403,
        )
        # Backend security is checked directly as well as through the Gateway.
        for port, path in [(8086, "/usuarios/me"), (8082, "/sedes")]:
            method = "GET" if port == 8086 else "POST"
            req = urllib.request.Request(
                f"http://localhost:{port}/api/v1" + path,
                method=method,
                data=None if method == "GET" else b"{}",
                headers={"Content-Type": "application/json"},
            )
            try:
                urllib.request.urlopen(req, timeout=5)
                raise AssertionError("Unprotected backend")
            except urllib.error.HTTPError as error:
                assert error.code == 401
        suffix = uuid.uuid4().hex[:8]
        a = request(
            "/categorias",
            admin,
            "POST",
            {"nombre": "Higiene " + suffix, "descripcion": "Prueba integración"},
            expected=201,
        )
        b = request(
            "/categorias",
            admin,
            "POST",
            {"nombre": "Cuidado " + suffix, "descripcion": "Prueba integración"},
            expected=201,
        )
        product_body = {
            "nombre": "Producto integrado " + suffix,
            "descripcion": "Prueba entrega y stock",
            "precio": 20,
            "stock": 20,
            "activo": True,
            "categoriaIds": [a["id"], b["id"]],
        }
        product = request("/productos", admin, "POST", product_body, expected=201)
        assert len(product["categorias"]) == 2
        for cat in [a, b]:
            result = request(
                "/productos?categoriaId=" + str(cat["id"]) + "&page=0&size=5"
            )
            assert any(x["id"] == product["id"] for x in result["content"])
        request("/productos?page=0&size=0", expected=400)
        request(
            "/productos",
            admin,
            "POST",
            {**product_body, "categoriaIds": [999999999]},
            expected=400,
        )
        roles = request("/usuarios/roles", admin)
        profile = request("/usuarios/me", client)
        profile_body = {
            k: profile.get(k) or ""
            for k in ["nombre", "email", "telefono", "direccion", "dni"]
        }
        request(
            "/usuarios/me",
            client,
            "PUT",
            {**profile_body, "telefono": "12345"},
            expected=400,
        )
        request(
            "/usuarios/me",
            client,
            "PUT",
            {**profile_body, "telefono": "987654321", "dni": "12345"},
            expected=400,
        )
        profile = request(
            "/usuarios/me",
            client,
            "PUT",
            {**profile_body, "telefono": "987654321", "dni": "12345678"},
        )
        assert request("/usuarios/me", client)["telefono"] == "987654321"
        internal = request(
            "/usuarios/roles",
            admin,
            "POST",
            {"nombre": "OPERADOR_" + suffix, "descripcion": "Clasificación interna"},
            expected=201,
        )
        request(f"/usuarios/{profile['id']}/roles/{internal['id']}", admin, "POST")
        request(
            "/categorias",
            client,
            "POST",
            {"nombre": "Intento no permitido"},
            expected=403,
        )
        sedes = request("/sedes")
        sede = next(s for s in sedes if s["nombre"] == "Garritas Miraflores")
        coverage = next(
            c for c in request("/coberturas") if c["activo"] and c["tarifa"] > 0
        )
        base = {
            "sedeId": sede["id"],
            "metodoPago": "YAPE",
            "detalles": [{"idProducto": product["id"], "cantidad": 1}],
        }
        delivery = {
            **base,
            "tipoEntrega": "ENVIO",
            "zonaId": coverage["zonaId"],
            "transportistaId": coverage["transportistaId"],
            "direccionEntrega": "Av. Perú 123, Lima - prueba",
            "tarifaCotizada": coverage["tarifa"],
        }
        request("/ventas", admin, "POST", delivery, key=str(uuid.uuid4()), expected=403)
        request(
            "/ventas",
            client,
            "POST",
            {**delivery, "tarifaCotizada": 0},
            key=str(uuid.uuid4()),
            expected=409,
        )
        key = str(uuid.uuid4())
        sale = request("/ventas", client, "POST", delivery, key=key, expected=201)
        assert sale["total"] == 20 + coverage["tarifa"] and sale["subtotal"] == 20
        sale = wait_state(sale["id"], client, "PAGADA")
        payment = request("/pagos/venta/" + str(sale["id"]), client)
        assert payment["monto"] == sale["total"]
        same = request("/ventas", client, "POST", delivery, key=key, expected=201)
        assert same["id"] == sale["id"]
        deliveries = request("/envios", client)
        dispatch = next(e for e in deliveries if e["idVenta"] == sale["id"])
        assert (
            dispatch["tarifa"] == coverage["tarifa"]
            and len([e for e in deliveries if e["idVenta"] == sale["id"]]) == 1
        )
        request(
            "/envios/" + str(dispatch["id"]) + "/en-transito",
            client,
            "POST",
            expected=403,
        )
        request("/envios/" + str(dispatch["id"]) + "/en-transito", admin, "POST")
        request("/envios/" + str(dispatch["id"]) + "/entregado", admin, "POST")
        pickup = request(
            "/ventas", client, "POST", base, key=str(uuid.uuid4()), expected=201
        )
        wait_state(pickup["id"], client, "PAGADA")
        request(
            "/envios",
            client,
            "POST",
            {
                "idVenta": pickup["id"],
                "zonaId": coverage["zonaId"],
                "transportistaId": coverage["transportistaId"],
                "direccionEntrega": "No se pagó este envío",
            },
            expected=409,
        )
        stock = request("/productos/" + str(product["id"]))["stock"]
        failed = request(
            "/ventas",
            client,
            "POST",
            {**delivery, "metodoPago": "TRANSFERENCIA"},
            key=str(uuid.uuid4()),
            expected=201,
        )
        wait_state(failed["id"], client, "CANCELADA")
        assert request("/productos/" + str(product["id"]))["stock"] == stock
        assert not any(e["idVenta"] == failed["id"] for e in request("/envios", client))
        # Replay the payment event and a semantic duplicate: one paid dispatch, no extra stock effect.
        sql = f"SELECT payload FROM outbox_event WHERE aggregate_id='{sale['id']}' AND payload::jsonb->>'type'='pago.validado' ORDER BY sequence LIMIT 1"
        event = json.loads(
            subprocess.run(
                [
                    "docker",
                    "exec",
                    "garritas-postgres-pago-dev",
                    "psql",
                    "-U",
                    "garritas",
                    "-d",
                    "garritas_pago_db",
                    "-Atc",
                    sql,
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
        duplicate = {**event, "eventId": str(uuid.uuid4())}
        lines = "".join(
            str(sale["id"]) + "\t" + json.dumps(e) + "\n" for e in [event, duplicate]
        )
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "kafka/compose-dev.yml",
                "exec",
                "-T",
                "kafka",
                "/opt/kafka/bin/kafka-console-producer.sh",
                "--bootstrap-server",
                "localhost:9092",
                "--topic",
                "garritas.ventas.v1",
                "--property",
                "parse.key=true",
                "--property",
                "key.separator=\t",
            ],
            input=lines,
            text=True,
            capture_output=True,
            check=True,
        )
        time.sleep(3)
        assert (
            len([e for e in request("/envios", client) if e["idVenta"] == sale["id"]])
            == 1
        )
        assert request("/productos/" + str(product["id"]))["stock"] == stock
        # Browser checkout must expose delivery before payment and the correct total.
        cp.reload()
        expect(cp.get_by_role("button", name="Salir", exact=True)).to_be_visible()
        cp.get_by_role("button", name="Nueva orden", exact=True).click()
        cp.get_by_role("searchbox", name="Buscar productos").fill(product["nombre"])
        cp.get_by_role(
            "button", name="Añadir " + product["nombre"] + " al carrito", exact=True
        ).click()
        cp.get_by_label("Sede de la compra").select_option(
            label=sede["nombre"] + " · " + sede["ciudad"]
        )
        cp.get_by_label("Forma de entrega", exact=True).select_option("ENVIO")
        (
            cp.get_by_label("Zona y transportista", exact=True).select_option(
                value="1: " + str(coverage["id"])
            )
            if False
            else None
        )
        select = cp.get_by_label("Zona y transportista", exact=True)
        option = (
            select.locator("option")
            .filter(has_text=coverage["zona"] + " · " + coverage["transportista"])
            .first
        )
        select.select_option(value=option.get_attribute("value"))
        cp.get_by_label("Dirección de entrega", exact=True).fill(
            "Av. Perú 123, Lima - prueba navegador"
        )
        expect(cp.get_by_test_id("cart-total")).to_contain_text(f"{sale['total']:.2f}")
        cp.screenshot(path=str(OUT / "carrito-delivery.png"), full_page=True)
        with cp.expect_response(
            lambda response: "/api/v1/ventas" in response.url
            and response.request.method == "POST"
            and response.status == 201
        ) as response:
            cp.get_by_role("button", name="Confirmar compra", exact=True).click()
        assert response.value.status == 201
        browser_sale = max(
            (
                v
                for v in request("/ventas", client)
                if any(d["idProducto"] == product["id"] for d in v["detalles"])
            ),
            key=lambda v: v["id"],
        )
        wait_state(browser_sale["id"], client, "PAGADA")
        # Packages are offered by sede; quoted package, components and duration survive price edits.
        offers = request("/sedes/" + str(sede["id"]) + "/prestaciones")
        pack = next(
            o
            for o in offers
            if o["activo"]
            and len(o.get("componentes") or []) >= 2
            and all(
                any(single["prestacionId"] == c["id"] for single in offers)
                for c in o["componentes"]
            )
        )
        pets = request("/usuarios/me/mascotas", client)
        pet = (
            pets[0]
            if pets
            else request(
                "/usuarios/me/mascotas",
                client,
                "POST",
                {
                    "nombre": "Luna " + suffix,
                    "especie": "Perro",
                    "raza": "Mestiza",
                    "edad": 3,
                    "edadUnidad": "MESES",
                },
                expected=201,
            )
        )
        pro = next(
            x
            for x in request("/especialistas")
            if x["activo"] and (x.get("sedeId") is None or x["sedeId"] == sede["id"])
        )
        future = int(time.time() + 60 * 60 * 24 * 40 + int(suffix[:4], 16) * 1800)
        future = future - future % 1800
        appointment = {
            "idMascota": pet["id"],
            "idSede": sede["id"],
            "profesionalId": pro["id"],
            "fechaHora": datetime.datetime.fromtimestamp(
                future, datetime.timezone.utc
            ).isoformat(),
            "motivo": "Paquete " + suffix,
            "prestacionIds": [pack["prestacionId"]],
        }
        cita = request("/citas", client, "POST", appointment, expected=201)
        assert (
            cita["total"] == pack["precio"]
            and cita["duracionMinutos"] == pack["duracionMinutos"]
            and cita["detalles"][0]["componentes"]
        )
        request("/citas", client, "POST", appointment, expected=409)
        request(
            "/citas",
            client,
            "POST",
            {
                **appointment,
                "prestacionIds": [pack["prestacionId"], pack["componentes"][0]["id"]],
            },
            expected=400,
        )
        # update package price and prove existing appointment is a snapshot
        request(
            "/sedes/" + str(sede["id"]) + "/prestaciones",
            admin,
            "PUT",
            {
                "prestacionId": pack["prestacionId"],
                "precio": pack["precio"] + 1,
                "duracionMinutos": pack["duracionMinutos"],
                "activo": True,
            },
        )
        assert request("/citas/" + str(cita["id"]), client)["total"] == pack["precio"]
        request(
            "/sedes/" + str(sede["id"]) + "/prestaciones",
            admin,
            "PUT",
            {
                "prestacionId": pack["prestacionId"],
                "precio": pack["precio"],
                "duracionMinutos": pack["duracionMinutos"],
                "activo": True,
            },
        )
        cp.get_by_role("button", name="Sedes", exact=True).click()
        card = cp.locator(".location-card").filter(has_text=sede["nombre"])
        card.get_by_role("button", name="Ver servicios y paquetes", exact=True).click()
        expect(
            cp.get_by_role("heading", name="Servicios y paquetes por sede", exact=True)
        ).to_be_visible()
        expect(
            cp.get_by_role("heading", name=pack["nombre"], exact=True)
        ).to_be_visible()
        cp.screenshot(path=str(OUT / "paquetes-sede.png"), full_page=True)
        cp.set_viewport_size({"width": 390, "height": 844})
        cp.screenshot(path=str(OUT / "paquetes-mobile.png"), full_page=True)
        assert cp.evaluate("document.documentElement.scrollWidth<=innerWidth+2")
        ap.get_by_role("button", name="Usuarios y roles", exact=True).click()
        expect(ap.get_by_text("Estos roles organizan", exact=False)).to_be_visible()
        ap.screenshot(path=str(OUT / "usuarios-roles.png"), full_page=True)
        evidence = {
            "multicategoria": True,
            "seguridad_directa_dos_servicios": True,
            "replay_pago_sin_duplicar_despacho": True,
            "roles_sin_escalada": True,
            "admin_no_compra": True,
            "celular_y_dni": True,
            "delivery_cobrado": sale["id"],
            "total": sale["total"],
            "pago": payment["monto"],
            "despacho_automatico": dispatch["id"],
            "reintento_misma_venta": True,
            "rechazo_compensa_stock": failed["id"],
            "compra_delivery_navegador": browser_sale["id"],
            "paquete_cita": cita["id"],
            "precio_historico": True,
            "solapamiento_rechazado": True,
            "paquete_sin_duplicar_componentes": True,
            "mobile_sin_desborde": True,
        }
        request("/productos/" + str(product["id"]), admin, "DELETE", expected=204)
        request("/citas/" + str(cita["id"]) + "/cancelar", client, "POST")
        request(f"/usuarios/{profile['id']}/roles/{internal['id']}", admin, "DELETE")
        request("/usuarios/roles/" + str(internal["id"]), admin, "DELETE", expected=204)
        browser.close()
    (OUT / "resultado.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
