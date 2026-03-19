#!/usr/bin/env python3
"""
Extrae las imágenes del PDF y las guarda en las carpetas de catalogo/ ya creadas.
Dependencia: pip install PyMuPDF
"""

import os
import re
from pathlib import Path
import fitz  # PyMuPDF

OUTPUT_DIR = Path("catalogo")

PRODUCT_PREFIXES = (
    "BODY CREAM", "BODY SPLASH", "BODY MIST", "BODY LOTION",
    "PERFUME", "DESODORANTE", "OLEO CAPILAR", "MASCARA CAPILAR",
    "CONDICIONADOR", "AMBIENTADOR",
)

PRICE_RE = re.compile(r"\$\s*([\d]+[,.][\d]{2})\s*$")
QTY_RE   = re.compile(r"\b(\d+(?:\.\d+)?\s*(?:G|ML))\s*$", re.IGNORECASE)
CODE_RE  = re.compile(r"^\d{4,}\s+")


def is_product_start(text):
    t = text.upper()
    if CODE_RE.match(t):
        return True
    return any(t.startswith(p) for p in PRODUCT_PREFIXES)


def extract_quantity(full_name):
    m = QTY_RE.search(full_name)
    if m:
        qty = m.group(1).upper().replace(" ", "")
        return full_name[: m.start()].strip(), qty
    return full_name, None


def to_folder_name(name, max_len=100):
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    clean = re.sub(r"\s+", "_", clean.strip())
    return clean[:max_len]


def get_text_lines(page):
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
    Parsea productos sabiendo que el nombre y el precio
    pueden estar en líneas SEPARADAS del mismo bloque.
    """
    products = []
    pending_name = None
    pending_y0   = None

    for ld in text_lines:
        line = ld["text"]
        bbox = ld["bbox"]

        pm = PRICE_RE.search(line)

        if pm:
            # Línea de precio
            before = line[: pm.start()].strip()
            price  = float(pm.group(1).replace(",", "."))

            # El nombre puede estar en 'before' o en pending_name anterior
            if before:
                full_name = (pending_name + " " + before).strip() if pending_name else before
            else:
                full_name = pending_name or ""

            full_name = CODE_RE.sub("", full_name).strip()

            if full_name:
                clean_name, quantity = extract_quantity(full_name)
                y0 = pending_y0 if pending_y0 is not None else bbox[1]
                products.append({
                    "nombre":      clean_name,
                    "cantidad":    quantity,
                    "precio":      price,
                    "descripcion": full_name,
                    "y0": y0,
                    "y1": bbox[3],
                })

            pending_name = None
            pending_y0   = None

        elif is_product_start(line):
            pending_name = line
            pending_y0   = bbox[1]

        elif pending_name:
            # Continuación de nombre multi-línea
            pending_name += " " + line

    return products


def get_images_ordered(page, doc):
    """
    Extrae imágenes de la página ordenadas por posición Y (de arriba a abajo).
    Descarta imágenes muy pequeñas (logos de fondo, íconos de cabecera).
    Los bloques tipo-1 en get_text('dict') ya incluyen los bytes de la imagen.
    """
    images = []

    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 1:
            continue

        bbox = block["bbox"]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w < 25 or h < 25:
            continue

        img_bytes = block.get("image")
        ext       = block.get("ext", "jpeg")

        if img_bytes:
            images.append({
                "bytes": img_bytes,
                "ext":   ext,
                "y_mid": (bbox[1] + bbox[3]) / 2,
            })

    return sorted(images, key=lambda x: x["y_mid"])


def assign_images(products, images, threshold=70.0):
    used = set()
    for prod in products:
        prod_y = (prod["y0"] + prod["y1"]) / 2
        best_i, best_d = None, float("inf")
        for i, img in enumerate(images):
            if i in used:
                continue
            d = abs(img["y_mid"] - prod_y)
            if d < best_d:
                best_d, best_i = d, i
        if best_i is not None and best_d <= threshold:
            prod["image"] = images[best_i]
            used.add(best_i)
        else:
            prod["image"] = None


def main():
    pdf_file = next(f for f in os.listdir(".") if f.endswith(".pdf"))
    print(f"Abriendo: {pdf_file}")

    doc = fitz.open(pdf_file)
    all_products = []

    for pnum in range(len(doc)):
        page  = doc[pnum]
        lines = get_text_lines(page)
        prods = parse_products(lines)
        imgs  = get_images_ordered(page, doc)
        assign_images(prods, imgs)

        print(f"  Página {pnum+1:2d}: {len(prods):3d} productos, {len(imgs):3d} imágenes")
        all_products.extend(prods)

    doc.close()

    # Guardar imágenes en las carpetas ya existentes
    seen_folders = {}
    saved = 0
    missing = 0

    for prod in all_products:
        base   = to_folder_name(prod["nombre"])
        n      = seen_folders.get(base, 0)
        seen_folders[base] = n + 1
        folder = base if n == 0 else f"{base}_{n}"

        pdir = OUTPUT_DIR / folder
        pdir.mkdir(exist_ok=True)

        img = prod.get("image")
        if img:
            out_path = pdir / f"imagen.{img['ext']}"
            out_path.write_bytes(img["bytes"])
            saved += 1
        else:
            missing += 1

    print(f"\nTotal productos  : {len(all_products)}")
    print(f"Imágenes guardadas: {saved}")
    print(f"Sin imagen        : {missing}")


if __name__ == "__main__":
    main()
