#!/usr/bin/env python3
"""CLI delgado para diagnosticar el CSV fuente canónico."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.diagnostics import DiagnosticCsvError, DiagnosticOutputError, generate_diagnostics, write_diagnostics  # noqa: E402


class DiagnosticsCliError(RuntimeError):
    """Error esperado del CLI de diagnóstico."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnostica el CSV fuente canónico sin limpieza.")
    parser.add_argument(
        "--source-csv",
        type=Path,
        default=ROOT / "data/source/establecimientos_diversificado_mineduc.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/tablas")
    parser.add_argument("--docs-file", type=Path, default=ROOT / "docs/diagnostico.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_csv = _resolve_source_csv(args.source_csv)
        output_dir = _resolve_output_dir(args.output_dir)
        docs_file = _resolve_docs_file(args.docs_file)
        report = generate_diagnostics(source_csv)
        outputs = write_diagnostics(report, output_dir=output_dir, docs_path=docs_file)
    except (DiagnosticsCliError, DiagnosticCsvError, DiagnosticOutputError, OSError, csv.Error) as exc:
        print(f"Error de diagnóstico: {exc}", file=sys.stderr)
        return 1
    print(f"Diagnóstico generado: {outputs.docs_path}")
    return 0


def _resolve_source_csv(source_csv: Path) -> Path:
    source_root = (ROOT / "data/source").resolve()
    destination = source_csv.resolve()
    if destination != source_root and source_root not in destination.parents:
        raise DiagnosticsCliError(f"--source-csv debe estar dentro de data/source: {source_csv}")
    return destination


def _resolve_output_dir(output_dir: Path) -> Path:
    output_root = (ROOT / "outputs/tablas").resolve()
    destination = output_dir.resolve()
    if destination != output_root and output_root not in destination.parents:
        raise DiagnosticsCliError(f"--output-dir debe estar dentro de outputs/tablas: {output_dir}")
    return destination


def _resolve_docs_file(docs_file: Path) -> Path:
    destination = docs_file.resolve()
    expected = (ROOT / "docs/diagnostico.md").resolve()
    if destination != expected:
        raise DiagnosticsCliError(f"--docs-file debe ser docs/diagnostico.md: {docs_file}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
