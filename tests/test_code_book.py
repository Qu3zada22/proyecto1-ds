from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import re

import pytest

from proyecto1_ds.code_book import CodeBookError, build_code_book, write_code_book


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generar_code_book.py"
ANGGIE = ROOT / "docs/code_book/variables_anggie.md"
TERRITORIAL = ROOT / "docs/code_book/variables_territoriales.md"
CLEAN = ROOT / "data/processed/establecimientos_diversificado_limpio.csv"
VARIABLE_HEADING = re.compile(r"^## `([^`]+)`$", re.MULTILINE)


def _header(path: Path = CLEAN) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


def _temporary_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    anggie = tmp_path / "docs/code_book/variables_anggie.md"
    territorial = tmp_path / "docs/code_book/variables_territoriales.md"
    clean = tmp_path / "data/processed/establecimientos_diversificado_limpio.csv"
    output = tmp_path / "docs/code_book.md"
    anggie.parent.mkdir(parents=True)
    clean.parent.mkdir(parents=True)
    anggie.write_text(ANGGIE.read_text(encoding="utf-8"), encoding="utf-8")
    territorial.write_text(TERRITORIAL.read_text(encoding="utf-8"), encoding="utf-8")
    clean.write_bytes(CLEAN.read_bytes())
    tables = tmp_path / "outputs/tablas"
    tables.mkdir(parents=True)
    for name in ("duplicados_parciales.csv", "problemas_potenciales.csv", "inconsistencias_territoriales.csv"):
        (tables / name).write_bytes((ROOT / "outputs/tablas" / name).read_bytes())
    return anggie, territorial, clean, output


def test_maestro_contiene_21_variables_exactas_en_orden_canonico():
    markdown = build_code_book(ANGGIE, TERRITORIAL, CLEAN)

    assert VARIABLE_HEADING.findall(markdown) == _header()
    assert len(VARIABLE_HEADING.findall(markdown)) == len(set(VARIABLE_HEADING.findall(markdown))) == 21


def test_cada_variable_conserva_campos_y_metadatos_obligatorios():
    markdown = build_code_book(ANGGIE, TERRITORIAL, CLEAN)
    starts = list(VARIABLE_HEADING.finditer(markdown))
    required = (
        "**Descripción:**", "**Tipo de dato:**", "**Dominio permitido:**", "**Valores posibles:**",
        "**Tratamiento en limpieza:**", "**Nulos/NA en el dataset limpio:**",
        "**Fuente/procedencia:**", "**Fecha exacta de extracción:**",
        "**Versión del conjunto limpio:**", "**Responsable de la sección:**", "**Variable derivada:**",
    )

    for index, match in enumerate(starts):
        section = markdown[match.start(): starts[index + 1].start() if index + 1 < len(starts) else len(markdown)]
        assert all(field in section for field in required), match.group(1)


def test_rechaza_dataset_header_only_y_cardinalidad_distinta_de_21(tmp_path):
    anggie, territorial, clean, output = _temporary_inputs(tmp_path)
    output.write_bytes(b"maestro anterior\n")
    _write_clean(clean, _header(), [])
    with pytest.raises(CodeBookError, match="sin registros"):
        write_code_book(build_code_book(anggie, territorial, clean), output)
    assert output.read_bytes() == b"maestro anterior\n"

    _write_clean(clean, _header()[:-1], [[""] * 20])
    with pytest.raises(CodeBookError, match="exactamente 21"):
        build_code_book(anggie, territorial, clean)


@pytest.mark.parametrize("mutation", [
    ("- **Descripción:** Código", "- **Descripción:**\n- **Tipo de dato:** Texto", "Descripción"),
    ("- **Valores posibles:** 11,867", "- **Ejemplos:** 11,867", "Valores posibles"),
])
def test_rechaza_etiqueta_vacia_o_campo_obligatorio_ausente(tmp_path, mutation):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    old, new, expected = mutation
    text = anggie.read_text(encoding="utf-8")
    if expected == "Descripción":
        text = text.replace(text[text.index(old):text.index(".", text.index(old)) + 1], new, 1)
    else:
        text = text.replace(old, new, 1)
    anggie.write_text(text, encoding="utf-8")

    with pytest.raises(CodeBookError, match=expected):
        build_code_book(anggie, territorial, clean)


@pytest.mark.parametrize("absolute", ["/etc/passwd", r"C:\\datos\\fuente.csv", r"\\\\servidor\\datos"])
def test_rechaza_cualquier_ruta_absoluta_en_fuentes(tmp_path, absolute):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    anggie.write_text(anggie.read_text(encoding="utf-8") + f"\nRuta: {absolute}\n", encoding="utf-8")

    with pytest.raises(CodeBookError, match="ruta absoluta"):
        build_code_book(anggie, territorial, clean)


def test_deriva_metadata_coincidente_y_rechaza_conteo_fuente_contradictorio(tmp_path):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    for path in (anggie, territorial):
        path.write_text(
            path.read_text(encoding="utf-8").replace("2026-07-14", "2026-07-15").replace("v0.1.0", "v0.2.0"),
            encoding="utf-8",
        )
    markdown = build_code_book(anggie, territorial, clean)
    assert "2026-07-15" in markdown and "v0.2.0" in markdown
    assert "2026-07-14" not in markdown and "v0.1.0" not in markdown
    assert "**Faltantes:**" not in markdown

    anggie.write_text(anggie.read_text(encoding="utf-8").replace("**Faltantes:** 0", "**Faltantes:** 1", 1), encoding="utf-8")
    with pytest.raises(CodeBookError, match="Faltantes contradictorios"):
        build_code_book(anggie, territorial, clean)


def test_rechaza_metadata_inconsistente_entre_fuentes(tmp_path):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    territorial.write_text(territorial.read_text(encoding="utf-8").replace("v0.1.0", "v9.9.9"), encoding="utf-8")

    with pytest.raises(CodeBookError, match="Metadatos.*incompatibles"):
        build_code_book(anggie, territorial, clean)


def test_maestro_mantiene_pendientes_rutas_portables_y_pdf_fuera_de_alcance():
    markdown = build_code_book(ANGGIE, TERRITORIAL, CLEAN)

    assert all(value in markdown for value in ("978 pares", "718 `duplicado_probable`", "260 `revisar`", "245 teléfonos sospechosos vigentes", "145 filas"))
    assert "11 pares `independiente_confirmado`" in markdown
    assert "6 normalizaciones telefónicas exactas" in markdown
    assert "201 hallazgos históricos agregados" in markdown
    assert "50 teléfonos numéricos vigentes con longitud distinta de 8" in markdown
    assert "no establece correspondencia registro por registro" in markdown
    assert "scripts/generar_code_book_pdf.py" in markdown
    assert "Anggie" in markdown and "Iris" in markdown and "Jonathan" in markdown
    assert "/home/" not in markdown and "C:\\" not in markdown
    assert "data/source/establecimientos_diversificado_mineduc.csv" in markdown


def test_maestro_documenta_markdown_versionado_y_commits_reales_del_equipo():
    markdown = build_code_book(ANGGIE, TERRITORIAL, CLEAN)

    assert "No existe un Google Docs" in markdown
    assert "archivo Markdown versionado" in markdown
    assert "7bac6048f68a116b30e93a65eedc4dcf87412407" in markdown
    assert "bdf87360b4fa7081dac347f373d6a739dc262c2e" in markdown
    assert "github.com/Qu3zada22/proyecto1-ds/commit/" in markdown


def test_maestro_deriva_pendientes_de_evidencia_vigente(tmp_path):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    duplicates = tmp_path / "outputs/tablas/duplicados_parciales.csv"
    rows = list(csv.DictReader(duplicates.open(encoding="utf-8", newline="")))
    previous = build_code_book(anggie, territorial, clean)
    rows[0]["decision"] = "revisar"
    with duplicates.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    current = build_code_book(anggie, territorial, clean)
    probable = sum(row["decision"] == "duplicado_probable" for row in rows)
    pending = sum(row["decision"] in {"revisar", "revisar_institucional"} for row in rows)
    confirmed = sum(row["decision"] == "independiente_confirmado" for row in rows)

    assert current != previous
    assert f"{probable} `duplicado_probable` + {pending} `revisar`" in current
    assert f"{confirmed} independientes confirmados" in current


def test_maestro_deriva_telefonos_vigentes_del_limpio(tmp_path):
    anggie, territorial, clean, _ = _temporary_inputs(tmp_path)
    rows = list(csv.reader(clean.open(encoding="utf-8", newline="")))
    phone_index = rows[0].index("TELEFONO")
    target = next(row for row in rows[1:] if len(row[phone_index]) == 8 and row[phone_index].isdigit())
    target[phone_index] = target[phone_index][:-1]
    _write_clean(clean, rows[0], rows[1:])

    markdown = build_code_book(anggie, territorial, clean)
    records = [dict(zip(rows[0], row, strict=True)) for row in rows[1:]]
    suspicious = sum(
        bool(row["TELEFONO"]) and (not row["TELEFONO"].isdigit() or len(row["TELEFONO"]) != 8)
        for row in records
    )
    numeric_wrong = sum(
        bool(row["TELEFONO"]) and row["TELEFONO"].isdigit() and len(row["TELEFONO"]) != 8
        for row in records
    )

    assert f"{suspicious} teléfonos sospechosos vigentes" in markdown
    assert f"{numeric_wrong} teléfonos numéricos vigentes con longitud distinta de 8" in markdown
    assert "201 hallazgos históricos agregados" in markdown


def test_escritura_es_idempotente_byte_a_byte(tmp_path):
    anggie, territorial, clean, output = _temporary_inputs(tmp_path)
    markdown = build_code_book(anggie, territorial, clean)

    write_code_book(markdown, output)
    first = output.read_bytes()
    write_code_book(markdown, output)

    assert output.read_bytes() == first


@pytest.mark.parametrize("failure", ["missing", "malformed", "duplicate", "order"])
def test_fuente_invalida_preserva_maestro_previo(tmp_path, failure):
    anggie, territorial, clean, output = _temporary_inputs(tmp_path)
    output.write_bytes(b"maestro anterior\n")
    if failure == "missing":
        territorial.unlink()
    elif failure == "malformed":
        anggie.write_text(anggie.read_text(encoding="utf-8").replace("- **Descripción:**", "- **Detalle:**", 1), encoding="utf-8")
    elif failure == "duplicate":
        territorial.write_text(territorial.read_text(encoding="utf-8") + "\n## `DEPARTAMENTO`\n", encoding="utf-8")
    else:
        text = territorial.read_text(encoding="utf-8")
        territorial.write_text(text.replace("## `DEPARTAMENTO`", "## `TEMP`").replace("## `MUNICIPIO`", "## `DEPARTAMENTO`").replace("## `TEMP`", "## `MUNICIPIO`"), encoding="utf-8")

    with pytest.raises(CodeBookError):
        write_code_book(build_code_book(anggie, territorial, clean), output)

    assert output.read_bytes() == b"maestro anterior\n"


def test_cli_genera_maestro(tmp_path, monkeypatch, capsys):
    _temporary_inputs(tmp_path)
    spec = importlib.util.spec_from_file_location("code_book_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main([]) == 0
    assert "21 variables" in capsys.readouterr().out
    assert (tmp_path / "docs/code_book.md").exists()


def _write_clean(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
