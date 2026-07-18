import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from proyecto1_ds.cleaning import CleaningResult
from proyecto1_ds.enrichment import enrich_result
from proyecto1_ds.territorial import validate_territorial, write_territorial_outputs

_SPEC = importlib.util.spec_from_file_location("catalog_generator", "scripts/generar_catalogo_territorial.py")
assert _SPEC and _SPEC.loader
catalog_generator = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(catalog_generator)


def _catalog_payload() -> bytes:
    departments = []
    municipality_code = 101
    for department_code in range(1, 23):
        count = 16 if department_code <= 10 else 15
        municipalities = [
            {"codigo": str(municipality_code + offset), "nombre": f"Municipio {municipality_code + offset}"}
            for offset in range(count)
        ]
        municipality_code += count
        departments.append(
            {"codigo": str(department_code), "nombre": f"Departamento {department_code}", "municipios": municipalities}
        )
    return json.dumps(departments).encode()


def test_generador_usa_espejo_inmutable_y_publica_catalogo_validado(tmp_path):
    payload = _catalog_payload()
    output = tmp_path / "catalogo.csv"

    catalog_generator.generate_catalog(
        payload,
        output,
        expected_sha256=hashlib.sha256(payload).hexdigest(),
    )

    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert len(rows) == 340
    assert len({row["departamento_codigo"] for row in rows}) == 22
    assert len({row["municipio_codigo"] for row in rows}) == 340
    assert "/main/" not in catalog_generator.SOURCE_URL
    assert catalog_generator.SOURCE_REVISION in catalog_generator.SOURCE_URL
    assert "espejo" in catalog_generator.SOURCE_DESCRIPTION.lower()
    assert "INE" in catalog_generator.PRIMARY_SOURCE


@pytest.mark.parametrize("failure", ["checksum", "schema", "count"])
def test_generador_preserva_catalogo_previo_ante_entrada_invalida(tmp_path, failure):
    payload = _catalog_payload()
    expected_hash = hashlib.sha256(payload).hexdigest()
    if failure == "schema":
        data = json.loads(payload)
        del data[0]["municipios"][0]["codigo"]
        payload = json.dumps(data).encode()
        expected_hash = hashlib.sha256(payload).hexdigest()
    elif failure == "count":
        data = json.loads(payload)[:-1]
        payload = json.dumps(data).encode()
        expected_hash = hashlib.sha256(payload).hexdigest()
    else:
        expected_hash = "0" * 64
    output = tmp_path / "catalogo.csv"
    output.write_bytes(b"catalogo anterior\n")

    with pytest.raises(catalog_generator.CatalogError):
        catalog_generator.generate_catalog(payload, output, expected_sha256=expected_hash)

    assert output.read_bytes() == b"catalogo anterior\n"


def test_enriquecimiento_separa_dos_typos_de_siete_codigos_provisionales():
    pairs = [
        ("QUICHE", "IXCAN"), ("QUICHE", "NEBAJ"), ("ALTA VERAPAZ", "LA TINTA"),
        ("QUETZALTENANGO", "GENOVA COSTA CUCA"), ("ALTA VERAPAZ", "LANQUIN"),
        ("SACATEPEQUEZ", "ALOTENANGO"), ("QUETZALTENANGO", "OLINTEPEQUE"),
        ("QUICHE", "PACHALUN"), ("SUCHITEPEQUEZ", "SAN MIGUEL PANAM"),
    ]
    result = CleaningResult(
        source_path=Path("data/source/fuente.csv"), original_header=["DEPARTAMENTO", "MUNICIPIO"],
        header=["DEPARTAMENTO", "MUNICIPIO"],
        rows=[{"DEPARTAMENTO": department, "MUNICIPIO": municipality} for department, municipality in pairs],
        cleaning_log=[], quality_report=[],
    )

    enriched = enrich_result(result)

    assert sum(row["MUNICIPIO"] != original[1] for row, original in zip(enriched.rows, pairs, strict=True)) == 2
    assert sum(bool(row["municipio_codigo"]) for row in enriched.rows) == 9
    assert sum(log["regla"] == "corregir_municipio_catalogo" for log in enriched.cleaning_log) == 2
    assert "provisionales" in enriched.cleaning_log[-1]["justificacion"]


def test_reporte_conserva_siete_parejas_y_145_filas_pendientes():
    report = validate_territorial(project_root=Path.cwd())

    assert (report.summary["parejas_inconsistentes"], report.summary["filas_inconsistentes"]) == (7, 145)
    assert {row["decision"] for row in report.inconsistencies} == {"revisar"}


def test_reporte_es_byte_estable_entre_raices_y_publicacion_es_conjunta(tmp_path, monkeypatch):
    rendered = []
    for root_name in ("a", "b"):
        root = tmp_path / root_name
        source = root / "data/processed/clean.csv"
        catalog = root / "data/reference/catalog.csv"
        source.parent.mkdir(parents=True)
        catalog.parent.mkdir(parents=True)
        source.write_text("DEPARTAMENTO,MUNICIPIO\nDEP,DESCONOCIDO\n", encoding="utf-8")
        catalog.write_text("departamento,municipio\nDEP,MUNICIPIO\n", encoding="utf-8")
        report = validate_territorial(source, catalog_csv=catalog, project_root=root)
        outputs = write_territorial_outputs(report, tables_dir=root / "outputs/tablas", reports_dir=root / "outputs/reportes")
        rendered.append(outputs.report_path.read_bytes())
        assert str(root).encode() not in rendered[-1]
        report_text = rendered[-1].decode("utf-8")
        assert "espejo/conversión comunitaria" in report_text
        assert "fuente primaria declarada: INE, Censo 2018" in report_text
    assert rendered[0] == rendered[1]

    first_root = tmp_path / "a"
    csv_path = first_root / "outputs/tablas/inconsistencias_territoriales.csv"
    md_path = first_root / "outputs/reportes/validacion_territorial.md"
    previous = (csv_path.read_bytes(), md_path.read_bytes())
    original_replace = Path.replace
    monkeypatch.setattr(Path, "replace", lambda self, target: (_ for _ in ()).throw(OSError("fallo")) if target == md_path else original_replace(self, target))
    with pytest.raises(OSError):
        write_territorial_outputs(report, tables_dir=csv_path.parent, reports_dir=md_path.parent)
    assert (csv_path.read_bytes(), md_path.read_bytes()) == previous
