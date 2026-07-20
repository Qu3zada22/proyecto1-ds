"""Validación y aplicación estricta de decisiones aprobadas."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from proyecto1_ds.cleaning import clean_dataset
from proyecto1_ds.decisions import DecisionManifestError, load_duplicate_decisions, load_phone_decisions
from proyecto1_ds.duplicates import CANDIDATE_FIELDS, apply_duplicate_decisions
from proyecto1_ds.enrichment import enrich_result


ROOT = Path(__file__).resolve().parents[1]
PHONE_MANIFEST = ROOT / "data/decisions/telefonos_aprobados.csv"
DUPLICATE_MANIFEST = ROOT / "data/decisions/duplicados_aprobados.csv"


def _write(path: Path, fields: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


def test_manifiestos_canonicos_tienen_11_y_6_decisiones_vigentes():
    with (ROOT / "data/source/establecimientos_diversificado_mineduc.csv").open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    with (ROOT / "outputs/tablas/duplicados_parciales.csv").open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))

    assert len(load_phone_decisions(PHONE_MANIFEST, source)) == 6
    assert len(load_duplicate_decisions(DUPLICATE_MANIFEST, candidates)) == 11


def test_limpio_real_solo_cambia_las_seis_celdas_telefonicas_aprobadas():
    source = ROOT / "data/source/establecimientos_diversificado_mineduc.csv"
    catalog = ROOT / "data/reference/catalogo_territorial.csv"
    expected_before = enrich_result(clean_dataset(source), catalog_csv=catalog)
    expected_after = enrich_result(
        clean_dataset(source, phone_decisions_csv=PHONE_MANIFEST), catalog_csv=catalog
    )
    with (ROOT / "data/processed/establecimientos_diversificado_limpio.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        published = list(csv.DictReader(handle))
    decisions = load_phone_decisions(PHONE_MANIFEST, expected_before.rows)

    assert expected_after.rows == published
    assert [row["CODIGO"] for row in expected_before.rows] == [row["CODIGO"] for row in published]
    changes = [
        (before["CODIGO"], field, before[field], after[field])
        for before, after in zip(expected_before.rows, expected_after.rows, strict=True)
        for field in expected_before.header
        if before[field] != after[field]
    ]
    assert changes == [
        (row["CODIGO"], "TELEFONO", row["original"], row["normalizado"])
        for row in decisions.values()
    ]


def test_limpieza_aplica_solo_manifest_telefonico_y_registra_evidencia(tmp_path):
    source = tmp_path / "source.csv"
    manifest = tmp_path / "telefonos.csv"
    _write(source, ["CODIGO", "TELEFONO"], [["A", "1234-5678"], ["B", "99999999"]])
    _write(
        manifest,
        ["CODIGO", "original", "normalizado", "razon", "aprobador", "fecha"],
        [["A", "1234-5678", "12345678", "Formato 4+4 aprobado", "maintainer", "2026-07-20"]],
    )

    result = clean_dataset(source, phone_decisions_csv=manifest)

    assert [row["TELEFONO"] for row in result.rows] == ["12345678", "99999999"]
    assert any(row["regla"] == "normalizar_telefono_aprobado" and row["filas_afectadas"] == "1" for row in result.cleaning_log)
    assert any(row["metrica"] == "telefonos_aprobados_normalizados" for row in result.quality_report)


@pytest.mark.parametrize("mutation", ["stale", "duplicate", "domain", "schema"])
def test_manifest_telefonico_invalido_falla_antes_de_publicar(tmp_path, mutation):
    source = tmp_path / "source.csv"
    manifest = tmp_path / "telefonos.csv"
    _write(source, ["CODIGO", "TELEFONO"], [["A", "1234-5678"]])
    fields = ["CODIGO", "original", "normalizado", "razon", "aprobador", "fecha"]
    row = ["A", "1234-5678", "12345678", "Aprobado", "maintainer", "2026-07-20"]
    rows = [row]
    if mutation == "stale":
        row[1] = "0000-0000"
    elif mutation == "duplicate":
        rows.append(row.copy())
    elif mutation == "domain":
        row[4] = "otro"
    else:
        fields = fields[:-1]
        rows = [row[:-1]]

    _write(manifest, fields, rows)

    with pytest.raises(DecisionManifestError):
        clean_dataset(source, phone_decisions_csv=manifest)


def test_decidir_duplicados_aplica_manifest_despues_del_triage(tmp_path):
    candidates = tmp_path / "candidatos.csv"
    manifest = tmp_path / "duplicados.csv"
    row = {
        "departamento": "GUATEMALA", "municipio": "MIXCO", "confianza": "media",
        "codigo_a": "A", "establecimiento_a": "COLEGIO I", "codigo_b": "B",
        "establecimiento_b": "COLEGIO II", "similitud_nombre": "95",
        "similitud_direccion": "90", "telefono_a": "11111111", "telefono_b": "11111111",
        "decision": "revisar",
    }
    with candidates.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)
    _write(
        manifest,
        ["codigo_a", "codigo_b", "decision", "razon", "evidencia", "aprobador", "fecha"],
        [["A", "B", "independiente_confirmado", "Sedes distintas", "Aprobación explícita", "maintainer", "2026-07-20"]],
    )

    summary = apply_duplicate_decisions(candidates, decisions_csv=manifest)

    assert summary.manuales == 1
    assert next(csv.DictReader(candidates.open(newline="", encoding="utf-8")))["decision"] == "independiente_confirmado"


def test_manifest_duplicados_stale_preserva_csv_previo(tmp_path):
    candidates = tmp_path / "candidatos.csv"
    manifest = tmp_path / "duplicados.csv"
    _write(candidates, CANDIDATE_FIELDS, [["", "", "media", "A", "", "B", "", "90", "90", "", "", "revisar"]])
    _write(
        manifest,
        ["codigo_a", "codigo_b", "decision", "razon", "evidencia", "aprobador", "fecha"],
        [["A", "C", "independiente_confirmado", "Sedes distintas", "Aprobación", "maintainer", "2026-07-20"]],
    )
    previous = candidates.read_bytes()

    with pytest.raises(DecisionManifestError, match="stale"):
        apply_duplicate_decisions(candidates, decisions_csv=manifest)

    assert candidates.read_bytes() == previous
