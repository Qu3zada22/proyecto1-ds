from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import subprocess

import pytest

from proyecto1_ds.code_book_pdf import PdfGenerationError, generate_code_book_pdf


CHROME_PDF = (
    b"%PDF-1.4\n" + b"contenido" * 10 +
    b"/CreationDate (D:20260720054906+00'00')\n"
    b"/ModDate (D:20260720054906+00'00')\n%%EOF\n"
)
MARKDOWN = "# Code Book maestro\n\n**Fecha exacta de extracción:** 2026-07-14.\n"
MARKDOWN_HASH = hashlib.sha256(MARKDOWN.encode()).hexdigest()
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generar_code_book_pdf.py"


def _fake_tools(monkeypatch, *, fail_on: str | None = None, pdfinfo: str | None = None, text: str | None = None):
    monkeypatch.setattr("proyecto1_ds.code_book_pdf.shutil.which", lambda name: f"/usr/bin/{name}")

    def run(command, **kwargs):
        tool = Path(command[0]).name
        if tool == fail_on:
            raise subprocess.CalledProcessError(1, command, stderr="fallo simulado")
        if tool == "pandoc":
            assert "pagetitle=Code Book maestro" in command and "title=Code Book maestro" not in command
            Path(command[command.index("--output") + 1]).write_text("<html>Code Book</html>", encoding="utf-8")
        elif tool == "chromium":
            output = next(value.split("=", 1)[1] for value in command if value.startswith("--print-to-pdf="))
            Path(output).write_bytes(CHROME_PDF)
        elif tool == "qpdf" and "--check" not in command:
            Path(command[-1]).write_bytes(Path(command[-2]).read_bytes())
        stdout = ""
        if tool == "pdfinfo":
            stdout = pdfinfo if pdfinfo is not None else "Pages: 13\nPage size: 612 x 792 pts (letter)\n"
        elif tool == "pdftotext":
            stdout = text if text is not None else f"Code Book maestro — Diversificado\nFuente Markdown SHA-256: {MARKDOWN_HASH}\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    monkeypatch.setattr("proyecto1_ds.code_book_pdf.subprocess.run", run)


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    markdown = tmp_path / "docs/code_book.md"
    stylesheet = tmp_path / "docs/code_book.css"
    output = tmp_path / "docs/code_book.pdf"
    markdown.parent.mkdir()
    markdown.write_text(MARKDOWN, encoding="utf-8")
    stylesheet.write_text("body { color: black; }\n", encoding="utf-8")
    return markdown, stylesheet, output


def test_genera_pdf_determinista_validado_y_con_fecha_de_extraccion(tmp_path, monkeypatch):
    markdown, stylesheet, output = _inputs(tmp_path)
    _fake_tools(monkeypatch)

    generate_code_book_pdf(markdown, stylesheet, output)
    first = output.read_bytes()
    generate_code_book_pdf(markdown, stylesheet, output)

    assert output.read_bytes() == first
    assert len(first) > 50 and first.startswith(b"%PDF-")
    assert first.count(b"D:20260714120000+00'00'") == 2


@pytest.mark.parametrize("failure", ["pandoc", "chromium", "qpdf", "pdfinfo", "pdftotext"])
def test_fallo_de_herramienta_preserva_pdf_previo(tmp_path, monkeypatch, failure):
    markdown, stylesheet, output = _inputs(tmp_path)
    output.write_bytes(b"PDF anterior")
    _fake_tools(monkeypatch, fail_on=failure)

    with pytest.raises(PdfGenerationError, match=failure):
        generate_code_book_pdf(markdown, stylesheet, output)
    assert output.read_bytes() == b"PDF anterior"


@pytest.mark.parametrize(("pdfinfo", "text", "message"), [
    ("Pages: 0\nPage size: 612 x 792 pts (letter)\n", None, "páginas"),
    ("Pages: 13\nPage size: 595 x 842 pts (A4)\n", None, "tamaño carta"),
    (None, "", "texto extraíble"),
    (None, "Code Book maestro\nCode Book maestro\n", "título"),
])
def test_pdf_invalido_preserva_salida_previa(tmp_path, monkeypatch, pdfinfo, text, message):
    markdown, stylesheet, output = _inputs(tmp_path)
    output.write_bytes(b"PDF anterior")
    _fake_tools(monkeypatch, pdfinfo=pdfinfo, text=text)

    with pytest.raises(PdfGenerationError, match=message):
        generate_code_book_pdf(markdown, stylesheet, output)
    assert output.read_bytes() == b"PDF anterior"


def test_rechaza_dependencias_ausentes_y_markdown_sin_fecha(tmp_path, monkeypatch):
    markdown, stylesheet, output = _inputs(tmp_path)
    monkeypatch.setattr("proyecto1_ds.code_book_pdf.shutil.which", lambda name: None)
    with pytest.raises(PdfGenerationError, match="pandoc"):
        generate_code_book_pdf(markdown, stylesheet, output)

    _fake_tools(monkeypatch)
    markdown.write_text("# Code Book sin fecha\n", encoding="utf-8")
    with pytest.raises(PdfGenerationError, match="fecha de extracción"):
        generate_code_book_pdf(markdown, stylesheet, output)


def test_timeout_y_fallo_mkdir_preservan_pdf_previo(tmp_path, monkeypatch):
    markdown, stylesheet, output = _inputs(tmp_path)
    output.write_bytes(b"PDF anterior")
    _fake_tools(monkeypatch)
    monkeypatch.setattr("proyecto1_ds.code_book_pdf.subprocess.run", lambda command, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(command, 120)))
    with pytest.raises(PdfGenerationError, match="(?i)tiempo"):
        generate_code_book_pdf(markdown, stylesheet, output)
    monkeypatch.setattr("proyecto1_ds.code_book_pdf.Path.mkdir", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("sin permiso")))
    with pytest.raises(PdfGenerationError, match="sin permiso"):
        generate_code_book_pdf(markdown, stylesheet, output)
    assert output.read_bytes() == b"PDF anterior"


@pytest.mark.parametrize("output", ["data/raw/code_book.pdf", "fuera.pdf", "docs"])
def test_cli_rechaza_output_fuera_de_docs_sin_generar(tmp_path, monkeypatch, output):
    spec = importlib.util.spec_from_file_location("pdf_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "generate_code_book_pdf", lambda *_args: pytest.fail("no debe generar fuera de docs"))
    destination = tmp_path / output

    assert module.main(["--output", str(destination)]) == 1
    assert not destination.exists()
