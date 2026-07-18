"""Enriquecimiento territorial: códigos oficiales INE y corrección trazable de typos."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import unicodedata

from .cleaning import CleaningResult


DEFAULT_CATALOG_CSV = Path("data/reference/catalogo_territorial.csv")
DEPARTMENT_COLUMN = "DEPARTAMENTO"
MUNICIPALITY_COLUMN = "MUNICIPIO"
DEP_CODE_COLUMN = "departamento_codigo"
MUN_CODE_COLUMN = "municipio_codigo"
CIUDAD_CAPITAL = "CIUDAD CAPITAL"
CIUDAD_CAPITAL_TARGET = ("GUATEMALA", "GUATEMALA")
CATALOG_EVIDENCE = "data/reference/catalogo_territorial.csv; outputs/tablas/inconsistencias_territoriales.csv"
CATALOG_FIELDS = ("departamento_codigo", "departamento", "municipio_codigo", "municipio")
# (departamento, municipio MINEDUC normalizados) -> (departamento, municipio oficiales, corrección de nombre|None).
# Curado con la evidencia de outputs/tablas/inconsistencias_territoriales.csv (INE, Censo 2018).
TERRITORIAL_ALIASES: dict[tuple[str, str], tuple[str, str, str | None]] = {
    ("QUICHE", "IXCAN"): ("QUICHE", "PLAYA GRANDE IXCAN", None),
    ("QUICHE", "NEBAJ"): ("QUICHE", "SANTA MARIA NEBAJ", None),
    ("ALTA VERAPAZ", "LA TINTA"): ("ALTA VERAPAZ", "SANTA CATALINA LA TINTA", None),
    ("QUICHE", "PACHALUN"): ("QUICHE", "PACHALUM", "PACHALUM"),
    ("QUETZALTENANGO", "GENOVA COSTA CUCA"): ("QUETZALTENANGO", "GENOVA", None),
    ("ALTA VERAPAZ", "LANQUIN"): ("ALTA VERAPAZ", "SAN AGUSTIN LANQUIN", None),
    ("SACATEPEQUEZ", "ALOTENANGO"): ("SACATEPEQUEZ", "SAN JUAN ALOTENANGO", None),
    ("QUETZALTENANGO", "OLINTEPEQUE"): ("QUETZALTENANGO", "SAN JUAN OLINTEPEQUE", None),
    ("SUCHITEPEQUEZ", "SAN MIGUEL PANAM"): ("SUCHITEPEQUEZ", "SAN MIGUEL PANAN", "SAN MIGUEL PANAN"),
}


class EnrichmentError(RuntimeError):
    """Error esperado al leer el catálogo territorial."""


def enrich_result(result: CleaningResult, *, catalog_csv: Path | str = DEFAULT_CATALOG_CSV) -> CleaningResult:
    """Agrega códigos oficiales de departamento y municipio y corrige typos con evidencia."""

    department_codes, municipality_codes = _load_catalog_codes(Path(catalog_csv))
    missing_pairs: set[tuple[str, str]] = set()
    for row in result.rows:
        department = _normalize(row.get(DEPARTMENT_COLUMN, ""))
        municipality = _normalize(row.get(MUNICIPALITY_COLUMN, ""))
        official_department, official_municipality, _correction = _catalog_target(department, municipality)
        if official_department not in department_codes or (official_department, official_municipality) not in municipality_codes:
            missing_pairs.add((department, municipality))
    if missing_pairs:
        sample = ", ".join(f"{department}/{municipality}" for department, municipality in sorted(missing_pairs)[:3])
        raise EnrichmentError(f"Catálogo territorial incompleto para la fuente: {sample}.")
    header = _insert_after(result.header, MUNICIPALITY_COLUMN, [DEP_CODE_COLUMN, MUN_CODE_COLUMN])

    new_rows: list[dict[str, str]] = []
    typo_fixes: Counter[tuple[str, str]] = Counter()
    resolved = 0
    provisional = 0
    for row in result.rows:
        norm_department = _normalize(row.get(DEPARTMENT_COLUMN, ""))
        norm_municipality = _normalize(row.get(MUNICIPALITY_COLUMN, ""))
        official_department, official_municipality, correction = _catalog_target(norm_department, norm_municipality)
        provisional += (norm_department, norm_municipality) in TERRITORIAL_ALIASES and correction is None

        new_row = dict(row)
        if correction is not None and new_row.get(MUNICIPALITY_COLUMN, "") != correction:
            typo_fixes[(norm_department, norm_municipality)] += 1
            new_row[MUNICIPALITY_COLUMN] = correction
        department_code = department_codes.get(official_department, "")
        municipality_code = municipality_codes.get((official_department, official_municipality), "")
        new_row[DEP_CODE_COLUMN] = department_code
        new_row[MUN_CODE_COLUMN] = municipality_code
        if municipality_code:
            resolved += 1
        new_rows.append(new_row)

    cleaning_log = list(result.cleaning_log)
    for (norm_department, norm_municipality), count in sorted(typo_fixes.items()):
        official_municipality = TERRITORIAL_ALIASES[(norm_department, norm_municipality)][1]
        cleaning_log.append(
            {
                "variable": MUNICIPALITY_COLUMN,
                "regla": "corregir_municipio_catalogo",
                "filas_afectadas": str(count),
                "justificacion": f"Nombre inválido corregido al oficial '{official_municipality}' según catálogo INE.",
                "riesgo": "bajo",
                "evidencia_fuente": CATALOG_EVIDENCE,
            }
        )
    cleaning_log.append(
        {
            "variable": f"{DEP_CODE_COLUMN}, {MUN_CODE_COLUMN}",
            "regla": "agregar_codigos_catalogo",
            "filas_afectadas": str(resolved),
            "justificacion": f"Códigos derivados del catálogo; {provisional} asignaciones usan aliases provisionales pendientes.",
            "riesgo": "medio",
            "evidencia_fuente": CATALOG_EVIDENCE,
        }
    )

    quality_report = list(result.quality_report)
    for metric in quality_report:
        if metric["metrica"] == "columnas" and metric["variable"] == "__dataset__":
            metric["despues"] = str(len(header))
            metric["nota"] = "Columna <NBSP> eliminada y dos códigos territoriales derivados agregados."
            break
    quality_report.append(
        {
            "metrica": "codigos_territoriales_asignados",
            "variable": "__dataset__",
            "antes": "0",
            "despues": str(resolved),
            "estado": "ejecutado",
            "nota": "Códigos oficiales de departamento y municipio agregados como variables derivadas.",
        }
    )
    quality_report.append(
        {
            "metrica": "typos_territoriales_corregidos",
            "variable": MUNICIPALITY_COLUMN,
            "antes": str(sum(typo_fixes.values())),
            "despues": "0",
            "estado": "ejecutado",
            "nota": "Municipios con typo corregidos al nombre oficial del catálogo.",
        }
    )

    return CleaningResult(
        source_path=result.source_path,
        original_header=result.original_header,
        header=header,
        rows=new_rows,
        cleaning_log=cleaning_log,
        quality_report=quality_report,
    )


def _insert_after(header: list[str], anchor: str, new_columns: list[str]) -> list[str]:
    if anchor not in header:
        return list(header) + new_columns
    index = header.index(anchor) + 1
    return header[:index] + new_columns + header[index:]


def _load_catalog_codes(path: Path) -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    department_codes: dict[str, str] = {}
    municipality_codes: dict[tuple[str, str], str] = {}
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, strict=True)
            if tuple(reader.fieldnames or ()) != CATALOG_FIELDS:
                raise EnrichmentError(f"Catálogo territorial con esquema inválido: {path}.")
            department_codes_by_name: dict[str, set[str]] = {}
            department_names_by_code: dict[str, set[str]] = {}
            municipality_keys: list[tuple[str, str]] = []
            municipality_code_values: list[str] = []
            for row in reader:
                values = [row.get(field) for field in CATALOG_FIELDS]
                if any(not isinstance(value, str) or not value.strip() for value in values):
                    raise EnrichmentError(f"Catálogo territorial contiene códigos o nombres vacíos: {path}.")
                department_code, department, municipality_code, municipality = (value.strip() for value in values)
                norm_department, norm_municipality = _normalize(department), _normalize(municipality)
                department_codes_by_name.setdefault(norm_department, set()).add(department_code)
                department_names_by_code.setdefault(department_code, set()).add(norm_department)
                municipality_keys.append((norm_department, norm_municipality))
                municipality_code_values.append(municipality_code)
                department_codes.setdefault(norm_department, department_code)
                municipality_codes[(norm_department, norm_municipality)] = municipality_code
            if not municipality_keys:
                raise EnrichmentError(f"Catálogo territorial sin registros: {path}.")
            if any(len(values) != 1 for values in (*department_codes_by_name.values(), *department_names_by_code.values())):
                raise EnrichmentError(f"Catálogo territorial contiene departamentos ambiguos: {path}.")
            if len(set(municipality_keys)) != len(municipality_keys) or len(set(municipality_code_values)) != len(municipality_code_values):
                raise EnrichmentError(f"Catálogo territorial contiene municipios o códigos duplicados: {path}.")
    except FileNotFoundError as exc:
        raise EnrichmentError(
            f"No existe el catálogo territorial: {path}. Genera primero con scripts/generar_catalogo_territorial.py."
        ) from exc
    except (csv.Error, TypeError, ValueError) as exc:
        raise EnrichmentError(f"Catálogo territorial malformado: {path}: {exc}") from exc
    return department_codes, municipality_codes


def _catalog_target(department: str, municipality: str) -> tuple[str, str, str | None]:
    if department == CIUDAD_CAPITAL:
        return *CIUDAD_CAPITAL_TARGET, None
    return TERRITORIAL_ALIASES.get((department, municipality), (department, municipality, None))


def _normalize(value: str) -> str:
    stripped = "".join(char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char))
    return " ".join(stripped.upper().split())
