import csv
from pathlib import Path

import pytest

from proyecto1_ds import cleaning
from proyecto1_ds.cleaning import CleaningCsvError, CleaningOutputError, clean_dataset, write_cleaning_outputs


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)


def _read_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def test_limpia_nbsp_ausencias_y_preserva_identificadores_como_texto(tmp_path):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(
        interim_csv,
        ["CODIGO", "DISTRITO", "TELEFONO", "ESTABLECIMIENTO", "DIRECTOR", "archivo_origen", "\xa0"],
        [
            ["001", " 01-403 ", " 2251\xa02759 ", " Instituto\xa0  Central ", "SIN DATO", "raw.csv", ""],
            ["002", "N/A", "-", "Colegio San José", "  Ana   Pérez ", "raw.csv", "\xa0"],
        ],
    )
    original_bytes = interim_csv.read_bytes()

    result = clean_dataset(interim_csv)

    assert interim_csv.read_bytes() == original_bytes
    assert result.header == ["CODIGO", "DISTRITO", "TELEFONO", "ESTABLECIMIENTO", "DIRECTOR", "archivo_origen"]
    assert result.rows == [
        {
            "CODIGO": "001",
            "DISTRITO": "01-403",
            "TELEFONO": "2251 2759",
            "ESTABLECIMIENTO": "Instituto Central",
            "DIRECTOR": "",
            "archivo_origen": "raw.csv",
        },
        {
            "CODIGO": "002",
            "DISTRITO": "",
            "TELEFONO": "",
            "ESTABLECIMIENTO": "Colegio San José",
            "DIRECTOR": "Ana Pérez",
            "archivo_origen": "raw.csv",
        },
    ]
    assert {
        "variable": "'<NBSP>'",
        "regla": "eliminar_columna_nbsp_vacia",
        "filas_afectadas": "2",
        "justificacion": "Columna compuesta solo por ausencias según diagnóstico y plan de limpieza.",
        "riesgo": "bajo",
        "evidencia_fuente": "docs/plan_limpieza.md; outputs/tablas/diagnostico_columnas.csv",
    } in result.cleaning_log


def test_conserva_columna_nbsp_con_contenido_y_reporta_decision_no_segura(tmp_path):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "\xa0"], [["001", "valor observado"], ["002", ""]])

    result = clean_dataset(interim_csv)

    assert result.header == ["CODIGO", "\xa0"]
    assert result.rows == [{"CODIGO": "001", "\xa0": "valor observado"}, {"CODIGO": "002", "\xa0": ""}]
    assert {
        "variable": "'<NBSP>'",
        "regla": "conservar_columna_nbsp_no_segura",
        "filas_afectadas": "1",
        "justificacion": "La columna contiene valores no ausentes; eliminarla requeriría revisión manual.",
        "riesgo": "alto",
        "evidencia_fuente": "CSV intermedio",
    } in result.cleaning_log


def test_rechaza_csv_malformado_y_permite_csv_solo_con_encabezados(tmp_path):
    malformed_cases = {
        "empty.csv": "",
        "duplicate_headers.csv": "CODIGO,CODIGO\n001,002\n",
        "extra_columns.csv": "CODIGO,NOMBRE\n001,Central,sobrante\n",
        "missing_columns.csv": "CODIGO,NOMBRE\n001\n",
        "open_quoted_field.csv": 'CODIGO,NOMBRE\n001,"Central\n',
    }
    for filename, content in malformed_cases.items():
        interim_csv = tmp_path / filename
        interim_csv.write_text(content, encoding="utf-8")

        with pytest.raises(CleaningCsvError, match="CSV intermedio malformado"):
            clean_dataset(interim_csv)

    header_only = tmp_path / "header_only.csv"
    header_only.write_text("CODIGO,DIRECTOR,\xa0\n", encoding="utf-8")

    result = clean_dataset(header_only)

    assert result.header == ["CODIGO", "DIRECTOR"]
    assert result.rows == []
    assert any(row["metrica"] == "filas" and row["antes"] == "0" and row["despues"] == "0" for row in result.quality_report)


def test_write_cleaning_outputs_restauracion_atomica_sin_parciales(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)
    previous_outputs = {
        clean_csv: clean_csv.read_bytes(),
        tables_dir / "bitacora_limpieza.csv": (tables_dir / "bitacora_limpieza.csv").read_bytes(),
        tables_dir / "reporte_calidad_antes_despues.csv": (tables_dir / "reporte_calidad_antes_despues.csv").read_bytes(),
    }

    updated_csv = tmp_path / "updated.csv"
    _write_csv(updated_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["002", "Bea", ""]])
    updated_result = clean_dataset(updated_csv)
    original_replace = Path.replace

    def fail_report_replace(self, target):
        target_path = Path(target)
        if self.name.startswith(".reporte_calidad_antes_despues.csv.") and self.name.endswith(".tmp"):
            raise OSError("report replace blocked")
        return original_replace(self, target_path)

    monkeypatch.setattr(Path, "replace", fail_report_replace)

    with pytest.raises(OSError, match="report replace blocked"):
        write_cleaning_outputs(updated_result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert {path: path.read_bytes() for path in previous_outputs} == previous_outputs
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(clean_csv.parent.glob("*.backup"))
    assert not list(tables_dir.glob("*.tmp"))
    assert not list(tables_dir.glob("*.backup"))


def test_write_cleaning_outputs_limpia_temporal_si_writer_falla_durante_escritura(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    original_write_rows = cleaning._write_rows

    def fail_after_creating_report_temp(path, fieldnames, rows):
        if path.name.startswith(".reporte_calidad_antes_despues.csv.") and path.name.endswith(".tmp"):
            path.write_text("partial report\n", encoding="utf-8")
            raise OSError("report temp write blocked")
        original_write_rows(path, fieldnames, rows)

    monkeypatch.setattr(cleaning, "_write_rows", fail_after_creating_report_temp)

    with pytest.raises(OSError, match="report temp write blocked"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert not clean_csv.exists()
    assert not (tables_dir / "bitacora_limpieza.csv").exists()
    assert not (tables_dir / "reporte_calidad_antes_despues.csv").exists()
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_rechaza_rutas_fuera_de_raices_permitidas_con_project_root(tmp_path):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    allowed_clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    allowed_tables_dir = tmp_path / "outputs" / "tablas"
    rejected_cases = [
        (
            tmp_path / "data" / "processed" / ".." / "escape.csv",
            allowed_tables_dir,
            tmp_path / "data" / "escape.csv",
        ),
        (allowed_clean_csv, tmp_path / "outputs" / "otra_tabla", tmp_path / "outputs" / "otra_tabla"),
    ]

    for clean_csv, tables_dir, rejected_path in rejected_cases:
        with pytest.raises(CleaningOutputError, match="ruta de salida no permitida"):
            write_cleaning_outputs(
                result,
                clean_csv_path=clean_csv,
                tables_dir=tables_dir,
                project_root=tmp_path,
            )

        assert not rejected_path.exists()
        assert not allowed_clean_csv.exists()
        assert not allowed_tables_dir.exists()

    outputs = write_cleaning_outputs(
        result,
        clean_csv_path=allowed_clean_csv,
        tables_dir=allowed_tables_dir,
        project_root=tmp_path,
    )

    assert outputs.clean_csv_path == allowed_clean_csv
    assert outputs.log_path == allowed_tables_dir / "bitacora_limpieza.csv"
    assert outputs.report_path == allowed_tables_dir / "reporte_calidad_antes_despues.csv"
    assert allowed_clean_csv.exists()
    assert (allowed_tables_dir / "bitacora_limpieza.csv").exists()
    assert (allowed_tables_dir / "reporte_calidad_antes_despues.csv").exists()


def test_write_cleaning_outputs_rechaza_rutas_personalizadas_sin_project_root_antes_de_escribir(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    rejected_cases = [
        (clean_csv, cleaning.DEFAULT_TABLES_DIR),
        (cleaning.DEFAULT_CLEAN_CSV, tables_dir),
        (clean_csv, tables_dir),
    ]

    def fail_mkdir(self, parents=False, exist_ok=False):
        pytest.fail(f"mkdir no debe ejecutarse para rutas personalizadas sin project_root: {self}")

    def fail_atomic_write(plans):
        pytest.fail("la escritura atómica no debe ejecutarse para rutas personalizadas sin project_root")

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)
    monkeypatch.setattr(cleaning, "_write_outputs_atomically", fail_atomic_write)

    for rejected_clean_csv, rejected_tables_dir in rejected_cases:
        with pytest.raises(CleaningOutputError, match="project_root"):
            write_cleaning_outputs(result, clean_csv_path=rejected_clean_csv, tables_dir=rejected_tables_dir)

    assert not clean_csv.exists()
    assert not tables_dir.exists()


def test_write_cleaning_outputs_defaults_se_resuelven_bajo_raices_seguras(monkeypatch, tmp_path):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    created_dirs: list[Path] = []
    planned_destinations: list[Path] = []

    def record_mkdir(self, parents=False, exist_ok=False):
        created_dirs.append(self)

    def record_atomic_plans(plans):
        planned_destinations.extend(destination for destination, _writer in plans)

    monkeypatch.setattr(Path, "mkdir", record_mkdir)
    monkeypatch.setattr(cleaning, "_write_outputs_atomically", record_atomic_plans)

    outputs = write_cleaning_outputs(result)

    project_root = Path(cleaning.__file__).resolve().parents[2]
    assert outputs.clean_csv_path == project_root / cleaning.DEFAULT_CLEAN_CSV
    assert outputs.log_path == project_root / cleaning.DEFAULT_TABLES_DIR / "bitacora_limpieza.csv"
    assert outputs.report_path == project_root / cleaning.DEFAULT_TABLES_DIR / "reporte_calidad_antes_despues.csv"
    assert planned_destinations == [outputs.clean_csv_path, outputs.log_path, outputs.report_path]
    assert created_dirs == [outputs.clean_csv_path.parent, outputs.log_path.parent, outputs.report_path.parent]


def test_salidas_son_byte_por_byte_deterministicas_e_idempotentes(tmp_path):
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", " SIN DATO ", ""]])
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"

    write_cleaning_outputs(clean_dataset(interim_csv), clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)
    first_run = {
        clean_csv: clean_csv.read_bytes(),
        tables_dir / "bitacora_limpieza.csv": (tables_dir / "bitacora_limpieza.csv").read_bytes(),
        tables_dir / "reporte_calidad_antes_despues.csv": (tables_dir / "reporte_calidad_antes_despues.csv").read_bytes(),
    }
    for path in first_run:
        path.write_text("stale\n", encoding="utf-8")

    write_cleaning_outputs(clean_dataset(interim_csv), clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    second_run = {path: path.read_bytes() for path in first_run}
    assert second_run == first_run
    assert all(b"stale" not in content for content in second_run.values())


def test_limpieza_no_muta_fuentes_crudas_intermedias_html_ni_documentos(tmp_path):
    raw_file = tmp_path / "data" / "raw" / "guatemala.html"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text("<html>raw</html>", encoding="utf-8")
    interim_csv = tmp_path / "data" / "interim" / "establecimientos_diversificado_raw_unificado.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "SIN DATO", ""]])
    diagnostics_doc = tmp_path / "docs" / "diagnostico.md"
    cleaning_plan = tmp_path / "docs" / "plan_limpieza.md"
    diagnostics_doc.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_doc.write_text("diagnóstico vigente", encoding="utf-8")
    cleaning_plan.write_text("plan vigente", encoding="utf-8")
    protected = {path: path.read_bytes() for path in [raw_file, interim_csv, diagnostics_doc, cleaning_plan]}

    write_cleaning_outputs(
        clean_dataset(interim_csv),
        clean_csv_path=tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv",
        tables_dir=tmp_path / "outputs" / "tablas",
        project_root=tmp_path,
    )

    assert {path: path.read_bytes() for path in protected} == protected
    assert (tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv").exists()
    assert (tmp_path / "outputs" / "tablas" / "bitacora_limpieza.csv").exists()
    assert (tmp_path / "outputs" / "tablas" / "reporte_calidad_antes_despues.csv").exists()
