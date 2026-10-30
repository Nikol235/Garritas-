"""Check the document against the pinned source and verify both delivered formats."""

from pathlib import Path
import json, re, subprocess
import fitz
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
data = json.loads((HERE / "referencias.json").read_text())
for key, r in data["references"].items():
    path = ROOT / r["path"]
    text = path.read_text()
    assert r["needle"] in text.splitlines()[r["line"] - 1], key
    assert (
        text
        == subprocess.check_output(
            ["git", "show", data["commit"] + ":" + r["path"]], cwd=ROOT
        ).decode()
    ), key
    assert r["url"].endswith("#L" + str(r["line"])), key
source = (HERE / "Guia-estudio-C4-Catalogo-Usuario.html").read_text()
assert len(re.findall(r"<svg\b", source)) == 8
assert not re.search(r'<(?:script|img|link)[^>]+(?:src|href)=["\']https?://', source)
assert "C4 · Nivel 1" in source and "C4 · Nivel 4" in source
pdf = fitz.open(HERE / "Guia-estudio-C4-Catalogo-Usuario.pdf")
text = "".join(p.get_text() for p in pdf)
normalized = re.sub(r"\s+", "", text)
for r in data["references"].values():
    assert re.sub(r"\s+", "", r["path"]) in normalized, r["path"]
for term in [
    "Compensación real",
    "ProductoController",
    "SuscripcionService",
    "JWKS",
    "Idempotency-Key",
    "local-admin-change-me",
    "Cliente123!",
]:
    assert term in text, term
for i, p in enumerate(pdf):
    assert len(p.get_text().strip()) > 200, (i + 1, "unexpected sparse page")
    # There must be no content clipped beyond a page edge.
    for block in p.get_text("blocks"):
        assert block[0] >= -1 and block[2] <= p.rect.width + 1, (
            i + 1,
            "horizontal clipping",
        )
uris = [link.get("uri", "") for p in pdf for link in p.get_links()]
for r in data["references"].values():
    assert r["url"] in uris, r["url"]
assert len(pdf.get_toc()) >= 19, "missing PDF navigation outline"
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"]
    )
    page = browser.new_page(viewport={"width": 1100, "height": 900})
    page.set_content(source)
    assert page.locator(".chapter").count() == 20
    for i in ["cat-codigo", "usr-codigo", "claves", "mapa"]:
        assert page.locator("#" + i).count() == 1
    page.locator('#indice a[href="#saga"]').click()
    assert page.evaluate("location.hash") == "#saga"
    browser.close()
result = {
    "source_commit": data["commit"],
    "pdf_pages": len(pdf),
    "references": len(data["references"]),
    "diagrams": 8,
    "source_paths_and_lines": "verified",
    "pdf_links": len(uris),
    "pdf_outline_entries": len(pdf.get_toc()),
    "html": "standalone with inline SVG",
    "pdf": "selectable text and clickable code links",
    "application_changes": False,
}
(HERE / "verificacion.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
