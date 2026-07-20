"""Reporte integral antes/después a partir de evidencias reproducibles existentes."""

from __future__ import annotations

import csv
from collections import Counter
import os
from pathlib import Path
from typing import Any

from proyecto1_ds.cleaning import CleaningCsvError, MISSING_MARKERS, clean_dataset
from proyecto1_ds.enrichment import EnrichmentError, enrich_result
from proyecto1_ds.validation import ValidationError, validate_dataset
from proyecto1_ds.decisions import DEFAULT_PHONE_DECISIONS_CSV, DecisionManifestError


REPORT_FIELDS = ["metrica", "antes", "despues", "unidad", "interpretacion", "evidencia"]
REQUIRED_CONTROLS = {
    "duplicados_exactos", "espacios_exteriores", "formato_telefonos", "catalogo_territorial",
    "tipos_esperados", "categorias_sin_variantes", "valores_invalidos_diagnosticados",
}


class QualityReportError(ValueError):
    """Entrada ausente o tabularmente inválida para el reporte integral."""


def build_quality_report(
    source_csv: Path | str,
    clean_csv: Path | str,
    problems_csv: Path | str,
    log_csv: Path | str,
    duplicates_csv: Path | str,
    territory_csv: Path | str,
    validation_csv: Path | str,
    exact_duplicates_csv: Path | str,
) -> list[dict[str, str]]:
    source_header, source = _read(Path(source_csv))
    clean_header, clean = _read(Path(clean_csv))
    _, problems = _read(Path(problems_csv), {"columna", "tipo", "conteo"})
    _, log = _read(Path(log_csv), {"variable", "regla", "filas_afectadas"})
    _, duplicates = _read(Path(duplicates_csv), {"decision"})
    _, territory = _read(Path(territory_csv), {"filas", "decision"})
    _, validation = _read(Path(validation_csv), {"control", "estado", "conteo", "detalle"})
    _, exact_duplicates = _read(Path(exact_duplicates_csv), {"firma_fila", "repeticiones_adicionales"})
    if not source:
        raise QualityReportError(f"Dataset fuente sin registros: {source_csv}")
    if not clean:
        raise QualityReportError(f"Dataset limpio sin registros: {clean_csv}")
    if len(source) != len(clean):
        raise QualityReportError(
            "Este pipeline conservador debe conservar el mismo número de registros; "
            f"fuente={len(source)}, limpio={len(clean)}."
        )
    catalog = Path(clean_csv).parents[2] / "data/reference/catalogo_territorial.csv"
    signatures = Counter(tuple(row[column] for column in source_header) for row in source)
    expected_exact = sorted(
        (" | ".join(signature), count - 1) for signature, count in signatures.items() if count > 1
    )
    actual_exact = sorted(
        (row["firma_fila"], _integer(row["repeticiones_adicionales"])) for row in exact_duplicates
    )
    if actual_exact != expected_exact:
        raise QualityReportError("Evidencia de duplicados exactos stale respecto de la fuente.")
    for row in log:
        _integer(row["filas_afectadas"])
    try:
        decisions = Path(source_csv).parents[2] / DEFAULT_PHONE_DECISIONS_CSV
        expected_cleaning = clean_dataset(
            source_csv, phone_decisions_csv=decisions if decisions.exists() else None
        )
        if catalog.exists():
            expected_cleaning = enrich_result(expected_cleaning, catalog_csv=catalog)
    except (CleaningCsvError, DecisionManifestError, EnrichmentError) as exc:
        raise QualityReportError(f"No se pudo recomputar la bitácora: {exc}") from exc
    log_key = lambda row: (row["variable"], row["regla"], row["filas_afectadas"])
    actual_cleaning_log = [log_key(row) for row in log if row["regla"] != "decidir_duplicados"]
    if actual_cleaning_log != [log_key(row) for row in expected_cleaning.cleaning_log]:
        raise QualityReportError("Evidencia de bitácora stale respecto de fuente y catálogo.")
    controls = {row["control"]: row for row in validation}
    if set(controls) != REQUIRED_CONTROLS or len(validation) != len(REQUIRED_CONTROLS):
        raise QualityReportError("Validación final sin los siete controles requeridos.")
    if any(row["estado"] not in {"cumple", "requiere_revision", "falla"} for row in validation):
        raise QualityReportError("Validación final con estado fuera de dominio.")
    try:
        current = validate_dataset(
            clean_csv, duplicates_csv, territory_csv, problems_csv,
            catalog_csv=catalog if catalog.exists() else None,
        )
    except ValidationError as exc:
        raise QualityReportError(f"No se pudo contrastar la validación final: {exc}") from exc
    current_controls = {row["control"]: row for row in current.rows}
    compared_fields = ("estado", "conteo", "detalle")
    if any(tuple(controls[name][field] for field in compared_fields) != tuple(current_controls[name][field] for field in compared_fields) for name in REQUIRED_CONTROLS):
        raise QualityReportError("Validación final incoherente con las evidencias actuales.")

    source_missing = _missing(source)
    clean_missing = _missing(clean)
    source_na = sum(any(_is_missing(row[column]) for row in source) for column in source_header)
    clean_na = sum(any(_is_missing(row[column]) for row in clean) for column in clean_header)
    exact_before = sum(_integer(row["repeticiones_adicionales"]) for row in exact_duplicates)
    exact_after = _exact_after(controls["duplicados_exactos"]["detalle"])
    pending_pairs = sum(row["decision"] in {"revisar", "revisar_institucional"} for row in duplicates)
    probable_pairs = sum(row["decision"] == "duplicado_probable" for row in duplicates)
    pending_total = probable_pairs + pending_pairs
    confirmed_duplicates = sum(row["decision"] == "duplicado_confirmado" for row in duplicates)
    confirmed_independent = sum(row["decision"] == "independiente_confirmado" for row in duplicates)
    phone_records = _prefix_integer(controls["formato_telefonos"]["conteo"])
    territorial_rows = sum(_integer(row["filas"]) for row in territory if row["decision"] == "revisar")
    format_columns = {
        row["columna"] for row in problems if row["tipo"] in {"texto_sospechoso", "formato_sospechoso"}
    }
    outer_space_columns = {
        column for column in clean_header if any(row[column] != row[column].strip() for row in clean)
    }
    outer_space_fields = _prefix_integer(controls["espacios_exteriores"]["conteo"])
    category_variants = sum(row["regla"] == "corregir_municipio_catalogo" for row in log)
    categories_after = _prefix_integer(controls["categorias_sin_variantes"]["conteo"])
    types_after = 0 if controls["tipos_esperados"]["estado"] == "cumple" else _prefix_integer(controls["tipos_esperados"]["conteo"])
    format_after_columns = outer_space_columns | ({"TELEFONO"} if phone_records else set())
    row_interpretation = "No se agregaron ni eliminaron establecimientos."
    corrections = {
        "ausencias": _log_sum(log, "normalizar_marcador_ausencia"),
        "espacios": _log_sum(log, "normalizar_espacios_nbsp"),
        "mayúsculas": _log_sum(log, "normalizar_mayusculas"),
        "territorios": _log_sum(log, "corregir_municipio_catalogo"),
        "códigos derivados": _log_sum(log, "agregar_codigos_catalogo"),
        "teléfonos aprobados": _log_sum(log, "normalizar_telefono_aprobado"),
    }
    corrected_summary = "; ".join(f"{count} {label}" for label, count in corrections.items())

    return [
        _row("registros", len(source), len(clean), "filas", row_interpretation, "data/source/establecimientos_diversificado_mineduc.csv; data/processed/establecimientos_diversificado_limpio.csv"),
        _row("variables", len(source_header), len(clean_header), "variables", "Se eliminó <NBSP> y se agregaron dos códigos territoriales.", "outputs/tablas/bitacora_limpieza.csv"),
        _row("valores_faltantes", _missing_value(source_missing, len(source), len(source_header)), _missing_value(clean_missing, len(clean), len(clean_header)), "celdas y porcentaje", "Porcentaje sobre todas las celdas de cada versión.", "data/source/establecimientos_diversificado_mineduc.csv; data/processed/establecimientos_diversificado_limpio.csv"),
        _row("variables_con_na", source_na, clean_na, "variables", "Columnas con al menos una ausencia inequívoca.", "data/source/establecimientos_diversificado_mineduc.csv; data/processed/establecimientos_diversificado_limpio.csv"),
        _row("duplicados_exactos", exact_before, exact_after, "registros adicionales", "Duplicados de fila completa; no se eliminó ninguna fila.", "outputs/tablas/duplicados_exactos.csv; outputs/tablas/validacion_final.csv"),
        _row("posibles_duplicados", "no evaluado", f"{len(duplicates)} (0 fusionados; {probable_pairs} probable; {pending_pairs} revisar; {confirmed_duplicates} duplicado confirmado; {confirmed_independent} independiente confirmado)", "pares", f"Candidatos por similitud; ninguna fusión es automática y {pending_total} pares requieren confirmación o revisión.", "outputs/tablas/duplicados_parciales.csv"),
        _row("formatos_inconsistentes", len(format_columns), f"{len(format_after_columns)} variables; {categories_after} categorías ({phone_records} registros TELEFONO; {outer_space_fields} campos exteriores)", "variables y categorías", "Integra espacios, teléfonos y categorías de los controles finales.", "outputs/tablas/problemas_potenciales.csv; outputs/tablas/validacion_final.csv"),
        _row("tipos_incorrectos", 0, types_after, "variables", "Contrato semántico: identificadores, códigos y teléfonos son texto.", "outputs/tablas/diagnostico_columnas.csv; outputs/tablas/validacion_final.csv"),
        _row("categorias_inconsistentes", category_variants, categories_after, "variantes", f"Variantes deterministas corregidas; {territorial_rows} filas territoriales permanecen en revisión.", "outputs/tablas/bitacora_limpieza.csv; outputs/tablas/validacion_final.csv"),
        _row("errores_corregidos", "0 aplicadas", corrected_summary, "resumen por tipo", "No se suman categorías superpuestas en un total artificial.", "outputs/tablas/bitacora_limpieza.csv"),
    ]


def write_quality_report(rows: list[dict[str, str]], output_csv: Path | str) -> Path:
    path = Path(output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def _read(path: Path, required: set[str] | None = None) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise QualityReportError(f"No se pudo leer evidencia: {path}: {exc}") from exc
    if not raw or not raw[0] or len(raw[0]) != len(set(raw[0])) or any(len(row) != len(raw[0]) for row in raw[1:]):
        raise QualityReportError(f"CSV vacío o malformado: {path}")
    if required and not required.issubset(raw[0]):
        raise QualityReportError(f"CSV sin columnas requeridas: {path}")
    return raw[0], [dict(zip(raw[0], row, strict=True)) for row in raw[1:]]


def _is_missing(value: str) -> bool:
    return value.replace("\xa0", " ").strip().casefold() in MISSING_MARKERS


def _missing(rows: list[dict[str, str]]) -> int:
    return sum(_is_missing(value) for row in rows for value in row.values())


def _missing_value(count: int, rows: int, columns: int) -> str:
    return f"{count} ({count * 100 / (rows * columns):.2f}%)" if rows and columns else f"{count} (0.00%)"


def _integer(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise QualityReportError(f"Conteo inválido: {value}") from exc
    if result < 0:
        raise QualityReportError(f"Conteo debe ser no negativo: {value}")
    return result


def _prefix_integer(value: str) -> int:
    return _integer(value.split(maxsplit=1)[0])


def _exact_after(detail: str) -> int:
    try:
        return _integer(detail.split("Duplicados exactos=", 1)[1].split(";", 1)[0])
    except IndexError as exc:
        raise QualityReportError("Detalle de duplicados exactos inválido.") from exc


def _log_sum(rows: list[dict[str, str]], rule: str) -> int:
    return sum(_integer(row["filas_afectadas"]) for row in rows if row["regla"] == rule)


def _row(metric: str, before: Any, after: Any, unit: str, interpretation: str, evidence: str) -> dict[str, str]:
    return dict(metrica=metric, antes=str(before), despues=str(after), unidad=unit, interpretacion=interpretation, evidencia=evidence)
