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
    header = _insert_after(result.header, MUNICIPALITY_COLUMN, [DEP_CODE_COLUMN, MUN_CODE_COLUMN])

    new_rows: list[dict[str, str]] = []
    typo_fixes: Counter[tuple[str, str]] = Counter()
    resolved = 0
    for row in result.rows:
        norm_department = _normalize(row.get(DEPARTMENT_COLUMN, ""))
        norm_municipality = _normalize(row.get(MUNICIPALITY_COLUMN, ""))
        correction: str | None = None
        if norm_department == CIUDAD_CAPITAL:
            official_department, official_municipality = CIUDAD_CAPITAL_TARGET
        elif (norm_department, norm_municipality) in TERRITORIAL_ALIASES:
            official_department, official_municipality, correction = TERRITORIAL_ALIASES[(norm_department, norm_municipality)]
        else:
            official_department, official_municipality = norm_department, norm_municipality

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
            "regla": "agregar_codigos_oficiales",
            "filas_afectadas": str(resolved),
            "justificacion": "Variables derivadas: códigos oficiales INE para habilitar cruces con otras fuentes.",
            "riesgo": "bajo",
            "evidencia_fuente": CATALOG_EVIDENCE,
        }
    )

    quality_report = list(result.quality_report)
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
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise EnrichmentError(f"Catálogo territorial vacío: {path}.")
            for row in reader:
                norm_department = _normalize(row.get("departamento", ""))
                norm_municipality = _normalize(row.get("municipio", ""))
                department_codes.setdefault(norm_department, row.get("departamento_codigo", ""))
                municipality_codes[(norm_department, norm_municipality)] = row.get("municipio_codigo", "")
    except FileNotFoundError as exc:
        raise EnrichmentError(
            f"No existe el catálogo territorial: {path}. Genera primero con scripts/generar_catalogo_territorial.py."
        ) from exc
    except csv.Error as exc:
        raise EnrichmentError(f"Catálogo territorial malformado: {path}: {exc}") from exc
    return department_codes, municipality_codes


def _normalize(value: str) -> str:
    stripped = "".join(char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char))
    return " ".join(stripped.upper().split())
