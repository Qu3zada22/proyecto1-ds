#!/usr/bin/env python3
"""CLI para generar recomendaciones de revisión sin alterar datasets."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.pending_review import (  # noqa: E402
    DEFAULT_CANDIDATES_CSV,
    DEFAULT_CATALOG_CSV,
    DEFAULT_CLEAN_CSV,
    DEFAULT_REPORTS_DIR,
    DEFAULT_TABLES_DIR,
    DEFAULT_TERRITORY_CSV,
    PendingReviewError,
    generate_pending_review,
)


class PendingReviewCliError(ValueError):
    """Ruta de salida no permitida por el CLI."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera recomendaciones auditables sin modificar datasets.")
    parser.add_argument("--clean-csv", type=Path, default=ROOT / DEFAULT_CLEAN_CSV)
    parser.add_argument("--candidates-csv", type=Path, default=ROOT / DEFAULT_CANDIDATES_CSV)
    parser.add_argument("--territory-csv", type=Path, default=ROOT / DEFAULT_TERRITORY_CSV)
    parser.add_argument("--catalog-csv", type=Path, default=ROOT / DEFAULT_CATALOG_CSV)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / DEFAULT_TABLES_DIR)
    parser.add_argument("--reports-dir", type=Path, default=ROOT / DEFAULT_REPORTS_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        tables = _under_outputs(args.tables_dir, "--tables-dir")
        reports = _under_outputs(args.reports_dir, "--reports-dir")
        outputs = generate_pending_review(
            args.clean_csv, args.candidates_csv, args.territory_csv, args.catalog_csv,
            tables_dir=tables, reports_dir=reports, project_root=ROOT,
        )
    except (PendingReviewCliError, PendingReviewError, OSError, csv.Error) as exc:
        print(f"Error de recomendaciones: {exc}", file=sys.stderr)
        return 1
    print("Recomendaciones generadas sin modificar datasets:")
    for path in (outputs.duplicates_path, outputs.phones_path, outputs.territory_path, outputs.report_path):
        print(f"  {path.relative_to(ROOT)}")
    return 0


def _under_outputs(path: Path, flag: str) -> Path:
    output_root = (ROOT / "outputs").resolve()
    resolved = path.resolve()
    if resolved != output_root and output_root not in resolved.parents:
        raise PendingReviewCliError(f"{flag} debe estar dentro de outputs: {path}")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
