"""Limpieza conservadora y trazable del CSV intermedio MINEDUC."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import os
from pathlib import Path
import secrets
import stat
from typing import Any, Callable, TextIO


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


@dataclass(frozen=True)
class _OutputWritePlan:
    path: Path
    parent_fd: int
    parent_path: Path
    writer: Callable[[TextIO], None]


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
    clean_path, tables_root, guard_root = _validate_output_roots(clean_path, tables_root, guard_root)
    log_path = tables_root / "bitacora_limpieza.csv"
    report_path = tables_root / "reporte_calidad_antes_despues.csv"
    for output_file in (clean_path, log_path, report_path):
        _require_output_csv_file(output_file)
    output_specs: list[tuple[Path, Callable[[TextIO], None]]] = [
        (clean_path, lambda csv_file: _write_rows(csv_file, result.header, result.rows)),
        (log_path, lambda csv_file: _write_rows(csv_file, LOG_FIELDS, result.cleaning_log)),
        (report_path, lambda csv_file: _write_rows(csv_file, REPORT_FIELDS, result.quality_report)),
    ]
    _validate_existing_outputs_without_creating_dirs([path for path, _writer in output_specs], guard_root)
    parent_fds = _open_secure_output_parent_fds([path for path, _writer in output_specs], guard_root)
    try:
        _write_outputs_atomically(
            [
                _OutputWritePlan(path=path, parent_fd=parent_fds[path.parent], parent_path=path.parent, writer=writer)
                for path, writer in output_specs
            ]
        )
    finally:
        for parent_fd in parent_fds.values():
            os.close(parent_fd)
    return CleaningOutputs(clean_csv_path=clean_path, log_path=log_path, report_path=report_path)


def _output_guard_root(clean_csv_path: Path, tables_dir: Path, project_root: Path | str | None) -> Path:
    if project_root is not None:
        return Path(project_root)
    if clean_csv_path == DEFAULT_CLEAN_CSV and tables_dir == DEFAULT_TABLES_DIR:
        return Path(__file__).resolve().parents[2]
    raise CleaningOutputError("project_root es obligatorio para rutas de salida personalizadas.")


def _validate_output_roots(clean_csv_path: Path, tables_dir: Path, project_root: Path) -> tuple[Path, Path, Path]:
    root = _absolute_lexical_path(project_root)
    clean_path = _absolute_lexical_path(clean_csv_path, root)
    tables_root = _absolute_lexical_path(tables_dir, root)
    processed_root = root / "data" / "processed"
    _require_path_strictly_under(clean_path, processed_root)
    _require_clean_csv_file(clean_path, processed_root)
    allowed_tables_root = root / "outputs" / "tablas"
    if tables_root != allowed_tables_root:
        raise CleaningOutputError(f"ruta de salida no permitida: {tables_root} debe ser exactamente {allowed_tables_root}.")
    return clean_path, tables_root, root


def _absolute_lexical_path(path: Path, root: Path | None = None) -> Path:
    base = path if path.is_absolute() else (root / path if root is not None else Path.cwd() / path)
    return Path(os.path.normpath(os.fspath(base)))


def _require_path_strictly_under(path: Path, allowed_root: Path) -> None:
    try:
        relative = path.relative_to(allowed_root)
    except ValueError as exc:
        raise CleaningOutputError(f"ruta de salida no permitida: {path} debe estar bajo {allowed_root}.") from exc
    if not relative.parts:
        raise CleaningOutputError(
            f"ruta de salida no permitida: {path} debe ser un archivo CSV dentro de {allowed_root}, "
            "no el directorio data/processed."
        )


def _require_clean_csv_file(path: Path, processed_root: Path) -> None:
    if path == processed_root:
        raise CleaningOutputError(
            f"ruta de salida no permitida: {path} debe ser un archivo CSV dentro de {processed_root}, "
            "no el directorio data/processed."
        )
    _require_output_csv_file(path)


def _require_output_csv_file(path: Path) -> None:
    if path.suffix.casefold() != ".csv":
        raise CleaningOutputError(f"ruta de salida no permitida: {path} debe ser un archivo CSV y terminar en .csv.")


def _validate_existing_outputs_without_creating_dirs(paths: list[Path], project_root: Path) -> None:
    for path in paths:
        parent_fd = _try_open_secure_existing_directory(project_root, path.parent)
        if parent_fd is None:
            continue
        try:
            _require_output_csv_entry(parent_fd, path.name, path)
        finally:
            os.close(parent_fd)


def _open_secure_output_parent_fds(paths: list[Path], project_root: Path) -> dict[Path, int]:
    parent_fds: dict[Path, int] = {}
    try:
        for path in paths:
            if path.parent not in parent_fds:
                parent_fds[path.parent] = _open_secure_output_directory(project_root, path.parent)
        for path in paths:
            _require_output_csv_entry(parent_fds[path.parent], path.name, path)
    except Exception:
        for parent_fd in parent_fds.values():
            os.close(parent_fd)
        raise
    return parent_fds


def _try_open_secure_existing_directory(project_root: Path, directory: Path) -> int | None:
    root_fd = _open_project_root(project_root)
    current_fd = root_fd
    display_path = project_root
    try:
        for component in _relative_directory_parts(directory, project_root):
            display_path = display_path / component
            try:
                next_fd = _open_directory_component(current_fd, component, display_path)
            except FileNotFoundError:
                os.close(current_fd)
                return None
            os.close(current_fd)
            current_fd = next_fd
        _require_directory_fd_matches_path(current_fd, directory)
        return current_fd
    except Exception:
        os.close(current_fd)
        raise


def _open_secure_output_directory(project_root: Path, directory: Path) -> int:
    root_fd = _open_project_root(project_root)
    current_fd = root_fd
    display_path = project_root
    try:
        for component in _relative_directory_parts(directory, project_root):
            display_path = display_path / component
            try:
                os.mkdir(component, mode=0o755, dir_fd=current_fd)
            except FileExistsError:
                pass
            except OSError as exc:
                raise CleaningOutputError(f"directorio de salida inseguro: {display_path} no se pudo crear.") from exc
            next_fd = _open_directory_component(current_fd, component, display_path)
            os.close(current_fd)
            current_fd = next_fd
        _require_directory_fd_matches_path(current_fd, directory)
        return current_fd
    except Exception:
        os.close(current_fd)
        raise


def _open_project_root(project_root: Path) -> int:
    flags = _directory_open_flags()
    try:
        return os.open(project_root, flags)
    except OSError as exc:
        raise CleaningOutputError(f"directorio de salida inseguro: raíz de proyecto no confiable {project_root}.") from exc


def _open_directory_component(parent_fd: int, component: str, display_path: Path) -> int:
    flags = _directory_open_flags()
    try:
        return os.open(component, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise CleaningOutputError(f"directorio de salida inseguro: {display_path} no es un directorio real sin symlinks.") from exc


def _directory_open_flags() -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    return flags


def _relative_directory_parts(directory: Path, project_root: Path) -> tuple[str, ...]:
    try:
        relative = directory.relative_to(project_root)
    except ValueError as exc:
        raise CleaningOutputError(f"ruta de salida no permitida: {directory} debe estar bajo {project_root}.") from exc
    parts = relative.parts
    if any(part in {"", ".", ".."} for part in parts):
        raise CleaningOutputError(f"ruta de salida no permitida: {directory} contiene componentes inseguros.")
    return parts


def _require_directory_fd_matches_path(directory_fd: int, directory: Path) -> None:
    try:
        path_status = os.stat(directory, follow_symlinks=False)
    except OSError as exc:
        raise CleaningOutputError(f"directorio de salida inseguro: {directory} cambió durante la validación.") from exc
    fd_status = os.fstat(directory_fd)
    if not stat.S_ISDIR(path_status.st_mode) or path_status.st_dev != fd_status.st_dev or path_status.st_ino != fd_status.st_ino:
        raise CleaningOutputError(f"directorio de salida inseguro: {directory} no coincide con el descriptor confiable.")


def _require_output_csv_entry(parent_fd: int, final_name: str, final_path: Path) -> None:
    try:
        final_status = os.stat(final_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(final_status.st_mode):
        raise CleaningOutputError(f"ruta de salida no permitida: {final_path} debe ser un archivo CSV, no un directorio o symlink.")


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


def _write_rows(csv_file: TextIO, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def _write_outputs_atomically(plans: list[_OutputWritePlan]) -> None:
    temps: list[tuple[int, Path, str, str, Path, os.stat_result]] = []
    backups: list[tuple[int, Path, str, str, bool]] = []
    committed = False
    try:
        for plan in plans:
            parent_fd = plan.parent_fd
            final_name = plan.path.name
            temp_name, temp_file, temp_status = _temporary_file(parent_fd, final_name, plan.parent_path)
            temps.append((parent_fd, plan.parent_path, temp_name, final_name, plan.path, temp_status))
            with temp_file as csv_file:
                plan.writer(csv_file)
                csv_file.flush()
            _require_same_temporary_file(parent_fd, temp_name, plan.parent_path / temp_name, temp_status)
        for parent_fd, parent_path, _temp_name, final_name, final_path, _temp_status in temps:
            backup_name = _backup_name(final_name)
            final_status = _stat_existing_output_file(parent_fd, final_name, final_path)
            if final_status is not None:
                os.replace(final_name, backup_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                try:
                    _require_backup_matches(parent_fd, backup_name, parent_path / backup_name, final_status)
                except CleaningOutputError:
                    _restore_swapped_backup(parent_fd, backup_name, final_name, final_path)
                    raise
                backups.append((parent_fd, parent_path, backup_name, final_name, True))
            else:
                backups.append((parent_fd, parent_path, backup_name, final_name, False))
        for parent_fd, parent_path, temp_name, final_name, final_path, temp_status in temps:
            _require_same_temporary_file(parent_fd, temp_name, parent_path / temp_name, temp_status)
            replaced_final = False
            try:
                os.replace(temp_name, final_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                replaced_final = True
                _require_same_temporary_file(parent_fd, final_name, final_path, temp_status)
            except Exception:
                if replaced_final:
                    _safe_unlink(parent_fd, final_name, final_path)
                raise
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
        for parent_fd, parent_path, temp_name, _final_name, _final_path, _temp_status in temps:
            _safe_unlink(parent_fd, temp_name, parent_path / temp_name)
        if committed:
            for parent_fd, parent_path, backup_name, _final_name, existed in backups:
                if existed:
                    _safe_unlink(parent_fd, backup_name, parent_path / backup_name)


def _temporary_file(parent_fd: int, final_name: str, parent_path: Path) -> tuple[str, TextIO, os.stat_result]:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    for _attempt in range(100):
        temp_name = f".{final_name}.{secrets.token_hex(16)}.tmp"
        try:
            file_descriptor = os.open(temp_name, flags, mode=0o600, dir_fd=parent_fd)
            break
        except FileExistsError:
            continue
        except OSError as exc:
            raise CleaningOutputError(f"no se pudo crear temporal seguro bajo {parent_path}.") from exc
    else:
        raise CleaningOutputError(f"no se pudo crear temporal seguro bajo {parent_path}: nombres agotados.")
    try:
        temp_status = os.fstat(file_descriptor)
        temp_file = os.fdopen(file_descriptor, "w", newline="", encoding="utf-8")
    except Exception:
        os.close(file_descriptor)
        _safe_unlink(parent_fd, temp_name, parent_path / temp_name)
        raise
    return temp_name, temp_file, temp_status


def _require_same_temporary_file(parent_fd: int, name: str, display_path: Path, expected_status: os.stat_result) -> None:
    try:
        actual_status = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise CleaningOutputError(f"ruta temporal insegura: {display_path} fue removida antes del reemplazo.") from exc
    if not stat.S_ISREG(actual_status.st_mode):
        raise CleaningOutputError(f"ruta temporal insegura: {display_path} dejó de ser un archivo regular.")
    if actual_status.st_dev != expected_status.st_dev or actual_status.st_ino != expected_status.st_ino:
        raise CleaningOutputError(f"ruta temporal insegura: {display_path} fue reemplazada antes del reemplazo atómico.")


def _stat_existing_output_file(parent_fd: int, final_name: str, final_path: Path) -> os.stat_result | None:
    try:
        final_status = os.stat(final_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(final_status.st_mode):
        raise CleaningOutputError(f"ruta de salida no permitida: {final_path} debe ser un archivo CSV, no un directorio o symlink.")
    return final_status


def _require_backup_matches(parent_fd: int, backup_name: str, backup_path: Path, expected_status: os.stat_result) -> None:
    try:
        backup_status = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise CleaningOutputError(f"backup inseguro: {backup_path} no fue creado desde el archivo final esperado.") from exc
    if not stat.S_ISREG(backup_status.st_mode):
        raise CleaningOutputError(f"ruta de salida no permitida: {backup_path} debe ser un archivo CSV, no un directorio o symlink.")
    if backup_status.st_dev != expected_status.st_dev or backup_status.st_ino != expected_status.st_ino:
        raise CleaningOutputError(f"backup inseguro: {backup_path} no corresponde al archivo final validado.")


def _restore_swapped_backup(parent_fd: int, backup_name: str, final_name: str, final_path: Path) -> None:
    try:
        os.replace(backup_name, final_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    except OSError as exc:
        raise CleaningOutputError(f"destino inseguro no restaurado={final_path}; backup={backup_name}; causa={exc}") from exc


def _backup_name(final_name: str) -> str:
    return f".{final_name}.{os.getpid()}.backup"


def _restore_outputs(backups: list[tuple[int, Path, str, str, bool]]) -> list[str]:
    restore_errors: list[str] = []
    for parent_fd, parent_path, backup_name, final_name, existed in reversed(backups):
        backup_path = parent_path / backup_name
        final_path = parent_path / final_name
        if existed:
            if _entry_exists(parent_fd, backup_name):
                remove_error = _remove_path_for_restore(parent_fd, final_name, final_path)
                if remove_error:
                    restore_errors.append(remove_error)
                    continue
                try:
                    os.replace(backup_name, final_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                except OSError as exc:
                    restore_errors.append(f"destino={final_path}; backup={backup_path}; causa={exc}")
        else:
            remove_error = _remove_path_for_restore(parent_fd, final_name, final_path)
            if remove_error:
                restore_errors.append(remove_error)
    return restore_errors


def _entry_exists(parent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def _remove_path_for_restore(parent_fd: int, name: str, path: Path) -> str:
    try:
        path_status = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if stat.S_ISDIR(path_status.st_mode):
            return f"destino inseguro no removido={path}; causa=es directorio"
        else:
            os.unlink(name, dir_fd=parent_fd)
    except FileNotFoundError:
        return ""
    except OSError as exc:
        return f"destino inseguro no removido={path}; causa={exc}"
    return ""


def _safe_unlink(parent_fd: int, name: str, path: Path) -> None:
    try:
        os.unlink(name, dir_fd=parent_fd)
    except FileNotFoundError:
        pass
    except IsADirectoryError:
        try:
            os.rmdir(name, dir_fd=parent_fd)
        except (FileNotFoundError, OSError):
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
