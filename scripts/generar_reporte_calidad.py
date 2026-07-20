#!/usr/bin/env python3
"""CLI delgado para generar el reporte integral de calidad antes/después."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.quality_report import QualityReportError, build_quality_report, write_quality_report  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera las métricas integrales de calidad antes/después.")
    parser.add_argument("--source-csv", type=Path, default=ROOT / "data/source/establecimientos_diversificado_mineduc.csv")
    parser.add_argument("--clean-csv", type=Path, default=ROOT / "data/processed/establecimientos_diversificado_limpio.csv")
    parser.add_argument("--problems-csv", type=Path, default=ROOT / "outputs/tablas/problemas_potenciales.csv")
    parser.add_argument("--log-csv", type=Path, default=ROOT / "outputs/tablas/bitacora_limpieza.csv")
    parser.add_argument("--duplicates-csv", type=Path, default=ROOT / "outputs/tablas/duplicados_parciales.csv")
    parser.add_argument("--territory-csv", type=Path, default=ROOT / "outputs/tablas/inconsistencias_territoriales.csv")
    parser.add_argument("--validation-csv", type=Path, default=ROOT / "outputs/tablas/validacion_final.csv")
    parser.add_argument("--exact-duplicates-csv", type=Path, default=ROOT / "outputs/tablas/duplicados_exactos.csv")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "outputs/tablas/reporte_calidad_antes_despues.csv")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source = _under(args.source_csv, ROOT / "data/source", "--source-csv")
        clean = _under(args.clean_csv, ROOT / "data/processed", "--clean-csv")
        evidence = [
            _under(value, ROOT / "outputs/tablas", flag) for value, flag in [
                (args.problems_csv, "--problems-csv"), (args.log_csv, "--log-csv"),
                (args.duplicates_csv, "--duplicates-csv"), (args.territory_csv, "--territory-csv"),
                (args.validation_csv, "--validation-csv"), (args.exact_duplicates_csv, "--exact-duplicates-csv"),
            ]
        ]
        output = _under(args.output_csv, ROOT / "outputs/tablas", "--output-csv")
        rows = build_quality_report(source, clean, *evidence)
        write_quality_report(rows, output)
    except (QualityReportError, OSError, csv.Error, ValueError) as exc:
        print(f"Error de reporte de calidad: {exc}", file=sys.stderr)
        return 1
    print(f"Reporte integral generado: {len(rows)} métricas en {output}")
    return 0


def _under(path: Path, allowed: Path, flag: str) -> Path:
    root, destination = allowed.resolve(), path.resolve()
    if destination != root and root not in destination.parents:
        raise ValueError(f"{flag} debe estar dentro de {allowed.relative_to(ROOT).as_posix()}: {path}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
