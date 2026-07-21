"""Ensamblado reproducible del Code Book maestro de 21 variables."""

from __future__ import annotations

import csv
from datetime import date
import os
from pathlib import Path
import re

from proyecto1_ds.cleaning import MISSING_MARKERS
from proyecto1_ds.decisions import DEFAULT_PHONE_DECISIONS_CSV, PHONE_DECISION_FIELDS


VARIABLE_HEADING = re.compile(r"^## `([^`]+)`$", re.MULTILINE)
ANY_H2 = re.compile(r"^## .+$", re.MULTILINE)
REQUIRED_FIELDS = (
    "Descripción", "Tipo de dato", "Dominio permitido", "Valores posibles",
    "Tratamiento en limpieza", "Variable derivada",
)
SOURCE_MISSING = re.compile(r"^- \*\*Faltantes:\*\*\s+([\d,]+)\b.*$", re.MULTILINE)
UNIX_ABSOLUTE = re.compile(r"(?<![:/\w])/(?!/)[^\s`<>()]+")
WINDOWS_ABSOLUTE = re.compile(r"(?:(?<!\w)[A-Za-z]:[\\/]|(?<!\\)\\{2,}[^\\\s]+\\)")


class CodeBookError(ValueError):
    """Fuente ausente o estructuralmente inválida para el Code Book maestro."""


def build_code_book(
    anggie_markdown: Path | str,
    territorial_markdown: Path | str,
    clean_csv: Path | str,
    duplicates_csv: Path | str | None = None,
    problems_csv: Path | str | None = None,
    territory_csv: Path | str | None = None,
) -> str:
    clean_path = Path(clean_csv)
    header, rows = _read_clean(clean_path)
    tables = clean_path.parents[2] / "outputs/tablas"
    duplicates = _read_evidence(Path(duplicates_csv) if duplicates_csv else tables / "duplicados_parciales.csv", {"decision"})
    problems = _read_evidence(Path(problems_csv) if problems_csv else tables / "problemas_potenciales.csv", {"columna", "tipo", "conteo"})
    territory = _read_evidence(Path(territory_csv) if territory_csv else tables / "inconsistencias_territoriales.csv", {"filas", "decision"})
    probable = sum(row["decision"] == "duplicado_probable" for row in duplicates)
    pending = sum(row["decision"] in {"revisar", "revisar_institucional"} for row in duplicates)
    confirmed_independent = sum(row["decision"] == "independiente_confirmado" for row in duplicates)
    historical_phones = sum(_integer(row["conteo"]) for row in problems if row["columna"] == "TELEFONO" and row["tipo"] == "formato_sospechoso")
    current_phones = sum(bool(row["TELEFONO"]) and (not row["TELEFONO"].isdigit() or len(row["TELEFONO"]) != 8) for row in rows)
    numeric_wrong_length = sum(bool(row["TELEFONO"]) and row["TELEFONO"].isdigit() and len(row["TELEFONO"]) != 8 for row in rows)
    territorial = sum(_integer(row["filas"]) for row in territory if row["decision"] == "revisar")
    phone_manifest = clean_path.parents[2] / DEFAULT_PHONE_DECISIONS_CSV
    approved_phones = len(_read_evidence(phone_manifest, set(PHONE_DECISION_FIELDS))) if phone_manifest.exists() else 0
    pending_duplicates = probable + pending
    if len(header) != 21:
        raise CodeBookError(f"El dataset limpio debe tener exactamente 21 variables; tiene {len(header)}")
    sources = [
        (Path(anggie_markdown), "Anggie", "MINEDUC y evidencias de diagnóstico/limpieza"),
        (Path(territorial_markdown), "Iris", "MINEDUC y catálogo territorial reproducible"),
    ]
    sections: dict[str, tuple[str, str, str]] = {}
    source_orders: list[list[str]] = []
    metadata: tuple[str, str] | None = None
    for path, owner, provenance in sources:
        text = _read_markdown(path)
        source_metadata = _common_metadata(path, text)
        if metadata is not None and source_metadata != metadata:
            raise CodeBookError(f"Metadatos comunes incompatibles entre fuentes: {metadata} != {source_metadata}")
        metadata = source_metadata
        parsed = _parse_sections(path, text)
        source_orders.append(list(parsed))
        for variable, body in parsed.items():
            if variable in sections:
                raise CodeBookError(f"Variable duplicada entre fuentes: {variable}")
            sections[variable] = (body, owner, provenance)

    expected = set(header)
    actual = set(sections)
    if len(sections) != 21:
        raise CodeBookError(f"El Code Book debe contener exactamente 21 variables; contiene {len(sections)}")
    if actual != expected:
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        raise CodeBookError(f"Variables incompatibles; faltantes={missing}; extras={extra}")
    for order in source_orders:
        if order != [variable for variable in header if variable in order]:
            raise CodeBookError(f"Orden de variables inválido: {order}")

    missing_counts = {
        column: sum(_is_missing(row[column]) for row in rows) for column in header
    }
    extraction_date, version = metadata or ("", "")
    lines = [
        "# Code Book maestro — Establecimientos educativos de nivel Diversificado",
        "",
        "Este documento reúne las 21 variables del dataset limpio en su orden canónico. Se genera desde "
        "`docs/code_book/variables_anggie.md` y `docs/code_book/variables_territoriales.md`; no debe editarse manualmente.",
        "",
        "- **Fuente canónica:** `data/source/establecimientos_diversificado_mineduc.csv`.",
        "- **Dataset documentado:** `data/processed/establecimientos_diversificado_limpio.csv`.",
        "- **Linaje:** HTML oficiales MINEDUC + manifest → fuente canónica → limpieza/enriquecimiento → dataset limpio.",
        f"- **Fecha exacta de extracción:** {extraction_date}.",
        f"- **Versión del conjunto limpio:** {version}.",
        "- **Contribuciones:** Anggie documenta 17 variables; Iris documenta 4 variables territoriales; Jonathan ensambla el maestro.",
        "- **Área de trabajo aceptada:** No existe un Google Docs asociado a esta entrega; este archivo Markdown versionado en GitHub es el área de trabajo admitida por la rúbrica.",
        "- **Evidencia de Anggie:** [`7bac6048f68a116b30e93a65eedc4dcf87412407`](https://github.com/Qu3zada22/proyecto1-ds/commit/7bac6048f68a116b30e93a65eedc4dcf87412407), sección de 17 variables.",
        "- **Evidencia de Iris:** [`bdf87360b4fa7081dac347f373d6a739dc262c2e`](https://github.com/Qu3zada22/proyecto1-ds/commit/bdf87360b4fa7081dac347f373d6a739dc262c2e), sección de variables territoriales.",
        f"- **Pendientes:** {pending_duplicates} pares ({probable} `duplicado_probable` + {pending} `revisar`), {current_phones} teléfonos sospechosos vigentes y {territorial} filas territoriales permanecen pendientes.",
        f"- **Decisiones aprobadas:** {confirmed_independent} pares `independiente_confirmado` y {approved_phones} normalizaciones telefónicas exactas; no hubo fusiones ni borrados.",
        f"- **Referencia histórica telefónica:** el diagnóstico inicial conserva {historical_phones} hallazgos históricos agregados por caracteres no numéricos; además, el control vigente detecta {numeric_wrong_length} teléfonos numéricos vigentes con longitud distinta de 8. La evidencia histórica agregada no establece correspondencia registro por registro.",
        "- **PDF reproducible:** `uv run python scripts/generar_code_book_pdf.py` genera `docs/code_book.pdf`.",
        "",
        "## Cómo leer este documento",
        "",
        "Los conteos de nulos corresponden al dataset limpio. `revisar` indica evidencia preservada, no un error corregido. "
        "Las secciones fuente continúan siendo la autoridad editable de cada responsable.",
        "",
    ]
    for variable in header:
        body, owner, provenance = sections[variable]
        count = missing_counts[variable]
        reported = _reported_missing(body)
        if reported is not None and reported != count:
            raise CodeBookError(
                f"Faltantes contradictorios para {variable}: fuente={reported}; dataset limpio={count}"
            )
        body = SOURCE_MISSING.sub("", body).strip()
        percentage = count * 100 / len(rows) if rows else 0
        lines.extend([
            f"## `{variable}`", "", body, "",
            f"- **Nulos/NA en el dataset limpio:** {count} ({percentage:.2f}%).",
            f"- **Fuente/procedencia:** {provenance}; ver la sección canónica de {owner}.",
            f"- **Fecha exacta de extracción:** {extraction_date}.",
            f"- **Versión del conjunto limpio:** {version}.",
            f"- **Responsable de la sección:** {owner}.", "", "---", "",
        ])
    lines.extend([
        "## Evidencia transversal y trabajo pendiente", "",
        f"- Duplicados: `outputs/tablas/duplicados_parciales.csv` conserva {pending_duplicates} pendientes ({probable} `duplicado_probable` + {pending} `revisar`) y {confirmed_independent} independientes confirmados.",
        f"- Teléfonos vigentes: el control estricto sobre el limpio conserva {current_phones} sospechosos; todo valor no vacío debe tener exactamente 8 dígitos.",
        f"- Referencia histórica: `outputs/tablas/problemas_potenciales.csv` conserva {historical_phones} hallazgos agregados del diagnóstico inicial por caracteres no numéricos; el limpio también contiene {numeric_wrong_length} valores numéricos con longitud distinta de 8, sin inferir correspondencia registro por registro.",
        f"- Territorio: `outputs/tablas/inconsistencias_territoriales.csv` conserva {territorial} filas `revisar`.",
        "- La auditoría de entrega se conserva como recibo interno en `docs/auditoria_final.md`; no sustituye ninguno de los cinco materiales exigidos.", "",
    ])
    return "\n".join(lines)


def write_code_book(markdown: str, output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(markdown, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def _read_clean(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise CodeBookError(f"No se pudo leer el dataset limpio: {path}: {exc}") from exc
    if not raw or not raw[0] or len(raw[0]) != len(set(raw[0])) or any(len(row) != len(raw[0]) for row in raw[1:]):
        raise CodeBookError(f"Dataset limpio vacío o malformado: {path}")
    if len(raw) == 1:
        raise CodeBookError(f"Dataset limpio sin registros: {path}")
    return raw[0], [dict(zip(raw[0], row, strict=True)) for row in raw[1:]]


def _read_evidence(path: Path, required: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise CodeBookError(f"No se pudo leer evidencia: {path}: {exc}") from exc
    if not raw or not required.issubset(raw[0]) or any(len(row) != len(raw[0]) for row in raw[1:]):
        raise CodeBookError(f"Evidencia vacía o malformada: {path}")
    return [dict(zip(raw[0], row, strict=True)) for row in raw[1:]]


def _integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise CodeBookError(f"Conteo inválido en evidencia: {value}") from exc
    if number < 0:
        raise CodeBookError(f"Conteo negativo en evidencia: {value}")
    return number


def _read_markdown(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CodeBookError(f"No se pudo leer la fuente del Code Book: {path}: {exc}") from exc
    if UNIX_ABSOLUTE.search(text) or WINDOWS_ABSOLUTE.search(text):
        raise CodeBookError(f"Fuente con ruta absoluta no portable: {path}")
    return text


def _common_metadata(path: Path, text: str) -> tuple[str, str]:
    extracted = re.search(r"^- \*\*Fecha exacta de extracción:\*\*\s+(\d{4}-\d{2}-\d{2})\b", text, re.MULTILINE)
    version = re.search(r"^- \*\*Versión del conjunto limpio:\*\*\s+(v\d+\.\d+\.\d+)\b", text, re.MULTILINE)
    origin = re.search(r"^- \*\*Fuente de origen(?: \([^\n*]+\))?:\*\*\s+(.\S.*)$", text, re.MULTILINE)
    if not extracted or not version or not origin:
        raise CodeBookError(f"Metadatos comunes incompletos o vacíos: {path}")
    try:
        date.fromisoformat(extracted.group(1))
    except ValueError as exc:
        raise CodeBookError(f"Fecha exacta de extracción inválida: {path}") from exc
    return extracted.group(1), version.group(1)


def _parse_sections(path: Path, text: str) -> dict[str, str]:
    headings = list(ANY_H2.finditer(text))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        match = VARIABLE_HEADING.fullmatch(heading.group())
        if match is None:
            continue
        variable = match.group(1)
        if variable in sections:
            raise CodeBookError(f"Variable duplicada en {path}: {variable}")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():end].strip()
        if body.endswith("---"):
            body = body[:-3].rstrip()
        for field in REQUIRED_FIELDS:
            _required_value(path, variable, body, field)
        sections[variable] = body
    if not sections:
        raise CodeBookError(f"Fuente sin variables documentadas: {path}")
    return sections


def _is_missing(value: str) -> bool:
    return value.replace("\xa0", " ").strip().casefold() in MISSING_MARKERS


def _required_value(path: Path, variable: str, body: str, field: str) -> str:
    match = re.search(
        rf"^- \*\*{re.escape(field)}:\*\*(.*?)(?=^- \*\*[^*\n]+:\*\*|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if match is None or not match.group(1).strip().strip("-").strip():
        raise CodeBookError(f"Campo {field} ausente o vacío para {variable} en {path}")
    return match.group(1).strip()


def _reported_missing(body: str) -> int | None:
    matches = SOURCE_MISSING.findall(body)
    if len(matches) > 1:
        raise CodeBookError("Una variable no puede declarar más de un conteo de Faltantes")
    return int(matches[0].replace(",", "")) if matches else None
