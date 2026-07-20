"""Detección y decisión de duplicados parciales por similitud, sin borrado automático."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import os
from pathlib import Path
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
                        "decision": "revisar",
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


def apply_duplicate_decisions(
    candidates_csv: Path | str = DEFAULT_CANDIDATES_CSV,
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
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise DuplicatesCsvError(f"CSV de candidatos vacío: {path}")
            rows = list(reader)
    except csv.Error as exc:
        raise DuplicatesCsvError(f"CSV de candidatos malformado: {path}: {exc}") from exc

    counts = {"duplicado_probable": 0, "independiente": 0, "revisar": 0}
    updated: list[dict[str, Any]] = []
    for row in rows:
        confianza = row.get("confianza", "")
        tel_a = row.get("telefono_a", "")
        tel_b = row.get("telefono_b", "")
        if confianza == "alta":
            decision = "duplicado_probable"
        elif confianza == "media" and tel_a and tel_b and tel_a != tel_b:
            decision = "independiente"
        else:
            decision = "revisar"
        counts[decision] += 1
        updated.append({**row, "decision": decision})

    _write_rows(path, CANDIDATE_FIELDS, updated)
    return DecisionSummary(
        candidates_path=path,
        duplicado_probable=counts["duplicado_probable"],
        independiente=counts["independiente"],
        revisar=counts["revisar"],
        total=len(updated),
    )


def write_duplicate_outputs(
    report: DuplicateReport,
    *,
    tables_dir: Path | str = DEFAULT_TABLES_DIR,
    reports_dir: Path | str = DEFAULT_REPORTS_DIR,
) -> DuplicateOutputs:
    tables_root = Path(tables_dir)
    reports_root = Path(reports_dir)
    tables_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)

    candidates_path = tables_root / "duplicados_parciales.csv"
    report_path = reports_root / "duplicados_parciales.md"

    _write_rows(candidates_path, CANDIDATE_FIELDS, report.candidates)
    report_path.write_text(_render_markdown(report), encoding="utf-8")
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


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            csv_file.flush()
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _render_markdown(report: DuplicateReport) -> str:
    summary = report.summary
    lines = [
        "# Duplicados parciales (candidatos)",
        "",
        f"Generado por código sobre `{report.source_path.as_posix()}` mediante similitud de cadenas (RapidFuzz).",
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
        "- **No se elimina ni fusiona ningún registro**: cada candidato queda con `decision = revisar`.",
        "",
        "## Resumen",
        "",
        f"- Bloques evaluados: {summary['bloques_evaluados']}",
        f"- Comparaciones realizadas: {summary['comparaciones']}",
        f"- Candidatos a duplicado parcial: {summary['candidatos_parciales']}",
        f"- Confianza alta: {summary['candidatos_confianza_alta']}",
        f"- Confianza media: {summary['candidatos_confianza_media']}",
        f"- Variantes de misma sede con distinta oferta (no duplicados): {summary['variantes_misma_sede_distinta_oferta']}",
        "",
        "## Salida",
        "",
        "- `outputs/tablas/duplicados_parciales.csv`: un par candidato por fila, con sus similitudes y la decisión pendiente.",
        "",
        "La decisión final de cada par requiere revisión humana; este reporte solo entrega evidencia trazable.",
        "",
    ]
    return "\n".join(lines)
