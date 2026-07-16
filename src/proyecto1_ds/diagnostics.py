"""Diagnóstico read-only de datos crudos consolidados."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Any


DEFAULT_SOURCE_CSV = Path("data/source/establecimientos_diversificado_mineduc.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/tablas")
DEFAULT_DOCS_PATH = Path("docs/diagnostico.md")
MISSING_MARKERS = {"", "n/a", "na", "null", "none", "-", ".", "sin dato", "----"}
TERRITORIAL_COLUMNS = {"departamento", "municipio", "departamento_origen"}
CODE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_TOP_N = 20


class DiagnosticCsvError(ValueError):
    """Error esperado cuando el CSV fuente no es tabularmente válido."""


class DiagnosticOutputError(RuntimeError):
    """Error esperado cuando no se pueden restaurar salidas diagnósticas."""


@dataclass(frozen=True)
class DiagnosticReport:
    """Resultado tabular del diagnóstico sin modificar el CSV fuente."""

    source_path: Path
    summary: dict[str, Any]
    column_metrics: list[dict[str, Any]]
    observed_domains: list[dict[str, Any]]
    duplicate_rows: list[dict[str, Any]]
    quality_issues: list[dict[str, Any]]


@dataclass(frozen=True)
class DiagnosticOutputs:
    """Rutas escritas por el diagnóstico reproducible."""

    table_paths: list[Path]
    docs_path: Path


def generate_diagnostics(source_csv: Path | str = DEFAULT_SOURCE_CSV) -> DiagnosticReport:
    """Calcula métricas requeridas sobre el CSV fuente sin limpiarlo."""

    source_path = Path(source_csv)
    header, rows = _read_csv(source_path)
    duplicate_rows = _exact_duplicate_rows(rows, header)
    column_metrics = [_column_metric(column, rows) for column in header]
    observed_domains = _observed_domains(header, rows)
    summary: dict[str, Any] = {
        "filas": len(rows),
        "columnas": len(header),
        "duplicados_exactos": len(duplicate_rows),
        "catalogo_territorial": "no verificable",
    }
    return DiagnosticReport(
        source_path=source_path,
        summary=summary,
        column_metrics=column_metrics,
        observed_domains=observed_domains,
        duplicate_rows=duplicate_rows,
        quality_issues=_quality_issues(header, rows, column_metrics, duplicate_rows),
    )


def write_diagnostics(
    report: DiagnosticReport,
    *,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    docs_path: Path | str = DEFAULT_DOCS_PATH,
) -> DiagnosticOutputs:
    """Escribe tablas CSV y `docs/diagnostico.md` generados por código."""

    tables_root = Path(output_dir)
    docs_file = Path(docs_path)
    tables_root.mkdir(parents=True, exist_ok=True)
    docs_file.parent.mkdir(parents=True, exist_ok=True)

    summary_path = tables_root / "resumen_dataset.csv"
    column_path = tables_root / "diagnostico_columnas.csv"
    duplicates_path = tables_root / "duplicados_exactos.csv"
    issues_path = tables_root / "problemas_potenciales.csv"
    domains_path = tables_root / "dominios_observados.csv"

    _write_outputs_atomically(
        [
            (summary_path, lambda path: _write_rows(path, ["metrica", "valor"], _summary_rows(report.summary))),
            (
                column_path,
                lambda path: _write_rows(
                    path,
                    ["columna", "columna_mostrada", "tipo_asignado", "faltantes", "porcentaje_faltantes", "unicos"],
                    report.column_metrics,
                ),
            ),
            (
                duplicates_path,
                lambda path: _write_rows(path, ["firma_fila", "repeticiones_adicionales"], report.duplicate_rows),
            ),
            (
                issues_path,
                lambda path: _write_rows(
                    path,
                    ["columna", "columna_mostrada", "tipo", "conteo", "descripcion"],
                    report.quality_issues,
                ),
            ),
            (
                domains_path,
                lambda path: _write_rows(
                    path,
                    ["columna", "columna_mostrada", "valor", "valor_mostrado", "frecuencia"],
                    report.observed_domains,
                ),
            ),
            (docs_file, lambda path: path.write_text(_render_markdown(report), encoding="utf-8")),
        ]
    )
    return DiagnosticOutputs(
        table_paths=[summary_path, column_path, duplicates_path, issues_path, domains_path],
        docs_path=docs_file,
    )


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, strict=True)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise DiagnosticCsvError(f"CSV intermedio malformado: {path} está vacío.") from exc
            _validate_header(path, header)
            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(header):
                    raise DiagnosticCsvError(
                        "CSV intermedio malformado: "
                        f"{path} fila {line_number} tiene {len(row)} columnas; se esperaban {len(header)}."
                    )
                rows.append(dict(zip(header, row, strict=True)))
            return header, rows
    except csv.Error as exc:
        raise DiagnosticCsvError(f"CSV intermedio malformado: {path}: {exc}") from exc


def _validate_header(path: Path, header: list[str]) -> None:
    if not header:
        raise DiagnosticCsvError(f"CSV intermedio malformado: {path} no contiene encabezados.")
    repeated = sorted({column for column in header if header.count(column) > 1})
    if repeated:
        repeated_display = ", ".join(_display_value(column) for column in repeated)
        raise DiagnosticCsvError(f"CSV intermedio malformado: encabezados duplicados: {repeated_display}.")


def _column_metric(column: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    values = [row.get(column, "") for row in rows]
    missing = sum(1 for value in values if _is_missing_like(value))
    percentage = (missing / len(rows) * 100) if rows else 0
    return {
        "columna": column,
        "columna_mostrada": _display_value(column),
        "tipo_asignado": "str",
        "faltantes": missing,
        "porcentaje_faltantes": f"{percentage:.2f}",
        "unicos": len(set(values)),
    }


def _exact_duplicate_rows(rows: list[dict[str, str]], header: list[str]) -> list[dict[str, Any]]:
    seen: set[tuple[str, ...]] = set()
    duplicates: dict[tuple[str, ...], int] = {}
    for row in rows:
        signature = tuple(row.get(column, "") for column in header)
        if signature in seen:
            duplicates[signature] = duplicates.get(signature, 0) + 1
        else:
            seen.add(signature)
    return [
        {"firma_fila": " | ".join(signature), "repeticiones_adicionales": count}
        for signature, count in duplicates.items()
    ]


def _observed_domains(header: list[str], rows: list[dict[str, str]], top_n: int = DOMAIN_TOP_N) -> list[dict[str, Any]]:
    domains: list[dict[str, Any]] = []
    for column in header:
        counts = Counter(_raw_value(row, column) for row in rows)
        for value, frequency in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_n]:
            domains.append(
                {
                    "columna": column,
                    "columna_mostrada": _display_value(column),
                    "valor": value,
                    "valor_mostrado": _display_value(value),
                    "frecuencia": frequency,
                }
            )
    return domains


def _quality_issues(
    header: list[str],
    rows: list[dict[str, str]],
    column_metrics: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    metrics_by_column = {metric["columna"]: metric for metric in column_metrics}
    for column in header:
        normalized_column = _normalize_label(column)
        if not normalized_column:
            issues.append(
                {
                    "columna": column,
                    "columna_mostrada": _display_value(column),
                    "tipo": "encabezado_sospechoso",
                    "conteo": 1,
                    "descripcion": "Encabezado vacío o compuesto solo por espacios; se reporta sin renombrarlo.",
                }
            )
        if metrics_by_column[column]["faltantes"]:
            issues.append(
                {
                    "columna": column,
                    "columna_mostrada": _display_value(column),
                    "tipo": "faltantes_detectados",
                    "conteo": metrics_by_column[column]["faltantes"],
                    "descripcion": "Valores vacíos, marcadores de ausencia o espacios detectados sin modificar los datos.",
                }
            )
        if normalized_column in TERRITORIAL_COLUMNS:
            issues.append(
                {
                    "columna": column,
                    "columna_mostrada": _display_value(column),
                    "tipo": "catalogo_no_verificable",
                    "conteo": 1,
                    "descripcion": "No se encontró catálogo oficial territorial; no se declaran inválidos sin evidencia suficiente.",
                }
            )
        if normalized_column == "telefono":
            count = sum(1 for row in rows if _has_suspicious_phone(_raw_value(row, column)))
            if count:
                issues.append(
                    {
                        "columna": column,
                        "columna_mostrada": _display_value(column),
                        "tipo": "formato_sospechoso",
                        "conteo": count,
                        "descripcion": "Teléfonos no vacíos con caracteres distintos de dígitos.",
                    }
                )
        if normalized_column == "codigo":
            count = sum(1 for row in rows if _has_suspicious_code(_raw_value(row, column)))
            if count:
                issues.append(
                    {
                        "columna": column,
                        "columna_mostrada": _display_value(column),
                        "tipo": "formato_sospechoso",
                        "conteo": count,
                        "descripcion": "Códigos que no siguen el patrón esperado NN-NN-NNNN-NN.",
                    }
                )
        text_count = sum(1 for row in rows if _has_suspicious_text(_raw_value(row, column)))
        if text_count:
            issues.append(
                {
                    "columna": column,
                    "columna_mostrada": _display_value(column),
                    "tipo": "texto_sospechoso",
                    "conteo": text_count,
                    "descripcion": "Texto con espacios iniciales/finales, espacios múltiples o caracteres no separables.",
                }
            )
    if duplicate_rows:
        issues.append(
            {
                "columna": "__fila__",
                "columna_mostrada": "__fila__",
                "tipo": "duplicados_exactos",
                "conteo": sum(int(row["repeticiones_adicionales"]) for row in duplicate_rows),
                "descripcion": "Registros idénticos detectados y reportados sin eliminarlos.",
            }
        )
    issues.append(
        {
            "columna": "__fila__",
            "columna_mostrada": "__fila__",
            "tipo": "duplicados_parciales_diferidos",
            "conteo": 0,
            "descripcion": "Los duplicados parciales quedan diferidos a la fase de limpieza; no se fusionan ni corrigen en diagnóstico.",
        }
    )
    return issues


def _summary_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"metrica": key, "valor": value} for key, value in summary.items()]


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_outputs_atomically(plans: list[tuple[Path, Any]]) -> None:
    temps: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path, bool]] = []
    committed = False
    try:
        for final_path, writer in plans:
            temp_path = _temporary_path(final_path)
            writer(temp_path)
            temps.append((temp_path, final_path))
        for _temp_path, final_path in temps:
            backup_path = _backup_path(final_path)
            if final_path.exists():
                final_path.replace(backup_path)
                backups.append((backup_path, final_path, True))
            else:
                backups.append((backup_path, final_path, False))
        for temp_path, final_path in temps:
            temp_path.replace(final_path)
        committed = True
    except Exception as exc:
        restore_errors = _restore_outputs(backups)
        if restore_errors:
            details = "; ".join(restore_errors)
            raise DiagnosticOutputError(
                "Falló la restauración de salidas diagnósticas; se preservaron backups para "
                f"recuperación manual. {details}"
            ) from exc
        raise
    finally:
        for temp_path, _final_path in temps:
            _safe_unlink(temp_path)
        if committed:
            for backup_path, _final_path, _existed in backups:
                _safe_unlink(backup_path)


def _temporary_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{os.getpid()}.tmp")


def _backup_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{os.getpid()}.backup")


def _restore_outputs(backups: list[tuple[Path, Path, bool]]) -> list[str]:
    restore_errors: list[str] = []
    for backup_path, final_path, existed in reversed(backups):
        if existed:
            if backup_path.exists():
                try:
                    backup_path.replace(final_path)
                except OSError as exc:
                    restore_errors.append(
                        f"destino={final_path}; backup={backup_path}; causa={exc}"
                    )
        else:
            _safe_unlink(final_path)
    return restore_errors


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _render_markdown(report: DiagnosticReport) -> str:
    issue_count = len(report.quality_issues)
    return f"""# Diagnóstico de datos crudos MINEDUC

Este diagnóstico fue generado por código sobre `{_report_path(report.source_path)}`.

## Resumen

- Filas: {report.summary["filas"]}
- Columnas: {report.summary["columnas"]}
- Duplicados exactos: {report.summary["duplicados_exactos"]}
- Catálogo territorial: {report.summary["catalogo_territorial"]}
- Problemas potenciales reportados: {issue_count} (incluye duplicados parciales diferidos)

## Flujo reproducible

El flujo completo conserva la línea de procedencia `adquisición → manifest → consolidación → diagnóstico`:

1. Adquisición: `uv run python scripts/adquirir_datos.py --capture-html --department-code 01 --department-name GUATEMALA --fecha-extraccion 2026-07-14`.
2. Manifest: `data/raw/manifest.json` registra fuente, cobertura, método, checksum y error de adquisición si aplica.
3. Consolidación: `uv run python scripts/consolidar_crudos.py` regenera `data/source/establecimientos_diversificado_mineduc.csv` sin limpieza.
4. Diagnóstico: `uv run python scripts/diagnosticar_crudos.py` regenera estas tablas y este documento.

El comando de adquisición mostrado es un ejemplo para un departamento. La adquisición preservada contiene 23 artefactos HTML departamentales en `data/raw/`; para recapturarla completa, repita el comando para cada código y nombre de departamento, o use los artefactos crudos ya preservados.

## Tablas generadas

- `outputs/tablas/resumen_dataset.csv`
- `outputs/tablas/diagnostico_columnas.csv`
- `outputs/tablas/duplicados_exactos.csv`
- `outputs/tablas/problemas_potenciales.csv`
- `outputs/tablas/dominios_observados.csv`

## Alcance y límites

No se aplicó limpieza, normalización, deduplicación, recodificación, corrección de tipos, eliminación de filas ni corrección de dominios. Los duplicados exactos se reportan sin eliminarlos. Los duplicados parciales quedan diferidos a la fase de limpieza para evitar fusiones o correcciones sin revisión.

## Limitación territorial

No se encontró catálogo oficial de departamentos o municipios en este slice. Por esa razón el diagnóstico documenta dominios territoriales como no verificables y evita declarar valores inválidos sin evidencia suficiente.
"""


def _raw_value(row: dict[str, str], column: str) -> str:
    return row.get(column, "")


def _is_missing_like(value: str) -> bool:
    normalized = value.replace("\xa0", " ").strip().casefold()
    return normalized in MISSING_MARKERS


def _has_suspicious_phone(value: str) -> bool:
    if _is_missing_like(value):
        return False
    return not value.isdigit()


def _has_suspicious_code(value: str) -> bool:
    if _is_missing_like(value):
        return False
    return CODE_PATTERN.fullmatch(value) is None


def _has_suspicious_text(value: str) -> bool:
    if _is_missing_like(value):
        return False
    collapsed = " ".join(value.strip().split())
    return value != value.strip() or "\xa0" in value or collapsed != value.strip()


def _normalize_label(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split()).casefold()


def _report_path(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.name


def _display_value(value: str) -> str:
    invisible_names = {"\xa0": "<NBSP>", " ": "<SPACE>", "\t": "<TAB>", "\n": "<LF>", "\r": "<CR>"}
    if value == "":
        return "''"
    if all(character in invisible_names for character in value):
        return "'" + "".join(invisible_names[character] for character in value) + "'"
    return "".join(invisible_names.get(character, character) if character != " " else character for character in value)
