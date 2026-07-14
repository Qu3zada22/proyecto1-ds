import importlib.util
from pathlib import Path

from proyecto1_ds.acquisition import AcquisitionError


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "adquirir_datos.py"


def load_cli_module():
    spec = importlib.util.spec_from_file_location("adquirir_datos_cli", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_parser_expone_contrato_publico():
    cli = load_cli_module()

    args = cli.build_parser().parse_args(
        [
            "--source-url",
            "https://www.mineduc.gob.gt/establecimientos.csv",
            "--output-file",
            "establecimientos.csv",
            "--manual-file",
            "manual.csv",
            "--fecha-extraccion",
            "2026-07-13",
            "--version-dataset",
            "v0.1.0",
            "--cobertura",
            "disponible: Guatemala",
            "--alcance-faltante",
            "faltante: otros departamentos",
            "--departamento",
            "Guatemala",
            "--confirm-overwrite",
        ]
    )

    assert args.raw_dir == cli.ROOT / "data/raw"
    assert args.manual_file == ["manual.csv"]
    assert args.confirm_overwrite is True
    assert args.alcance_faltante == "faltante: otros departamentos"


def test_parser_expone_recaptura_html_mineduc_por_departamento():
    cli = load_cli_module()

    args = cli.build_parser().parse_args(
        [
            "--capture-html",
            "--department-code",
            "01",
            "--department-name",
            "GUATEMALA",
            "--output-file",
            "guatemala.html",
        ]
    )

    assert args.capture_html is True
    assert args.department_code == "01"
    assert args.department_name == "GUATEMALA"
    assert args.output_file == "guatemala.html"


def test_cli_missing_manual_file_falla_sin_traceback(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    monkeypatch.setattr(cli, "ROOT", tmp_path)

    exit_code = cli.main(["--manual-file", "missing.csv"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error de adquisición" in captured.err
    assert "missing.csv" in captured.err
    assert "Traceback" not in captured.err


def test_cli_propaga_confirmacion_de_sobrescritura(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    captured_calls = {}

    def fake_acquire(raw_dir, **kwargs):
        captured_calls["raw_dir"] = raw_dir
        captured_calls.update(kwargs)
        return [object()]

    monkeypatch.setattr(cli, "acquire_or_register_raw", fake_acquire)

    exit_code = cli.main(["--confirm-overwrite", "--source-url", "https://www.mineduc.gob.gt/datos.csv"])

    assert exit_code == 0
    assert captured_calls["allow_overwrite"] is True
    assert captured_calls["raw_dir"] == tmp_path / "data/raw"
    assert "Manifest actualizado con 1 lote" in capsys.readouterr().out


def test_cli_recaptura_html_mineduc_por_departamento(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    captured_calls = {}

    def fake_capture(raw_dir, **kwargs):
        captured_calls["raw_dir"] = raw_dir
        captured_calls.update(kwargs)
        return [object(), object()]

    monkeypatch.setattr(cli, "capture_mineduc_diversificado_html", fake_capture)

    exit_code = cli.main(
        [
            "--capture-html",
            "--department-code",
            "01",
            "--department-name",
            "GUATEMALA",
            "--fecha-extraccion",
            "2026-07-14",
            "--confirm-overwrite",
        ]
    )

    assert exit_code == 0
    assert captured_calls["raw_dir"] == tmp_path / "data/raw"
    assert captured_calls["department_code"] == "01"
    assert captured_calls["department_name"] == "GUATEMALA"
    assert captured_calls["extraction_date"] == "2026-07-14"
    assert captured_calls["allow_overwrite"] is True
    assert "Manifest actualizado con 2 lote" in capsys.readouterr().out


def test_cli_recaptura_html_exige_departamento(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    monkeypatch.setattr(cli, "ROOT", tmp_path)

    exit_code = cli.main(["--capture-html", "--department-code", "01"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "--department-code y --department-name" in captured.err


def test_cli_reporta_errores_de_adquisicion_en_stderr(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    monkeypatch.setattr(cli, "ROOT", tmp_path)

    def fake_acquire(*_args, **_kwargs):
        raise AcquisitionError("falló la fuente oficial")

    monkeypatch.setattr(cli, "acquire_or_register_raw", fake_acquire)

    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "falló la fuente oficial" in captured.err


def test_cli_restringe_raw_dir_fuera_de_data_raw(monkeypatch, tmp_path, capsys):
    cli = load_cli_module()
    project_root = tmp_path / "project"
    outside = tmp_path / "outside"
    monkeypatch.setattr(cli, "ROOT", project_root)

    exit_code = cli.main(["--raw-dir", str(outside), "--manual-file", "manual.csv"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "data/raw" in captured.err
