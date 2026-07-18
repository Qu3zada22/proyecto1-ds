"""Validación territorial contra catálogo oficial, sin corrección automática."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any
import unicodedata

from rapidfuzz import process


DEFAULT_CLEAN_CSV = Path("data/processed/establecimientos_diversificado_limpio.csv")
DEFAULT_CATALOG_CSV = Path("data/reference/catalogo_territorial.csv")
DEFAULT_TABLES_DIR = Path("outputs/tablas")
DEFAULT_REPORTS_DIR = Path("outputs/reportes")
DEPARTMENT_COLUMN = "DEPARTAMENTO"
MUNICIPALITY_COLUMN = "MUNICIPIO"
SUGGESTION_THRESHOLD = 80.0
# MINEDUC usa CIUDAD CAPITAL para el municipio de Guatemala; las "ZONA N" son sus zonas.
SPECIAL_DEPARTMENTS = {"CIUDAD CAPITAL": ("GUATEMALA", "GUATEMALA")}
INCONSISTENCY_FIELDS = [
    "departamento",
    "municipio",
    "filas",
    "tipo",
    "sugerencia_oficial",
    "similitud",
    "decision",
]


class TerritorialError(ValueError):
    """Error esperado al leer el CSV limpio o el catálogo."""


@dataclass(frozen=True)
class Catalog:
    departments: set[str]
    municipalities_by_department: dict[str, set[str]]
    department_by_municipality: dict[str, set[str]]
    official_department: dict[str, str]
    official_municipality: dict[str, str]


@dataclass(frozen=True)
class TerritorialReport:
    source_path: Path
    catalog_path: Path
    inconsistencies: list[dict[str, Any]]
    summary: dict[str, Any]


@dataclass(frozen=True)
class TerritorialOutputs:
    inconsistencies_path: Path
    report_path: Path


def validate_territorial(
    source_csv: Path | str = DEFAULT_CLEAN_CSV,
    *,
    catalog_csv: Path | str = DEFAULT_CATALOG_CSV,
    project_root: Path | str = Path.cwd(),
) -> TerritorialReport:
    """Compara cada pareja departamento-municipio contra el catálogo oficial."""

    source_path = Path(source_csv)
    catalog_path = Path(catalog_csv)
    catalog = _load_catalog(catalog_path)
    pair_counts = _count_pairs(source_path)

    inconsistencies: list[dict[str, Any]] = []
    valid_pairs = 0
    special_pairs = 0
    for (departamento, municipio), count in pair_counts.items():
        norm_department = _normalize(departamento)
        norm_municipality = _normalize(municipio)
        if norm_department in SPECIAL_DEPARTMENTS:
            special_pairs += 1
            continue
        result = _classify_pair(norm_department, norm_municipality, catalog)
        if result is None:
            valid_pairs += 1
            continue
        tipo, suggestion, score = result
        inconsistencies.append(
            {
                "departamento": departamento,
                "municipio": municipio,
                "filas": count,
                "tipo": tipo,
                "sugerencia_oficial": suggestion,
                "similitud": "" if score is None else round(score, 2),
                "decision": "revisar",
            }
        )

    inconsistencies.sort(key=lambda item: (-item["filas"], item["departamento"], item["municipio"]))
    logical_source = _logical_path(source_path, Path(project_root))
    logical_catalog = _logical_path(catalog_path, Path(project_root))
    summary = {
        "catalogo": logical_catalog.as_posix(),
        "parejas_distintas": len(pair_counts),
        "parejas_validas": valid_pairs,
        "parejas_regla_ciudad_capital": special_pairs,
        "parejas_inconsistentes": len(inconsistencies),
        "filas_inconsistentes": sum(item["filas"] for item in inconsistencies),
        "decision_por_defecto": "revisar (sin corrección automática)",
    }
    return TerritorialReport(
        source_path=logical_source,
        catalog_path=logical_catalog,
        inconsistencies=inconsistencies,
        summary=summary,
    )


def write_territorial_outputs(
    report: TerritorialReport,
    *,
    tables_dir: Path | str = DEFAULT_TABLES_DIR,
    reports_dir: Path | str = DEFAULT_REPORTS_DIR,
) -> TerritorialOutputs:
    tables_root = Path(tables_dir)
    reports_root = Path(reports_dir)
    tables_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)

    inconsistencies_path = tables_root / "inconsistencias_territoriales.csv"
    report_path = reports_root / "validacion_territorial.md"
    csv_bytes = _rows_bytes(INCONSISTENCY_FIELDS, report.inconsistencies)
    markdown_bytes = _render_markdown(report).encode()
    _replace_pair({inconsistencies_path: csv_bytes, report_path: markdown_bytes})
    return TerritorialOutputs(inconsistencies_path=inconsistencies_path, report_path=report_path)


def _classify_pair(
    norm_department: str,
    norm_municipality: str,
    catalog: Catalog,
) -> tuple[str, str, float | None] | None:
    if norm_department not in catalog.departments:
        suggestion, score = _suggest(norm_department, catalog.official_department)
        return "departamento_invalido", suggestion, score
    if norm_municipality in catalog.municipalities_by_department[norm_department]:
        return None
    owners = catalog.department_by_municipality.get(norm_municipality)
    if owners:
        suggestion = ", ".join(sorted(catalog.official_department[owner] for owner in owners))
        return "municipio_en_otro_departamento", suggestion, None
    candidates = {
        municipality: catalog.official_municipality[municipality]
        for municipality in catalog.municipalities_by_department[norm_department]
    }
    suggestion, score = _suggest(norm_municipality, candidates)
    return "municipio_desconocido", suggestion, score


def _suggest(value: str, candidates: dict[str, str]) -> tuple[str, float | None]:
    if not candidates:
        return "", None
    match = process.extractOne(value, list(candidates.keys()))
    if match is None or match[1] < SUGGESTION_THRESHOLD:
        return "", None
    return candidates[match[0]], match[1]


def _count_pairs(path: Path) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    header, rows = _read_csv(path)
    for column in (DEPARTMENT_COLUMN, MUNICIPALITY_COLUMN):
        if column not in header:
            raise TerritorialError(f"CSV limpio sin columna {column} en {path}.")
    for row in rows:
        key = (row.get(DEPARTMENT_COLUMN, ""), row.get(MUNICIPALITY_COLUMN, ""))
        counts[key] = counts.get(key, 0) + 1
    return counts


def _load_catalog(path: Path) -> Catalog:
    header, rows = _read_csv(path)
    required = {"departamento", "municipio"}
    if not required.issubset(header):
        raise TerritorialError(f"Catálogo sin columnas requeridas en {path}: {', '.join(sorted(required))}.")
    departments: set[str] = set()
    municipalities_by_department: dict[str, set[str]] = {}
    department_by_municipality: dict[str, set[str]] = {}
    official_department: dict[str, str] = {}
    official_municipality: dict[str, str] = {}
    for row in rows:
        departamento = row.get("departamento", "")
        municipio = row.get("municipio", "")
        norm_department = _normalize(departamento)
        norm_municipality = _normalize(municipio)
        departments.add(norm_department)
        municipalities_by_department.setdefault(norm_department, set()).add(norm_municipality)
        department_by_municipality.setdefault(norm_municipality, set()).add(norm_department)
        official_department.setdefault(norm_department, departamento)
        official_municipality.setdefault(norm_municipality, municipio)
    return Catalog(
        departments=departments,
        municipalities_by_department=municipalities_by_department,
        department_by_municipality=department_by_municipality,
        official_department=official_department,
        official_municipality=official_municipality,
    )


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise TerritorialError(f"Archivo vacío: {path}.")
            return list(reader.fieldnames), list(reader)
    except FileNotFoundError as exc:
        raise TerritorialError(f"No existe el archivo: {path}. ¿Generaste el catálogo?") from exc
    except csv.Error as exc:
        raise TerritorialError(f"CSV malformado: {path}: {exc}") from exc


def _normalize(value: str) -> str:
    stripped = "".join(char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char))
    return " ".join(stripped.upper().split())


def _logical_path(path: Path, project_root: Path) -> Path:
    try:
        return path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return Path(path.name)


def _rows_bytes(fieldnames: list[str], rows: list[dict[str, Any]]) -> bytes:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def _replace_pair(contents: dict[Path, bytes]) -> None:
    previous = {path: path.read_bytes() if path.exists() else None for path in contents}
    staged = {path: path.with_name(f".{path.name}.{os.getpid()}.tmp") for path in contents}
    try:
        for path, content in contents.items():
            staged[path].write_bytes(content)
        for path in contents:
            staged[path].replace(path)
    except OSError:
        for path, content in previous.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    finally:
        for temp_path in staged.values():
            temp_path.unlink(missing_ok=True)


def _render_markdown(report: TerritorialReport) -> str:
    summary = report.summary
    lines = [
        "# Validación territorial (departamento–municipio)",
        "",
        f"Generado por código sobre `{report.source_path.as_posix()}` contra el "
        f"espejo/conversión comunitaria `{report.catalog_path.as_posix()}` "
        "(fuente primaria declarada: INE, Censo 2018).",
        "",
        "## Método",
        "",
        "- Los nombres se comparan normalizando mayúsculas y tildes.",
        "- Regla documentada: `CIUDAD CAPITAL` se trata como el municipio de Guatemala; las `ZONA N` son sus zonas.",
        "- Cada pareja no reconocida se clasifica y se sugiere el nombre oficial más parecido (RapidFuzz).",
        "- **No se corrige ningún valor**: cada inconsistencia queda con `decision = revisar`.",
        "",
        "## Tipos de inconsistencia",
        "",
        "- `departamento_invalido`: el departamento no existe en el catálogo.",
        "- `municipio_en_otro_departamento`: el municipio existe, pero pertenece a otro departamento.",
        "- `municipio_desconocido`: el municipio no aparece en ese departamento; se sugiere el más parecido.",
        "",
        "## Resumen",
        "",
        f"- Parejas distintas evaluadas: {summary['parejas_distintas']}",
        f"- Parejas válidas: {summary['parejas_validas']}",
        f"- Parejas por regla CIUDAD CAPITAL: {summary['parejas_regla_ciudad_capital']}",
        f"- Parejas inconsistentes: {summary['parejas_inconsistentes']}",
        f"- Filas afectadas: {summary['filas_inconsistentes']}",
        "",
        "## Salida",
        "",
        "- `outputs/tablas/inconsistencias_territoriales.csv`: una pareja por fila, con tipo, sugerencia y decisión pendiente.",
        "",
        "La decisión final requiere revisión humana; este reporte solo entrega evidencia trazable.",
        "",
    ]
    return "\n".join(lines)
