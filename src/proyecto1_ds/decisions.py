"""Lectura estricta de decisiones aprobadas y versionadas."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


DEFAULT_PHONE_DECISIONS_CSV = Path("data/decisions/telefonos_aprobados.csv")
DEFAULT_DUPLICATE_DECISIONS_CSV = Path("data/decisions/duplicados_aprobados.csv")
PHONE_DECISION_FIELDS = ["CODIGO", "original", "normalizado", "razon", "aprobador", "fecha"]
DUPLICATE_DECISION_FIELDS = [
    "codigo_a", "codigo_b", "decision", "razon", "evidencia", "aprobador", "fecha",
]


class DecisionManifestError(ValueError):
    """El manifiesto no es válido o ya no coincide con la evidencia vigente."""


def load_phone_decisions(path: Path | str, records: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    rows = _read(Path(path), PHONE_DECISION_FIELDS)
    by_code = _unique_records(records, "CODIGO")
    decisions: dict[str, dict[str, str]] = {}
    for row in rows:
        code = row["CODIGO"]
        _metadata(row, Path(path))
        if code in decisions:
            raise DecisionManifestError(f"Código duplicado en manifiesto telefónico: {code}")
        if code not in by_code or by_code[code].get("TELEFONO", "") != row["original"]:
            raise DecisionManifestError(f"Manifiesto telefónico stale para {code}")
        if not row["normalizado"].isdigit() or len(row["normalizado"]) != 8 or row["normalizado"] == row["original"]:
            raise DecisionManifestError(f"Normalización telefónica fuera de dominio para {code}")
        decisions[code] = row
    return decisions


def load_duplicate_decisions(path: Path | str, candidates: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    rows = _read(Path(path), DUPLICATE_DECISION_FIELDS)
    candidate_keys = {_pair(row) for row in candidates}
    if None in candidate_keys:
        raise DecisionManifestError("Candidato a duplicado sin códigos")
    decisions: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        _metadata(row, Path(path), require_evidence=True)
        key = _pair(row)
        if key is None or key[0] == key[1]:
            raise DecisionManifestError("Par inválido en manifiesto de duplicados")
        if key in decisions:
            raise DecisionManifestError(f"Par duplicado en manifiesto: {key}")
        if row["decision"] != "independiente_confirmado":
            raise DecisionManifestError(f"Decisión fuera de dominio para {key}: {row['decision']}")
        if key not in candidate_keys:
            raise DecisionManifestError(f"Manifiesto de duplicados stale para {key}")
        decisions[key] = row
    return decisions


def _read(path: Path, fields: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise DecisionManifestError(f"Manifiesto ilegible o malformado: {path}: {exc}") from exc
    if not raw or raw[0] != fields or any(len(row) != len(fields) for row in raw[1:]):
        raise DecisionManifestError(f"Esquema inválido en manifiesto: {path}")
    return [dict(zip(fields, row, strict=True)) for row in raw[1:]]


def _metadata(row: dict[str, str], path: Path, *, require_evidence: bool = False) -> None:
    required = ["razon", "aprobador", "fecha"] + (["evidencia"] if require_evidence else [])
    if any(not row[field].strip() for field in required) or row["aprobador"] != "maintainer":
        raise DecisionManifestError(f"Metadatos de aprobación inválidos en {path}")
    try:
        date.fromisoformat(row["fecha"])
    except ValueError as exc:
        raise DecisionManifestError(f"Fecha inválida en {path}: {row['fecha']}") from exc


def _unique_records(records: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in records:
        value = row.get(field, "")
        if not value or value in result:
            raise DecisionManifestError(f"Entrada con {field} vacío o duplicado: {value}")
        result[value] = row
    return result


def _pair(row: dict[str, str]) -> tuple[str, str] | None:
    codes = sorted((row.get("codigo_a", ""), row.get("codigo_b", "")))
    return (codes[0], codes[1]) if all(codes) else None
