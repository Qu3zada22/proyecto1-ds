from pathlib import Path

import pytest

from proyecto1_ds import acquisition
from proyecto1_ds.acquisition import (
    AcquisitionError,
    InvalidSourceUrlError,
    RawFileExistsError,
    acquire_or_register_raw,
    capture_mineduc_diversificado_html,
)


def test_rechaza_url_no_mineduc(tmp_path):
    with pytest.raises(InvalidSourceUrlError, match="MINEDUC"):
        acquire_or_register_raw(tmp_path, source_url="https://example.com/data.csv")


def test_rechaza_descarga_mineduc_sin_https(tmp_path):
    with pytest.raises(InvalidSourceUrlError, match="HTTPS"):
        acquire_or_register_raw(tmp_path, source_url="http://www.mineduc.gob.gt/establecimientos.csv")


def test_no_sobrescribe_csv_crudo_existente(tmp_path):
    existing = tmp_path / "establecimientos.csv"
    existing.write_text("codigo,nombre\n001,Original\n", encoding="utf-8")

    with pytest.raises(RawFileExistsError, match="sobrescribir"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
        )

    assert existing.read_text(encoding="utf-8") == "codigo,nombre\n001,Original\n"


def test_registra_fallback_manual_con_error_explicito(tmp_path):
    manual = tmp_path / "manual.csv"
    manual.write_text("codigo,nombre\n001,Instituto\n", encoding="utf-8")

    entries = acquire_or_register_raw(
        tmp_path,
        source_url="https://www.mineduc.gob.gt/establecimientos.csv",
        downloader=lambda _url: (_ for _ in ()).throw(RuntimeError("sin exportación CSV")),
        cobertura="Diversificado disponible",
        departamento="Guatemala",
    )

    assert len(entries) == 1
    assert entries[0].archivo == "manual.csv"
    assert entries[0].metodo == "manual"
    assert "sin exportación CSV" in entries[0].error_adquisicion


def test_registra_fallback_manual_cuando_mineduc_responde_html_invalido(tmp_path):
    manual = tmp_path / "manual.csv"
    manual.write_text("codigo,nombre\n001,Instituto\n", encoding="utf-8")

    entries = acquire_or_register_raw(
        tmp_path,
        source_url="https://www.mineduc.gob.gt/establecimientos.csv",
        downloader=lambda _url: b"<html><body>No hay CSV directo</body></html>",
        cobertura="Diversificado disponible",
    )

    assert len(entries) == 1
    assert entries[0].archivo == "manual.csv"
    assert entries[0].metodo == "manual"
    assert "parece HTML" in entries[0].error_adquisicion


def test_respuesta_html_mineduc_sin_manual_falla_con_contexto_de_fallback(tmp_path):
    with pytest.raises(AcquisitionError) as error:
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            downloader=lambda _url: b"<html><body>No hay CSV directo</body></html>",
        )

    message = str(error.value)
    assert "no hay CSV crudos manuales" in message
    assert "parece HTML" in message


def test_archivo_manual_faltante_es_error_de_adquisicion(tmp_path):
    with pytest.raises(AcquisitionError, match="missing.csv"):
        acquire_or_register_raw(tmp_path, manual_files=["missing.csv"])


def test_documenta_alcance_disponible_y_faltante(tmp_path):
    manual = tmp_path / "manual.csv"
    manual.write_text("codigo,nombre\n001,Instituto\n", encoding="utf-8")

    entries = acquire_or_register_raw(
        tmp_path,
        manual_files=["manual.csv"],
        cobertura="disponible: departamento Guatemala",
        alcance_faltante="faltante: departamentos sin exportación CSV",
    )

    assert "disponible: departamento Guatemala" in entries[0].cobertura
    assert "faltante: departamentos sin exportación CSV" in entries[0].cobertura


def test_descarga_oficial_y_metadatos_completos(tmp_path):
    entries = acquire_or_register_raw(
        tmp_path,
        source_url="https://www.mineduc.gob.gt/establecimientos.csv",
        output_filename="establecimientos.csv",
        downloader=lambda _url: b"codigo,nombre\n001,Instituto\n",
        extraction_date="2026-07-13",
        version_dataset="v0.1.0",
        cobertura="Diversificado nacional disponible",
        departamento="Guatemala",
    )

    assert Path(tmp_path / "establecimientos.csv").exists()
    entry = entries[0]
    assert entry.fuente_url == "https://www.mineduc.gob.gt/establecimientos.csv"
    assert entry.fecha_extraccion == "2026-07-13"
    assert entry.version_dataset == "v0.1.0"
    assert entry.cobertura == "Diversificado nacional disponible"
    assert entry.departamento == "Guatemala"
    assert len(entry.checksum_sha256) == 64


def test_reporta_alcance_faltante_sin_csv(tmp_path):
    with pytest.raises(AcquisitionError, match="alcance faltante"):
        acquire_or_register_raw(tmp_path)


def test_rechaza_descarga_vacia_o_html_sin_crear_csv(tmp_path):
    with pytest.raises(AcquisitionError, match="CSV"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            downloader=lambda _url: b"<html><body>Error</body></html>",
        )

    assert not (tmp_path / "establecimientos.csv").exists()


def test_sobrescritura_confirmada_no_destruye_archivo_si_descarga_es_invalida(tmp_path):
    existing = tmp_path / "establecimientos.csv"
    existing.write_text("codigo,nombre\n001,Original\n", encoding="utf-8")

    with pytest.raises(AcquisitionError, match="CSV"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: b"",
        )

    assert existing.read_text(encoding="utf-8") == "codigo,nombre\n001,Original\n"


def test_sobrescritura_confirmada_exitosa_reemplaza_y_limpia_temporales(tmp_path):
    existing = tmp_path / "establecimientos.csv"
    existing.write_text("codigo,nombre\n001,Original\n", encoding="utf-8")

    entries = acquire_or_register_raw(
        tmp_path,
        source_url="https://www.mineduc.gob.gt/establecimientos.csv",
        output_filename="establecimientos.csv",
        allow_overwrite=True,
        downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
    )

    assert existing.read_text(encoding="utf-8") == "codigo,nombre\n001,Nuevo\n"
    assert entries[0].archivo == "establecimientos.csv"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["establecimientos.csv", "manifest.json"]


def test_sobrescritura_confirmada_restaurar_original_si_manifest_falla(monkeypatch, tmp_path):
    existing = tmp_path / "establecimientos.csv"
    manifest = tmp_path / "manifest.json"
    original_content = "codigo,nombre\n001,Original\n"
    existing.write_text(original_content, encoding="utf-8")
    manifest.write_text('{"lotes": []}\n', encoding="utf-8")

    def failing_write_manifest(*_args, **_kwargs):
        raise OSError("manifest storage unavailable")

    monkeypatch.setattr(acquisition, "write_manifest", failing_write_manifest)

    with pytest.raises(AcquisitionError, match="manifest"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
        )

    assert existing.read_text(encoding="utf-8") == original_content
    assert manifest.read_text(encoding="utf-8") == '{"lotes": []}\n'
    assert sorted(path.name for path in tmp_path.iterdir()) == ["establecimientos.csv", "manifest.json"]


def test_sobrescritura_confirmada_restaurar_manifest_si_persistencia_lo_corrompe(monkeypatch, tmp_path):
    existing = tmp_path / "establecimientos.csv"
    manifest = tmp_path / "manifest.json"
    existing.write_text("codigo,nombre\n001,Original\n", encoding="utf-8")
    previous_manifest = '{"lotes": [{"archivo": "establecimientos.csv"}]}\n'
    manifest.write_text(previous_manifest, encoding="utf-8")

    def corrupting_write_manifest(_entries, manifest_path):
        manifest_path.write_text('{"lotes": [', encoding="utf-8")
        raise OSError("manifest interrupted")

    monkeypatch.setattr(acquisition, "write_manifest", corrupting_write_manifest)

    with pytest.raises(AcquisitionError, match="manifest"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
        )

    assert existing.read_text(encoding="utf-8") == "codigo,nombre\n001,Original\n"
    assert manifest.read_text(encoding="utf-8") == previous_manifest
    assert sorted(path.name for path in tmp_path.iterdir()) == ["establecimientos.csv", "manifest.json"]


def test_sobrescritura_confirmada_restaurar_original_si_backup_manifest_falla(monkeypatch, tmp_path):
    existing = tmp_path / "establecimientos.csv"
    manifest = tmp_path / "manifest.json"
    original_content = "codigo,nombre\n001,Original\n"
    previous_manifest = (
        '{"lotes": [{"archivo": "establecimientos.csv", '
        '"fuente_url": "manual", "fecha_extraccion": "2026-07-13", '
        '"version_dataset": "v0.1.0", "cobertura": "original", '
        '"departamento": "Guatemala", "metodo": "manual", '
        '"checksum_sha256": "0000000000000000000000000000000000000000000000000000000000000000", '
        '"error_adquisicion": null}]}\n'
    )
    existing.write_text(original_content, encoding="utf-8")
    manifest.write_text(previous_manifest, encoding="utf-8")

    def failing_manifest_backup(_source, _destination):
        raise OSError("manifest backup unavailable")

    monkeypatch.setattr(acquisition.shutil, "copy2", failing_manifest_backup)

    with pytest.raises(AcquisitionError, match="manifest"):
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
        )

    assert existing.read_text(encoding="utf-8") == original_content
    assert manifest.read_text(encoding="utf-8") == previous_manifest
    assert sorted(path.name for path in tmp_path.iterdir()) == ["establecimientos.csv", "manifest.json"]


def test_fallo_restaurando_crudo_preserva_backup_para_recuperacion_manual(monkeypatch, tmp_path):
    existing = tmp_path / "establecimientos.csv"
    manifest = tmp_path / "manifest.json"
    original_content = "codigo,nombre\n001,Original\n"
    downloaded_content = "codigo,nombre\n001,Nuevo\n"
    existing.write_text(original_content, encoding="utf-8")
    manifest.write_text('{"lotes": []}\n', encoding="utf-8")

    def failing_write_manifest(*_args, **_kwargs):
        raise OSError("manifest storage unavailable")

    original_replace = Path.replace

    def fail_when_restoring_target(self, target):
        target_path = Path(target)
        if self.name.endswith(".backup") and not self.name.endswith(".manifest.backup"):
            if target_path.name == "establecimientos.csv":
                raise OSError("target restore unavailable")
        return original_replace(self, target)

    monkeypatch.setattr(acquisition, "write_manifest", failing_write_manifest)
    monkeypatch.setattr(Path, "replace", fail_when_restoring_target)

    with pytest.raises(AcquisitionError) as error:
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: downloaded_content.encode("utf-8"),
        )

    message = str(error.value)
    assert "recuperación manual" in message
    assert "establecimientos.csv" in message
    assert ".backup" in message
    assert existing.read_text(encoding="utf-8") == downloaded_content
    assert manifest.read_text(encoding="utf-8") == '{"lotes": []}\n'
    preserved_backups = [path for path in tmp_path.iterdir() if path.name.endswith(".backup")]
    assert len(preserved_backups) == 1
    assert preserved_backups[0].read_text(encoding="utf-8") == original_content
    assert not [path for path in tmp_path.iterdir() if path.name.endswith(".tmp")]


def test_fallo_restaurando_manifest_preserva_backup_para_recuperacion_manual(monkeypatch, tmp_path):
    existing = tmp_path / "establecimientos.csv"
    manifest = tmp_path / "manifest.json"
    original_content = "codigo,nombre\n001,Original\n"
    previous_manifest = '{"lotes": [{"archivo": "establecimientos.csv"}]}\n'
    corrupted_manifest = '{"lotes": ['
    existing.write_text(original_content, encoding="utf-8")
    manifest.write_text(previous_manifest, encoding="utf-8")

    def corrupting_write_manifest(_entries, manifest_path):
        manifest_path.write_text(corrupted_manifest, encoding="utf-8")
        raise OSError("manifest interrupted")

    original_replace = Path.replace

    def fail_when_restoring_manifest(self, target):
        target_path = Path(target)
        if self.name.endswith(".manifest.backup") and target_path.name == "manifest.json":
            raise OSError("manifest restore unavailable")
        return original_replace(self, target)

    monkeypatch.setattr(acquisition, "write_manifest", corrupting_write_manifest)
    monkeypatch.setattr(Path, "replace", fail_when_restoring_manifest)

    with pytest.raises(AcquisitionError) as error:
        acquire_or_register_raw(
            tmp_path,
            source_url="https://www.mineduc.gob.gt/establecimientos.csv",
            output_filename="establecimientos.csv",
            allow_overwrite=True,
            downloader=lambda _url: b"codigo,nombre\n001,Nuevo\n",
        )

    message = str(error.value)
    assert "recuperación manual" in message
    assert "manifest.json" in message
    assert ".manifest.backup" in message
    assert existing.read_text(encoding="utf-8") == original_content
    assert manifest.read_text(encoding="utf-8") == corrupted_manifest
    preserved_manifest_backups = [path for path in tmp_path.iterdir() if path.name.endswith(".manifest.backup")]
    assert len(preserved_manifest_backups) == 1
    assert preserved_manifest_backups[0].read_text(encoding="utf-8") == previous_manifest
    assert not [path for path in tmp_path.iterdir() if path.name.endswith(".tmp")]


def test_captura_html_oficial_diversificado_sin_convertirlo_a_csv(tmp_path):
    initial_page = """
    <form>
      <input type="hidden" name="__VIEWSTATE" value="state" />
      <input type="hidden" name="__EVENTVALIDATION" value="event" />
      <input name="_ctl0:ContentPlaceHolder1:txtCodEstab" type="text" value="" />
    </form>
    """
    result_page = """
    <html><body>
      <table id="_ctl0_ContentPlaceHolder1_dgResultado">
        <tr><td>CODIGO</td><td>NIVEL</td><td>DEPARTAMENTO</td></tr>
        <tr><td>01-01-0007-46</td><td>DIVERSIFICADO</td><td>GUATEMALA</td></tr>
      </table>
    </body></html>
    """
    posted_forms = []

    def fake_fetcher(url, data=None):
        assert url == "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/"
        if data is None:
            return initial_page.encode("utf-8")
        posted_forms.append(data.decode("utf-8"))
        return result_page.encode("utf-8")

    entries = capture_mineduc_diversificado_html(
        tmp_path,
        department_code="01",
        department_name="GUATEMALA",
        extraction_date="2026-07-14",
        fetcher=fake_fetcher,
    )

    assert len(entries) == 1
    entry = entries[0]
    assert entry.archivo == "mineduc_busca_establecimiento_diversificado_01.html"
    assert entry.metodo == "html-form"
    assert entry.fuente_url == "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/"
    assert "NIVEL ESCOLAR: DIVERSIFICADO" in entry.cobertura
    assert "GUATEMALA" in entry.cobertura
    assert len(entry.checksum_sha256) == 64
    assert (tmp_path / entry.archivo).read_text(encoding="utf-8") == result_page
    assert not list(tmp_path.glob("*.csv"))
    assert "%3AContentPlaceHolder1%3AcmbNivel=46" in posted_forms[0]
    assert "%3AContentPlaceHolder1%3AcmbDepartamento=01" in posted_forms[0]
    assert "__VIEWSTATE=state" in posted_forms[0]
    assert "__EVENTVALIDATION=event" in posted_forms[0]


def test_captura_html_oficial_no_sobrescribe_artefacto_existente(tmp_path):
    existing = tmp_path / "mineduc_busca_establecimiento_diversificado_01.html"
    existing.write_text("<html>original</html>", encoding="utf-8")

    with pytest.raises(RawFileExistsError, match="sobrescribir"):
        capture_mineduc_diversificado_html(
            tmp_path,
            department_code="01",
            department_name="GUATEMALA",
            fetcher=lambda _url, _data=None: b"<html>DIVERSIFICADO</html>",
        )

    assert existing.read_text(encoding="utf-8") == "<html>original</html>"


def test_captura_html_falla_si_markup_inicial_no_tiene_campos_webforms(tmp_path):
    with pytest.raises(AcquisitionError, match="__EVENTVALIDATION"):
        capture_mineduc_diversificado_html(
            tmp_path,
            department_code="01",
            department_name="GUATEMALA",
            fetcher=lambda _url, _data=None: b'<input type="hidden" name="__VIEWSTATE" value="state" />',
        )


def test_captura_html_convierte_fallo_de_red_en_error_de_adquisicion(tmp_path):
    def failing_fetcher(_url, _data=None):
        raise OSError("network down")

    with pytest.raises(AcquisitionError, match="network down"):
        capture_mineduc_diversificado_html(
            tmp_path,
            department_code="01",
            department_name="GUATEMALA",
            fetcher=failing_fetcher,
        )
