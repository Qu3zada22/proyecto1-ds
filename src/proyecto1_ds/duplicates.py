"""Detección y decisión de duplicados parciales por similitud, sin borrado automático."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
import os
from pathlib import Path
import shutil
from typing import Any

from rapidfuzz import fuzz


DEFAULT_CLEAN_CSV = Path("data/processed/establecimientos_diversificado_limpio.csv")
DEFAULT_CANDIDATES_CSV = Path("outputs/tablas/duplicados_parciales.csv")
DEFAULT_TABLES_DIR = Path("outputs/tablas")
DEFAULT_REPORTS_DIR = Path("outputs/reportes")
NAME_THRESHOLD = 90.0
ADDRESS_THRESHOLD = 88.0
BLOCK_COLUMNS = ("DEPARTAMENTO", "MUNICIPIO")
NAME_COLUMN = "ESTABLECIMIENTO"
ADDRESS_COLUMN = "DIRECCION"
PHONE_COLUMN = "TELEFONO"
CODE_COLUMN = "CODIGO"
# Campos que definen la oferta; si difieren, es la misma sede con otra jornada/plan, no un duplicado.
DISCRIMINATOR_COLUMNS = ("SECTOR", "MODALIDAD", "JORNADA", "PLAN")
CANDIDATE_FIELDS = [
    "departamento",
    "municipio",
    "confianza",
    "codigo_a",
    "establecimiento_a",
    "codigo_b",
    "establecimiento_b",
    "similitud_nombre",
    "similitud_direccion",
    "telefono_a",
    "telefono_b",
    "decision",
]
AUTOMATIC_DECISIONS = {"duplicado_probable", "independiente", "revisar"}
MANUAL_FINAL_DECISIONS = {"duplicado_confirmado", "independiente_confirmado"}
MANUAL_PENDING_DECISIONS = {"revisar_institucional"}
MANUAL_DECISIONS = MANUAL_FINAL_DECISIONS | MANUAL_PENDING_DECISIONS
VALID_DECISIONS = AUTOMATIC_DECISIONS | MANUAL_DECISIONS
LOG_FIELDS = ["variable", "regla", "filas_afectadas", "justificacion", "riesgo", "evidencia_fuente"]


class DuplicatesCsvError(ValueError):
    """Error esperado cuando el CSV limpio no es tabularmente válido."""


@dataclass(frozen=True)
class DuplicateReport:
    source_path: Path
    threshold: float
    candidates: list[dict[str, Any]]
    summary: dict[str, Any]


@dataclass(frozen=True)
class DuplicateOutputs:
    candidates_path: Path
    report_path: Path


def detect_partial_duplicates(
    source_csv: Path | str = DEFAULT_CLEAN_CSV,
    *,
    threshold: float = NAME_THRESHOLD,
) -> DuplicateReport:
    """Reporta pares de establecimientos similares dentro de una misma localidad."""

    source_path = Path(source_csv)
    header, rows = _read_csv(source_path)
    _require_columns(source_path, header)

    blocks = _group_by_block(rows)
    candidates: list[dict[str, Any]] = []
    comparisons = 0
    site_variants = 0
    for (departamento, municipio), records in blocks.items():
        for index_a in range(len(records)):
            for index_b in range(index_a + 1, len(records)):
                record_a = records[index_a]
                record_b = records[index_b]
                comparisons += 1
                name_score = fuzz.token_sort_ratio(record_a["nombre"], record_b["nombre"])
                if name_score < threshold:
                    continue
                address_score = _pair_score(record_a["direccion"], record_b["direccion"])
                phone_match = record_a["telefono"] != "" and record_a["telefono"] == record_b["telefono"]
                address_match = address_score is not None and address_score >= ADDRESS_THRESHOLD
                if not (address_match or phone_match):
                    continue
                if record_a["oferta"] != record_b["oferta"]:
                    site_variants += 1
                    continue
                candidates.append(
                    {
                        "departamento": departamento,
                        "municipio": municipio,
                        "confianza": "alta" if address_match and phone_match else "media",
                        "codigo_a": record_a["codigo"],
                        "establecimiento_a": record_a["nombre"],
                        "codigo_b": record_b["codigo"],
                        "establecimiento_b": record_b["nombre"],
                        "similitud_nombre": round(name_score, 2),
                        "similitud_direccion": "" if address_score is None else round(address_score, 2),
                        "telefono_a": record_a["telefono"],
                        "telefono_b": record_b["telefono"],
                        "decision": _classify_decision(
                            "alta" if address_match and phone_match else "media",
                            record_a["telefono"],
                            record_b["telefono"],
                        ),
                    }
                )

    candidates.sort(
        key=lambda item: (item["confianza"] != "alta", -item["similitud_nombre"], item["departamento"], item["municipio"])
    )
    summary = {
        "umbral_similitud_nombre": threshold,
        "umbral_similitud_direccion": ADDRESS_THRESHOLD,
        "bloques_evaluados": len(blocks),
        "comparaciones": comparisons,
        "candidatos_parciales": len(candidates),
        "candidatos_confianza_alta": sum(1 for item in candidates if item["confianza"] == "alta"),
        "candidatos_confianza_media": sum(1 for item in candidates if item["confianza"] == "media"),
        "variantes_misma_sede_distinta_oferta": site_variants,
        "decision_por_defecto": "revisar (sin borrado automático)",
    }
    return DuplicateReport(source_path=source_path, threshold=threshold, candidates=candidates, summary=summary)


@dataclass(frozen=True)
class DecisionSummary:
    candidates_path: Path
    duplicado_probable: int
    independiente: int
    revisar: int
    total: int
    manuales: int = 0


def apply_duplicate_decisions(
    candidates_csv: Path | str = DEFAULT_CANDIDATES_CSV,
    *,
    bitacora_csv: Path | str | None = None,
) -> DecisionSummary:
    """Aplica reglas documentadas al CSV de candidatos y actualiza la columna `decision`.

    Reglas (sin borrado automático):
    - duplicado_probable: confianza == "alta" (dirección Y teléfono coinciden).
    - independiente: confianza == "media" Y ambos teléfonos no vacíos Y distintos.
    - revisar: todos los demás pares (ambiguos; requieren revisión humana).

    Escribe el CSV actualizado en la misma ruta de entrada.
    """
    path = Path(candidates_csv)
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            raw = list(csv.reader(csv_file, strict=True))
            if not raw:
                raise DuplicatesCsvError(f"CSV de candidatos vacío: {path}")
            if raw[0] != CANDIDATE_FIELDS or any(len(row) != len(CANDIDATE_FIELDS) for row in raw[1:]):
                raise DuplicatesCsvError(f"CSV de candidatos sin encabezado canónico: {path}")
            rows = [dict(zip(CANDIDATE_FIELDS, row, strict=True)) for row in raw[1:]]
    except csv.Error as exc:
        raise DuplicatesCsvError(f"CSV de candidatos malformado: {path}: {exc}") from exc

    counts = {decision: 0 for decision in VALID_DECISIONS}
    updated: list[dict[str, Any]] = []
    for row in rows:
        previous = row.get("decision", "")
        if previous not in VALID_DECISIONS | {""}:
            raise DuplicatesCsvError(f"Decisión inválida en {path}: {previous}")
        decision = previous if previous in MANUAL_DECISIONS else _classify_decision(
            row.get("confianza", ""), row.get("telefono_a", ""), row.get("telefono_b", "")
        )
        counts[decision] += 1
        updated.append({**row, "decision": decision})

    summary = DecisionSummary(
        candidates_path=path,
        duplicado_probable=counts["duplicado_probable"],
        independiente=counts["independiente"],
        revisar=counts["revisar"],
        total=len(updated),
        manuales=sum(counts[decision] for decision in MANUAL_DECISIONS),
    )
    contents = {path: _rows_bytes(CANDIDATE_FIELDS, updated)}
    if bitacora_csv is not None:
        log_path = Path(bitacora_csv)
        existing_log = _read_optional_rows(log_path)
        retained_log = [
            row
            for row in existing_log
            if not (row.get("variable") == "DUPLICADOS_PARCIALES" and row.get("regla") == "decidir_duplicados")
        ]
        contents[log_path] = _rows_bytes(LOG_FIELDS, [*retained_log, _decision_log_row(summary)])
    _replace_outputs(contents)
    return summary


def write_duplicate_outputs(
    report: DuplicateReport,
    *,
    tables_dir: Path | str = DEFAULT_TABLES_DIR,
    reports_dir: Path | str = DEFAULT_REPORTS_DIR,
    project_root: Path | str | None = None,
) -> DuplicateOutputs:
    tables_root = Path(tables_dir)
    reports_root = Path(reports_dir)
    tables_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)

    candidates_path = tables_root / "duplicados_parciales.csv"
    report_path = reports_root / "duplicados_parciales.md"

    candidates = _preserve_existing_decisions(candidates_path, report.candidates)
    rendered_report = DuplicateReport(
        source_path=report.source_path,
        threshold=report.threshold,
        candidates=candidates,
        summary={
            **report.summary,
            "duplicado_probable": sum(row["decision"] == "duplicado_probable" for row in candidates),
            "independiente": sum(row["decision"] == "independiente" for row in candidates),
            "revisar": sum(row["decision"] == "revisar" for row in candidates),
            "duplicado_confirmado": sum(row["decision"] == "duplicado_confirmado" for row in candidates),
            "independiente_confirmado": sum(row["decision"] == "independiente_confirmado" for row in candidates),
            "revisar_institucional": sum(row["decision"] == "revisar_institucional" for row in candidates),
        },
    )
    _replace_outputs(
        {
            candidates_path: _rows_bytes(CANDIDATE_FIELDS, candidates),
            report_path: _render_markdown(rendered_report, project_root=project_root).encode(),
        }
    )
    return DuplicateOutputs(candidates_path=candidates_path, report_path=report_path)


def _group_by_block(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    blocks: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        nombre = row.get(NAME_COLUMN, "")
        if not nombre:
            continue
        key = (row.get("DEPARTAMENTO", ""), row.get("MUNICIPIO", ""))
        blocks.setdefault(key, []).append(
            {
                "codigo": row.get(CODE_COLUMN, ""),
                "nombre": nombre,
                "direccion": row.get(ADDRESS_COLUMN, ""),
                "telefono": row.get(PHONE_COLUMN, ""),
                "oferta": tuple(row.get(column, "") for column in DISCRIMINATOR_COLUMNS),
            }
        )
    return blocks


def _pair_score(value_a: str, value_b: str) -> float | None:
    if not value_a or not value_b:
        return None
    return fuzz.token_sort_ratio(value_a, value_b)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise DuplicatesCsvError(f"CSV limpio malformado: {path} está vacío.")
            return list(reader.fieldnames), list(reader)
    except csv.Error as exc:
        raise DuplicatesCsvError(f"CSV limpio malformado: {path}: {exc}") from exc


def _require_columns(path: Path, header: list[str]) -> None:
    required = {CODE_COLUMN, NAME_COLUMN, *BLOCK_COLUMNS}
    missing = sorted(column for column in required if column not in header)
    if missing:
        raise DuplicatesCsvError(f"CSV limpio sin columnas requeridas en {path}: {', '.join(missing)}.")


def _classify_decision(confianza: str, telefono_a: str, telefono_b: str) -> str:
    if confianza == "alta":
        return "duplicado_probable"
    if confianza == "media" and telefono_a and telefono_b and telefono_a != telefono_b:
        return "independiente"
    return "revisar"


def _decision_log_row(summary: DecisionSummary) -> dict[str, str]:
    return {
        "variable": "DUPLICADOS_PARCIALES",
        "regla": "decidir_duplicados",
        "filas_afectadas": str(summary.total),
        "justificacion": (
            "Reglas de decisión aplicadas sin borrado automático: "
            f"duplicado_probable={summary.duplicado_probable} (confianza alta), "
            f"independiente={summary.independiente} (media + teléfonos distintos), "
            f"revisar={summary.revisar} (ambiguos)."
        ),
        "riesgo": "bajo",
        "evidencia_fuente": (
            "docs/planificacion.md; outputs/tablas/duplicados_parciales.csv; "
            "src/proyecto1_ds/duplicates.py apply_duplicate_decisions"
        ),
    }


def _read_optional_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return list(reader)


def _pair_key(row: dict[str, Any]) -> tuple[str, str] | None:
    codes = sorted((str(row.get("codigo_a", "")), str(row.get("codigo_b", ""))))
    if not all(codes):
        return None
    return codes[0], codes[1]


def _preserve_existing_decisions(
    path: Path, candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    existing = _read_optional_rows(path)
    invalid = sorted({row.get("decision", "") for row in existing} - VALID_DECISIONS - {""})
    if invalid:
        raise DuplicatesCsvError(f"Decisión inválida en {path}: {invalid}")
    decisions = {
        key: row.get("decision", "")
        for row in existing
        if (key := _pair_key(row)) is not None
        and row.get("decision", "") in MANUAL_DECISIONS
    }
    return [
        {**row, "decision": decisions.get(_pair_key(row), row["decision"])}
        for row in candidates
    ]


def _rows_bytes(fieldnames: list[str], rows: list[dict[str, Any]]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def _replace_outputs(contents: dict[Path, bytes]) -> None:
    staged = {path: path.with_name(f".{path.name}.{os.getpid()}.tmp") for path in contents}
    backups = {path: path.with_name(f".{path.name}.{os.getpid()}.backup") for path in contents}
    backed_up: set[Path] = set()
    try:
        for path, content in contents.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            staged[path].write_bytes(content)
    except OSError:
        for temp_path in staged.values():
            temp_path.unlink(missing_ok=True)
        raise
    existed = {path: path.exists() for path in contents}
    try:
        for path in contents:
            if existed[path]:
                shutil.copyfile(path, backups[path])
                backed_up.add(path)
        for path in contents:
            staged[path].replace(path)
    except OSError:
        for path in reversed(contents):
            if path in backed_up:
                backups[path].replace(path)
            elif not existed.get(path, False):
                path.unlink(missing_ok=True)
        raise
    finally:
        for temp_path in staged.values():
            temp_path.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def _logical_path(path: Path, project_root: Path | str | None) -> Path:
    if project_root is None:
        return path if not path.is_absolute() else Path(path.name)
    try:
        return path.resolve().relative_to(Path(project_root).resolve())
    except ValueError:
        return Path(path.name)


def _render_markdown(report: DuplicateReport, *, project_root: Path | str | None = None) -> str:
    summary = report.summary
    lines = [
        "# Duplicados parciales (candidatos)",
        "",
        f"Generado por código sobre `{_logical_path(report.source_path, project_root).as_posix()}` mediante similitud de cadenas (RapidFuzz).",
        "",
        "## Método",
        "",
        "- Bloqueo por `DEPARTAMENTO` + `MUNICIPIO`: solo se comparan establecimientos de la misma localidad.",
        f"- Similitud de nombres con `token_sort_ratio`; umbral de nombre: {report.threshold}.",
        "- Corroboración de sede: además del nombre, el par debe coincidir en dirección "
        f"(similitud >= {summary['umbral_similitud_direccion']}) o en teléfono.",
        "- Corroboración de oferta: el par debe coincidir en `SECTOR`, `MODALIDAD`, `JORNADA` y `PLAN`. "
        "Si difieren, es la misma sede con distinta jornada o plan (oferta legítima), no un duplicado.",
        "- `confianza = alta` cuando coinciden dirección y teléfono; `media` cuando solo una corrobora.",
        "- **No se elimina ni fusiona ningún registro**: las reglas solo clasifican el triage.",
        "- Al regenerar, una decisión vigente se conserva por el par estable de códigos; los pares nuevos reciben el triage determinista.",
        "",
        "## Resumen",
        "",
        f"- Bloques evaluados: {summary['bloques_evaluados']}",
        f"- Comparaciones realizadas: {summary['comparaciones']}",
        f"- Candidatos a duplicado parcial: {summary['candidatos_parciales']}",
        f"- Confianza alta: {summary['candidatos_confianza_alta']}",
        f"- Confianza media: {summary['candidatos_confianza_media']}",
        f"- Variantes de misma sede con distinta oferta (no duplicados): {summary['variantes_misma_sede_distinta_oferta']}",
        f"- Duplicado probable: {summary['duplicado_probable']}",
        f"- Independiente: {summary['independiente']}",
        f"- Revisión institucional/manual pendiente: {summary['revisar']}",
        f"- Duplicados confirmados manualmente: {summary['duplicado_confirmado']}",
        f"- Independientes confirmados manualmente: {summary['independiente_confirmado']}",
        f"- Revisión institucional explícita: {summary['revisar_institucional']}",
        "",
        "## Salida",
        "",
        "- `outputs/tablas/duplicados_parciales.csv`: un par candidato por fila, con sus similitudes y decisión de triage.",
        "",
        "Los pares marcados `revisar` requieren revisión institucional/manual; el triage no equivale a una resolución final.",
        "",
    ]
    return "\n".join(lines)
