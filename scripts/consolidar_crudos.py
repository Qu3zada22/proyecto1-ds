#!/usr/bin/env python3
"""CLI delgado para consolidar artefactos crudos en data/source."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.consolidation import ConsolidationError, consolidate_raw  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consolida CSV crudos o HTML oficial MINEDUC sin limpieza.")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--manifest", type=Path, default=None, help="Ruta opcional al manifest.json crudo.")
    parser.add_argument(
        "--output-file",
        type=Path,
        default=ROOT / "data/source/establecimientos_diversificado_mineduc.csv",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        raw_dir = _resolve_cli_raw_dir(args.raw_dir)
        manifest_path = _resolve_cli_manifest(args.manifest)
        output_file = _resolve_cli_output_file(args.output_file)
        output_path = consolidate_raw(raw_dir=raw_dir, manifest_path=manifest_path, output_path=output_file)
    except ConsolidationError as exc:
        print(f"Error de consolidación: {exc}", file=sys.stderr)
        return 1
    print(f"Fuente canónica generada: {output_path}")
    return 0


def _resolve_cli_raw_dir(raw_dir: Path) -> Path:
    raw_root = (ROOT / "data/raw").resolve()
    resolved = raw_dir.resolve()
    if raw_root != resolved and raw_root not in resolved.parents:
        raise ConsolidationError(f"--raw-dir debe estar dentro de data/raw: {raw_dir}")
    return resolved


def _resolve_cli_manifest(manifest: Path | None) -> Path | None:
    if manifest is None:
        return None
    raw_root = (ROOT / "data/raw").resolve()
    resolved = manifest.resolve()
    if raw_root != resolved and raw_root not in resolved.parents:
        raise ConsolidationError(f"--manifest debe estar dentro de data/raw: {manifest}")
    return resolved


def _resolve_cli_output_file(output_file: Path) -> Path:
    source_root = (ROOT / "data/source").resolve()
    destination = output_file.resolve()
    if source_root != destination.parent and source_root not in destination.parents:
        raise ConsolidationError(f"--output-file debe estar dentro de data/source: {output_file}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
