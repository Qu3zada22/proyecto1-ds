"""Limpieza conservadora y trazable del CSV intermedio MINEDUC."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Callable


DEFAULT_INTERIM_CSV = Path("data/interim/establecimientos_diversificado_raw_unificado.csv")
DEFAULT_CLEAN_CSV = Path("data/processed/establecimientos_diversificado_limpio.csv")
DEFAULT_TABLES_DIR = Path("outputs/tablas")
NBSP = "\xa0"
MISSING_MARKERS = {"", "n/a", "na", "null", "none", "-", ".", "sin dato", "----"}
LOG_FIELDS = ["variable", "regla", "filas_afectadas", "justificacion", "riesgo", "evidencia_fuente"]
REPORT_FIELDS = ["metrica", "variable", "antes", "despues", "estado", "nota"]


class CleaningCsvError(ValueError):
    """Error esperado cuando el CSV intermedio no es tabularmente válido."""


class CleaningOutputError(RuntimeError):
    """Error esperado cuando no se pueden restaurar salidas de limpieza."""


@dataclass(frozen=True)
class CleaningResult:
    """Resultado en memoria de la limpieza conservadora."""

    source_path: Path
    original_header: list[str]
    header: list[str]
    rows: list[dict[str, str]]
    cleaning_log: list[dict[str, str]]
    quality_report: list[dict[str, str]]


@dataclass(frozen=True)
class CleaningOutputs:
    """Rutas comprometidas por la escritura atómica de limpieza."""

    clean_csv_path: Path
    log_path: Path
    report_path: Path


def clean_dataset(interim_csv: Path | str = DEFAULT_INTERIM_CSV) -> CleaningResult:
    """Limpia el CSV intermedio con reglas determinísticas y conservadoras."""

    source_path = Path(interim_csv)
    original_header, raw_rows = _read_csv(source_path)
    normalized_rows = [_normalize_row(row, original_header) for row in raw_rows]
    header = list(original_header)
    log_rows: list[dict[str, str]] = []
    nbsp_status = _evaluate_nbsp_column(original_header, normalized_rows, log_rows)
    if nbsp_status == "removed":
        header = [column for column in header if column != NBSP]
        normalized_rows = [{column: value for column, value in row.items() if column != NBSP} for row in normalized_rows]
    log_rows.extend(_normalization_log(original_header, raw_rows, normalized_rows, removed_nbsp=nbsp_status == "removed"))
    report_rows = _quality_report(original_header, header, raw_rows, normalized_rows, log_rows, nbsp_status)
    return CleaningResult(
        source_path=source_path,
        original_header=original_header,
        header=header,
        rows=normalized_rows,
        cleaning_log=log_rows,
        quality_report=report_rows,
    )


def write_cleaning_outputs(
    result: CleaningResult,
    *,
    clean_csv_path: Path | str = DEFAULT_CLEAN_CSV,
    tables_dir: Path | str = DEFAULT_TABLES_DIR,
    project_root: Path | str | None = None,
) -> CleaningOutputs:
    """Escribe CSV limpio, bitácora y reporte como un único conjunto atómico.

    Si se reciben rutas personalizadas, ``project_root`` es obligatorio. Las rutas
    por defecto infieren la raíz del repositorio. En ambos casos, las salidas se
    restringen a ``data/processed/`` y ``outputs/tablas/`` dentro de esa raíz.
    """

    clean_path = Path(clean_csv_path)
    tables_root = Path(tables_dir)
    guard_root = _output_guard_root(clean_path, tables_root, project_root)
    clean_path, tables_root = _validate_output_roots(clean_path, tables_root, guard_root)
    log_path = tables_root / "bitacora_limpieza.csv"
    report_path = tables_root / "reporte_calidad_antes_despues.csv"
    for destination in (clean_path, log_path, report_path):
        destination.parent.mkdir(parents=True, exist_ok=True)
    _write_outputs_atomically(
        [
            (clean_path, lambda path: _write_rows(path, result.header, result.rows)),
            (log_path, lambda path: _write_rows(path, LOG_FIELDS, result.cleaning_log)),
            (report_path, lambda path: _write_rows(path, REPORT_FIELDS, result.quality_report)),
        ]
    )
    return CleaningOutputs(clean_csv_path=clean_path, log_path=log_path, report_path=report_path)


def _output_guard_root(clean_csv_path: Path, tables_dir: Path, project_root: Path | str | None) -> Path:
    if project_root is not None:
        return Path(project_root)
    if clean_csv_path == DEFAULT_CLEAN_CSV and tables_dir == DEFAULT_TABLES_DIR:
        return Path(__file__).resolve().parents[2]
    raise CleaningOutputError("project_root es obligatorio para rutas de salida personalizadas.")


def _validate_output_roots(clean_csv_path: Path, tables_dir: Path, project_root: Path) -> tuple[Path, Path]:
    root = project_root.resolve(strict=False)
    clean_path = _resolve_from_root(clean_csv_path, root)
    tables_root = _resolve_from_root(tables_dir, root)
    _require_path_under(clean_path, root / "data" / "processed")
    _require_path_under(tables_root, root / "outputs" / "tablas")
    return clean_path, tables_root


def _resolve_from_root(path: Path, root: Path) -> Path:
    if path.is_absolute():
        return path.resolve(strict=False)
    return (root / path).resolve(strict=False)


def _require_path_under(path: Path, allowed_root: Path) -> None:
    allowed = allowed_root.resolve(strict=False)
    try:
        path.relative_to(allowed)
    except ValueError as exc:
        raise CleaningOutputError(f"ruta de salida no permitida: {path} debe estar bajo {allowed}.") from exc


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, strict=True)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise CleaningCsvError(f"CSV intermedio malformado: {path} está vacío.") from exc
            _validate_header(path, header)
            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(header):
                    raise CleaningCsvError(
                        "CSV intermedio malformado: "
                        f"{path} fila {line_number} tiene {len(row)} columnas; se esperaban {len(header)}."
                    )
                rows.append(dict(zip(header, row, strict=True)))
            return header, rows
    except csv.Error as exc:
        raise CleaningCsvError(f"CSV intermedio malformado: {path}: {exc}") from exc


def _validate_header(path: Path, header: list[str]) -> None:
    if not header:
        raise CleaningCsvError(f"CSV intermedio malformado: {path} no contiene encabezados.")
    repeated = sorted({column for column in header if header.count(column) > 1})
    if repeated:
        repeated_display = ", ".join(_display_value(column) for column in repeated)
        raise CleaningCsvError(f"CSV intermedio malformado: encabezados duplicados: {repeated_display}.")


def _normalize_row(row: dict[str, str], header: list[str]) -> dict[str, str]:
    return {column: _normalize_value(row.get(column, "")) for column in header}


def _normalize_value(value: str) -> str:
    normalized = " ".join(value.replace(NBSP, " ").strip().split())
    if normalized.casefold() in MISSING_MARKERS:
        return ""
    return normalized


def _evaluate_nbsp_column(
    header: list[str],
    rows: list[dict[str, str]],
    log_rows: list[dict[str, str]],
) -> str:
    if NBSP not in header:
        return "absent"
    non_missing = sum(1 for row in rows if row.get(NBSP, "") != "")
    if non_missing == 0:
        log_rows.append(
            _log_row(
                variable=_display_value(NBSP),
                rule="eliminar_columna_nbsp_vacia",
                affected=len(rows),
                justification="Columna compuesta solo por ausencias según diagnóstico y plan de limpieza.",
                risk="bajo",
                evidence="docs/plan_limpieza.md; outputs/tablas/diagnostico_columnas.csv",
            )
        )
        return "removed"
    log_rows.append(
        _log_row(
            variable=_display_value(NBSP),
            rule="conservar_columna_nbsp_no_segura",
            affected=non_missing,
            justification="La columna contiene valores no ausentes; eliminarla requeriría revisión manual.",
            risk="alto",
            evidence="CSV intermedio",
        )
    )
    return "kept_non_empty"


def _normalization_log(
    original_header: list[str],
    raw_rows: list[dict[str, str]],
    clean_rows: list[dict[str, str]],
    *,
    removed_nbsp: bool,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for column in original_header:
        if removed_nbsp and column == NBSP:
            continue
        missing_count = 0
        whitespace_count = 0
        for raw_row, clean_row in zip(raw_rows, clean_rows, strict=True):
            raw_value = raw_row.get(column, "")
            clean_value = clean_row.get(column, "")
            if clean_value == "" and _normalized_candidate(raw_value).casefold() in MISSING_MARKERS and raw_value != "":
                missing_count += 1
            elif raw_value != clean_value:
                whitespace_count += 1
        if whitespace_count:
            rows.append(
                _log_row(
                    variable=_display_value(column),
                    rule="normalizar_espacios_nbsp",
                    affected=whitespace_count,
                    justification="Normalización conservadora de NBSP, bordes y espacios internos múltiples.",
                    risk="bajo",
                    evidence="docs/plan_limpieza.md",
                )
            )
        if missing_count:
            rows.append(
                _log_row(
                    variable=_display_value(column),
                    rule="normalizar_marcador_ausencia",
                    affected=missing_count,
                    justification="Marcadores inequívocos de ausencia convertidos a vacío consistente.",
                    risk="bajo",
                    evidence="docs/plan_limpieza.md",
                )
            )
    return rows


def _quality_report(
    original_header: list[str],
    clean_header: list[str],
    raw_rows: list[dict[str, str]],
    clean_rows: list[dict[str, str]],
    log_rows: list[dict[str, str]],
    nbsp_status: str,
) -> list[dict[str, str]]:
    report = [
        _report_row(
            metrica="filas",
            variable="__dataset__",
            before=len(raw_rows),
            after=len(clean_rows),
            status="ejecutado",
            note="Conteo de filas preservado.",
        ),
        _report_row(
            metrica="columnas",
            variable="__dataset__",
            before=len(original_header),
            after=len(clean_header),
            status="ejecutado",
            note=_nbsp_note(nbsp_status),
        ),
    ]
    for column in original_header:
        before = sum(1 for row in raw_rows if _is_missing_like(row.get(column, "")))
        after = "NA" if column not in clean_header else sum(1 for row in clean_rows if row.get(column, "") == "")
        report.append(
            _report_row(
                metrica="faltantes",
                variable=_display_value(column),
                before=before,
                after=after,
                status="ejecutado",
                note="Conteo comparable antes/después.",
            )
        )
    markers_normalized = sum(int(row["filas_afectadas"]) for row in log_rows if row["regla"] == "normalizar_marcador_ausencia")
    report.append(
        _report_row(
            metrica="marcadores_ausencia_normalizados",
            variable="__dataset__",
            before=markers_normalized,
            after=markers_normalized,
            status="ejecutado",
            note="Marcadores claros convertidos a vacío consistente.",
        )
    )
    report.extend(
        [
            _report_row(
                metrica="decision_diferida",
                variable="territorio",
                before="pendiente",
                after="pendiente",
                status="diferido",
                note="Validación territorial requiere catálogo oficial.",
            ),
            _report_row(
                metrica="decision_diferida",
                variable="telefonos",
                before="pendiente",
                after="pendiente",
                status="manual",
                note="Teléfonos ambiguos no se corrigen automáticamente.",
            ),
            _report_row(
                metrica="decision_diferida",
                variable="duplicados_parciales",
                before="pendiente",
                after="pendiente",
                status="manual",
                note="No se fusionan ni eliminan registros parciales.",
            ),
            _report_row(
                metrica="decision_diferida",
                variable="texto_libre",
                before="pendiente",
                after="pendiente",
                status="manual",
                note="No se reescriben nombres, direcciones ni responsables.",
            ),
        ]
    )
    return report


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_outputs_atomically(plans: list[tuple[Path, Callable[[Path], None]]]) -> None:
    temps: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path, bool]] = []
    committed = False
    try:
        for final_path, writer in plans:
            temp_path = _temporary_path(final_path)
            temps.append((temp_path, final_path))
            writer(temp_path)
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
            raise CleaningOutputError(
                "Falló la restauración de salidas de limpieza; se preservaron backups para "
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
                    restore_errors.append(f"destino={final_path}; backup={backup_path}; causa={exc}")
        else:
            _safe_unlink(final_path)
    return restore_errors


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _log_row(*, variable: str, rule: str, affected: int, justification: str, risk: str, evidence: str) -> dict[str, str]:
    return {
        "variable": variable,
        "regla": rule,
        "filas_afectadas": str(affected),
        "justificacion": justification,
        "riesgo": risk,
        "evidencia_fuente": evidence,
    }


def _report_row(*, metrica: str, variable: str, before: Any, after: Any, status: str, note: str) -> dict[str, str]:
    return {
        "metrica": metrica,
        "variable": variable,
        "antes": str(before),
        "despues": str(after),
        "estado": status,
        "nota": note,
    }


def _normalized_candidate(value: str) -> str:
    return " ".join(value.replace(NBSP, " ").strip().split())


def _is_missing_like(value: str) -> bool:
    return _normalized_candidate(value).casefold() in MISSING_MARKERS


def _nbsp_note(status: str) -> str:
    notes = {
        "removed": "Columna <NBSP> eliminada por estar completamente vacía.",
        "kept_non_empty": "Columna <NBSP> conservada por contener valores no ausentes.",
        "absent": "Columna <NBSP> no presente en la entrada.",
    }
    return notes[status]


def _display_value(value: str) -> str:
    invisible_names = {NBSP: "<NBSP>", " ": "<SPACE>", "\t": "<TAB>", "\n": "<LF>", "\r": "<CR>"}
    if value == "":
        return "''"
    if all(character in invisible_names for character in value):
        return "'" + "".join(invisible_names[character] for character in value) + "'"
    return "".join(invisible_names.get(character, character) if character != " " else character for character in value)
