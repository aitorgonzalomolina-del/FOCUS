#!/usr/bin/env python3
"""
Extractor de catálogo de perfumes y cosméticos desde PDF.

Genera la estructura:
  catalogo/
    <NOMBRE_PRODUCTO>/
      imagen.<ext>   (si existe en el PDF)
      info.json

Dependencia:
  pip install PyMuPDF
"""

import json
import re
from pathlib import Path

import fitz  # PyMuPDF  (pip install PyMuPDF)

# ── Configuración ─────────────────────────────────────────────────────────────

PDF_PATH   = "PERFUMES Y COSMÉTICOS 01-03-2026.pdf"
OUTPUT_DIR = Path("catalogo")

# Prefijos que identifican el inicio de una línea de producto
PRODUCT_PREFIXES = (
    "BODY CREAM", "BODY SPLASH", "BODY MIST", "BODY LOTION",
    "PERFUME", "DESODORANTE", "OLEO CAPILAR", "MASCARA CAPILAR",
    "CONDICIONADOR", "AMBIENTADOR",
)

PRICE_RE = re.compile(r"\$\s*([\d]+[,.][\d]{2})\s*$")
QTY_RE   = re.compile(r"\b(\d+(?:\.\d+)?\s*(?:G|ML))\s*$", re.IGNORECASE)
CODE_RE  = re.compile(r"^\d{4,}\s+")   # ej. "66860 " (códigos FOLIE PURE)


# ── Utilidades ────────────────────────────────────────────────────────────────

def is_product_start(text):
    """Devuelve True si la línea comienza una nueva entrada de producto."""
    t = text.upper()
    if CODE_RE.match(t):
        return True
    return any(t.startswith(p) for p in PRODUCT_PREFIXES)


def extract_quantity(full_name):
    """
    Separa la cantidad (ej. 250G, 100ML) del final del nombre.
    Retorna (nombre_limpio, cantidad_o_None).
    """
    m = QTY_RE.search(full_name)
    if m:
        qty = m.group(1).upper().replace(" ", "")
        return full_name[: m.start()].strip(), qty
    return full_name, None


def to_folder_name(name, max_len=100):
    """Convierte el nombre en un identificador de carpeta válido."""
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    clean = re.sub(r"\s+", "_", clean.strip())
    return clean[:max_len]


# ── Extracción de texto ───────────────────────────────────────────────────────

def get_text_lines(page):
    """Retorna todas las líneas de texto de la página con su bounding box."""
    lines = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            text = " ".join(sp["text"] for sp in line["spans"]).strip()
            if text:
                lines.append({"text": text, "bbox": line["bbox"]})
    return lines


def parse_products(text_lines):
    """
    Extrae los productos de las líneas de texto de una página.
    Maneja nombres que se extienden en varias líneas (ej. productos con
    descripción larga que rompe en la siguiente fila).

    Cada producto se identifica porque su última línea contiene un precio
    con formato "$ DD,DD".
    """
    products = []
    accum    = []        # partes acumuladas del nombre actual
    first_y0 = None      # coordenada Y del inicio del nombre

    def flush(price, bbox):
        nonlocal accum, first_y0
        raw = " ".join(accum).strip()
        raw = CODE_RE.sub("", raw).strip()   # eliminar código numérico inicial
        if raw:
            clean_name, quantity = extract_quantity(raw)
            products.append({
                "nombre":      clean_name,
                "cantidad":    quantity,
                "precio":      price,
                "descripcion": raw,
                "y0": first_y0 if first_y0 is not None else bbox[1],
                "y1": bbox[3],
                "image": None,
            })
        accum.clear()
        first_y0 = None

    for ld in text_lines:
        line, bbox = ld["text"], ld["bbox"]
        pm = PRICE_RE.search(line)

        if pm:
            # Línea con precio: puede tener texto antes ("NOMBRE... $ XX,XX")
            # o solo el precio ("$ XX,XX") cuando el nombre estaba en líneas previas.
            before = line[: pm.start()].strip()
            if before:
                if first_y0 is None:
                    first_y0 = bbox[1]
                accum.append(before)
            flush(float(pm.group(1).replace(",", ".")), bbox)

        elif is_product_start(line):
            # Nueva entrada de producto: descarta acumulación previa sin precio
            # (encabezados de marca como "AFEER", "LATTAFA", etc.)
            accum.clear()
            accum.append(line)
            first_y0 = bbox[1]

        elif accum:
            # Continuación del nombre del producto actual (nombre multi-línea)
            accum.append(line)

        # Si accum está vacío y la línea no es inicio de producto → encabezado,
        # se ignora automáticamente.

    return products


# ── Extracción de imágenes ────────────────────────────────────────────────────

def get_images(page, doc):
    """Extrae todas las imágenes de la página con su posición Y central."""
    images = []
    seen   = set()

    for img_info in page.get_images(full=True):
        xref = img_info[0]
        if xref in seen:
            continue
        seen.add(xref)

        rects = page.get_image_rects(xref)
        if not rects:
            continue

        rect = rects[0]
        base = doc.extract_image(xref)
        images.append({
            "bytes": base["image"],
            "ext":   base["ext"],
            "y_mid": (rect.y0 + rect.y1) / 2,
        })

    return sorted(images, key=lambda x: x["y_mid"])


def assign_images(products, images, threshold=60.0):
    """
    Asigna la imagen más próxima (en coordenada Y) a cada producto.
    Cada imagen se usa a lo sumo una vez.
    threshold: distancia máxima en puntos PDF para considerar una coincidencia.
    """
    used = set()

    for prod in products:
        prod_y  = (prod["y0"] + prod["y1"]) / 2
        best_i  = None
        best_d  = float("inf")

        for i, img in enumerate(images):
            if i in used:
                continue
            d = abs(img["y_mid"] - prod_y)
            if d < best_d:
                best_d, best_i = d, i

        if best_i is not None and best_d <= threshold:
            prod["image"] = images[best_i]
            used.add(best_i)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    doc          = fitz.open(PDF_PATH)
    all_products = []

    for pnum in range(len(doc)):
        page  = doc[pnum]
        lines = get_text_lines(page)
        prods = parse_products(lines)
        imgs  = get_images(page, doc)
        assign_images(prods, imgs)
        all_products.extend(prods)

    doc.close()

    seen_folders = {}
    total        = 0

    for prod in all_products:
        base   = to_folder_name(prod["nombre"])
        n      = seen_folders.get(base, 0)
        seen_folders[base] = n + 1
        folder = base if n == 0 else f"{base}_{n}"

        pdir = OUTPUT_DIR / folder
        pdir.mkdir(exist_ok=True)

        # ── Guardar imagen del producto ────────────────────────────────────
        img = prod.get("image")
        if img:
            (pdir / f"imagen.{img['ext']}").write_bytes(img["bytes"])

        # ── Guardar info.json ──────────────────────────────────────────────
        info = {
            "nombre":      prod["nombre"],
            "cantidad":    prod["cantidad"],
            "precio":      prod["precio"],
            "descripcion": prod["descripcion"],
        }
        (pdir / "info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        total += 1

    print(f"✓ {total} productos guardados en '{OUTPUT_DIR}/'")
    print(f"  Estructura: {OUTPUT_DIR}/<NOMBRE_PRODUCTO>/{{info.json, imagen.*}}")


if __name__ == "__main__":
    main()
