#!/usr/bin/env python3
"""Orquesta el pipeline reproducible de consolidación, limpieza y entrega."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "data/reference/catalogo_territorial.csv"
BASE_STAGES = (
    ("Consolidación de los HTML oficiales", "consolidar_crudos.py"),
    ("Diagnóstico de la fuente canónica", "diagnosticar_crudos.py"),
    ("Limpieza y enriquecimiento", "limpiar_dataset.py"),
    ("Detección de duplicados parciales", "detectar_duplicados.py"),
    ("Aplicación de decisiones aprobadas", "decidir_duplicados.py"),
    ("Validación territorial", "validar_territorio.py"),
    ("Recomendaciones para revisión pendiente", "revisar_pendientes.py"),
    ("Validación final", "validar_dataset.py"),
    ("Reporte integral de calidad", "generar_reporte_calidad.py"),
    ("Code Book Markdown", "generar_code_book.py"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline reproducible desde los HTML oficiales hasta los entregables finales."
    )
    parser.add_argument(
        "--regenerar-catalogo",
        action="store_true",
        help="Descarga el espejo territorial fijado y verifica su hash antes de limpiar.",
    )
    parser.add_argument(
        "--sin-pdf",
        action="store_true",
        help="Omite el PDF cuando no están instaladas sus herramientas externas.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if Path.cwd().resolve() != ROOT:
        print(
            f"Error: ejecute este archivo desde la raíz del repositorio: {ROOT}",
            file=sys.stderr,
        )
        return 2
    if not args.regenerar_catalogo and not CATALOG.is_file():
        print(
            "Error: falta data/reference/catalogo_territorial.csv; "
            "use --regenerar-catalogo para reconstruirlo.",
            file=sys.stderr,
        )
        return 2

    stages = list(BASE_STAGES)
    if args.regenerar_catalogo:
        stages.insert(2, ("Catálogo territorial reproducible", "generar_catalogo_territorial.py"))
    if not args.sin_pdf:
        stages.append(("Code Book PDF", "generar_code_book_pdf.py"))

    for index, (description, script) in enumerate(stages, start=1):
        print(f"[{index}/{len(stages)}] {description}", flush=True)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            check=False,
        )
        if result.returncode:
            print(
                f"Error: {script} terminó con código {result.returncode}; el pipeline se detuvo.",
                file=sys.stderr,
            )
            return result.returncode

    print(
        "Pipeline reproducido. Los pendientes institucionales permanecen documentados; "
        "esta ejecución no los aprueba ni los resuelve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
