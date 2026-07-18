#!/usr/bin/env python3
"""CLI delgado para generar el dataset limpio trazable."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.cleaning import (  # noqa: E402
    DEFAULT_CLEAN_CSV,
    DEFAULT_SOURCE_CSV,
    DEFAULT_TABLES_DIR,
    CleaningCsvError,
    CleaningOutputError,
    clean_dataset,
    write_cleaning_outputs,
)
from proyecto1_ds.enrichment import DEFAULT_CATALOG_CSV, EnrichmentError, enrich_result  # noqa: E402


class CleaningCliError(RuntimeError):
    """Error esperado del CLI de limpieza."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera el dataset limpio conservador y trazable.")
    parser.add_argument("--source-csv", type=Path, default=ROOT / DEFAULT_SOURCE_CSV)
    parser.add_argument("--output-file", type=Path, default=ROOT / DEFAULT_CLEAN_CSV)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / DEFAULT_TABLES_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 1
    try:
        source_csv = _resolve_source_csv(args.source_csv)
        output_file = _resolve_output_file(args.output_file)
        tables_dir = _resolve_tables_dir(args.tables_dir)
        result = clean_dataset(source_csv)
        result = enrich_result(result, catalog_csv=ROOT / DEFAULT_CATALOG_CSV)
        outputs = write_cleaning_outputs(
            result,
            clean_csv_path=output_file,
            tables_dir=tables_dir,
            project_root=ROOT,
        )
    except (CleaningCliError, CleaningCsvError, CleaningOutputError, EnrichmentError, OSError, csv.Error) as exc:
        print(f"Error de limpieza: {exc}", file=sys.stderr)
        return 1
    print(f"Dataset limpio generado: {outputs.clean_csv_path}")
    print(f"Bitácora de limpieza: {outputs.log_path}")
    print(f"Reporte antes/después: {outputs.report_path}")
    return 0


def _resolve_source_csv(source_csv: Path) -> Path:
    source_root = Path(os.path.normpath(ROOT / "data/source"))
    source = _absolute_lexical_path(source_csv)
    try:
        relative_source = source.relative_to(source_root)
    except ValueError:
        raise CleaningCliError(f"--source-csv debe estar dentro de data/source: {source_csv}")
    _reject_symlinked_source(source_root, relative_source, source_csv)
    return source


def _absolute_lexical_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    return Path(os.path.normpath(candidate))


def _reject_symlinked_source(source_root: Path, relative_source: Path, original_source: Path) -> None:
    current = source_root
    if current.is_symlink():
        raise CleaningCliError(f"--source-csv debe estar dentro de data/source: {original_source}")
    for part in relative_source.parts:
        current = current / part
        if current.is_symlink():
            raise CleaningCliError(f"--source-csv debe estar dentro de data/source: {original_source}")


def _resolve_output_file(output_file: Path) -> Path:
    """Valida temprano para UX; el core mantiene el guard autoritativo al escribir."""

    processed_root = (ROOT / "data/processed").resolve()
    destination = output_file.resolve()
    if destination != processed_root and processed_root not in destination.parents:
        raise CleaningCliError(f"--output-file debe estar dentro de data/processed: {output_file}")
    if destination == processed_root:
        raise CleaningCliError("--output-file debe ser un archivo .csv dentro de data/processed, no data/processed")
    if destination.exists() and destination.is_dir():
        raise CleaningCliError(f"--output-file debe ser un archivo .csv, no un directorio: {output_file}")
    if destination.suffix.casefold() != ".csv":
        raise CleaningCliError(f"--output-file debe terminar en .csv: {output_file}")
    return destination


def _resolve_tables_dir(tables_dir: Path) -> Path:
    tables_root = (ROOT / "outputs/tablas").resolve()
    destination = tables_dir.resolve()
    if destination != tables_root and tables_root not in destination.parents:
        raise CleaningCliError(f"--tables-dir debe estar dentro de outputs/tablas: {tables_dir}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
