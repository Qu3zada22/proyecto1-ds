"""Pruebas para apply_duplicate_decisions (reglas de Anggie, R5g)."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.duplicates import (
    CANDIDATE_FIELDS,
    DEFAULT_CANDIDATES_CSV,
    DecisionSummary,
    DuplicatesCsvError,
    apply_duplicate_decisions,
    detect_partial_duplicates,
    write_duplicate_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DECISION_SCRIPT = ROOT / "scripts" / "decidir_duplicados.py"


def _write_candidates(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANDIDATE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_decision_cli():
    spec = importlib.util.spec_from_file_location("decidir_duplicados_cli", DECISION_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_clean_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "CODIGO", "DEPARTAMENTO", "MUNICIPIO", "ESTABLECIMIENTO", "DIRECCION",
        "TELEFONO", "SECTOR", "MODALIDAD", "JORNADA", "PLAN",
    ]
    rows = [
        ["01", "GUATEMALA", "GUATEMALA", "COLEGIO A", "CALLE 1", "11111111", "PRIVADO", "MONOLINGUE", "MATUTINA", "DIARIO"],
        ["02", "GUATEMALA", "GUATEMALA", "COLEGIO A", "CALLE 1", "11111111", "PRIVADO", "MONOLINGUE", "MATUTINA", "DIARIO"],
        ["03", "GUATEMALA", "GUATEMALA", "COLEGIO B", "CALLE 2", "22222222", "PRIVADO", "MONOLINGUE", "MATUTINA", "DIARIO"],
        ["04", "GUATEMALA", "GUATEMALA", "COLEGIO B", "CALLE 2", "33333333", "PRIVADO", "MONOLINGUE", "MATUTINA", "DIARIO"],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


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


@pytest.mark.parametrize("header", [
    CANDIDATE_FIELDS[:-1],
    [*CANDIDATE_FIELDS[:-1], CANDIDATE_FIELDS[0]],
    [CANDIDATE_FIELDS[1], CANDIDATE_FIELDS[0], *CANDIDATE_FIELDS[2:]],
])
def test_csv_candidatos_rechaza_encabezado_no_canonico_sin_publicar(tmp_path, header):
    csv_path = tmp_path / "candidatos.csv"
    csv_path.write_text(",".join(header) + "\n", encoding="utf-8")
    previous = csv_path.read_bytes()

    with pytest.raises(DuplicatesCsvError):
        apply_duplicate_decisions(csv_path)

    assert csv_path.read_bytes() == previous


def test_modifica_decision_previa(tmp_path):
    csv_path = tmp_path / "candidatos.csv"
    row = _make_candidate("alta", "55551111", "55551111", decision="revisar")
    _write_candidates(csv_path, [row])

    apply_duplicate_decisions(csv_path)

    rows = _read_candidates(csv_path)
    assert rows[0]["decision"] == "duplicado_probable"


def test_deteccion_regenerada_aplica_triage_y_reporta_decisiones_con_ruta_portable(tmp_path):
    source = tmp_path / "data" / "processed" / "establecimientos.csv"
    _write_clean_source(source)
    report = detect_partial_duplicates(source)

    outputs = write_duplicate_outputs(
        report,
        tables_dir=tmp_path / "outputs" / "tablas",
        reports_dir=tmp_path / "outputs" / "reportes",
        project_root=tmp_path,
    )

    decisions = [row["decision"] for row in _read_candidates(outputs.candidates_path)]
    markdown = outputs.report_path.read_text(encoding="utf-8")
    assert decisions == ["duplicado_probable", "independiente"]
    assert "Duplicado probable: 1" in markdown
    assert "Independiente: 1" in markdown
    assert "Revisión institucional/manual pendiente: 0" in markdown
    assert str(tmp_path) not in markdown
    assert "data/processed/establecimientos.csv" in markdown


def test_deteccion_preserva_decision_vigente_por_identidad_del_par(tmp_path):
    source = tmp_path / "data" / "processed" / "establecimientos.csv"
    _write_clean_source(source)
    report = detect_partial_duplicates(source)
    tables_dir = tmp_path / "outputs" / "tablas"
    reports_dir = tmp_path / "outputs" / "reportes"
    outputs = write_duplicate_outputs(
        report, tables_dir=tables_dir, reports_dir=reports_dir, project_root=tmp_path
    )
    rows = _read_candidates(outputs.candidates_path)
    rows[0]["decision"] = "duplicado_confirmado"
    rows[1]["decision"] = "revisar"
    _write_candidates(outputs.candidates_path, rows)

    write_duplicate_outputs(
        detect_partial_duplicates(source),
        tables_dir=tables_dir,
        reports_dir=reports_dir,
        project_root=tmp_path,
    )

    decisions = [row["decision"] for row in _read_candidates(outputs.candidates_path)]
    assert decisions == ["duplicado_confirmado", "independiente"]


@pytest.mark.parametrize("manual", ["duplicado_confirmado", "independiente_confirmado", "revisar_institucional"])
def test_decidir_preserva_dominio_manual_cerrado(tmp_path, manual):
    path = tmp_path / "candidatos.csv"
    _write_candidates(path, [_make_candidate("alta", decision=manual)])

    apply_duplicate_decisions(path)

    assert _read_candidates(path)[0]["decision"] == manual


def test_decidir_rechaza_decision_manual_ambigua_sin_publicar(tmp_path):
    path = tmp_path / "candidatos.csv"
    _write_candidates(path, [_make_candidate("alta", decision="validacion_institucional")])
    previous = path.read_bytes()

    with pytest.raises(DuplicatesCsvError, match="Decisión inválida"):
        apply_duplicate_decisions(path)
    assert path.read_bytes() == previous


def test_publicacion_mantiene_destino_canonico_presente(tmp_path, monkeypatch):
    import proyecto1_ds.duplicates as duplicates

    path = tmp_path / "candidatos.csv"
    _write_candidates(path, [_make_candidate("alta")])
    original_replace = duplicates.Path.replace

    def assert_destination_present(source, target):
        if source.name.endswith(".tmp"):
            assert target.exists()
        return original_replace(source, target)

    monkeypatch.setattr(duplicates.Path, "replace", assert_destination_present)
    apply_duplicate_decisions(path)


def test_fallo_en_segundo_temporal_no_borra_salidas_previas(tmp_path, monkeypatch):
    import proyecto1_ds.duplicates as duplicates

    candidates = tmp_path / "candidatos.csv"
    log = tmp_path / "bitacora.csv"
    _write_candidates(candidates, [_make_candidate("alta")])
    log.write_bytes(b"bitacora anterior\n")
    previous = {candidates: candidates.read_bytes(), log: log.read_bytes()}
    original_write = duplicates.Path.write_bytes

    def fail_second_temporary(path, content):
        if path.name.startswith(".bitacora.csv.") and path.name.endswith(".tmp"):
            raise OSError("segundo temporal bloqueado")
        return original_write(path, content)

    monkeypatch.setattr(duplicates.Path, "write_bytes", fail_second_temporary)

    with pytest.raises(OSError, match="segundo temporal bloqueado"):
        apply_duplicate_decisions(candidates, bitacora_csv=log)
    assert {path: path.read_bytes() for path in previous} == previous


def test_cli_decision_es_idempotente_en_csv_y_bitacora(tmp_path, monkeypatch):
    cli = _load_decision_cli()
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    candidates = tmp_path / "outputs" / "tablas" / "duplicados_parciales.csv"
    _write_candidates(candidates, [_make_candidate("alta")])

    assert cli.main([]) == 0
    first = {
        candidates: candidates.read_bytes(),
        tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv": (
            tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv"
        ).read_bytes(),
    }
    assert cli.main([]) == 0

    assert {path: path.read_bytes() for path in first} == first
    with (tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert [row["regla"] for row in rows] == ["decidir_duplicados"]


def test_cli_decision_restaura_salidas_si_falla_segunda_publicacion(tmp_path, monkeypatch, capsys):
    import proyecto1_ds.duplicates as duplicates

    cli = _load_decision_cli()
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    candidates = tmp_path / "outputs" / "tablas" / "duplicados_parciales.csv"
    bitacora = tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv"
    _write_candidates(candidates, [_make_candidate("media", "11111111", "22222222")])
    bitacora.write_text(
        "variable,regla,filas_afectadas,justificacion,riesgo,evidencia_fuente\n"
        "BASE,conservar,1,evidencia previa,bajo,fuente\n",
        encoding="utf-8",
    )
    previous = {candidates: candidates.read_bytes(), bitacora: bitacora.read_bytes()}
    original_replace = duplicates.Path.replace

    def fail_second_publication(path, target):
        if path.name.startswith(".bitacora_limpieza.csv.") and path.name.endswith(".tmp"):
            raise OSError("segunda publicación bloqueada")
        return original_replace(path, target)

    monkeypatch.setattr(duplicates.Path, "replace", fail_second_publication)

    assert cli.main([]) == 1

    assert {path: path.read_bytes() for path in previous} == previous
    assert "segunda publicación bloqueada" in capsys.readouterr().err
