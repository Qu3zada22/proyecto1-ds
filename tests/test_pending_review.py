"""Contratos de la unidad reproducible de recomendaciones pendientes."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.pending_review import PendingReviewError, generate_pending_review


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data/processed/establecimientos_diversificado_limpio.csv"
CANDIDATES = ROOT / "outputs/tablas/duplicados_parciales.csv"
TERRITORY = ROOT / "outputs/tablas/inconsistencias_territoriales.csv"
CATALOG = ROOT / "data/reference/catalogo_territorial.csv"
SCRIPT = ROOT / "scripts/revisar_pendientes.py"


def _generate(tmp_path: Path):
    return generate_pending_review(
        CLEAN,
        CANDIDATES,
        TERRITORY,
        CATALOG,
        tables_dir=tmp_path / "outputs/tablas",
        reports_dir=tmp_path / "outputs/reportes",
        project_root=ROOT,
    )


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_genera_conteos_y_contratos_sin_modificar_datasets(tmp_path):
    protected = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (CLEAN, CATALOG)}

    result = _generate(tmp_path)

    duplicates = _rows(result.duplicates_path)
    phones = _rows(result.phones_path)
    territory = _rows(result.territory_path)
    assert len(duplicates) == 978
    assert sum(row["recomendacion"] == "duplicado_confirmable_local" for row in duplicates) == 0
    assert sum(row["recomendacion"] == "independiente_confirmable_por_evidencia" for row in duplicates) == 0
    assert sum(row["recomendacion"] == "requiere_fuente_institucional" for row in duplicates) == 978
    assert len(phones) == 245
    assert sum(row["recomendacion"] == "normalizacion_segura" for row in phones) == 0
    assert sum(row["recomendacion"] == "conservar_y_documentar" for row in phones) == 196
    assert sum(row["recomendacion"] == "requiere_fuente_institucional" for row in phones) == 49
    assert sum(row["grupo_vigente"] == "no_numerico" for row in phones) == 195
    assert sum(row["grupo_vigente"] == "numerico_longitud_incorrecta" for row in phones) == 50
    assert len(territory) == 7
    assert sum(int(row["filas"]) for row in territory) == 145
    assert {row["recomendacion"] for row in territory} == {"alias_confirmable_por_catalogo"}
    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected} == protected


def test_normalizaciones_aprobadas_ya_no_aparecen_pendientes(tmp_path):
    result = _generate(tmp_path)
    phones = _rows(result.phones_path)
    assert not {
        "00-01-9513-46", "00-17-9771-46", "01-08-8979-46", "08-01-0261-46",
        "10-03-2495-46", "18-02-0347-46",
    }.intersection(row["CODIGO"] for row in phones)
    assert next(row for row in phones if row["CODIGO"] == "08-02-0065-46")["propuesta"] == "77374579 | 45436421 (solo referencia)"


def test_reporte_es_portable_y_declara_limites(tmp_path):
    result = _generate(tmp_path)
    report = result.report_path.read_text(encoding="utf-8")

    assert str(ROOT) not in report
    assert "no equivalen a aprobación institucional" in report
    assert "No se modificó ni fusionó ningún dataset" in report
    assert "7 parejas territoriales (145 filas)" in report


def test_doble_ejecucion_es_byte_identica(tmp_path):
    first = _generate(tmp_path)
    paths = (first.duplicates_path, first.phones_path, first.territory_path, first.report_path)
    hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

    second = _generate(tmp_path)

    assert second == first
    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths} == hashes


@pytest.mark.parametrize("input_name", ["candidates", "territory"])
def test_rechaza_evidencia_stale_y_preserva_salidas(tmp_path, input_name):
    candidates = tmp_path / "duplicados.csv"
    territory = tmp_path / "territorio.csv"
    candidates.write_bytes(CANDIDATES.read_bytes())
    territory.write_bytes(TERRITORY.read_bytes())
    output = tmp_path / "outputs/tablas/recomendaciones_duplicados.csv"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"salida previa\n")
    target = candidates if input_name == "candidates" else territory
    lines = target.read_text(encoding="utf-8").splitlines()
    target.write_text("\n".join([lines[0], *lines[2:]]) + "\n", encoding="utf-8")

    with pytest.raises(PendingReviewError, match="stale"):
        generate_pending_review(
            CLEAN, candidates, territory, CATALOG,
            tables_dir=tmp_path / "outputs/tablas",
            reports_dir=tmp_path / "outputs/reportes",
            project_root=ROOT,
        )

    assert output.read_bytes() == b"salida previa\n"


def test_rechaza_csv_malformado_y_preserva_salidas(tmp_path):
    candidates = tmp_path / "duplicados.csv"
    candidates.write_text('codigo_a,codigo_b,decision\n"sin cierre\n', encoding="utf-8")
    output = tmp_path / "outputs/tablas/recomendaciones_telefonos.csv"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"salida previa\n")

    with pytest.raises(PendingReviewError, match="malformado"):
        generate_pending_review(
            CLEAN, candidates, TERRITORY, CATALOG,
            tables_dir=tmp_path / "outputs/tablas",
            reports_dir=tmp_path / "outputs/reportes",
            project_root=ROOT,
        )

    assert output.read_bytes() == b"salida previa\n"


def test_cli_restringe_salidas_al_directorio_outputs(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("revisar_pendientes_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", ROOT)

    assert module.main(["--tables-dir", str(tmp_path)]) == 1
    assert "debe estar dentro de outputs" in capsys.readouterr().err
