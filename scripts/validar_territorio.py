#!/usr/bin/env python3
"""CLI delgado para validar la consistencia territorial contra el catálogo oficial."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.territorial import (  # noqa: E402
    TerritorialError,
    validate_territorial,
    write_territorial_outputs,
)


class TerritorialCliError(RuntimeError):
    """Error esperado del CLI de validación territorial."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valida departamento-municipio contra el catálogo oficial.")
    parser.add_argument(
        "--source-csv",
        type=Path,
        default=ROOT / "data/processed/establecimientos_diversificado_limpio.csv",
    )
    parser.add_argument("--catalog-csv", type=Path, default=ROOT / "data/reference/catalogo_territorial.csv")
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "outputs/tablas")
    parser.add_argument("--reports-dir", type=Path, default=ROOT / "outputs/reportes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_csv = _resolve_under(args.source_csv, ROOT / "data/processed", "--source-csv")
        catalog_csv = _resolve_under(args.catalog_csv, ROOT / "data/reference", "--catalog-csv")
        tables_dir = _resolve_under(args.tables_dir, ROOT / "outputs/tablas", "--tables-dir")
        reports_dir = _resolve_under(args.reports_dir, ROOT / "outputs/reportes", "--reports-dir")
        report = validate_territorial(source_csv, catalog_csv=catalog_csv, project_root=ROOT)
        outputs = write_territorial_outputs(report, tables_dir=tables_dir, reports_dir=reports_dir)
    except (TerritorialCliError, TerritorialError, OSError, csv.Error) as exc:
        print(f"Error de validación territorial: {exc}", file=sys.stderr)
        return 1
    print(f"Parejas inconsistentes: {report.summary['parejas_inconsistentes']} "
          f"({report.summary['filas_inconsistentes']} filas)")
    print(f"Tabla: {outputs.inconsistencies_path}")
    print(f"Reporte: {outputs.report_path}")
    return 0


def _resolve_under(path: Path, allowed_root: Path, flag: str) -> Path:
    root = allowed_root.resolve()
    destination = path.resolve()
    if destination != root and root not in destination.parents:
        raise TerritorialCliError(f"{flag} debe estar dentro de {allowed_root.relative_to(ROOT).as_posix()}: {path}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
