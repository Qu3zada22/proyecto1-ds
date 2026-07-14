from pathlib import Path

import pytest

from proyecto1_ds.manifest import (
    ManifestEntry,
    checksum_sha256,
    next_dataset_version,
    read_manifest,
    validate_dataset_version,
    write_manifest,
)


def test_version_dataset_usa_formato_semver_like():
    assert validate_dataset_version("v0.1.0") == "v0.1.0"
    assert next_dataset_version("v0.1.0", "metadata") == "v0.1.1"
    assert next_dataset_version("v0.1.1", "dataset") == "v0.2.0"

    with pytest.raises(ValueError, match="vMAJOR.MINOR.PATCH"):
        validate_dataset_version("0.1.0")


def test_manifest_escribe_metadatos_y_checksum(tmp_path):
    raw_file = tmp_path / "establecimientos.csv"
    raw_file.write_text("codigo,nombre\n001,Instituto\n", encoding="utf-8")

    entry = ManifestEntry(
        archivo="establecimientos.csv",
        fuente_url="https://www.mineduc.gob.gt/estadistica.csv",
        fecha_extraccion="2026-07-13",
        version_dataset="v0.1.0",
        cobertura="Diversificado nacional disponible",
        departamento="Guatemala",
        metodo="manual",
        checksum_sha256=checksum_sha256(raw_file),
        error_adquisicion="Descarga automática no disponible",
    )

    manifest_path = tmp_path / "manifest.json"
    write_manifest([entry], manifest_path)

    loaded = read_manifest(manifest_path)
    assert loaded == [entry]
    assert len(loaded[0].checksum_sha256) == 64


def test_manifest_preserva_historial_y_actualiza_por_archivo(tmp_path):
    old_file = tmp_path / "antiguo.csv"
    old_file.write_text("codigo,nombre\n001,Antiguo\n", encoding="utf-8")
    updated_old_file = tmp_path / "antiguo_actualizado.csv"
    updated_old_file.write_text("codigo,nombre\n001,Actualizado\n", encoding="utf-8")
    new_file = tmp_path / "nuevo.csv"
    new_file.write_text("codigo,nombre\n002,Nuevo\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"

    old_entry = ManifestEntry(
        archivo="antiguo.csv",
        fuente_url="manual",
        fecha_extraccion="2026-07-12",
        version_dataset="v0.1.0",
        cobertura="disponible: Guatemala",
        departamento="Guatemala",
        metodo="manual",
        checksum_sha256=checksum_sha256(old_file),
    )
    updated_old_entry = ManifestEntry(
        archivo="antiguo.csv",
        fuente_url="manual",
        fecha_extraccion="2026-07-13",
        version_dataset="v0.1.1",
        cobertura="disponible: Guatemala; faltante: no documentado",
        departamento="Guatemala",
        metodo="manual",
        checksum_sha256=checksum_sha256(updated_old_file),
    )
    new_entry = ManifestEntry(
        archivo="nuevo.csv",
        fuente_url="manual",
        fecha_extraccion="2026-07-13",
        version_dataset="v0.2.0",
        cobertura="disponible: Escuintla",
        departamento="Escuintla",
        metodo="manual",
        checksum_sha256=checksum_sha256(new_file),
    )

    write_manifest([old_entry], manifest_path)
    write_manifest([new_entry, updated_old_entry], manifest_path)

    loaded = read_manifest(manifest_path)
    assert [entry.archivo for entry in loaded] == ["antiguo.csv", "nuevo.csv"]
    assert loaded[0] == updated_old_entry
    assert loaded[1] == new_entry


def test_manifest_conserva_archivo_previo_si_replace_atomico_falla(monkeypatch, tmp_path):
    raw_file = tmp_path / "establecimientos.csv"
    raw_file.write_text("codigo,nombre\n001,Original\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    old_entry = ManifestEntry(
        archivo="establecimientos.csv",
        fuente_url="manual",
        fecha_extraccion="2026-07-12",
        version_dataset="v0.1.0",
        cobertura="disponible: Guatemala",
        departamento="Guatemala",
        metodo="manual",
        checksum_sha256=checksum_sha256(raw_file),
    )
    write_manifest([old_entry], manifest_path)
    previous_manifest = manifest_path.read_text(encoding="utf-8")
    new_entry = ManifestEntry(
        archivo="establecimientos.csv",
        fuente_url="manual",
        fecha_extraccion="2026-07-13",
        version_dataset="v0.1.1",
        cobertura="disponible: Guatemala actualizado",
        departamento="Guatemala",
        metodo="manual",
        checksum_sha256=checksum_sha256(raw_file),
    )
    original_replace = Path.replace

    def failing_replace(self, target):
        if Path(target) == manifest_path:
            raise OSError("replace unavailable")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", failing_replace)

    with pytest.raises(OSError, match="replace unavailable"):
        write_manifest([new_entry], manifest_path)

    assert manifest_path.read_text(encoding="utf-8") == previous_manifest
    assert read_manifest(manifest_path) == [old_entry]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["establecimientos.csv", "manifest.json"]
