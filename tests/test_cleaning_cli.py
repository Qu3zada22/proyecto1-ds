import csv
import importlib.util
from pathlib import Path

from proyecto1_ds.cleaning import CleaningOutputError


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "limpiar_dataset.py"


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
        writer.writerow(["CODIGO", "DIRECTOR", "\xa0"])
        writer.writerow(["001", " SIN DATO ", ""])


def test_cli_limpia_interim_default_y_escribe_salidas_permitidas(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_interim_csv(interim_csv)
    original_interim = interim_csv.read_bytes()
    cli = _load_cli_module()
    cli.ROOT = tmp_path

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
    assert (tables_dir / "reporte_calidad_antes_despues.csv").exists()


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


def test_cli_restringe_entrada_a_data_interim_y_salidas_a_raices_permitidas(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_interim_csv(interim_csv)
    outside_interim = tmp_path / "outside" / "source.csv"
    _write_interim_csv(outside_interim)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    rejected_interim = cli.main(["--interim-csv", str(outside_interim)])
    rejected_output = cli.main(["--output-file", str(tmp_path / "data" / "escape.csv")])
    rejected_tables = cli.main(["--tables-dir", str(tmp_path / "outputs" / "other")])

    captured = capsys.readouterr()
    assert rejected_interim == 1
    assert rejected_output == 1
    assert rejected_tables == 1
    assert "data/interim" in captured.err
    assert "data/processed" in captured.err
    assert "outputs/tablas" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "data" / "escape.csv").exists()
    assert not (tmp_path / "outputs" / "other").exists()


def test_cli_rechaza_data_interim_symlink_a_directorio_externo_sin_crear_salidas(tmp_path, capsys):
    outside_interim = tmp_path / "outside" / "interim"
    outside_csv = outside_interim / "establecimientos_diversificado_raw_unificado.csv"
    _write_interim_csv(outside_csv)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    symlinked_interim = data_dir / "interim"
    symlinked_interim.symlink_to(outside_interim, target_is_directory=True)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--interim-csv", str(symlinked_interim / outside_csv.name)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error de limpieza" in captured.err
    assert "data/interim" in captured.err
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
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
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
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
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
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_interim_csv(interim_csv)
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
    assert (tmp_path / "outputs" / "tablas" / "reporte_calidad_antes_despues.csv").exists()


def test_cli_reporta_error_de_escritura_sin_traceback(tmp_path, capsys, monkeypatch):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_interim_csv(interim_csv)
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
