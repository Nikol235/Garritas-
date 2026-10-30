"""DEV: create and book a package through Angular and verify mobile form validation."""

import os, uuid, time, datetime, json
from smoke import login, request
from playwright.sync_api import sync_playwright, expect
from pathlib import Path

OUT = Path("docs/evidencias-integracion-fio")


def select_id(field, id):
    option = field.locator(f'option[value="{id}"],option[value$=": {id}"]')
    expect(option).to_have_count(1)
    field.select_option(value=option.get_attribute("value"))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
            args=["--no-sandbox"],
        )
        ac, ap, admin = login(browser, "admin-store", "Admin123!")
        cc, cp, client = login(browser, "cliente", "Cliente123!")
        sede = next(
            s for s in request("/sedes") if s["nombre"] == "Garritas Miraflores"
        )
        name = "Paquete de prueba " + uuid.uuid4().hex[:7]
        ap.get_by_role("button", name="Servicios por sede", exact=True).click()
        ap.get_by_label("Nombre de prestación", exact=True).fill(name)
        ap.get_by_label("Descripción de prestación", exact=True).fill(
            "Consulta y vacuna en un solo paquete"
        )
        ap.get_by_role("group", name="Componentes del paquete (opcional)").get_by_role(
            "checkbox", name="Consulta veterinaria", exact=True
        ).check()
        ap.get_by_role("group", name="Componentes del paquete (opcional)").get_by_role(
            "checkbox", name="Vacunación", exact=True
        ).check()
        with ap.expect_response(
            lambda r: r.url.endswith("/prestaciones")
            and r.request.method == "POST"
            and r.status == 201
        ):
            ap.get_by_role("button", name="Guardar prestación", exact=True).click()
        package = next(
            x for x in request("/prestaciones", admin) if x["nombre"] == name
        )
        select_id(ap.get_by_label("Sede de atención", exact=True), sede["id"])
        select_id(ap.get_by_label("Prestación para la sede", exact=True), package["id"])
        ap.get_by_label("Precio de la prestación", exact=True).fill("85")
        ap.get_by_label("Duración en minutos", exact=True).fill("60")
        with ap.expect_response(
            lambda r: r.url.endswith("/prestaciones")
            and r.request.method == "PUT"
            and r.status == 200
        ):
            ap.get_by_role("button", name="Guardar oferta", exact=True).click()
        expect(ap.get_by_role("heading", name=name, exact=True)).to_be_visible()
        ap.screenshot(path=str(OUT / "admin-paquetes.png"), full_page=True)
        cp.get_by_role("button", name="Servicios por sede", exact=True).click()
        select_id(cp.get_by_label("Sede de atención", exact=True), sede["id"])
        cp.get_by_role("button", name="Reservar " + name, exact=True).click()
        expect(
            cp.get_by_role("heading", name="Reservar cita", exact=True)
        ).to_be_visible()
        expect(cp.get_by_role("checkbox", name=name, exact=False)).to_be_checked()
        pet = request("/usuarios/me/mascotas", client)[0]
        pro = next(
            x
            for x in request("/especialistas")
            if x["activo"] and (x.get("sedeId") is None or x["sedeId"] == sede["id"])
        )
        select_id(cp.get_by_label("Mascota para la cita", exact=True), pet["id"])
        select_id(cp.get_by_label("Profesional", exact=True), pro["id"])
        ts = int(time.time() + 3600 * 24 * 500 + int(uuid.uuid4().hex[:3], 16) * 1800)
        ts -= ts % 1800
        cp.get_by_label("Fecha y hora de la cita", exact=True).fill(
            datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M"
            )
        )
        cp.get_by_label("Motivo de la cita", exact=True).fill(name)
        with cp.expect_response(
            lambda r: r.url.endswith("/citas")
            and r.request.method == "POST"
            and r.status == 201
        ):
            cp.get_by_role("button", name="Reservar cita", exact=True).click()
        cita = next(x for x in request("/citas", client) if x["motivo"] == name)
        assert (
            cita["total"] == 85
            and "Consulta veterinaria" in cita["detalles"][0]["componentes"]
        )
        cp.screenshot(path=str(OUT / "cita-paquete.png"), full_page=True)
        # Validate the persisted profile form rejects a malformed mobile in the browser.
        cp.get_by_role("button", name="Mi cuenta y mascotas", exact=True).click()
        phone = cp.get_by_label("Teléfono de contacto", exact=True)
        phone.fill("12345")
        expect(
            cp.get_by_role("button", name="Guardar perfil", exact=True)
        ).to_be_disabled()
        phone.fill("987654321")
        expect(
            cp.get_by_role("button", name="Guardar perfil", exact=True)
        ).to_be_enabled()
        request("/citas/" + str(cita["id"]) + "/cancelar", client, "POST")
        request("/prestaciones/" + str(package["id"]), admin, "DELETE", expected=204)
        result = {
            "crear_paquete_desde_angular": True,
            "asignar_precio_y_sede_desde_angular": True,
            "reservar_paquete_desde_angular": cita["id"],
            "precio_y_componentes_guardados": True,
            "celular_invalido_bloquea_guardar": True,
        }
        (OUT / "frontend-paquetes.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
