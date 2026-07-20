"""Generación reproducible y validada del PDF definitivo del Code Book."""

from __future__ import annotations

from datetime import date
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


EXTRACTION_DATE = re.compile(r"\*\*Fecha exacta de extracción:\*\*\s+(\d{4}-\d{2}-\d{2})")
PDF_DATE = re.compile(rb"D:\d{14}\+00'00'")
TOOLS = ("pandoc", "chromium", "qpdf", "pdfinfo", "pdftotext")


class PdfGenerationError(RuntimeError):
    """El PDF no pudo generarse o validarse sin riesgo para la salida previa."""


def generate_code_book_pdf(
    markdown_path: Path | str,
    stylesheet_path: Path | str,
    output_path: Path | str,
) -> Path:
    markdown = Path(markdown_path)
    stylesheet = Path(stylesheet_path)
    output = Path(output_path)
    tools = {name: shutil.which(name) for name in TOOLS}
    missing = [name for name, executable in tools.items() if executable is None]
    if missing:
        raise PdfGenerationError(f"Herramientas requeridas ausentes: {', '.join(missing)}")

    try:
        source = markdown.read_text(encoding="utf-8")
        stylesheet.read_text(encoding="utf-8")
    except OSError as exc:
        raise PdfGenerationError(f"No se pudo leer una entrada del PDF: {exc}") from exc
    match = EXTRACTION_DATE.search(source)
    if match is None:
        raise PdfGenerationError("El Markdown no declara la fecha de extracción")
    try:
        extraction_date = date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise PdfGenerationError("La fecha de extracción del Markdown es inválida") from exc

    environment = {**os.environ, "LANG": "C.UTF-8", "TZ": "UTC"}
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".code-book-pdf-", dir=output.parent) as directory:
            temporary = Path(directory)
            markdown_hash = hashlib.sha256(source.encode()).hexdigest()
            render_source = temporary / "source.md"
            render_source.write_text(source + f"\n\nFuente Markdown SHA-256: `{markdown_hash}`\n", encoding="utf-8")
            html = temporary / "code_book.html"
            chrome_pdf = temporary / "chrome.pdf"
            normalized_pdf = temporary / "normalized.pdf"
            final_pdf = temporary / output.name
            _run([
                tools["pandoc"], str(render_source), "--from=gfm", "--standalone", "--embed-resources",
                "--metadata", "pagetitle=Code Book maestro", "--css", str(stylesheet), "--output", str(html),
            ], environment)
            _run([
                tools["chromium"], "--headless", "--no-sandbox", "--disable-gpu",
                f"--user-data-dir={temporary / 'chromium'}", "--no-pdf-header-footer",
                f"--print-to-pdf={chrome_pdf}", html.as_uri(),
            ], environment)
            _normalize_dates(chrome_pdf, normalized_pdf, extraction_date)
            _run([tools["qpdf"], "--deterministic-id", str(normalized_pdf), str(final_pdf)], environment)
            _run([tools["qpdf"], "--check", str(final_pdf)], environment)
            _validate_pdf(final_pdf, tools, environment, markdown_hash)
            final_pdf.replace(output)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        if isinstance(exc, subprocess.TimeoutExpired):
            raise PdfGenerationError(f"Tiempo agotado al ejecutar {Path(exc.cmd[0]).name}") from exc
        command = Path(exc.cmd[0]).name if isinstance(exc, subprocess.CalledProcessError) else "sistema"
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
        raise PdfGenerationError(f"Falló {command}: {detail}") from exc
    return output


def _normalize_dates(source: Path, destination: Path, extraction_date: date) -> None:
    pdf = source.read_bytes()
    fixed = f"D:{extraction_date:%Y%m%d}120000+00'00'".encode()
    pdf, replacements = PDF_DATE.subn(fixed, pdf)
    if replacements != 2:
        raise PdfGenerationError(f"Metadatos PDF inesperados: {replacements} fechas encontradas")
    destination.write_bytes(pdf)


def _validate_pdf(path: Path, tools: dict[str, str | None], environment: dict[str, str], markdown_hash: str) -> None:
    content = path.read_bytes()
    if len(content) <= 50 or not content.startswith(b"%PDF-"):
        raise PdfGenerationError("La salida PDF está vacía o tiene una firma inválida")
    info = _run([tools["pdfinfo"], str(path)], environment).stdout
    pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if pages is None or int(pages.group(1)) < 1:
        raise PdfGenerationError("El PDF no contiene páginas")
    if not re.search(r"^Page size:\s+612 x 792 pts \(letter\)$", info, re.MULTILINE):
        raise PdfGenerationError("El PDF no usa tamaño carta")
    text = _run([tools["pdftotext"], str(path), "-"], environment).stdout.strip()
    if not text:
        raise PdfGenerationError("El PDF no contiene texto extraíble")
    if text.count("Code Book maestro") != 1:
        raise PdfGenerationError("El PDF debe contener un solo título Code Book maestro")
    if markdown_hash not in text:
        raise PdfGenerationError("El PDF no acredita el hash del Markdown vigente")


def _run(command: list[str | None], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True, env=environment, timeout=120)
