#!/usr/bin/env python3
"""CLI delgado para generar el PDF definitivo del Code Book."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto1_ds.code_book_pdf import PdfGenerationError, generate_code_book_pdf  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera reproduciblemente el PDF del Code Book maestro.")
    parser.add_argument("--markdown", type=Path, default=ROOT / "docs/code_book.md")
    parser.add_argument("--stylesheet", type=Path, default=ROOT / "docs/code_book.css")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/code_book.pdf")
    args = parser.parse_args(argv)
    try:
        docs = (ROOT / "docs").resolve()
        output = args.output.resolve()
        if output == docs or docs not in output.parents or output.suffix.casefold() != ".pdf":
            raise PdfGenerationError(f"--output debe ser un archivo PDF dentro de docs: {args.output}")
        output = generate_code_book_pdf(args.markdown, args.stylesheet, output)
    except PdfGenerationError as exc:
        print(f"Error al generar PDF: {exc}", file=sys.stderr)
        return 1
    print(f"PDF del Code Book generado: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
