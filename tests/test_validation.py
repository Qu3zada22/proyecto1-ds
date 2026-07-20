from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.validation import ValidationError, validate_dataset, write_validation_output
from proyecto1_ds.duplicates import apply_duplicate_decisions, detect_partial_duplicates, write_duplicate_outputs
from proyecto1_ds.territorial import validate_territorial, write_territorial_outputs


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validar_dataset.py"
HEADER = [
    "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO", "departamento_codigo",
    "municipio_codigo", "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "SUPERVISOR",
    "DIRECTOR", "NIVEL", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA",
    "PLAN", "DEPARTAMENTAL", "archivo_origen", "departamento_origen",
]


def _write(path: Path, fields: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


def _inputs(root: Path, *, pending: bool = False, dirty: bool = False) -> tuple[Path, ...]:
    clean = root / "data/processed/establecimientos_diversificado_limpio.csv"
    row = ["" for _ in HEADER]
    row[0], row[2], row[3], row[6], row[8] = "01-01", "GUATEMALA", "GUATEMALA", "COLEGIO", "12345678"
    rows = [row, row.copy()] if dirty else [row]
    if dirty:
        rows[1][6] = " COLEGIO"
    duplicates = root / "outputs/tablas/duplicados_parciales.csv"
    territory = root / "outputs/tablas/inconsistencias_territoriales.csv"
    problems = root / "outputs/tablas/problemas_potenciales.csv"
    _write(clean, HEADER, rows)
    _write(duplicates, ["decision"], [["revisar"]] if pending else [])
    _write(territory, ["filas", "decision"], [["2", "revisar"]] if pending else [])
    _write(
        problems, ["columna", "tipo", "conteo"],
        [["TELEFONO", "formato_sospechoso", "3"]] if pending else [],
    )
    return clean, duplicates, territory, problems


def test_evalua_exactamente_siete_controles_con_cumple_revision_y_falla(tmp_path):
    clean = validate_dataset(*_inputs(tmp_path / "clean"))
    review = validate_dataset(*_inputs(tmp_path / "review", pending=True))
    failed = validate_dataset(*_inputs(tmp_path / "failed", dirty=True))

    assert len(clean.rows) == 7
    assert {row["estado"] for row in clean.rows} == {"cumple"}
    assert {row["estado"] for row in review.rows} == {"cumple", "requiere_revision"}
    assert {row["estado"] for row in failed.rows} == {"cumple", "falla"}
    assert [row["control"] for row in clean.rows] == [
        "duplicados_exactos", "espacios_exteriores", "formato_telefonos",
        "catalogo_territorial", "tipos_esperados", "categorias_sin_variantes",
        "valores_invalidos_diagnosticados",
    ]


def test_caso_real_conserva_conteos_y_unidades_explicitas():
    result = validate_dataset(
        ROOT / "data/processed/establecimientos_diversificado_limpio.csv",
        ROOT / "outputs/tablas/duplicados_parciales.csv",
        ROOT / "outputs/tablas/inconsistencias_territoriales.csv",
        ROOT / "outputs/tablas/problemas_potenciales.csv",
    )
    rows = {row["control"]: row for row in result.rows}

    assert (result.source_rows, result.source_columns) == (11_867, 21)
    assert (rows["duplicados_exactos"]["estado"], rows["duplicados_exactos"]["conteo"]) == ("requiere_revision", "989 pares")
    assert "718 duplicado_probable" in rows["duplicados_exactos"]["detalle"]
    assert "271 revisar" in rows["duplicados_exactos"]["detalle"]
    assert rows["formato_telefonos"]["conteo"] == "251 registros"
    assert rows["catalogo_territorial"]["conteo"] == "145 filas"
    assert rows["valores_invalidos_diagnosticados"]["conteo"] == "396 hallazgos"
    assert "251 teléfonos vigentes + 145 filas territoriales" in rows["valores_invalidos_diagnosticados"]["detalle"]
    assert "data/processed/establecimientos_diversificado_limpio.csv" in rows["valores_invalidos_diagnosticados"]["evidencia"]
    assert "201" not in rows["valores_invalidos_diagnosticados"]["detalle"]
    assert "texto" in rows["tipos_esperados"]["detalle"]
    assert all(not Path(item).is_absolute() for row in result.rows for item in row["evidencia"].split("; "))


@pytest.mark.parametrize("phone", ["1234-5678", "1234567", "123456789"])
def test_telefono_invalido_en_limpio_queda_en_revision_aunque_diagnostico_este_vacio(tmp_path, phone):
    paths = _inputs(tmp_path)
    rows = list(csv.reader(paths[0].open(encoding="utf-8", newline="")))
    rows[1][HEADER.index("TELEFONO")] = phone
    _write(paths[0], HEADER, rows[1:])

    result = {row["control"]: row for row in validate_dataset(*paths).rows}

    assert result["formato_telefonos"]["estado"] == "requiere_revision"
    assert result["formato_telefonos"]["conteo"] == "1 registros"


def test_valores_invalidos_incluye_otros_formatos_diagnosticados(tmp_path):
    paths = _inputs(tmp_path)
    _write(paths[3], ["columna", "tipo", "conteo"], [["CODIGO", "formato_sospechoso", "2"]])

    result = {row["control"]: row for row in validate_dataset(*paths).rows}

    assert result["valores_invalidos_diagnosticados"]["conteo"] == "2 hallazgos"


@pytest.mark.parametrize("failure", ["missing", "malformed"])
def test_entrada_invalida_preserva_salida_previa(tmp_path, failure):
    paths = list(_inputs(tmp_path))
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    output.write_bytes(b"salida anterior\n")
    if failure == "missing":
        paths[1].unlink()
    else:
        paths[2].write_text("filas,decision\n1\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        write_validation_output(validate_dataset(*paths), output)

    assert output.read_bytes() == b"salida anterior\n"


def test_dataset_limpio_sin_registros_preserva_salida_previa(tmp_path):
    paths = _inputs(tmp_path)
    _write(paths[0], HEADER, [])
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    output.write_bytes(b"salida anterior\n")

    with pytest.raises(ValidationError, match="sin registros"):
        write_validation_output(validate_dataset(*paths), output)

    assert output.read_bytes() == b"salida anterior\n"


@pytest.mark.parametrize(("evidence", "rows"), [
    ("problems", [["TELEFONO", "formato_sospechoso", "-1"]]),
    ("territory", [["-2", "revisar"]]),
])
def test_rechaza_conteos_negativos_preservando_salida(tmp_path, evidence, rows):
    paths = _inputs(tmp_path)
    target = paths[3] if evidence == "problems" else paths[2]
    fields = ["columna", "tipo", "conteo"] if evidence == "problems" else ["filas", "decision"]
    _write(target, fields, rows)
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    output.write_bytes(b"salida anterior\n")

    with pytest.raises(ValidationError, match="no negativo"):
        write_validation_output(validate_dataset(*paths), output)
    assert output.read_bytes() == b"salida anterior\n"


def test_rechaza_decision_de_duplicado_fuera_de_dominio(tmp_path):
    paths = _inputs(tmp_path)
    _write(paths[1], ["decision"], [["fusionado"]])

    with pytest.raises(ValidationError, match="Decisión inválida"):
        validate_dataset(*paths)


@pytest.mark.parametrize("stale", ["duplicates", "territory"])
def test_evidencia_stale_falla_y_preserva_salida(tmp_path, stale):
    paths, catalog = _coherent_lineage(tmp_path)
    target = paths[1] if stale == "duplicates" else paths[2]
    rows = list(csv.reader(target.open(encoding="utf-8", newline="")))
    if stale == "duplicates":
        rows[1][rows[0].index("establecimiento_a")] = "EVIDENCIA VIEJA"
    else:
        rows.append(["GUATEMALA", "MIXCO", "1", "municipio_desconocido", "", "", "revisar"])
    _write(target, rows[0], rows[1:])
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    output.write_bytes(b"salida anterior\n")

    with pytest.raises(ValidationError, match="stale"):
        write_validation_output(validate_dataset(*paths, catalog_csv=catalog), output)
    assert output.read_bytes() == b"salida anterior\n"


def test_par_duplicado_en_evidencia_falla_y_preserva_salida(tmp_path):
    paths, catalog = _coherent_lineage(tmp_path)
    rows = list(csv.reader(paths[1].open(encoding="utf-8", newline="")))
    _write(paths[1], rows[0], [rows[1], rows[1]])
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    output.write_bytes(b"salida anterior\n")

    with pytest.raises(ValidationError, match="par repetido"):
        write_validation_output(validate_dataset(*paths, catalog_csv=catalog), output)
    assert output.read_bytes() == b"salida anterior\n"


def test_pipeline_detectar_decidir_validar_preserva_decision_manual(tmp_path):
    paths, catalog = _coherent_lineage(tmp_path)
    rows = list(csv.DictReader(paths[1].open(encoding="utf-8", newline="")))
    rows[0]["decision"] = "duplicado_confirmado"
    _write(paths[1], list(rows[0]), [[row[field] for field in rows[0]] for row in rows])

    apply_duplicate_decisions(paths[1])
    result = validate_dataset(*paths, catalog_csv=catalog)

    assert next(csv.DictReader(paths[1].open(encoding="utf-8")))["decision"] == "duplicado_confirmado"
    assert len(result.rows) == 7
    assert "1 duplicado_confirmado" in result.rows[0]["detalle"]


def _coherent_lineage(tmp_path):
    paths = list(_inputs(tmp_path))
    clean_rows = list(csv.reader(paths[0].open(encoding="utf-8", newline="")))
    duplicate = clean_rows[1].copy()
    duplicate[0] = "01-02"
    _write(paths[0], HEADER, [clean_rows[1], duplicate])
    catalog = tmp_path / "data/reference/catalogo_territorial.csv"
    _write(catalog, ["departamento_codigo", "departamento", "municipio_codigo", "municipio"], [["1", "Guatemala", "101", "Guatemala"]])
    write_duplicate_outputs(
        detect_partial_duplicates(paths[0]), tables_dir=paths[1].parent,
        reports_dir=tmp_path / "outputs/reportes", project_root=tmp_path,
    )
    write_territorial_outputs(
        validate_territorial(paths[0], catalog_csv=catalog, project_root=tmp_path),
        tables_dir=paths[2].parent, reports_dir=tmp_path / "outputs/reportes",
    )
    return paths, catalog


def test_salida_es_idempotente_byte_a_byte(tmp_path):
    output = tmp_path / "outputs/tablas/validacion_final.csv"
    result = validate_dataset(*_inputs(tmp_path, pending=True))

    write_validation_output(result, output)
    first = output.read_bytes()
    write_validation_output(result, output)

    assert output.read_bytes() == first


def test_cli_genera_validacion_y_reporta_revisiones(tmp_path, monkeypatch, capsys):
    _inputs(tmp_path, pending=True)
    spec = importlib.util.spec_from_file_location("validar_dataset_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    original_validate = module.validate_dataset
    monkeypatch.setattr(module, "validate_dataset", lambda clean, duplicates, territory, problems, **_kwargs: original_validate(clean, duplicates, territory, problems))

    assert module.main([]) == 0

    output = tmp_path / "outputs/tablas/validacion_final.csv"
    assert output.exists()
    assert "7 controles" in capsys.readouterr().out

    _inputs(tmp_path, dirty=True)
    assert module.main([]) == 1
    assert "1 fallan" in capsys.readouterr().out
