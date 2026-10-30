"""S6 DEV: suspend only the known local logistics process, verify bounded failure, recover.
Never run against another host or a production stack.
"""

import json, os, signal, time, uuid, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from smoke import login, request, wait_state

ROOT = Path(__file__).resolve().parents[2]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
            args=["--no-sandbox"],
        )
        ac, ap, admin = login(browser, "admin-store", "Admin123!")
        cc, cp, client = login(browser, "cliente", "Cliente123!")
        category = request(
            "/categorias",
            admin,
            "POST",
            {"nombre": "Resiliencia logística " + uuid.uuid4().hex[:8]},
            expected=201,
        )
        product = request(
            "/productos",
            admin,
            "POST",
            {
                "nombre": "Prueba timeout " + uuid.uuid4().hex[:8],
                "precio": 10,
                "stock": 5,
                "activo": True,
                "categoriaId": category["id"],
            },
            expected=201,
        )
        coverage = next(c for c in request("/coberturas") if c["activo"])
        body = {
            "sedeId": request("/sedes")[0]["id"],
            "metodoPago": "YAPE",
            "detalles": [{"idProducto": product["id"], "cantidad": 1}],
            "tipoEntrega": "ENVIO",
            "zonaId": coverage["zonaId"],
            "transportistaId": coverage["transportistaId"],
            "tarifaCotizada": coverage["tarifa"],
            "direccionEntrega": "Av. Prueba 123, Lima",
        }
        pid = int((ROOT / ".runtime/garritas-envio-ms.pid").read_text())
        assert (
            b".runtime/garritas-envio-ms/app.jar"
            in Path(f"/proc/{pid}/cmdline").read_bytes()
        )
        times = []
        try:
            os.kill(pid, signal.SIGSTOP)
            for i in range(6):
                start = time.monotonic()
                request(
                    "/ventas", client, "POST", body, key=str(uuid.uuid4()), expected=503
                )
                times.append(round(time.monotonic() - start, 3))
            assert max(times) < 8, times
            assert times[-1] < 1.5, times
            assert not any(
                any(d["idProducto"] == product["id"] for d in v["detalles"])
                for v in request("/ventas", client)
            )
            assert request("/productos/" + str(product["id"]))["stock"] == 5
        finally:
            os.kill(pid, signal.SIGCONT)
        # The configured open state lasts ten seconds. Wait only long enough to probe recovery.
        time.sleep(11)
        sale = request(
            "/ventas", client, "POST", body, key=str(uuid.uuid4()), expected=201
        )
        wait_state(sale["id"], client, "PAGADA")
        request("/productos/" + str(product["id"]), admin, "DELETE", expected=204)
        result = {
            "fallos_controlados_503": 6,
            "segundos_por_peticion": times,
            "sin_venta_ni_cobro_durante_fallo": True,
            "circuito_abierto_ultima_peticion": times[-1] < 1.5,
            "recuperacion_pagada": sale["id"],
        }
        (ROOT / "docs/evidencias-integracion-fio/resiliencia.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(json.dumps(result, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
