import csv
import importlib.util
from pathlib import Path

import pytest

from proyecto1_ds.diagnostics import DEFAULT_SOURCE_CSV, DiagnosticCsvError, DiagnosticOutputError, generate_diagnostics, write_diagnostics


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "diagnosticar_crudos.py"
CANONICAL_SOURCE = Path("data/source/establecimientos_diversificado_mineduc.csv")


def test_default_y_cli_consumen_solo_fuente_canonica(tmp_path):
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    args = cli.build_parser().parse_args([])
    assert DEFAULT_SOURCE_CSV == CANONICAL_SOURCE
    assert args.source_csv == tmp_path / CANONICAL_SOURCE
    assert "--" + "interim" + "-csv" not in cli.build_parser().format_help()


def _write_interim_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["codigo", "nombre", "departamento", "telefono"])
        writer.writerow(["01-01-0007-46", " Instituto Central ", "Guatemala", "22512759"])
        writer.writerow(["01-01-0008-46", "", "Escuintla", "abc123"])
        writer.writerow(["01-01-0008-46", "", "Escuintla", "abc123"])
        writer.writerow(["codigo roto", "Sin dato", "", ""]) 


def _read_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def test_genera_metricas_obligatorias_sin_modificar_csv_intermedio(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    original_content = interim_csv.read_text(encoding="utf-8")

    report = generate_diagnostics(interim_csv)

    assert interim_csv.read_text(encoding="utf-8") == original_content
    assert report.summary["filas"] == 4
    assert report.summary["columnas"] == 4
    assert report.summary["duplicados_exactos"] == 1
    assert report.summary["catalogo_territorial"] == "no verificable"

    metrics_by_column = {metric["columna"]: metric for metric in report.column_metrics}
    assert metrics_by_column["nombre"] == {
        "columna": "nombre",
        "columna_mostrada": "nombre",
        "tipo_asignado": "str",
        "faltantes": 3,
        "porcentaje_faltantes": "75.00",
        "unicos": 3,
    }
    assert metrics_by_column["telefono"]["faltantes"] == 1
    assert metrics_by_column["telefono"]["unicos"] == 3


def test_genera_dominios_observados_con_frecuencias_sin_limpiar_valores(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)

    report = generate_diagnostics(interim_csv)

    domains = {
        (row["columna"], row["valor"]): row["frecuencia"] for row in report.observed_domains
    }
    assert domains[("departamento", "Escuintla")] == 2
    assert domains[("departamento", "Guatemala")] == 1
    assert domains[("nombre", " Instituto Central ")] == 1


def test_rechaza_csv_intermedio_malformado_sin_generar_diagnostico(tmp_path):
    cases = {
        "empty.csv": "",
        "duplicate_headers.csv": "codigo,codigo\n01,02\n",
        "extra_columns.csv": "codigo,nombre\n01,Central,sobrante\n",
        "missing_columns.csv": "codigo,nombre\n01\n",
        "open_quoted_field.csv": 'codigo,nombre\n01,"Central\n',
    }

    for filename, content in cases.items():
        interim_csv = tmp_path / filename
        interim_csv.write_text(content, encoding="utf-8")

        with pytest.raises(DiagnosticCsvError, match="CSV intermedio malformado"):
            generate_diagnostics(interim_csv)


def test_reporta_patrones_sospechosos_y_difiere_duplicados_parciales(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)

    report = generate_diagnostics(interim_csv)

    issues = {(issue["columna"], issue["tipo"]): issue for issue in report.quality_issues}
    assert issues[("departamento", "catalogo_no_verificable")]["conteo"] == 1
    assert "catálogo oficial" in issues[("departamento", "catalogo_no_verificable")]["descripcion"]
    assert issues[("telefono", "formato_sospechoso")]["conteo"] == 2
    assert issues[("codigo", "formato_sospechoso")]["conteo"] == 1
    assert issues[("nombre", "texto_sospechoso")]["conteo"] == 1
    assert any(issue["tipo"] == "duplicados_parciales_diferidos" for issue in report.quality_issues)


def test_reporta_encabezados_sospechosos_sin_renombrar_columnas(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    interim_csv.parent.mkdir(parents=True, exist_ok=True)
    interim_csv.write_text("\xa0,codigo\n,01-01-0007-46\n", encoding="utf-8")

    report = generate_diagnostics(interim_csv)

    assert report.column_metrics[0]["columna"] == "\xa0"
    assert report.column_metrics[0]["columna_mostrada"] == "'<NBSP>'"
    assert {
        "columna": "\xa0",
        "columna_mostrada": "'<NBSP>'",
        "tipo": "encabezado_sospechoso",
        "conteo": 1,
        "descripcion": "Encabezado vacío o compuesto solo por espacios; se reporta sin renombrarlo.",
    } in report.quality_issues


def test_escribe_tablas_y_diagnostico_markdown_generados_por_codigo(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    output_dir = tmp_path / "outputs" / "tablas"
    docs_path = tmp_path / "docs" / "diagnostico.md"
    _write_interim_csv(interim_csv)
    report = generate_diagnostics(interim_csv)

    outputs = write_diagnostics(report, output_dir=output_dir, docs_path=docs_path)

    assert outputs.docs_path == docs_path
    assert {path.name for path in outputs.table_paths} == {
        "resumen_dataset.csv",
        "diagnostico_columnas.csv",
        "duplicados_exactos.csv",
        "problemas_potenciales.csv",
        "dominios_observados.csv",
    }
    assert _read_table(output_dir / "resumen_dataset.csv") == [
        {"metrica": "filas", "valor": "4"},
        {"metrica": "columnas", "valor": "4"},
        {"metrica": "duplicados_exactos", "valor": "1"},
        {"metrica": "catalogo_territorial", "valor": "no verificable"},
    ]
    markdown = docs_path.read_text(encoding="utf-8")
    assert "# Diagnóstico de datos crudos MINEDUC" in markdown
    assert str(tmp_path) not in markdown
    assert "Duplicados exactos: 1" in markdown
    assert "Problemas potenciales reportados: 9 (incluye duplicados parciales diferidos)" in markdown
    assert "dominios_observados.csv" in markdown
    assert "Los duplicados parciales quedan diferidos" in markdown
    assert "No se aplicó limpieza" in markdown
    assert "El comando de adquisición mostrado es un ejemplo para un departamento" in markdown
    assert "preservada contiene 23 artefactos HTML departamentales" in markdown
    assert "repita el comando para cada código y nombre de departamento" in markdown

    observed_domains = _read_table(output_dir / "dominios_observados.csv")
    assert {
        "columna": "departamento",
        "columna_mostrada": "departamento",
        "valor": "Escuintla",
        "valor_mostrado": "Escuintla",
        "frecuencia": "2",
    } in observed_domains
    assert {
        "columna": "nombre",
        "columna_mostrada": "nombre",
        "valor": " Instituto Central ",
        "valor_mostrado": " Instituto Central ",
        "frecuencia": "1",
    } in observed_domains


def test_write_diagnostics_preserva_salidas_previas_si_falla_generacion(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    output_dir = tmp_path / "outputs" / "tablas"
    docs_path = tmp_path / "docs" / "diagnostico.md"
    _write_interim_csv(interim_csv)
    report = generate_diagnostics(interim_csv)
    write_diagnostics(report, output_dir=output_dir, docs_path=docs_path)
    previous_summary = (output_dir / "resumen_dataset.csv").read_text(encoding="utf-8")
    previous_docs = docs_path.read_text(encoding="utf-8")

    def fail_render(_report):
        raise RuntimeError("boom")

    monkeypatch.setattr("proyecto1_ds.diagnostics._render_markdown", fail_render)

    with pytest.raises(RuntimeError, match="boom"):
        write_diagnostics(report, output_dir=output_dir, docs_path=docs_path)

    assert (output_dir / "resumen_dataset.csv").read_text(encoding="utf-8") == previous_summary
    assert docs_path.read_text(encoding="utf-8") == previous_docs
    assert not list(output_dir.glob("*.tmp"))
    assert not list(output_dir.glob("*.backup"))


def test_write_diagnostics_reporta_contexto_si_falla_restauracion(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    output_dir = tmp_path / "outputs" / "tablas"
    docs_path = tmp_path / "docs" / "diagnostico.md"
    _write_interim_csv(interim_csv)
    report = generate_diagnostics(interim_csv)
    write_diagnostics(report, output_dir=output_dir, docs_path=docs_path)
    previous_summary = (output_dir / "resumen_dataset.csv").read_text(encoding="utf-8")

    original_replace = Path.replace

    def fail_commit_and_summary_restore(self, target):
        target_path = Path(target)
        if self.name.startswith(".diagnostico.md.") and self.name.endswith(".tmp") and target_path.name == "diagnostico.md":
            raise OSError("docs replace blocked")
        if self.name.startswith(".resumen_dataset.csv.") and self.name.endswith(".backup"):
            raise OSError("summary restore blocked")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_commit_and_summary_restore)

    with pytest.raises(DiagnosticOutputError) as error:
        write_diagnostics(report, output_dir=output_dir, docs_path=docs_path)

    message = str(error.value)
    assert "recuperación manual" in message
    assert "resumen_dataset.csv" in message
    assert "summary restore blocked" in message
    preserved_backups = list(output_dir.glob(".resumen_dataset.csv.*.backup"))
    assert len(preserved_backups) == 1
    assert preserved_backups[0].read_text(encoding="utf-8") == previous_summary


def test_cli_diagnostica_interim_y_restringe_salidas_al_proyecto(tmp_path, capsys):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    exit_code = cli.main(["--source-csv", str(interim_csv)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Diagnóstico generado" in captured.out
    assert (tmp_path / "outputs" / "tablas" / "diagnostico_columnas.csv").exists()
    assert (tmp_path / "docs" / "diagnostico.md").exists()

    rejected = cli.main([
        "--source-csv",
        str(interim_csv),
        "--docs-file",
        str(tmp_path / "fuera" / "diagnostico.md"),
    ])
    assert rejected == 1
    assert "docs/diagnostico.md" in capsys.readouterr().err

    rejected_interim = cli.main(["--source-csv", str(tmp_path / "fuera" / "datos.csv")])
    assert rejected_interim == 1
    assert "data/source" in capsys.readouterr().err


def test_cli_reporta_fallo_de_restauracion_de_salidas_sin_traceback(tmp_path, capsys, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_interim_csv(interim_csv)
    cli = _load_cli_module()
    cli.ROOT = tmp_path

    def fail_write_diagnostics(*_args, **_kwargs):
        raise DiagnosticOutputError("recuperación manual requerida")

    monkeypatch.setattr(cli, "write_diagnostics", fail_write_diagnostics)

    exit_code = cli.main(["--source-csv", str(interim_csv)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "recuperación manual requerida" in captured.err
    assert "Traceback" not in captured.err


def _load_cli_module():
    spec = importlib.util.spec_from_file_location("diagnosticar_crudos_cli", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
