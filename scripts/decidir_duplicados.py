#!/usr/bin/env python3
"""CLI delgado para aplicar reglas de decisión a los candidatos a duplicado parcial."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.duplicates import (  # noqa: E402
    DEFAULT_CANDIDATES_CSV,
    DuplicatesCsvError,
    apply_duplicate_decisions,
)

BITACORA_PATH = ROOT / "outputs/tablas/bitacora_limpieza.csv"
BITACORA_FIELDS = ["variable", "regla", "filas_afectadas", "justificacion", "riesgo", "evidencia_fuente"]


class DecisionCliError(RuntimeError):
    """Error esperado del CLI de decisión de duplicados."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aplica reglas documentadas de decisión al CSV de candidatos a duplicado parcial."
    )
    parser.add_argument(
        "--candidates-csv",
        type=Path,
        default=ROOT / DEFAULT_CANDIDATES_CSV,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        candidates_csv = _resolve_under(
            args.candidates_csv, ROOT / "outputs/tablas", "--candidates-csv"
        )
        summary = apply_duplicate_decisions(candidates_csv)
    except (DecisionCliError, DuplicatesCsvError, OSError, csv.Error) as exc:
        print(f"Error de decisión: {exc}", file=sys.stderr)
        return 1

    _append_bitacora(summary.total, summary.duplicado_probable, summary.independiente, summary.revisar)

    print(f"Decisiones aplicadas: {summary.total} pares en {summary.candidates_path}")
    print(f"  duplicado_probable : {summary.duplicado_probable}")
    print(f"  independiente      : {summary.independiente}")
    print(f"  revisar            : {summary.revisar}")
    print(f"Bitácora actualizada: {BITACORA_PATH}")
    return 0


def _append_bitacora(total: int, dup_prob: int, indep: int, rev: int) -> None:
    write_header = not BITACORA_PATH.exists()
    temp_path = BITACORA_PATH.with_name(f".{BITACORA_PATH.name}.{os.getpid()}.tmp")
    existing: list[dict[str, str]] = []
    if BITACORA_PATH.exists():
        with BITACORA_PATH.open(newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    new_row = {
        "variable": "DUPLICADOS_PARCIALES",
        "regla": "decidir_duplicados",
        "filas_afectadas": str(total),
        "justificacion": (
            f"Reglas de decisión aplicadas sin borrado automático: "
            f"duplicado_probable={dup_prob} (confianza alta), "
            f"independiente={indep} (media + teléfonos distintos), "
            f"revisar={rev} (ambiguos)."
        ),
        "riesgo": "bajo",
        "evidencia_fuente": (
            "docs/planificacion.md; outputs/tablas/duplicados_parciales.csv; "
            "src/proyecto1_ds/duplicates.py apply_duplicate_decisions"
        ),
    }
    all_rows = existing + [new_row]
    try:
        with temp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=BITACORA_FIELDS, lineterminator="\n")
            if write_header or not existing:
                writer.writeheader()
            elif existing:
                writer.writeheader()
            writer.writerows(all_rows)
            f.flush()
        temp_path.replace(BITACORA_PATH)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _resolve_under(path: Path, allowed_root: Path, flag: str) -> Path:
    root = allowed_root.resolve()
    destination = path.resolve()
    if destination != root and root not in destination.parents:
        raise DecisionCliError(
            f"{flag} debe estar dentro de {allowed_root.relative_to(ROOT).as_posix()}: {path}"
        )
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
