import csv
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

from proyecto1_ds.consolidation import ConsolidationError, consolidate_raw
from proyecto1_ds.manifest import ManifestEntry, checksum_sha256, write_manifest


FIXTURE_RAW = Path(__file__).resolve().parent / "fixtures" / "raw"
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "consolidar_crudos.py"


def _entry(raw_dir: Path, filename: str, *, departamento: str | None, metodo: str = "manual") -> ManifestEntry:
    return ManifestEntry(
        archivo=filename,
        fuente_url="manual" if metodo != "html-form" else "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/",
        fecha_extraccion="2026-07-14",
        version_dataset="v0.1.0",
        cobertura="Diversificado disponible",
        departamento=departamento,
        metodo=metodo,
        checksum_sha256=checksum_sha256(raw_dir / filename),
    )


def _copy_fixture(raw_dir: Path, filename: str) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURE_RAW / filename, raw_dir / filename)


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return reader.fieldnames or [], list(reader)


def test_consolida_csv_compatibles_preservando_valores_y_procedencia(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    _copy_fixture(raw_dir, "establecimientos_compatible_escuintla.csv")
    manifest = [
        _entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala"),
        _entry(raw_dir, "establecimientos_compatible_escuintla.csv", departamento="Escuintla"),
    ]

    result_path = consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert result_path == output_path
    header, rows = _read_rows(output_path)
    assert header == ["codigo", "nombre", "departamento", "archivo_origen", "departamento_origen"]
    assert rows == [
        {
            "codigo": "001",
            "nombre": "Instituto Central",
            "departamento": "Guatemala",
            "archivo_origen": "establecimientos_compatible_guatemala.csv",
            "departamento_origen": "Guatemala",
        },
        {
            "codigo": "002",
            "nombre": "Instituto del Sur",
            "departamento": "Escuintla",
            "archivo_origen": "establecimientos_compatible_escuintla.csv",
            "departamento_origen": "Escuintla",
        },
    ]


def test_reporta_esquema_incompatible_sin_generar_salida_parcial(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    _copy_fixture(raw_dir, "establecimientos_incompatible.csv")
    manifest = [
        _entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala"),
        _entry(raw_dir, "establecimientos_incompatible.csv", departamento="Guatemala"),
    ]

    with pytest.raises(ConsolidationError, match="columnas incompatibles.*establecimientos_incompatible.csv"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


@pytest.mark.parametrize(
    ("filename", "content", "expected"),
    [
        ("ragged_extra.csv", "codigo,nombre\n01,Central,EXTRA\n02,Sur\n", "fila 2 tiene 3 columnas; se esperaban 2"),
        ("ragged_missing.csv", "codigo,nombre\n01,Central\n02\n", "fila 3 tiene 1 columnas; se esperaban 2"),
    ],
)
def test_rechaza_csv_crudo_con_filas_ragged_sin_generar_salida(tmp_path, filename, content, expected):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    (raw_dir / filename).write_text(content, encoding="utf-8")
    manifest = [_entry(raw_dir, filename, departamento="Guatemala")]

    with pytest.raises(ConsolidationError, match=expected):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


def test_conserva_departamento_ambiguo_como_pendiente_para_diagnostico(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_departamento_ambiguo.csv")

    consolidate_raw(
        [_entry(raw_dir, "establecimientos_departamento_ambiguo.csv", departamento=None)],
        raw_dir=raw_dir,
        output_path=output_path,
    )

    _header, rows = _read_rows(output_path)
    assert rows == [
        {
            "codigo": "004",
            "nombre": "Instituto con alcance pendiente",
            "departamento": "",
            "archivo_origen": "establecimientos_departamento_ambiguo.csv",
            "departamento_origen": "pendiente",
        }
    ]


def test_extrae_tabla_html_oficial_sin_limpiar_texto_de_celdas(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "mineduc_busca_establecimiento_diversificado_01.html"
    (raw_dir / html_name).write_text(
        """
        <html><body>
          <table id="_ctl0_ContentPlaceHolder1_dgResultado">
            <tr><td>CODIGO</td><td>ESTABLECIMIENTO</td><td>DIRECCION</td><td>TELEFONO</td></tr>
            <tr><td>01-01-0007-46</td><td>  Instituto Central  </td><td>2A. AVENIDA &quot;A&quot;</td><td>&nbsp;</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    header, rows = _read_rows(output_path)
    assert header == ["CODIGO", "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "archivo_origen", "departamento_origen"]
    assert rows == [
        {
            "CODIGO": "01-01-0007-46",
            "ESTABLECIMIENTO": "  Instituto Central  ",
            "DIRECCION": '2A. AVENIDA "A"',
            "TELEFONO": "\xa0",
            "archivo_origen": html_name,
            "departamento_origen": "GUATEMALA",
        }
    ]


def test_excluye_filas_html_estructurales_sin_datos_reales_preservando_valores_nbsp(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "mineduc_busca_establecimiento_diversificado_footer.html"
    (raw_dir / html_name).write_text(
        """
        <html><body>
          <table id="_ctl0_ContentPlaceHolder1_dgResultado">
            <tr><td>CODIGO</td><td>ESTABLECIMIENTO</td><td>TELEFONO</td></tr>
            <tr><td>01-01-0007-46</td><td>Instituto Central</td><td>&nbsp;</td></tr>
            <tr style="background-color:Gold;"><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    _header, rows = _read_rows(output_path)
    assert rows == [
        {
            "CODIGO": "01-01-0007-46",
            "ESTABLECIMIENTO": "Instituto Central",
            "TELEFONO": "\xa0",
            "archivo_origen": html_name,
            "departamento_origen": "GUATEMALA",
        }
    ]


def test_html_sin_tabla_esperada_reporta_error_y_no_genera_salida(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "sin_tabla.html"
    (raw_dir / html_name).write_text("<html><body><table><tr><td>sin resultados</td></tr></table></body></html>", encoding="utf-8")
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    with pytest.raises(ConsolidationError, match="tabla oficial de resultados.*sin_tabla.html"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


def test_html_truncado_con_fila_abierta_falla_sin_generar_salida(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "mineduc_busca_establecimiento_diversificado_truncado.html"
    (raw_dir / html_name).write_text(
        """
        <html><body>
          <table id="_ctl0_ContentPlaceHolder1_dgResultado">
            <tr><td>CODIGO</td><td>ESTABLECIMIENTO</td></tr>
            <tr><td>01-01-0007-46</td><td>Instituto truncado
        """,
        encoding="utf-8",
    )
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    with pytest.raises(ConsolidationError, match="HTML incompleto.*fila abierta.*truncado"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


def test_html_con_encabezado_sin_filas_y_sin_marcador_oficial_falla_como_parcial(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "mineduc_busca_establecimiento_diversificado_solo_encabezado.html"
    (raw_dir / html_name).write_text(
        """
        <html><body>
          <table id="_ctl0_ContentPlaceHolder1_dgResultado">
            <tr><td>CODIGO</td><td>ESTABLECIMIENTO</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    with pytest.raises(ConsolidationError, match="sin filas de datos.*sin marcador oficial"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


def test_html_con_tabla_vacia_y_marcador_oficial_consolida_departamento_vacio(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    html_name = "mineduc_busca_establecimiento_diversificado_sin_resultados.html"
    (raw_dir / html_name).write_text(
        """
        <html><body>
          <span>No se encontraron registros para los criterios seleccionados.</span>
          <table id="_ctl0_ContentPlaceHolder1_dgResultado">
            <tr><td>CODIGO</td><td>ESTABLECIMIENTO</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )
    manifest = [_entry(raw_dir, html_name, departamento="GUATEMALA", metodo="html-form")]

    consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    header, rows = _read_rows(output_path)
    assert header == ["CODIGO", "ESTABLECIMIENTO", "archivo_origen", "departamento_origen"]
    assert rows == []


def test_valida_checksum_del_manifest_antes_de_consolidar(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    manifest = [_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")]
    (raw_dir / "establecimientos_compatible_guatemala.csv").write_text(
        "codigo,nombre,departamento\n999,Archivo alterado,Guatemala\n",
        encoding="utf-8",
    )

    with pytest.raises(ConsolidationError, match="checksum_sha256.*establecimientos_compatible_guatemala.csv"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert not output_path.exists()


def test_escritura_csv_es_atomica_y_preserva_salida_existente_si_falla(tmp_path, monkeypatch):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("contenido,previo\nno,destruir\n", encoding="utf-8")
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    manifest = [_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")]

    def fail_after_header(self, rowdicts):
        raise RuntimeError("fallo simulado durante escritura")

    monkeypatch.setattr(csv.DictWriter, "writerows", fail_after_header)

    with pytest.raises(RuntimeError, match="fallo simulado"):
        consolidate_raw(manifest, raw_dir=raw_dir, output_path=output_path)

    assert output_path.read_text(encoding="utf-8") == "contenido,previo\nno,destruir\n"
    assert not list(output_path.parent.glob(f".{output_path.name}.*.tmp"))


def test_cli_consolida_desde_manifest_publico(tmp_path, capsys):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    write_manifest([_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")], raw_dir / "manifest.json")
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--output-file", str(output_path)])

    assert exit_code == 0
    assert output_path.exists()
    assert "Dataset intermedio generado" in capsys.readouterr().out


def test_cli_rechaza_output_file_fuera_de_data_interim(tmp_path, capsys):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "fuera.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    write_manifest([_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")], raw_dir / "manifest.json")
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--output-file", str(output_path)])

    assert exit_code == 1
    assert not output_path.exists()
    assert "data/interim" in capsys.readouterr().err


def test_cli_rechaza_raw_dir_fuera_de_data_raw(tmp_path, capsys):
    raw_dir = tmp_path / "fuera" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    write_manifest([_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")], raw_dir / "manifest.json")
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--output-file", str(output_path)])

    assert exit_code == 1
    assert "data/raw" in capsys.readouterr().err
    assert not output_path.exists()


def test_cli_rechaza_manifest_fuera_de_data_raw(tmp_path, capsys):
    raw_dir = tmp_path / "data" / "raw"
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    manifest_path = tmp_path / "manifest.json"
    _copy_fixture(raw_dir, "establecimientos_compatible_guatemala.csv")
    write_manifest([_entry(raw_dir, "establecimientos_compatible_guatemala.csv", departamento="Guatemala")], manifest_path)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--manifest", str(manifest_path), "--output-file", str(output_path)])

    assert exit_code == 1
    assert "data/raw" in capsys.readouterr().err
    assert not output_path.exists()


def test_cli_reporta_manifest_json_invalido_sin_traceback(tmp_path, capsys):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    manifest_path = raw_dir / "manifest.json"
    manifest_path.write_text("{manifest inválido", encoding="utf-8")
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--manifest", str(manifest_path), "--output-file", str(output_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error de consolidación" in captured.err
    assert "manifest" in captured.err
    assert "Traceback" not in captured.err
    assert not output_path.exists()


def test_cli_reporta_schema_de_manifest_invalido_sin_traceback(tmp_path, capsys):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    manifest_path = raw_dir / "manifest.json"
    manifest_path.write_text(json.dumps({"lotes": [{"archivo": "sin_campos.csv"}]}), encoding="utf-8")
    output_path = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--raw-dir", str(raw_dir), "--manifest", str(manifest_path), "--output-file", str(output_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error de consolidación" in captured.err
    assert "manifest" in captured.err
    assert "Traceback" not in captured.err
    assert not output_path.exists()


def _load_cli_module():
    spec = importlib.util.spec_from_file_location("consolidar_crudos_cli", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
