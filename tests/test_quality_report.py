from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.quality_report import QualityReportError, build_quality_report, write_quality_report
from proyecto1_ds.validation import validate_dataset


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generar_reporte_calidad.py"
METRICS = [
    "registros", "variables", "valores_faltantes", "variables_con_na",
    "duplicados_exactos", "posibles_duplicados", "formatos_inconsistentes",
    "tipos_incorrectos", "categorias_inconsistentes", "errores_corregidos",
]


def _write(path: Path, fields: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


def _inputs(root: Path) -> tuple[Path, ...]:
    paths = (
        root / "data/source/establecimientos_diversificado_mineduc.csv",
        root / "data/processed/establecimientos_diversificado_limpio.csv",
        root / "outputs/tablas/problemas_potenciales.csv", root / "outputs/tablas/bitacora_limpieza.csv",
        root / "outputs/tablas/duplicados_parciales.csv", root / "outputs/tablas/inconsistencias_territoriales.csv",
        root / "outputs/tablas/validacion_final.csv", root / "outputs/tablas/duplicados_exactos.csv",
    )
    _write(paths[0], ["CODIGO", "TELEFONO", "CATEGORIA"], [["01", "-", "A"], ["02", "", "A"]])
    _write(paths[1], ["CODIGO", "TELEFONO", "CATEGORIA", "codigo_derivado"], [["01", "123", "A", "1"], ["02", "", "A", "2"]])
    _write(paths[2], ["columna", "tipo", "conteo"], [["TELEFONO", "formato_sospechoso", "1"]])
    _write(paths[3], ["variable", "regla", "filas_afectadas"], [["TELEFONO", "normalizar_marcador_ausencia", "1"]])
    _write(paths[4], ["decision"], [["revisar"]])
    _write(paths[5], ["filas", "decision"], [["2", "revisar"]])
    _refresh_validation(paths)
    _write(paths[7], ["firma_fila", "repeticiones_adicionales"], [])
    return paths


def _refresh_validation(paths: tuple[Path, ...] | list[Path]) -> None:
    result = validate_dataset(paths[1], paths[4], paths[5], paths[2])
    _write(paths[6], ["control", "estado", "conteo", "detalle"], [
        [row["control"], row["estado"], row["conteo"], row["detalle"]] for row in result.rows
    ])


def test_reporte_contiene_cada_metrica_exigida_una_vez(tmp_path):
    result = build_quality_report(*_inputs(tmp_path))

    assert [row["metrica"] for row in result] == METRICS
    assert len({row["metrica"] for row in result}) == 10
    assert all(row["unidad"] and row["interpretacion"] and row["evidencia"] for row in result)


def test_caso_real_publica_conteos_por_unidad_y_porcentajes_reproducibles():
    result = {row["metrica"]: row for row in build_quality_report(
        ROOT / "data/source/establecimientos_diversificado_mineduc.csv",
        ROOT / "data/processed/establecimientos_diversificado_limpio.csv",
        ROOT / "outputs/tablas/problemas_potenciales.csv",
        ROOT / "outputs/tablas/bitacora_limpieza.csv",
        ROOT / "outputs/tablas/duplicados_parciales.csv",
        ROOT / "outputs/tablas/inconsistencias_territoriales.csv",
        ROOT / "outputs/tablas/validacion_final.csv",
        ROOT / "outputs/tablas/duplicados_exactos.csv",
    )}

    assert (result["registros"]["antes"], result["registros"]["despues"]) == ("11867", "11867")
    assert (result["variables"]["antes"], result["variables"]["despues"]) == ("20", "21")
    assert (result["valores_faltantes"]["antes"], result["valores_faltantes"]["despues"]) == ("15796 (6.66%)", "3929 (1.58%)")
    assert (result["variables_con_na"]["antes"], result["variables_con_na"]["despues"]) == ("7", "6")
    assert result["duplicados_exactos"]["despues"] == "0"
    assert result["posibles_duplicados"]["despues"] == "1355 (0 fusionados; 718 probable; 260 revisar; 0 duplicado confirmado; 11 independiente confirmado)"
    assert result["formatos_inconsistentes"]["despues"] == "1 variables; 0 categorías (245 registros TELEFONO; 0 campos exteriores)"
    assert result["tipos_incorrectos"]["despues"] == "0"
    assert result["categorias_inconsistentes"]["despues"] == "0"
    assert "3929 ausencias" in result["errores_corregidos"]["despues"]
    assert "6 teléfonos aprobados" in result["errores_corregidos"]["despues"]
    assert "145 filas territoriales" in result["categorias_inconsistentes"]["interpretacion"]


@pytest.mark.parametrize("failure", ["missing", "malformed"])
def test_entrada_invalida_preserva_salida_previa(tmp_path, failure):
    inputs = list(_inputs(tmp_path))
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    output.write_bytes(b"reporte anterior\n")
    if failure == "missing":
        inputs[4].unlink()
    else:
        inputs[6].write_text("control,estado\nfila\n", encoding="utf-8")

    with pytest.raises(QualityReportError):
        write_quality_report(build_quality_report(*inputs), output)

    assert output.read_bytes() == b"reporte anterior\n"


def test_reporte_es_idempotente_byte_a_byte(tmp_path):
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    result = build_quality_report(*_inputs(tmp_path))
    write_quality_report(result, output)
    first = output.read_bytes()

    write_quality_report(result, output)

    assert output.read_bytes() == first


@pytest.mark.parametrize("dataset", ["source", "clean"])
def test_rechaza_dataset_final_header_only_preservando_reporte(tmp_path, dataset):
    inputs = list(_inputs(tmp_path))
    target = inputs[0] if dataset == "source" else inputs[1]
    header = next(csv.reader(target.open(encoding="utf-8", newline="")))
    _write(target, header, [])
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    output.write_bytes(b"reporte anterior\n")

    with pytest.raises(QualityReportError, match="sin registros"):
        write_quality_report(build_quality_report(*inputs), output)
    assert output.read_bytes() == b"reporte anterior\n"


def test_rechaza_conteos_negativos_y_diferencia_de_registros(tmp_path):
    inputs = list(_inputs(tmp_path))
    _write(inputs[3], ["variable", "regla", "filas_afectadas"], [["TELEFONO", "normalizar_marcador_ausencia", "-1"]])
    with pytest.raises(QualityReportError, match="no negativo"):
        build_quality_report(*inputs)

    inputs = list(_inputs(tmp_path / "rows"))
    clean = list(csv.reader(inputs[1].open(encoding="utf-8", newline="")))
    _write(inputs[1], clean[0], clean[1:2])
    _refresh_validation(inputs)
    with pytest.raises(QualityReportError, match="conservar el mismo número de registros"):
        build_quality_report(*inputs)


def test_reporte_rechaza_controles_ausentes_o_evidencia_incoherente(tmp_path):
    inputs = list(_inputs(tmp_path))
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    output.write_bytes(b"reporte anterior\n")
    rows = list(csv.reader(inputs[6].open(encoding="utf-8", newline="")))
    _write(inputs[6], rows[0], rows[1:-1])

    with pytest.raises(QualityReportError, match="controles"):
        write_quality_report(build_quality_report(*inputs), output)
    assert output.read_bytes() == b"reporte anterior\n"

    _refresh_validation(inputs)
    _write(inputs[5], ["filas", "decision"], [["3", "revisar"]])
    with pytest.raises(QualityReportError, match="incoherente"):
        build_quality_report(*inputs)


def test_rechaza_duplicados_exactos_stale_preservando_reporte(tmp_path):
    inputs = list(_inputs(tmp_path))
    source = list(csv.reader(inputs[0].open(encoding="utf-8", newline="")))
    clean = list(csv.reader(inputs[1].open(encoding="utf-8", newline="")))
    _write(inputs[0], source[0], [*source[1:], source[1]])
    _write(inputs[1], clean[0], [*clean[1:], clean[1]])
    _refresh_validation(inputs)
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    output.write_bytes(b"reporte anterior\n")

    with pytest.raises(QualityReportError, match="duplicados exactos.*stale"):
        write_quality_report(build_quality_report(*inputs), output)
    assert output.read_bytes() == b"reporte anterior\n"


def test_rechaza_bitacora_stale_preservando_reporte(tmp_path):
    inputs = list(_inputs(tmp_path))
    rows = list(csv.reader(inputs[3].open(encoding="utf-8", newline="")))
    rows[1][2] = "999"
    _write(inputs[3], rows[0], rows[1:])
    output = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    output.write_bytes(b"reporte anterior\n")

    with pytest.raises(QualityReportError, match="bitácora.*stale"):
        write_quality_report(build_quality_report(*inputs), output)
    assert output.read_bytes() == b"reporte anterior\n"


def test_metricas_posteriores_usan_conteos_reales_y_texto_dinamico(tmp_path):
    inputs = list(_inputs(tmp_path))
    clean = list(csv.reader(inputs[1].open(encoding="utf-8", newline="")))
    clean[1][1] = "12-3"
    clean[1][2] = " A"
    _write(inputs[1], clean[0], clean[1:])
    _refresh_validation(inputs)

    report = {row["metrica"]: row for row in build_quality_report(*inputs)}
    type_count = next(row for row in csv.DictReader(inputs[6].open(encoding="utf-8", newline="")) if row["control"] == "tipos_esperados")["conteo"].split()[0]
    assert report["tipos_incorrectos"]["despues"] == type_count
    assert report["formatos_inconsistentes"]["despues"].startswith("2 variables; 0 categorías")
    assert report["registros"]["interpretacion"] == "No se agregaron ni eliminaron establecimientos."


def test_interpretacion_de_duplicados_deriva_pendientes_sin_hardcode(tmp_path):
    inputs = list(_inputs(tmp_path))
    _write(inputs[4], ["decision"], [["duplicado_probable"], ["revisar"], ["revisar_institucional"]])
    _refresh_validation(inputs)

    report = {row["metrica"]: row for row in build_quality_report(*inputs)}

    assert "3 pares requieren" in report["posibles_duplicados"]["interpretacion"]


def test_cli_genera_reporte_integral(tmp_path, monkeypatch, capsys):
    _inputs(tmp_path)
    spec = importlib.util.spec_from_file_location("quality_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main([]) == 0
    assert "10 métricas" in capsys.readouterr().out
    assert (tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv").exists()
