#!/usr/bin/env python3
"""CLI delgado para ensamblar el Code Book maestro Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.code_book import CodeBookError, build_code_book, write_code_book  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensambla el Code Book maestro de 21 variables.")
    parser.add_argument("--anggie", type=Path, default=ROOT / "docs/code_book/variables_anggie.md")
    parser.add_argument("--territorial", type=Path, default=ROOT / "docs/code_book/variables_territoriales.md")
    parser.add_argument("--clean-csv", type=Path, default=ROOT / "data/processed/establecimientos_diversificado_limpio.csv")
    parser.add_argument("--duplicates-csv", type=Path, default=ROOT / "outputs/tablas/duplicados_parciales.csv")
    parser.add_argument("--problems-csv", type=Path, default=ROOT / "outputs/tablas/problemas_potenciales.csv")
    parser.add_argument("--territory-csv", type=Path, default=ROOT / "outputs/tablas/inconsistencias_territoriales.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/code_book.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        anggie = _under(args.anggie, ROOT / "docs/code_book", "--anggie")
        territorial = _under(args.territorial, ROOT / "docs/code_book", "--territorial")
        clean = _under(args.clean_csv, ROOT / "data/processed", "--clean-csv")
        duplicates = _under(args.duplicates_csv, ROOT / "outputs/tablas", "--duplicates-csv")
        problems = _under(args.problems_csv, ROOT / "outputs/tablas", "--problems-csv")
        territory = _under(args.territory_csv, ROOT / "outputs/tablas", "--territory-csv")
        output = _under(args.output, ROOT / "docs", "--output")
        markdown = build_code_book(anggie, territorial, clean, duplicates, problems, territory)
        write_code_book(markdown, output)
    except (CodeBookError, OSError, ValueError) as exc:
        print(f"Error de Code Book: {exc}", file=sys.stderr)
        return 1
    print(f"Code Book maestro generado: 21 variables en {output}")
    return 0


def _under(path: Path, allowed: Path, flag: str) -> Path:
    root, destination = allowed.resolve(), path.resolve()
    if destination != root and root not in destination.parents:
        raise ValueError(f"{flag} debe estar dentro de {allowed.relative_to(ROOT).as_posix()}: {path}")
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
