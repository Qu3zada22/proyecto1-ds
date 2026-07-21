from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pipeline_limpieza.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("pipeline_limpieza", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_pipeline_ejecuta_flujo_completo_en_orden_con_catalogo_versionado(monkeypatch):
    module = _load_module()
    calls: list[tuple[list[str], Path]] = []

    def runner(command, *, cwd, check):
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", runner)
    monkeypatch.setattr(module.Path, "cwd", lambda: ROOT)

    assert module.main([]) == 0
    assert [Path(command[1]).name for command, _ in calls] == [
        "consolidar_crudos.py",
        "diagnosticar_crudos.py",
        "limpiar_dataset.py",
        "detectar_duplicados.py",
        "decidir_duplicados.py",
        "validar_territorio.py",
        "revisar_pendientes.py",
        "validar_dataset.py",
        "generar_reporte_calidad.py",
        "generar_code_book.py",
        "generar_code_book_pdf.py",
    ]
    assert all(command[0] == sys.executable and cwd == ROOT for command, cwd in calls)


def test_pipeline_permite_regenerar_catalogo_y_omitir_pdf(monkeypatch):
    module = _load_module()
    scripts: list[str] = []

    def runner(command, *, cwd, check):
        scripts.append(Path(command[1]).name)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", runner)
    monkeypatch.setattr(module.Path, "cwd", lambda: ROOT)

    assert module.main(["--regenerar-catalogo", "--sin-pdf"]) == 0
    assert scripts.index("generar_catalogo_territorial.py") < scripts.index("limpiar_dataset.py")
    assert "generar_code_book_pdf.py" not in scripts


def test_pipeline_se_detiene_en_el_primer_fallo(monkeypatch, capsys):
    module = _load_module()
    scripts: list[str] = []

    def runner(command, *, cwd, check):
        name = Path(command[1]).name
        scripts.append(name)
        return subprocess.CompletedProcess(command, 4 if name == "limpiar_dataset.py" else 0)

    monkeypatch.setattr(module.subprocess, "run", runner)
    monkeypatch.setattr(module.Path, "cwd", lambda: ROOT)

    assert module.main([]) == 4
    assert scripts[-1] == "limpiar_dataset.py"
    assert "limpiar_dataset.py" in capsys.readouterr().err


def test_pipeline_rechaza_ejecucion_fuera_de_la_raiz(monkeypatch, tmp_path, capsys):
    module = _load_module()
    monkeypatch.setattr(module.Path, "cwd", lambda: tmp_path)

    assert module.main([]) == 2
    assert "raíz del repositorio" in capsys.readouterr().err


def test_pipeline_falla_antes_de_escribir_si_falta_el_catalogo(monkeypatch, tmp_path, capsys):
    module = _load_module()
    monkeypatch.setattr(module.Path, "cwd", lambda: ROOT)
    monkeypatch.setattr(module, "CATALOG", tmp_path / "catalogo_territorial.csv")

    assert module.main([]) == 2
    assert "--regenerar-catalogo" in capsys.readouterr().err
