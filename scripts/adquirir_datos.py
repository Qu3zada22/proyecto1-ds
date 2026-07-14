#!/usr/bin/env python3
"""CLI delgado para registrar CSV crudos o recapturar HTML oficial MINEDUC."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.acquisition import AcquisitionError, acquire_or_register_raw, capture_mineduc_diversificado_html  # noqa: E402


def _resolve_cli_raw_dir(raw_dir: Path) -> Path:
    candidate = raw_dir if raw_dir.is_absolute() else ROOT / raw_dir
    resolved = candidate.resolve()
    allowed_root = (ROOT / "data/raw").resolve()
    if resolved != allowed_root and allowed_root not in resolved.parents:
        raise AcquisitionError("El CLI público solo puede escribir dentro de data/raw del proyecto.")
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Registra CSV crudos o recaptura HTML oficial de MINEDUC.")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--source-url", help="URL oficial MINEDUC para descarga automática.")
    parser.add_argument("--output-file", help="Nombre del CSV o HTML destino dentro de data/raw/.")
    parser.add_argument("--manual-file", action="append", default=None, help="CSV manual existente dentro de data/raw/.")
    parser.add_argument("--fecha-extraccion")
    parser.add_argument("--version-dataset", default="v0.1.0")
    parser.add_argument("--cobertura", default="Alcance disponible registrado")
    parser.add_argument("--alcance-faltante", help="Alcance esperado que MINEDUC no publicó o no estuvo disponible.")
    parser.add_argument("--departamento")
    parser.add_argument("--capture-html", action="store_true", help="Recaptura HTML WebForms oficial de diversificado por departamento.")
    parser.add_argument("--department-code", help="Código de departamento usado por el formulario MINEDUC.")
    parser.add_argument("--department-name", help="Nombre de departamento para registrar en el manifest.")
    parser.add_argument("--confirm-overwrite", action="store_true", help="Confirma sobrescritura de CSV crudo existente.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        raw_dir = _resolve_cli_raw_dir(args.raw_dir)
        if args.capture_html:
            if not args.department_code or not args.department_name:
                raise AcquisitionError("--department-code y --department-name son obligatorios con --capture-html.")
            entries = capture_mineduc_diversificado_html(
                raw_dir,
                department_code=args.department_code,
                department_name=args.department_name,
                output_filename=args.output_file,
                extraction_date=args.fecha_extraccion,
                version_dataset=args.version_dataset,
                allow_overwrite=args.confirm_overwrite,
            )
        else:
            entries = acquire_or_register_raw(
                raw_dir,
                source_url=args.source_url,
                output_filename=args.output_file,
                manual_files=args.manual_file,
                extraction_date=args.fecha_extraccion,
                version_dataset=args.version_dataset,
                cobertura=args.cobertura,
                alcance_faltante=args.alcance_faltante,
                departamento=args.departamento,
                allow_overwrite=args.confirm_overwrite,
            )
    except AcquisitionError as exc:
        print(f"Error de adquisición: {exc}", file=sys.stderr)
        return 1
    print(f"Manifest actualizado con {len(entries)} lote(s): {raw_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
