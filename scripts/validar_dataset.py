#!/usr/bin/env python3
"""CLI delgado para ejecutar los siete controles finales del dataset limpio."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.validation import ValidationError, validate_dataset, write_validation_output  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valida los siete controles finales del conjunto limpio.")
    parser.add_argument("--clean-csv", type=Path, default=ROOT / "data/processed/establecimientos_diversificado_limpio.csv")
    parser.add_argument("--duplicates-csv", type=Path, default=ROOT / "outputs/tablas/duplicados_parciales.csv")
    parser.add_argument("--territory-csv", type=Path, default=ROOT / "outputs/tablas/inconsistencias_territoriales.csv")
    parser.add_argument("--problems-csv", type=Path, default=ROOT / "outputs/tablas/problemas_potenciales.csv")
    parser.add_argument("--catalog-csv", type=Path, default=ROOT / "data/reference/catalogo_territorial.csv")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "outputs/tablas/validacion_final.csv")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        clean = _under(args.clean_csv, ROOT / "data/processed", "--clean-csv")
        duplicates = _under(args.duplicates_csv, ROOT / "outputs/tablas", "--duplicates-csv")
        territory = _under(args.territory_csv, ROOT / "outputs/tablas", "--territory-csv")
        problems = _under(args.problems_csv, ROOT / "outputs/tablas", "--problems-csv")
        catalog = _under(args.catalog_csv, ROOT / "data/reference", "--catalog-csv")
        output = _under(args.output_csv, ROOT / "outputs/tablas", "--output-csv")
        result = validate_dataset(clean, duplicates, territory, problems, catalog_csv=catalog)
        write_validation_output(result, output)
    except (ValidationError, OSError, csv.Error, ValueError) as exc:
        print(f"Error de validación final: {exc}", file=sys.stderr)
        return 1
    reviews = sum(row["estado"] == "requiere_revision" for row in result.rows)
    failures = sum(row["estado"] == "falla" for row in result.rows)
    print(f"Validación final: 7 controles; {reviews} requieren revisión; {failures} fallan.")
    print(f"Tabla: {output}")
    return 1 if failures else 0


def _under(path: Path, allowed: Path, flag: str) -> Path:
    root, destination = allowed.resolve(), path.resolve()
    if destination != root and root not in destination.parents:
        raise ValueError(f"{flag} debe estar dentro de {allowed.relative_to(ROOT).as_posix()}: {path}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
