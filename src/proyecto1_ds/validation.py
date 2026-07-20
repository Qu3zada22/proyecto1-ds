"""Validación final reproducible de los siete controles del conjunto limpio."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import os
from pathlib import Path

from proyecto1_ds.duplicates import (
    AUTOMATIC_DECISIONS, CANDIDATE_FIELDS, MANUAL_PENDING_DECISIONS,
    VALID_DECISIONS, DuplicatesCsvError, detect_partial_duplicates,
)
from proyecto1_ds.territorial import (
    INCONSISTENCY_FIELDS, TerritorialError, validate_territorial,
)

OUTPUT_FIELDS = ["control", "estado", "conteo", "detalle", "evidencia"]
EXPECTED_COLUMNS = [
    "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO", "departamento_codigo",
    "municipio_codigo", "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "SUPERVISOR",
    "DIRECTOR", "NIVEL", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA",
    "PLAN", "DEPARTAMENTAL", "archivo_origen", "departamento_origen",
]
CATEGORY_COLUMNS = {
    "DEPARTAMENTO", "MUNICIPIO", "NIVEL", "SECTOR", "AREA", "STATUS",
    "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL", "departamento_origen",
}


class ValidationError(ValueError):
    """Entrada ausente o tabularmente inválida para la validación final."""


@dataclass(frozen=True)
class ValidationResult:
    source_rows: int
    source_columns: int
    rows: list[dict[str, str]]


def validate_dataset(
    clean_csv: Path | str,
    duplicates_csv: Path | str,
    territory_csv: Path | str,
    problems_csv: Path | str,
    *,
    catalog_csv: Path | str | None = None,
) -> ValidationResult:
    header, clean = _read_csv(Path(clean_csv))
    duplicate_header, duplicates = _read_csv(Path(duplicates_csv), {"decision"})
    territory_header, territory = _read_csv(Path(territory_csv), {"filas", "decision"})
    _, problems = _read_csv(Path(problems_csv), {"columna", "tipo", "conteo"})
    if not clean:
        raise ValidationError(f"CSV limpio sin registros: {clean_csv}")
    invalid_decisions = sorted({row["decision"] for row in duplicates} - VALID_DECISIONS)
    if invalid_decisions:
        raise ValidationError(f"Decisión inválida en {duplicates_csv}: {invalid_decisions}")
    if duplicate_header == CANDIDATE_FIELDS:
        pair_keys = [_pair_key(row) for row in duplicates]
        if len(pair_keys) != len(set(pair_keys)):
            raise ValidationError(f"Evidencia de duplicados con par repetido: {duplicates_csv}")
    if any(row["decision"] != "revisar" for row in territory):
        raise ValidationError(f"Decisión inválida en {territory_csv}")
    for row in problems:
        _integer(row["conteo"], problems_csv)
    if catalog_csv is not None:
        _validate_lineage(
            Path(clean_csv), Path(catalog_csv), duplicate_header, duplicates,
            territory_header, territory,
        )

    exact = len(clean) - len({tuple(row.get(column, "") for column in header) for row in clean})
    probable_duplicates = sum(row["decision"] == "duplicado_probable" for row in duplicates)
    ambiguous_duplicates = sum(row["decision"] == "revisar" for row in duplicates)
    institutional_duplicates = sum(row["decision"] in MANUAL_PENDING_DECISIONS for row in duplicates)
    confirmed_duplicates = sum(row["decision"] == "duplicado_confirmado" for row in duplicates)
    confirmed_independent = sum(row["decision"] == "independiente_confirmado" for row in duplicates)
    pending_duplicates = probable_duplicates + ambiguous_duplicates + institutional_duplicates
    outer_spaces = sum(value != value.strip() for row in clean for value in row.values())
    suspicious_phones = sum(
        bool(row.get("TELEFONO")) and (not row["TELEFONO"].isdigit() or len(row["TELEFONO"]) != 8)
        for row in clean
    )
    other_invalid_findings = sum(
        _integer(row["conteo"], problems_csv)
        for row in problems
        if row["columna"] != "TELEFONO" and row["tipo"] == "formato_sospechoso"
    )
    pending_territory = sum(
        _integer(row["filas"], territory_csv)
        for row in territory
        if row["decision"] == "revisar"
    )
    schema_differences = len(set(header) ^ set(EXPECTED_COLUMNS))
    category_collisions = _category_collisions(clean, header)
    invalid_findings = suspicious_phones + other_invalid_findings + pending_territory
    phone_state = _review_state(suspicious_phones)

    duplicate_state = "falla" if exact else "requiere_revision" if pending_duplicates else "cumple"
    duplicate_count = f"{exact} registros" if exact else f"{pending_duplicates} pares" if pending_duplicates else "0 registros"
    rows = [
        _row("duplicados_exactos", duplicate_state, duplicate_count,
             f"Duplicados exactos={exact}; pendientes: {probable_duplicates} duplicado_probable, {ambiguous_duplicates} revisar y {institutional_duplicates} institucional; finales: {confirmed_duplicates} duplicado_confirmado y {confirmed_independent} independiente_confirmado.",
             "data/processed/establecimientos_diversificado_limpio.csv; outputs/tablas/duplicados_parciales.csv"),
        _row("espacios_exteriores", _failure_state(outer_spaces), f"{outer_spaces} campos",
             "Celdas de texto con espacios al inicio o al final.", "data/processed/establecimientos_diversificado_limpio.csv"),
        _row("formato_telefonos", phone_state, f"{suspicious_phones} registros",
             "Teléfonos inspeccionados en el limpio; problemas_potenciales es diagnóstico histórico de la fuente.",
             "data/processed/establecimientos_diversificado_limpio.csv; outputs/tablas/problemas_potenciales.csv"),
        _row("catalogo_territorial", _review_state(pending_territory), f"{pending_territory} filas",
             "Filas territoriales conservadas para revisión contra catálogo.", "outputs/tablas/inconsistencias_territoriales.csv"),
        _row("tipos_esperados", _failure_state(schema_differences),
             f"{schema_differences} variables" if schema_differences else f"{len(header)} variables",
             "Esquema semántico esperado; identificadores, códigos y teléfonos se preservan como texto en CSV.",
             "data/processed/establecimientos_diversificado_limpio.csv; docs/code_book/variables_anggie.md"),
        _row("categorias_sin_variantes", _failure_state(category_collisions), f"{category_collisions} categorías",
             "Categorías distintas que colapsan al normalizar espacios y mayúsculas.", "data/processed/establecimientos_diversificado_limpio.csv"),
        _row("valores_invalidos_diagnosticados", _review_state(invalid_findings), f"{invalid_findings} hallazgos",
             f"{suspicious_phones} teléfonos vigentes + {pending_territory} filas territoriales + {other_invalid_findings} otros hallazgos históricos; no representa filas únicas ni suma el diagnóstico telefónico histórico.",
             "data/processed/establecimientos_diversificado_limpio.csv; outputs/tablas/problemas_potenciales.csv; outputs/tablas/inconsistencias_territoriales.csv"),
    ]
    return ValidationResult(len(clean), len(header), rows)


def write_validation_output(result: ValidationResult, output_csv: Path | str) -> Path:
    path = Path(output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(result.rows)
            handle.flush()
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def _read_csv(path: Path, required: set[str] | None = None) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise ValidationError(f"No se pudo leer CSV de validación: {path}: {exc}") from exc
    if not raw or not raw[0] or len(raw[0]) != len(set(raw[0])):
        raise ValidationError(f"CSV vacío o con encabezados inválidos: {path}")
    header = raw[0]
    if any(len(row) != len(header) for row in raw[1:]):
        raise ValidationError(f"CSV con filas irregulares: {path}")
    if required and not required.issubset(header):
        raise ValidationError(f"CSV sin columnas requeridas: {path}")
    return header, [dict(zip(header, row, strict=True)) for row in raw[1:]]


def _integer(value: str, path: Path | str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise ValidationError(f"Conteo inválido en {path}: {value}") from exc
    if result < 0:
        raise ValidationError(f"Conteo debe ser no negativo en {path}: {value}")
    return result


def _validate_lineage(
    clean: Path, catalog: Path, duplicate_header: list[str], duplicates: list[dict[str, str]],
    territory_header: list[str], territory: list[dict[str, str]],
) -> None:
    if duplicate_header != CANDIDATE_FIELDS or territory_header != INCONSISTENCY_FIELDS:
        raise ValidationError("Evidencia stale o sin esquema canónico para recomputación")
    try:
        expected_duplicates = detect_partial_duplicates(clean).candidates
        expected_territory = validate_territorial(clean, catalog_csv=catalog).inconsistencies
    except (DuplicatesCsvError, TerritorialError) as exc:
        raise ValidationError(f"No se pudo recomputar evidencia: {exc}") from exc
    fields = CANDIDATE_FIELDS[:-1]
    expected = {_pair_key(row): _signature(row, fields) for row in expected_duplicates}
    actual = {_pair_key(row): _signature(row, fields) for row in duplicates}
    decisions = {_pair_key(row): row["decision"] for row in duplicates}
    automatic = {_pair_key(row): row["decision"] for row in expected_duplicates}
    if expected != actual or any(
        decisions[key] in AUTOMATIC_DECISIONS and decisions[key] != automatic[key] for key in decisions
    ):
        raise ValidationError("Evidencia de duplicados stale respecto del limpio")
    if sorted(_signature(row, INCONSISTENCY_FIELDS) for row in territory) != sorted(
        _signature(row, INCONSISTENCY_FIELDS) for row in expected_territory
    ):
        raise ValidationError("Evidencia territorial stale respecto del limpio")


def _pair_key(row: dict[str, object]) -> tuple[str, str]:
    return tuple(sorted((str(row.get("codigo_a", "")), str(row.get("codigo_b", "")))))


def _signature(row: dict[str, object], fields: list[str]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in fields)


def _category_collisions(rows: list[dict[str, str]], header: list[str]) -> int:
    collisions = 0
    for column in CATEGORY_COLUMNS.intersection(header):
        groups: dict[str, set[str]] = {}
        for row in rows:
            value = row[column]
            if value:
                groups.setdefault(" ".join(value.split()).casefold(), set()).add(value)
        collisions += sum(len(values) > 1 for values in groups.values())
    return collisions


def _failure_state(count: int) -> str:
    return "falla" if count else "cumple"


def _review_state(count: int) -> str:
    return "requiere_revision" if count else "cumple"


def _row(control: str, estado: str, conteo: str, detalle: str, evidencia: str) -> dict[str, str]:
    return dict(control=control, estado=estado, conteo=conteo, detalle=detalle, evidencia=evidencia)
