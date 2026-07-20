#!/usr/bin/env python3
"""CLI delgado para aplicar reglas de decisión a los candidatos a duplicado parcial."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.duplicates import (  # noqa: E402
    DEFAULT_CANDIDATES_CSV,
    DuplicatesCsvError,
    apply_duplicate_decisions,
)

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
        bitacora_path = ROOT / "outputs/tablas/bitacora_limpieza.csv"
        summary = apply_duplicate_decisions(candidates_csv, bitacora_csv=bitacora_path)
    except (DecisionCliError, DuplicatesCsvError, OSError, csv.Error) as exc:
        print(f"Error de decisión: {exc}", file=sys.stderr)
        return 1

    print(f"Decisiones aplicadas: {summary.total} pares en {summary.candidates_path}")
    print(f"  duplicado_probable : {summary.duplicado_probable}")
    print(f"  independiente      : {summary.independiente}")
    print(f"  revisar            : {summary.revisar}")
    print(f"Bitácora actualizada: {bitacora_path}")
    return 0


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
