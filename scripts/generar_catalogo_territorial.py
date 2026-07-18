#!/usr/bin/env python3
"""Genera un catálogo versionado desde un espejo del INE/Censo 2018."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REVISION = "05b3fce5d7ad57ee09d429b58ee9be17dd117d7a"
SOURCE_URL = (
    f"https://raw.githubusercontent.com/dervinluna/guatemala-lugares-json/{SOURCE_REVISION}/"
    "centroides-de-lugares-poblados-de-la-republica-de-guatemala.-censo-2018.json"
)
SOURCE_SHA256 = "e94f891411281b1c77f12a1c46fa424d62d033d7b7021318585065b3e5c57455"
SOURCE_DESCRIPTION = "Espejo/conversión comunitaria fijada; no es una publicación primaria del INE."
PRIMARY_SOURCE = "INE Guatemala, Censo 2018 (fuente primaria declarada por el espejo)."
OUTPUT = ROOT / "data/reference/catalogo_territorial.csv"
FIELDS = ["departamento_codigo", "departamento", "municipio_codigo", "municipio"]


class CatalogError(ValueError):
    """El recurso no satisface el contrato reproducible del catálogo."""


def generate_catalog(payload: bytes, output: Path = OUTPUT, *, expected_sha256: str = SOURCE_SHA256) -> None:
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise CatalogError("El SHA-256 del espejo territorial no coincide con el valor fijado.")
    try:
        data = json.loads(payload)
        rows = [
            {"departamento_codigo": department["codigo"], "departamento": department["nombre"],
             "municipio_codigo": municipality["codigo"], "municipio": municipality["nombre"]}
            for department in data for municipality in department["municipios"]
        ]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise CatalogError("El espejo territorial no cumple el esquema JSON esperado.") from exc
    department_codes = {row["departamento_codigo"] for row in rows}
    municipality_codes = [row["municipio_codigo"] for row in rows]
    if (len(data), len(rows), len(department_codes)) != (22, 340, 22):
        raise CatalogError("El catálogo debe contener 22 departamentos y 340 municipios.")
    if any(not all(str(value).strip() for value in row.values()) for row in rows):
        raise CatalogError("El catálogo contiene códigos o nombres vacíos.")
    if len(set(municipality_codes)) != 340:
        raise CatalogError("Los códigos municipales deben ser únicos.")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        temp_path.write_text(buffer.getvalue(), encoding="utf-8", newline="")
        temp_path.replace(output)
    finally:
        temp_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:  # noqa: S310 - espejo fijado por revisión y hash.
            payload = response.read()
        generate_catalog(payload)
    except (OSError, CatalogError) as exc:
        print(f"Error al generar el catálogo territorial: {exc}", file=sys.stderr)
        return 1
    print(f"Catálogo territorial generado: {OUTPUT} (340 municipios; {SOURCE_DESCRIPTION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
