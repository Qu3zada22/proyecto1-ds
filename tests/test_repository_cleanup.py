import csv
import hashlib
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "openspec/specs/.gitkeep",
    "openspec/changes/archive/.gitkeep",
    "openspec/changes/anggie-csv-reconciliation",
    ".atl",
    ".pytest_cache",
}


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, check=check, capture_output=True, text=True
    )


def _preflight(root: Path, targets: list[str], protected: list[str]) -> None:
    try:
        actual = Path(_git(root, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("raíz Git inválida") from exc
    if actual != root.resolve():
        raise ValueError("raíz Git inválida")
    for target in targets:
        parts = Path(target).parts
        ignored = any(part == "__pycache__" or part.endswith(".egg-info") for part in parts)
        if target not in ALLOWED and not ignored:
            raise ValueError(f"objetivo fuera de allowlist: {target}")
    for path in protected:
        unstaged = _git(root, "diff", "--quiet", "--", path, check=False).returncode
        staged = _git(root, "diff", "--cached", "--quiet", "--", path, check=False).returncode
        if unstaged or staged:
            raise ValueError(f"ruta protegida modificada: {path}")


def _repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "--quiet")
    protected = root / "manifest.json"
    protected.write_text("baseline\n", encoding="utf-8")
    _git(root, "add", "manifest.json")
    _git(
        root,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "--quiet",
        "-m",
        "baseline",
    )
    return root


def test_preflight_rechaza_cwd_ajeno_y_objetivos_no_permitidos(tmp_path):
    with pytest.raises(ValueError, match="raíz Git"):
        _preflight(tmp_path, [".pytest_cache"], [])

    root = _repository(tmp_path)
    for target in ("docs", ".venv"):
        with pytest.raises(ValueError, match="allowlist"):
            _preflight(root, [target], [])


@pytest.mark.parametrize("staged", [False, True])
def test_preflight_rechaza_cambios_protegidos_staged_y_unstaged(tmp_path, staged):
    root = _repository(tmp_path)
    (root / "manifest.json").write_text("alterado\n", encoding="utf-8")
    if staged:
        _git(root, "add", "manifest.json")

    with pytest.raises(ValueError, match="protegida"):
        _preflight(root, [".pytest_cache"], ["manifest.json"])


def test_recibo_anggie_documenta_objeto_parser_comando_y_metricas_reproducidas():
    receipt = (ROOT / "docs/reconciliacion_anggie.md").read_text(encoding="utf-8")
    evidence = (
        "6e83a26a71d743ce08bbec592821da35df52ceef",
        "2e27f11a8fb882594b8434f4d85b2ca75bc43b8a",
        "ca738d5d0628613c8ad5519e15a5f20c4c1e8d536bd4510a2235e893ee3d4fd5",
        'encoding="utf-8"',
        "strict=False",
        "skipinitialspace=True",
        "12,948",
        "11,867",
        "1,081",
        "12,807: retirada",
        "git show",
    )
    assert all(item in receipt for item in evidence)


def test_estado_final_elimina_allowlist_rastreada_y_preserva_protegidos():
    removed = (
        "openspec/specs/.gitkeep",
        "openspec/changes/archive/.gitkeep",
        "openspec/changes/anggie-csv-reconciliation",
    )
    assert all(not (ROOT / path).exists() for path in removed)

    protected_hashes = {
        "data/raw/manifest.json": "8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07",
        "data/source/establecimientos_diversificado_mineduc.csv": "c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f",
        "data/reference/catalogo_territorial.csv": "64b86ba51f813d0ce6806a3a948af34e5d5a5ad8425ed62f0e0e1d72a53387f2",
        "data/processed/establecimientos_diversificado_limpio.csv": "86e411c5f6f11f2af67b2d1dddf199f17ddc5a7fd9b429347bb38dde9e17d521",
        "outputs/tablas/bitacora_limpieza.csv": "61a013ebbdb9b76d68ce670166fa252a7b40226e953e96f32655f6fa9d2b5a66",
        "outputs/tablas/diagnostico_columnas.csv": "e41123edcb09b3ae78cbf6f8555d317d0f55f222ce2132db70a5de1d1f06d69f",
        "outputs/tablas/dominios_observados.csv": "c95d4905a15854653a64b720bcc956c2151d2dda3569ee33de0de60fa1896f19",
        "outputs/tablas/duplicados_exactos.csv": "81cc2a2a3e2c9afa93030cd73e31966889297b9cd65730683ef40915e0f89bd3",
        "outputs/tablas/problemas_potenciales.csv": "9ccfa68b289547254ac47edb4fb646bbb1fa9f1e4c4b971959d30dd08df40170",
        "outputs/tablas/reporte_limpieza_base.csv": "9e97b1f6d7007e90b8a40ffa14466f01ad1a9b4df199fb6c6606c400210b4475",
        "outputs/tablas/reporte_calidad_antes_despues.csv": "02665aca30d9a08b176dbd22841d41d25915cf29c5f5e79f31467f3558b3a92b",
        "outputs/tablas/resumen_dataset.csv": "2033301b36a70926a0a7dd45313e6298cbdfb5e59227964199131dbf1ad7bb2a",
        "outputs/tablas/inconsistencias_territoriales.csv": "961565cc3bbf6ea18cd9b012525ce47acada935e88ed37fb4ceb5e50854b48fd",
        "outputs/reportes/validacion_territorial.md": "3620b867483bb442d0d2ea28d083325a1ecc4c2985a0c722658fb1363a5b0724",
    }
    for relative, expected in protected_hashes.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    assert len(tuple((ROOT / "data/raw").glob("*.html"))) == 23
    assert (ROOT / ".venv").is_dir()


def test_salidas_limpias_y_territoriales_reflejan_el_contrato_actual():
    clean_path = ROOT / "data/processed/establecimientos_diversificado_limpio.csv"
    with clean_path.open(encoding="utf-8", newline="") as handle:
        clean_rows = list(csv.DictReader(handle))
    assert len(clean_rows) == 11_867
    assert len(clean_rows[0]) == 21

    quality = list(csv.DictReader(
        (ROOT / "outputs/tablas/reporte_calidad_antes_despues.csv").open(
            encoding="utf-8", newline=""
        )
    ))
    columns = next(row for row in quality if row["metrica"] == "variables")
    assert (columns["antes"], columns["despues"]) == ("20", "21")

    territorial = list(csv.DictReader(
        (ROOT / "outputs/tablas/inconsistencias_territoriales.csv").open(
            encoding="utf-8", newline=""
        )
    ))
    assert len(territorial) == 7
    assert sum(int(row["filas"]) for row in territorial) == 145
    assert {row["decision"] for row in territorial} == {"revisar"}


def _planning_rows(prefix: str) -> dict[str, list[str]]:
    plan = (ROOT / "docs/planificacion.md").read_text(encoding="utf-8")
    rows = {}
    for line in plan.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0].startswith(prefix):
            rows[cells[0]] = cells
    return rows


def test_plan_cubre_todos_los_requisitos_con_campos_verificables():
    expected = {
        "R1", "R2", "R3a", "R3b", "R3c", "R3d", "R3e", "R3f", "R3g", "R3h",
        "R4a", "R4b", "R4c", "R5a", "R5b", "R5c", "R5d", "R5e", "R5f", "R5g",
        "R5h", "R5i", "R6", "R7", "R8", "R9", "R10", "RE", "RT",
    }
    rows = _planning_rows("R")
    assert set(rows) == expected
    assert all(len(cells) == 10 and all(cells) for cells in rows.values())
    assert {cells[3] for cells in rows.values()} <= {
        "Completado", "Parcial", "Faltante", "Incierto"
    }


def test_plan_asigna_git_y_code_book_a_cada_integrante():
    rows = _planning_rows("A-")
    assert set(rows) == {"A-Anggie", "A-Iris", "A-Jonathan"}
    assert all(len(cells) == 7 and all(cells) for cells in rows.values())
    assert all("commit" in cells[5].lower() and "Code Book" in cells[4] for cells in rows.values())


def test_plan_mantiene_entregables_futuros_y_rutas_canonicas():
    plan = (ROOT / "docs/planificacion.md").read_text(encoding="utf-8")
    for pending in (
        "catálogo territorial", "duplicados parciales", "245 teléfonos",
        "auditoría interna", "aceptación institucional",
    ):
        assert pending in plan
    assert "Planificado/no implementado" in plan
    assert "data/source/establecimientos_diversificado_mineduc.csv" in plan
    assert "data/processed/establecimientos_diversificado_limpio.csv" in plan
    assert "data/interim/" not in plan and "data/clean/" not in plan
    assert "| Unidad |" in plan and "| PR |" not in plan and "PR1" not in plan


def test_documentacion_refleja_el_cierre_territorial_sin_cerrar_el_proyecto():
    plan = (ROOT / "docs/planificacion.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    code_book = (ROOT / "docs/code_book/variables_territoriales.md").read_text(
        encoding="utf-8"
    )

    for document in (plan, agents, code_book):
        assert "espejo/conversión comunitaria" in document
        assert "INE, Censo 2018" in document
    assert "11,867×21" in plan
    assert "21 variables" in plan
    assert "7 parejas" in code_book and "145 filas" in code_book
    assert "decision=revisar" in code_book
    assert "4 variables territoriales" in code_book
    assert "Iris" in plan and "Code Book territorial completo" in plan

    for document in (plan, agents):
        assert "Anggie" in document
        assert "Jonathan" in document
        assert "pendient" in document.lower()
    # La automatización está completa; la aceptación institucional sigue pendiente.
    assert "completado" in agents.lower() or "completado" in plan.lower()
    assert "aceptación institucional" in plan.lower()


def test_documentacion_distingue_triage_de_revision_manual_de_anggie():
    plan = (ROOT / "docs/planificacion.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    code_book = (ROOT / "docs/code_book/variables_anggie.md").read_text(encoding="utf-8")

    for document in (plan, agents):
        assert all(value in document for value in ("718", "260", "11", "245"))
        assert "duplicad" in document.lower()
        assert "confirm" in document.lower() and "revis" in document.lower()
    assert "SUPERVISOR" in code_book and "668" in code_book
    assert "DIRECTOR" in code_book and "2,912" in code_book
    assert "comparación directa" in code_book.lower()

    requirement_rows = _planning_rows("R")
    assert requirement_rows["R5g"][3] == "Parcial"
    assert "independiente_confirmado" in requirement_rows["R5g"][4]
    assert "978" in requirement_rows["R5g"][5]
    counts = {state: 0 for state in ("Completado", "Parcial", "Faltante", "Incierto")}
    for cells in requirement_rows.values():
        counts[cells[3]] += 1
    assert counts == {"Completado": 23, "Parcial": 6, "Faltante": 0, "Incierto": 0}
    assert requirement_rows["R8"][3] == "Completado"
    expected_states = {
        "R5a": "Completado", "R5e": "Parcial", "R5g": "Parcial",
        "R6": "Completado", "R7": "Parcial", "R9": "Parcial",
        "R10": "Completado", "RE": "Parcial", "RT": "Completado",
    }
    assert {name: requirement_rows[name][3] for name in expected_states} == expected_states
    assert "docs/code_book.pdf" in requirement_rows["R10"][4]
    assert "978" in requirement_rows["R5g"][5]
    assert "c871bd7" in plan
    assert (ROOT / "docs/code_book.pdf").read_bytes().startswith(b"%PDF-")


def test_auditoria_interna_distingue_materiales_de_bloqueos():
    audit = (ROOT / "docs/auditoria_final.md").read_text(encoding="utf-8")

    assert "RECIBO INTERNO" in audit and "no es un sexto material" in audit
    assert "NO APTO PARA CIERRE INSTITUCIONAL" in audit
    assert all(item in audit for item in ("Código fuente", "Repositorio", "Área de trabajo", "Documento PDF", "Data limpia"))
    assert all(item in audit for item in ("718", "260", "245", "201", "145", "11"))
    assert "201 hallazgos históricos agregados" in audit
    assert "245 teléfonos" in audit
    assert all(item in audit for item in ("Anggie", "Iris", "Jonathan"))
    assert all(item in audit for item in ("R5e", "R5f", "R5g", "R7", "R9", "RE", "RT"))
    assert "c871bd7" in audit and "RT satisfecho" in audit
    assert "integración sin publicar" not in audit.lower()


def test_readme_documenta_proposito_requisitos_ejecucion_y_salidas_principales():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert all(item in readme for item in ("Diversificado", "MINEDUC", "Guatemala"))
    assert all(item in readme for item in (
        "Python 3.11",
        "`uv`",
        "Pandoc",
        "Chromium",
        "qpdf",
        "pdfinfo",
        "pdftotext",
    ))
    assert "uv sync" in readme
    assert "uv run python pipeline_limpieza.py" in readme
    assert "uv run python pipeline_limpieza.py --sin-pdf" in readme
    assert "uv run python pipeline_limpieza.py --regenerar-catalogo" in readme
    assert all(item in readme for item in (
        "data/processed/establecimientos_diversificado_limpio.csv",
        "docs/code_book.md",
        "docs/code_book.pdf",
    ))


def test_documentacion_distingue_telefono_historico_de_pendiente_vigente():
    paths = (
        "AGENTS.md", "docs/planificacion.md", "docs/auditoria_final.md",
        "docs/code_book.md", "docs/code_book/variables_anggie.md",
        "openspec/specs/plan-entrega-restante/spec.md",
        "openspec/specs/limpieza-dataset-trazable/spec.md",
    )
    documents = [(ROOT / path).read_text(encoding="utf-8") for path in paths]

    assert all("245" in document for document in documents)
    assert all("201" in document and ("históric" in document.lower() or "diagnóstico inicial" in document.lower()) for document in documents)
    assert "23 `Completado`, 6 `Parcial`" in documents[1]
    assert "NO APTO PARA CIERRE INSTITUCIONAL" in documents[2]
