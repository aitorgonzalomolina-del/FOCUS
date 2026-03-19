#!/usr/bin/env python3
"""
Web Search Agent — FOCUS
Busca en DuckDuckGo sin necesitar API key.

Uso:
  python web_search_agent.py "consulta de búsqueda"
  python web_search_agent.py "consulta" --resultados 10
  python web_search_agent.py "consulta" --modo noticias
  python web_search_agent.py "consulta" --guardar
"""

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

# Forzar UTF-8 en Windows para evitar errores de encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


MODOS = {
    "web":      "Búsqueda web general",
    "noticias": "Noticias recientes",
    "imagenes": "Imágenes (URLs)",
}


def buscar_web(consulta: str, max_resultados: int = 5) -> list[dict]:
    with DDGS() as ddg:
        return list(ddg.text(consulta, max_results=max_resultados))


def buscar_noticias(consulta: str, max_resultados: int = 5) -> list[dict]:
    with DDGS() as ddg:
        return list(ddg.news(consulta, max_results=max_resultados))


def buscar_imagenes(consulta: str, max_resultados: int = 5) -> list[dict]:
    with DDGS() as ddg:
        return list(ddg.images(consulta, max_results=max_resultados))


def imprimir_resultados_web(resultados: list[dict]) -> None:
    for i, r in enumerate(resultados, 1):
        print(f"\n{'─'*60}")
        print(f"  [{i}] {r.get('title', 'Sin título')}")
        print(f"  URL : {r.get('href', '')}")
        print(f"  {r.get('body', '')[:200]}...")


def imprimir_resultados_noticias(resultados: list[dict]) -> None:
    for i, r in enumerate(resultados, 1):
        fecha = r.get("date", "")[:10] if r.get("date") else "?"
        print(f"\n{'─'*60}")
        print(f"  [{i}] {r.get('title', 'Sin título')}")
        print(f"  Fuente : {r.get('source', '')}  |  Fecha: {fecha}")
        print(f"  URL    : {r.get('url', '')}")
        print(f"  {r.get('body', '')[:200]}...")


def imprimir_resultados_imagenes(resultados: list[dict]) -> None:
    for i, r in enumerate(resultados, 1):
        print(f"\n  [{i}] {r.get('title', 'Sin título')}")
        print(f"  URL imagen : {r.get('image', '')}")
        print(f"  Fuente     : {r.get('url', '')}")


def guardar_resultados(consulta: str, modo: str, resultados: list[dict]) -> Path:
    salidas = Path("busquedas")
    salidas.mkdir(exist_ok=True)
    nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{modo}.json"
    archivo = salidas / nombre
    datos = {
        "consulta":   consulta,
        "modo":       modo,
        "fecha":      datetime.now().isoformat(),
        "resultados": resultados,
    }
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return archivo


def main():
    parser = argparse.ArgumentParser(
        description="Web Search Agent — FOCUS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("consulta", help="Texto a buscar")
    parser.add_argument(
        "--resultados", "-r", type=int, default=5,
        help="Número de resultados (default: 5)",
    )
    parser.add_argument(
        "--modo", "-m", choices=MODOS.keys(), default="web",
        help="Tipo de búsqueda: web | noticias | imagenes (default: web)",
    )
    parser.add_argument(
        "--guardar", "-g", action="store_true",
        help="Guardar resultados en busquedas/<timestamp>.json",
    )
    args = parser.parse_args()

    print(f"\nFOCUS — Web Search Agent")
    print(f"   Consulta : {args.consulta}")
    print(f"   Modo     : {MODOS[args.modo]}")
    print(f"   Resultados pedidos: {args.resultados}")

    try:
        if args.modo == "web":
            resultados = buscar_web(args.consulta, args.resultados)
            imprimir_resultados_web(resultados)
        elif args.modo == "noticias":
            resultados = buscar_noticias(args.consulta, args.resultados)
            imprimir_resultados_noticias(resultados)
        elif args.modo == "imagenes":
            resultados = buscar_imagenes(args.consulta, args.resultados)
            imprimir_resultados_imagenes(resultados)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'─'*60}")
    print(f"  Total encontrados: {len(resultados)}")

    if args.guardar:
        archivo = guardar_resultados(args.consulta, args.modo, resultados)
        print(f"  Guardado en: {archivo}")


if __name__ == "__main__":
    main()
