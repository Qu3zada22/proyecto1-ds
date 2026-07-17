#!/usr/bin/env python3
"""CLI delgado para detectar duplicados parciales por similitud."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.duplicates import (  # noqa: E402
    NAME_THRESHOLD,
    DuplicatesCsvError,
    detect_partial_duplicates,
    write_duplicate_outputs,
)


class DuplicatesCliError(RuntimeError):
    """Error esperado del CLI de duplicados."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detecta duplicados parciales sin borrado automático.")
    parser.add_argument(
        "--source-csv",
        type=Path,
        default=ROOT / "data/processed/establecimientos_diversificado_limpio.csv",
    )
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "outputs/tablas")
    parser.add_argument("--reports-dir", type=Path, default=ROOT / "outputs/reportes")
    parser.add_argument("--threshold", type=float, default=NAME_THRESHOLD)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_csv = _resolve_under(args.source_csv, ROOT / "data/processed", "--source-csv")
        tables_dir = _resolve_under(args.tables_dir, ROOT / "outputs/tablas", "--tables-dir")
        reports_dir = _resolve_under(args.reports_dir, ROOT / "outputs/reportes", "--reports-dir")
        report = detect_partial_duplicates(source_csv, threshold=args.threshold)
        outputs = write_duplicate_outputs(report, tables_dir=tables_dir, reports_dir=reports_dir)
    except (DuplicatesCliError, DuplicatesCsvError, OSError, csv.Error) as exc:
        print(f"Error de duplicados: {exc}", file=sys.stderr)
        return 1
    print(f"Candidatos a duplicado parcial: {report.summary['candidatos_parciales']}")
    print(f"Tabla de candidatos: {outputs.candidates_path}")
    print(f"Reporte: {outputs.report_path}")
    return 0


def _resolve_under(path: Path, allowed_root: Path, flag: str) -> Path:
    root = allowed_root.resolve()
    destination = path.resolve()
    if destination != root and root not in destination.parents:
        raise DuplicatesCliError(f"{flag} debe estar dentro de {allowed_root.relative_to(ROOT).as_posix()}: {path}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
