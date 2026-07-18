#!/usr/bin/env python3
"""Genera el catálogo territorial oficial (INE, Censo 2018) versionado en data/reference/."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = (
    "https://raw.githubusercontent.com/dervinluna/guatemala-lugares-json/main/"
    "centroides-de-lugares-poblados-de-la-republica-de-guatemala.-censo-2018.json"
)
OUTPUT = ROOT / "data/reference/catalogo_territorial.csv"
FIELDS = ["departamento_codigo", "departamento", "municipio_codigo", "municipio"]


def main(argv: list[str] | None = None) -> int:
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:  # noqa: S310 - URL fija de fuente oficial.
            data = json.loads(response.read().decode("utf-8"))
    except OSError as exc:
        print(f"Error al descargar el catálogo INE: {exc}", file=sys.stderr)
        return 1

    rows = [
        {
            "departamento_codigo": departamento["codigo"],
            "departamento": departamento["nombre"],
            "municipio_codigo": municipio["codigo"],
            "municipio": municipio["nombre"],
        }
        for departamento in data
        for municipio in departamento["municipios"]
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temp_path = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temp_path.replace(OUTPUT)
    print(f"Catálogo territorial generado: {OUTPUT} ({len(rows)} municipios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
