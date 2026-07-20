import csv
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.cleaning import DEFAULT_SOURCE_CSV, CleaningOutputError


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "limpiar_dataset.py"


def test_cli_expone_source_csv_sin_alias_interim(tmp_path):
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    parser = cli.build_parser()
    args = parser.parse_args([])
    assert DEFAULT_SOURCE_CSV == Path("data/source/establecimientos_diversificado_mineduc.csv")
    assert args.source_csv == tmp_path / DEFAULT_SOURCE_CSV
    assert "--" + "interim" + "-csv" not in parser.format_help()


def _load_cli_module():
    spec = importlib.util.spec_from_file_location("limpiar_dataset_cli", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_interim_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["CODIGO", "DIRECTOR", "DEPARTAMENTO", "MUNICIPIO", "\xa0"])
        writer.writerow(["001", " SIN DATO ", "GUATEMALA", "GUATEMALA", ""])


def _write_valid_catalog(root: Path) -> None:
    catalog = root / "data" / "reference" / "catalogo_territorial.csv"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    with catalog.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["departamento_codigo", "departamento", "municipio_codigo", "municipio"])
        writer.writerow(["1", "Guatemala", "101", "Guatemala"])


def test_cli_limpia_fuente_default_y_escribe_salidas_permitidas(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    _write_valid_catalog(tmp_path)
    original_interim = interim_csv.read_bytes()
    cli = _load_cli_module()
    cli.ROOT = tmp_path
    integral = tmp_path / "outputs/tablas/reporte_calidad_antes_despues.csv"
    integral.parent.mkdir(parents=True)
    integral.write_bytes(b"reporte integral previo\n")

    exit_code = cli.main([])

    captured = capsys.readouterr()
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    assert exit_code == 0
    assert "Dataset limpio generado" in captured.out
    assert captured.err == ""
    assert interim_csv.read_bytes() == original_interim
    assert clean_csv.exists()
    assert (tables_dir / "bitacora_limpieza.csv").exists()
    assert (tables_dir / "reporte_limpieza_base.csv").exists()
    assert integral.read_bytes() == b"reporte integral previo\n"


def test_cli_reporta_entrada_ausente_sin_traceback_ni_parciales(tmp_path, capsys):
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error de limpieza" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "data" / "processed").exists()
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_cli_reporta_catalogo_ausente_con_fuente_valida_sin_escribir_parciales(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    original_interim = interim_csv.read_bytes()
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "catálogo territorial" in captured.err
    assert "Traceback" not in captured.err
    assert interim_csv.read_bytes() == original_interim
    assert not (tmp_path / "data" / "processed").exists()
    assert not (tmp_path / "outputs" / "tablas").exists()


@pytest.mark.parametrize(
    "catalog_rows",
    [
        [["departamento_codigo", "departamento", "municipio_codigo", "municipio"]],
        [["departamento", "municipio"], ["Guatemala", "Guatemala"]],
        [["departamento_codigo", "departamento", "municipio_codigo", "municipio"],
         ["2", "El Progreso", "201", "Guastatoya"]],
        [["departamento_codigo", "departamento", "municipio_codigo", "municipio"], ["", "Guatemala", "101", "Guatemala"]],
        [["departamento_codigo", "departamento", "municipio_codigo", "municipio"],
         ["1", "Guatemala", "101", "Guatemala"], ["2", "El Progreso", "101", "Guastatoya"]],
        [["departamento_codigo", "departamento", "municipio_codigo", "municipio"],
         ["1", "Guatemala", "101", "Guatemala"], ["2", "Guatemala", "102", "Mixco"]],
    ],
    ids=["solo-encabezado", "esquema-invalido", "cobertura-incompleta", "codigo-vacio", "codigo-duplicado", "departamento-ambiguo"],
)
def test_cli_rechaza_catalogo_invalido_sin_alterar_fuente_ni_salidas(tmp_path, capsys, catalog_rows):
    source = tmp_path / "data/source/establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(source)
    catalog = tmp_path / "data/reference/catalogo_territorial.csv"
    catalog.parent.mkdir(parents=True)
    with catalog.open("w", newline="", encoding="utf-8") as csv_file:
        csv.writer(csv_file).writerows(catalog_rows)
    outputs = [
        tmp_path / "data/processed/establecimientos_diversificado_limpio.csv",
        tmp_path / "outputs/tablas/bitacora_limpieza.csv",
        tmp_path / "outputs/tablas/reporte_limpieza_base.csv",
    ]
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"salida previa\n")
    source_before = source.read_bytes()
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    assert cli.main([]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "catálogo territorial" in captured.err.lower()
    assert "Traceback" not in captured.err
    assert source.read_bytes() == source_before
    assert [output.read_bytes() for output in outputs] == [b"salida previa\n"] * 3


def test_cli_restringe_entrada_a_data_source_y_salidas_a_raices_permitidas(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    outside_interim = tmp_path / "outside" / "source.csv"
    _write_interim_csv(outside_interim)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    rejected_interim = cli.main(["--source-csv", str(outside_interim)])
    rejected_output = cli.main(["--output-file", str(tmp_path / "data" / "escape.csv")])
    rejected_tables = cli.main(["--tables-dir", str(tmp_path / "outputs" / "other")])

    captured = capsys.readouterr()
    assert rejected_interim == 1
    assert rejected_output == 1
    assert rejected_tables == 1
    assert "data/source" in captured.err
    assert "data/processed" in captured.err
    assert "outputs/tablas" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "data" / "escape.csv").exists()
    assert not (tmp_path / "outputs" / "other").exists()


def test_cli_rechaza_data_source_symlink_a_directorio_externo_sin_crear_salidas(tmp_path, capsys):
    outside_interim = tmp_path / "outside" / "source"
    outside_csv = outside_interim / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(outside_csv)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    symlinked_interim = data_dir / "source"
    symlinked_interim.symlink_to(outside_interim, target_is_directory=True)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--source-csv", str(symlinked_interim / outside_csv.name)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error de limpieza" in captured.err
    assert "data/source" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "data" / "processed").exists()
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_cli_argumento_desconocido_devuelve_exit_1_con_uso_sin_traceback(tmp_path, capsys):
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    rejected_cases = [["--desconocido"], ["--output-file"]]

    for invalid_argv in rejected_cases:
        exit_code = cli.main(invalid_argv)

        captured = capsys.readouterr()
        assert exit_code == 1
        assert captured.out == ""
        assert "usage:" in captured.err
        assert invalid_argv[0] in captured.err
        assert "Traceback" not in captured.err
        assert not (tmp_path / "data" / "processed").exists()
        assert not (tmp_path / "outputs" / "tablas").exists()


def test_cli_rechaza_data_processed_como_archivo_de_salida_sin_crear_directorio(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--output-file", str(tmp_path / "data" / "processed")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error de limpieza" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "data" / "processed").exists()
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_cli_rechaza_directorio_existente_como_archivo_de_salida_sin_mutarlo(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    processed_root = tmp_path / "data" / "processed"
    processed_root.mkdir(parents=True)
    nested_output_dir = processed_root / "salida_existente"
    nested_output_dir.mkdir()
    marker = nested_output_dir / "marker.txt"
    marker.write_text("preservar directorio", encoding="utf-8")
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    root_exit_code = cli.main(["--output-file", str(processed_root)])
    nested_exit_code = cli.main(["--output-file", str(nested_output_dir)])

    captured = capsys.readouterr()
    assert root_exit_code == 1
    assert nested_exit_code == 1
    assert captured.out == ""
    assert "Error de limpieza" in captured.err
    assert "Traceback" not in captured.err
    assert processed_root.is_dir()
    assert nested_output_dir.is_dir()
    assert marker.read_text(encoding="utf-8") == "preservar directorio"
    assert not list(processed_root.glob(".*.backup"))
    assert not list(processed_root.glob(".*.tmp"))
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_cli_permite_archivo_csv_valido_bajo_data_processed(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    _write_valid_catalog(tmp_path)
    clean_csv = tmp_path / "data" / "processed" / "custom_clean.csv"
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--output-file", str(clean_csv)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dataset limpio generado" in captured.out
    assert captured.err == ""
    assert clean_csv.is_file()
    assert (tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv").exists()
    assert (tmp_path / "outputs" / "tablas" / "reporte_limpieza_base.csv").exists()


def test_cli_reporta_error_de_escritura_sin_traceback(tmp_path, capsys, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    _write_valid_catalog(tmp_path)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    def fail_write_cleaning_outputs(*_args, **_kwargs):
        raise CleaningOutputError("recuperación manual requerida")

    monkeypatch.setattr(cli, "write_cleaning_outputs", fail_write_cleaning_outputs)

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "recuperación manual requerida" in captured.err
    assert "Traceback" not in captured.err
