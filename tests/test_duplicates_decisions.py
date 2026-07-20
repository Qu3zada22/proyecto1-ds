"""Pruebas para apply_duplicate_decisions (reglas de Anggie, R5g)."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from proyecto1_ds.duplicates import (
    CANDIDATE_FIELDS,
    DEFAULT_CANDIDATES_CSV,
    DecisionSummary,
    DuplicatesCsvError,
    apply_duplicate_decisions,
)


def _write_candidates(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANDIDATE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_candidate(
    confianza: str,
    telefono_a: str = "12345678",
    telefono_b: str = "12345678",
    decision: str = "revisar",
) -> dict:
    return {
        "departamento": "GUATEMALA",
        "municipio": "GUATEMALA",
        "confianza": confianza,
        "codigo_a": "01-01-0001-46",
        "establecimiento_a": "COLEGIO A",
        "codigo_b": "01-01-0002-46",
        "establecimiento_b": "COLEGIO A",
        "similitud_nombre": "100.0",
        "similitud_direccion": "100.0",
        "telefono_a": telefono_a,
        "telefono_b": telefono_b,
        "decision": decision,
    }


def test_ruta_default_candidatos():
    assert DEFAULT_CANDIDATES_CSV == Path("outputs/tablas/duplicados_parciales.csv")


def test_confianza_alta_produce_duplicado_probable(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    _write_candidates(csv_path, [_make_candidate("alta", "55551111", "55551111")])

    result = apply_duplicate_decisions(csv_path)

    assert isinstance(result, DecisionSummary)
    assert result.duplicado_probable == 1
    assert result.independiente == 0
    assert result.revisar == 0
    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "duplicado_probable"


def test_confianza_media_telefonos_distintos_produce_independiente(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    _write_candidates(csv_path, [_make_candidate("media", "55551111", "99998888")])

    result = apply_duplicate_decisions(csv_path)

    assert result.independiente == 1
    assert result.duplicado_probable == 0
    assert result.revisar == 0
    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "independiente"


def test_confianza_media_telefonos_iguales_produce_revisar(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    _write_candidates(csv_path, [_make_candidate("media", "55551111", "55551111")])

    result = apply_duplicate_decisions(csv_path)

    assert result.revisar == 1
    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "revisar"


def test_confianza_media_telefono_vacio_produce_revisar(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    _write_candidates(csv_path, [_make_candidate("media", "", "")])

    result = apply_duplicate_decisions(csv_path)

    assert result.revisar == 1
    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "revisar"


def test_totales_coherentes(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    _write_candidates(
        csv_path,
        [
            _make_candidate("alta", "11111111", "11111111"),
            _make_candidate("media", "22222222", "33333333"),
            _make_candidate("media", "44444444", "44444444"),
        ],
    )

    result = apply_duplicate_decisions(csv_path)

    assert result.total == 3
    assert result.duplicado_probable + result.independiente + result.revisar == result.total


def test_csv_vacio_lanza_error(tmp_path):
    csv_path = tmp_path / "vacio.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(DuplicatesCsvError):
        apply_duplicate_decisions(csv_path)


def test_modifica_decision_previa(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    row = _make_candidate("alta", "55551111", "55551111", decision="revisar")
    _write_candidates(csv_path, [row])

    apply_duplicate_decisions(csv_path)

    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "duplicado_probable"
