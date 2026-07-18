import csv
import os
from pathlib import Path

import pytest

from proyecto1_ds import cleaning
from proyecto1_ds.cleaning import DEFAULT_SOURCE_CSV, CleaningCsvError, CleaningOutputError, clean_dataset, write_cleaning_outputs


def test_default_de_limpieza_usa_fuente_canonica():
    assert DEFAULT_SOURCE_CSV == Path("data/source/establecimientos_diversificado_mineduc.csv")


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
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
            "ESTABLECIMIENTO": "INSTITUTO CENTRAL",
            "DIRECTOR": "",
            "archivo_origen": "raw.csv",
        },
        {
            "CODIGO": "002",
            "DISTRITO": "",
            "TELEFONO": "",
            "ESTABLECIMIENTO": "COLEGIO SAN JOSÉ",
            "DIRECTOR": "ANA PÉREZ",
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


def test_normaliza_establecimiento_y_director_a_mayusculas_y_registra_la_regla(tmp_path):
    source_csv = tmp_path / "mixed_case.csv"
    _write_csv(
        source_csv,
        ["ESTABLECIMIENTO", "DIRECTOR"],
        [["Instituto Mixto Álvaro Arzú", "Ana Lucía Pérez"]],
    )

    result = clean_dataset(source_csv)

    assert result.rows == [
        {
            "ESTABLECIMIENTO": "INSTITUTO MIXTO ÁLVARO ARZÚ",
            "DIRECTOR": "ANA LUCÍA PÉREZ",
        }
    ]
    uppercase_log = {
        row["variable"]: row["filas_afectadas"]
        for row in result.cleaning_log
        if row["regla"] == "normalizar_mayusculas"
    }
    assert uppercase_log == {"ESTABLECIMIENTO": "1", "DIRECTOR": "1"}


def test_conserva_columna_nbsp_con_contenido_y_reporta_decision_no_segura(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
    original_replace = cleaning.os.replace

    def fail_report_replace(source, target, *args, **kwargs):
        if Path(source).name.startswith(".reporte_calidad_antes_despues.csv.") and Path(source).name.endswith(".tmp"):
            raise OSError("report replace blocked")
        return original_replace(source, target, *args, **kwargs)

    monkeypatch.setattr(cleaning.os, "replace", fail_report_replace)

    with pytest.raises(OSError, match="report replace blocked"):
        write_cleaning_outputs(updated_result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert {path: path.read_bytes() for path in previous_outputs} == previous_outputs
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(clean_csv.parent.glob("*.backup"))
    assert not list(tables_dir.glob("*.tmp"))
    assert not list(tables_dir.glob("*.backup"))


def test_write_cleaning_outputs_limpia_temporal_si_writer_falla_durante_escritura(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    original_write_rows = cleaning._write_rows

    def fail_after_creating_report_temp(csv_file, fieldnames, rows):
        if fieldnames == cleaning.REPORT_FIELDS:
            csv_file.write("partial report\n")
            raise OSError("report temp write blocked")
        original_write_rows(csv_file, fieldnames, rows)

    monkeypatch.setattr(cleaning, "_write_rows", fail_after_creating_report_temp)

    with pytest.raises(OSError, match="report temp write blocked"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert not clean_csv.exists()
    assert not (tables_dir / "bitacora_limpieza.csv").exists()
    assert not (tables_dir / "reporte_calidad_antes_despues.csv").exists()
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_ignora_temporal_predecible_preexistente_como_symlink(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    clean_csv.parent.mkdir(parents=True)
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    redirected_target = outside_root / "redirected.csv"
    redirected_target.write_text("outside sentinel\n", encoding="utf-8")
    predictable_temp_symlink = clean_csv.parent / f".{clean_csv.name}.{os.getpid()}.tmp"
    predictable_temp_symlink.symlink_to(redirected_target)

    write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert redirected_target.read_text(encoding="utf-8") == "outside sentinel\n"
    assert predictable_temp_symlink.is_symlink()
    assert not clean_csv.is_symlink()
    assert clean_csv.read_text(encoding="utf-8") == "CODIGO,DIRECTOR\n001,ANA\n"


def test_capacidad_dir_fd_permanece_detectable_al_sustituir_os_open(monkeypatch):
    if not cleaning._secure_fd_writes_supported():
        pytest.skip("la plataforma no ofrece la rama segura con dir_fd")
    original_open = cleaning.os.open

    def substituted_open(path, flags, mode=0o777, *, dir_fd=None):
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(cleaning.os, "open", substituted_open)

    assert cleaning._secure_fd_writes_supported()


def test_write_cleaning_outputs_usa_rama_portatil_sin_capacidad_dir_fd(tmp_path, monkeypatch):
    source_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(source_csv, ["CODIGO", "DIRECTOR"], [["001", "Ana Pérez"]])
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"

    monkeypatch.setattr(cleaning, "_OS_OPEN_SUPPORTS_DIR_FD", False)
    monkeypatch.setattr(
        cleaning,
        "_write_outputs_atomically",
        lambda _plans: pytest.fail("la rama segura no debe ejecutarse sin capacidad dir_fd"),
    )

    write_cleaning_outputs(
        clean_dataset(source_csv),
        clean_csv_path=clean_csv,
        tables_dir=tables_dir,
        project_root=tmp_path,
    )

    assert clean_csv.read_text(encoding="utf-8") == "CODIGO,DIRECTOR\n001,ANA PÉREZ\n"
    assert (tables_dir / "bitacora_limpieza.csv").is_file()
    assert (tables_dir / "reporte_calidad_antes_despues.csv").is_file()


def test_write_cleaning_outputs_rechaza_temporal_intercambiado_por_symlink_sin_redirigir(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    redirected_target = outside_root / "redirected.csv"
    redirected_target.write_text("outside sentinel\n", encoding="utf-8")
    swapped_temp_paths: list[Path] = []
    original_open = cleaning.os.open

    def open_then_swap_temp_once(path, flags, mode=0o777, *, dir_fd=None):
        file_descriptor = original_open(path, flags, mode, dir_fd=dir_fd)
        if dir_fd is not None and Path(path).name.endswith(".tmp") and not swapped_temp_paths:
            temp_name = Path(path).name
            cleaning.os.unlink(temp_name, dir_fd=dir_fd)
            cleaning.os.symlink(redirected_target, temp_name, dir_fd=dir_fd)
            swapped_temp_paths.append(clean_csv.parent / temp_name)
        return file_descriptor

    monkeypatch.setattr(cleaning.os, "open", open_then_swap_temp_once)

    with pytest.raises(CleaningOutputError, match="ruta temporal insegura"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert redirected_target.read_text(encoding="utf-8") == "outside sentinel\n"
    assert not clean_csv.is_symlink()
    assert all(not temp_path.exists() for temp_path in swapped_temp_paths)
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_restaura_si_temporal_se_intercambia_por_directorio_antes_de_replace(
    tmp_path,
    monkeypatch,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    write_cleaning_outputs(clean_dataset(interim_csv), clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)
    previous_outputs = {
        clean_csv: clean_csv.read_bytes(),
        tables_dir / "bitacora_limpieza.csv": (tables_dir / "bitacora_limpieza.csv").read_bytes(),
        tables_dir / "reporte_calidad_antes_despues.csv": (tables_dir / "reporte_calidad_antes_despues.csv").read_bytes(),
    }

    updated_csv = tmp_path / "updated.csv"
    _write_csv(updated_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["002", "Bea", ""]])
    updated_result = clean_dataset(updated_csv)
    original_replace = cleaning.os.replace
    swapped_once: list[Path] = []

    def swap_clean_temp_to_directory_before_replace(source, target, *args, **kwargs):
        source_name = Path(source).name
        source_path = clean_csv.parent / source if isinstance(source, str) else Path(source)
        if not swapped_once and source_name.startswith(f".{clean_csv.name}.") and source_name.endswith(".tmp"):
            if kwargs.get("src_dir_fd") is not None:
                cleaning.os.unlink(source_name, dir_fd=kwargs["src_dir_fd"])
                cleaning.os.mkdir(source_name, dir_fd=kwargs["src_dir_fd"])
            else:
                source_path.unlink()
                source_path.mkdir()
            swapped_once.append(source_path)
        return original_replace(source, target, *args, **kwargs)

    monkeypatch.setattr(cleaning.os, "replace", swap_clean_temp_to_directory_before_replace)

    with pytest.raises(CleaningOutputError, match="ruta temporal insegura"):
        write_cleaning_outputs(updated_result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert swapped_once
    assert {path: path.read_bytes() for path in previous_outputs} == previous_outputs
    assert clean_csv.is_file()
    assert not any(path.is_dir() for path in previous_outputs)
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))
    assert not list(clean_csv.parent.glob("*.backup"))
    assert not list(tables_dir.glob("*.backup"))


def test_write_cleaning_outputs_limpia_directorio_temporal_intercambiado_antes_de_validacion(
    tmp_path,
    monkeypatch,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    original_open = cleaning.os.open
    swapped_temp_dirs: list[Path] = []

    def open_then_swap_temp_to_directory_once(path, flags, mode=0o777, *, dir_fd=None):
        file_descriptor = original_open(path, flags, mode, dir_fd=dir_fd)
        if dir_fd is not None and Path(path).name.endswith(".tmp") and not swapped_temp_dirs:
            temp_name = Path(path).name
            cleaning.os.unlink(temp_name, dir_fd=dir_fd)
            cleaning.os.mkdir(temp_name, dir_fd=dir_fd)
            swapped_temp_dirs.append(clean_csv.parent / temp_name)
        return file_descriptor

    monkeypatch.setattr(cleaning.os, "open", open_then_swap_temp_to_directory_once)

    with pytest.raises(CleaningOutputError, match="ruta temporal insegura"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert swapped_temp_dirs
    assert all(not temp_dir.exists() for temp_dir in swapped_temp_dirs)
    assert not clean_csv.exists()
    assert not (tables_dir / "bitacora_limpieza.csv").exists()
    assert not (tables_dir / "reporte_calidad_antes_despues.csv").exists()
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_revalida_destino_final_antes_de_backup_si_se_intercambia_por_directorio(
    tmp_path,
    monkeypatch,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    write_cleaning_outputs(clean_dataset(interim_csv), clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    updated_csv = tmp_path / "updated.csv"
    _write_csv(updated_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["002", "Bea", ""]])
    updated_result = clean_dataset(updated_csv)
    original_replace = cleaning.os.replace
    backup_paths: list[Path] = []

    def swap_final_to_directory_after_revalidation(source, target, *args, **kwargs):
        if Path(source).name == clean_csv.name and not backup_paths:
            clean_csv.unlink()
            clean_csv.mkdir()
            (clean_csv / "marker.txt").write_text("preservar directorio intercambiado", encoding="utf-8")
            backup_paths.append(clean_csv.parent / Path(target).name)
        return original_replace(source, target, *args, **kwargs)

    monkeypatch.setattr(cleaning.os, "replace", swap_final_to_directory_after_revalidation)

    with pytest.raises(CleaningOutputError, match="archivo CSV"):
        write_cleaning_outputs(updated_result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert backup_paths
    assert clean_csv.is_dir()
    assert (clean_csv / "marker.txt").read_text(encoding="utf-8") == "preservar directorio intercambiado"
    assert all(not backup_path.exists() for backup_path in backup_paths)
    assert not list(clean_csv.parent.glob("*.backup"))
    assert not list(tables_dir.glob("*.backup"))
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_no_borra_directorio_destino_creado_antes_de_replace(
    tmp_path,
    monkeypatch,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    original_replace = cleaning.os.replace
    swapped: list[Path] = []

    def swap_final_to_directory_before_temp_commit(source, target, *args, **kwargs):
        if Path(target) == Path(clean_csv.name) and not swapped:
            clean_csv.mkdir()
            (clean_csv / "marker.txt").write_text("directorio externo preservado", encoding="utf-8")
            swapped.append(clean_csv)
        return original_replace(source, target, *args, **kwargs)

    monkeypatch.setattr(cleaning.os, "replace", swap_final_to_directory_before_temp_commit)

    with pytest.raises(CleaningOutputError, match="destino inseguro no removido"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert swapped
    assert clean_csv.is_dir()
    assert (clean_csv / "marker.txt").read_text(encoding="utf-8") == "directorio externo preservado"
    assert not list(clean_csv.parent.glob("*.backup"))
    assert not list(tables_dir.glob("*.backup"))
    assert not list(clean_csv.parent.glob("*.tmp"))
    assert not list(tables_dir.glob("*.tmp"))


def test_write_cleaning_outputs_rechaza_parent_intercambiado_por_symlink_antes_de_abrirlo(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    clean_csv.parent.mkdir(parents=True)
    outside_root = tmp_path / "outside_parent"
    outside_root.mkdir()
    original_parent = tmp_path / "processed_original"
    original_open_secure_output_directory = cleaning._open_secure_output_directory
    swapped: list[Path] = []

    def swap_parent_before_open(project_root, directory):
        if directory == clean_csv.parent and not swapped:
            directory.rename(original_parent)
            directory.symlink_to(outside_root, target_is_directory=True)
            swapped.append(directory)
        return original_open_secure_output_directory(project_root, directory)

    monkeypatch.setattr(cleaning, "_open_secure_output_directory", swap_parent_before_open)

    with pytest.raises(CleaningOutputError, match="directorio de salida inseguro"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert swapped
    assert not any(outside_root.iterdir())
    assert not clean_csv.exists()


def test_write_cleaning_outputs_rechaza_data_processed_symlink_a_data_raw_sin_mutar_raw(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    raw_marker = raw_dir / "sentinel.txt"
    raw_marker.write_text("raw protegido\n", encoding="utf-8")
    processed_link = tmp_path / "data" / "processed"
    processed_link.symlink_to(raw_dir, target_is_directory=True)

    with pytest.raises(CleaningOutputError, match="directorio de salida inseguro|symlink"):
        write_cleaning_outputs(
            result,
            clean_csv_path=processed_link / "establecimientos_diversificado_limpio.csv",
            tables_dir=tmp_path / "outputs" / "tablas",
            project_root=tmp_path,
        )

    assert raw_marker.read_text(encoding="utf-8") == "raw protegido\n"
    assert not (raw_dir / "establecimientos_diversificado_limpio.csv").exists()
    assert not list(raw_dir.glob("*.csv"))
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_write_cleaning_outputs_rechaza_ancestro_data_intercambiado_por_symlink_antes_de_crear_dirs(
    tmp_path,
    monkeypatch,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    outside_data = tmp_path / "outside_data"
    outside_data.mkdir()
    original_data = tmp_path / "data_original"
    original_mkdir = cleaning.os.mkdir
    swapped: list[Path] = []

    def swap_data_before_processed_creation(path, mode=0o777, *, dir_fd=None):
        if dir_fd is not None and Path(path) == Path("processed") and not swapped:
            (tmp_path / "data").rename(original_data)
            (tmp_path / "data").symlink_to(outside_data, target_is_directory=True)
            swapped.append(tmp_path / "data")
        return original_mkdir(path, mode, dir_fd=dir_fd)

    monkeypatch.setattr(cleaning.os, "mkdir", swap_data_before_processed_creation)

    with pytest.raises(CleaningOutputError, match="directorio de salida inseguro"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert swapped
    assert not list(outside_data.rglob("*.csv"))
    assert not clean_csv.exists()


@pytest.mark.parametrize("symlink_case", ["outputs", "tablas"])
def test_write_cleaning_outputs_rechaza_outputs_o_tablas_symlink_sin_escribir_fuera(
    tmp_path,
    symlink_case,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    outside_tables = tmp_path / "outside_tables"
    outside_tables.mkdir()
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_marker = raw_dir / "sentinel.txt"
    raw_marker.write_text("raw protegido\n", encoding="utf-8")

    if symlink_case == "outputs":
        (tmp_path / "outputs").symlink_to(outside_tables, target_is_directory=True)
    else:
        (tmp_path / "outputs").mkdir()
        (tmp_path / "outputs" / "tablas").symlink_to(raw_dir, target_is_directory=True)

    with pytest.raises(CleaningOutputError, match="directorio de salida inseguro|symlink"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tmp_path / "outputs" / "tablas", project_root=tmp_path)

    assert raw_marker.read_text(encoding="utf-8") == "raw protegido\n"
    assert not list(outside_tables.rglob("*.csv"))
    assert not list(raw_dir.glob("*.csv"))
    assert not clean_csv.exists()


def test_write_cleaning_outputs_rechaza_rutas_fuera_de_raices_permitidas_con_project_root(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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


def test_write_cleaning_outputs_rechaza_data_processed_como_csv_limpio_antes_de_escribir(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)

    def fail_atomic_write(plans):
        pytest.fail("la escritura atómica no debe ejecutarse si el CSV limpio apunta a data/processed")

    monkeypatch.setattr(cleaning, "_write_outputs_atomically", fail_atomic_write)

    with pytest.raises(CleaningOutputError, match="archivo CSV"):
        write_cleaning_outputs(
            result,
            clean_csv_path=tmp_path / "data" / "processed",
            tables_dir=tmp_path / "outputs" / "tablas",
            project_root=tmp_path,
        )

    assert not (tmp_path / "data" / "processed").exists()
    assert not (tmp_path / "outputs" / "tablas").exists()


def test_write_cleaning_outputs_rechaza_directorio_existente_como_csv_limpio_sin_mutarlo(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    output_dir = tmp_path / "data" / "processed" / "salida_existente"
    output_dir.mkdir(parents=True)
    marker = output_dir / "marker.txt"
    marker.write_text("preservar directorio", encoding="utf-8")

    def fail_atomic_write(plans):
        pytest.fail("la escritura atómica no debe ejecutarse si el CSV limpio es un directorio")

    monkeypatch.setattr(cleaning, "_write_outputs_atomically", fail_atomic_write)

    with pytest.raises(CleaningOutputError, match="archivo CSV"):
        write_cleaning_outputs(
            result,
            clean_csv_path=output_dir,
            tables_dir=tmp_path / "outputs" / "tablas",
            project_root=tmp_path,
        )

    assert output_dir.is_dir()
    assert marker.read_text(encoding="utf-8") == "preservar directorio"
    assert not list(output_dir.parent.glob(".*.backup"))
    assert not list(output_dir.parent.glob(".*.tmp"))
    assert not (tmp_path / "outputs" / "tablas").exists()


@pytest.mark.parametrize("table_filename", ["bitacora_limpieza.csv", "reporte_calidad_antes_despues.csv"])
def test_write_cleaning_outputs_rechaza_directorio_existente_como_tabla_fija_sin_mutarlo(
    tmp_path,
    monkeypatch,
    table_filename,
):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    clean_csv = tmp_path / "data" / "processed" / "establecimientos_diversificado_limpio.csv"
    tables_dir = tmp_path / "outputs" / "tablas"
    table_output_dir = tables_dir / table_filename
    table_output_dir.mkdir(parents=True)
    marker = table_output_dir / "marker.txt"
    marker.write_text("preservar tabla como directorio", encoding="utf-8")

    def fail_atomic_write(plans):
        pytest.fail("la escritura atómica no debe ejecutarse si una tabla fija apunta a un directorio")

    monkeypatch.setattr(cleaning, "_write_outputs_atomically", fail_atomic_write)

    with pytest.raises(CleaningOutputError, match="archivo CSV"):
        write_cleaning_outputs(result, clean_csv_path=clean_csv, tables_dir=tables_dir, project_root=tmp_path)

    assert table_output_dir.is_dir()
    assert marker.read_text(encoding="utf-8") == "preservar tabla como directorio"
    assert not list(tables_dir.glob(".*.backup"))
    assert not list(tables_dir.glob(".*.tmp"))
    assert not clean_csv.parent.exists()


def test_write_cleaning_outputs_rechaza_rutas_personalizadas_sin_project_root_antes_de_escribir(tmp_path, monkeypatch):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
    _write_csv(interim_csv, ["CODIGO", "DIRECTOR", "\xa0"], [["001", "Ana", ""]])
    result = clean_dataset(interim_csv)
    planned_destinations: list[Path] = []

    def record_atomic_plans(plans):
        planned_destinations.extend(plan.path for plan in plans)

    monkeypatch.setattr(cleaning, "_output_guard_root", lambda _clean_path, _tables_dir, _project_root: tmp_path)
    monkeypatch.setattr(cleaning, "_write_outputs_atomically", record_atomic_plans)

    outputs = write_cleaning_outputs(result)

    project_root = tmp_path
    assert outputs.clean_csv_path == project_root / cleaning.DEFAULT_CLEAN_CSV
    assert outputs.log_path == project_root / cleaning.DEFAULT_TABLES_DIR / "bitacora_limpieza.csv"
    assert outputs.report_path == project_root / cleaning.DEFAULT_TABLES_DIR / "reporte_calidad_antes_despues.csv"
    assert planned_destinations == [outputs.clean_csv_path, outputs.log_path, outputs.report_path]
    assert outputs.clean_csv_path.parent.is_dir()
    assert outputs.log_path.parent.is_dir()


def test_salidas_son_byte_por_byte_deterministicas_e_idempotentes(tmp_path):
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
    interim_csv = tmp_path / "data" / "source" / "establecimientos_diversificado_mineduc.csv"
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
