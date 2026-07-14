"""Adquisición o registro trazable de CSV crudos MINEDUC."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

from .manifest import Manifest, ManifestEntry, checksum_sha256, validate_dataset_version, write_manifest


class AcquisitionError(RuntimeError):
    """Error explícito de adquisición o registro de alcance."""


class InvalidSourceUrlError(AcquisitionError):
    """La URL no pertenece a la fuente oficial esperada."""


class RawFileExistsError(AcquisitionError):
    """La operación intentaría sobrescribir un CSV crudo."""


MINEDUC_BUSCA_ESTABLECIMIENTO_URL = "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/"
MINEDUC_DIVERSIFICADO_LEVEL_CODE = "46"
REQUIRED_WEBFORMS_FIELDS = ("__VIEWSTATE", "__EVENTVALIDATION")


def is_mineduc_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (host == "mineduc.gob.gt" or host.endswith(".mineduc.gob.gt"))


def _validate_source_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise InvalidSourceUrlError("Se requiere HTTPS para descargas automáticas de MINEDUC.")
    if not is_mineduc_url(url):
        raise InvalidSourceUrlError("Se rechaza URL no MINEDUC para datos crudos oficiales.")


def _default_downloader(url: str) -> bytes:
    with urlopen(url, timeout=30) as response:  # noqa: S310 - URL validada contra dominio MINEDUC.
        return response.read()


def _default_form_fetcher(url: str, data: bytes | None = None) -> bytes:
    request = Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0 proyecto1-ds acquisition",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": url,
        },
    )
    with urlopen(request, timeout=60) as response:  # noqa: S310 - URL validada contra dominio MINEDUC.
        return response.read()


def _safe_csv_path(raw_dir: Path, name: str | Path) -> Path:
    path = raw_dir / name if not Path(name).is_absolute() else Path(name)
    raw_root = raw_dir.resolve()
    resolved = path.resolve()
    if raw_root != resolved and raw_root not in resolved.parents:
        raise AcquisitionError("La ruta del CSV crudo debe permanecer dentro de data/raw/.")
    if resolved.suffix.lower() != ".csv":
        raise AcquisitionError("Solo se registran archivos CSV crudos.")
    return resolved


def _safe_raw_artifact_path(raw_dir: Path, name: str | Path, *, suffix: str) -> Path:
    path = raw_dir / name if not Path(name).is_absolute() else Path(name)
    raw_root = raw_dir.resolve()
    resolved = path.resolve()
    if raw_root != resolved and raw_root not in resolved.parents:
        raise AcquisitionError("La ruta del artefacto crudo debe permanecer dentro de data/raw/.")
    if resolved.suffix.lower() != suffix:
        raise AcquisitionError(f"El artefacto crudo debe usar extensión {suffix}.")
    return resolved


def _manual_csv_files(raw_dir: Path, manual_files: list[Path | str] | None) -> list[Path]:
    files = [_safe_csv_path(raw_dir, file) for file in manual_files] if manual_files else _csv_files(raw_dir)
    missing = [file for file in files if not file.exists()]
    if missing:
        names = ", ".join(file.name for file in missing)
        raise AcquisitionError(f"CSV manual no existe dentro de data/raw/: {names}")
    return files


def _csv_files(raw_dir: Path) -> list[Path]:
    return sorted(path.resolve() for path in raw_dir.glob("*.csv") if path.is_file())


def _filename_from_url(source_url: str) -> str:
    name = Path(urlparse(source_url).path).name
    return name if name.endswith(".csv") else "mineduc_raw.csv"


def _format_cobertura(cobertura: str, alcance_faltante: str | None) -> str:
    if not alcance_faltante:
        return cobertura
    return f"{cobertura}; {alcance_faltante}"


def _validate_downloaded_csv_content(content: bytes) -> None:
    if not content or not content.strip():
        raise AcquisitionError("La descarga MINEDUC no contiene contenido CSV válido.")
    sample = content[:2048].lstrip().lower()
    if sample.startswith((b"<html", b"<!doctype html")) or b"<html" in sample or b"</html>" in sample:
        raise AcquisitionError("La descarga MINEDUC parece HTML, no CSV crudo válido.")


def _validate_mineduc_search_html_content(content: bytes) -> None:
    text = content.decode("utf-8", errors="replace")
    if "_ctl0_ContentPlaceHolder1_dgResultado" not in text:
        raise AcquisitionError("La respuesta MINEDUC no contiene la tabla oficial de resultados.")
    if "DIVERSIFICADO" not in text.upper():
        raise AcquisitionError("La respuesta MINEDUC no contiene registros de nivel diversificado.")


class _AspNetFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fields: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "input":
            return
        data = {key: value or "" for key, value in attrs}
        name = data.get("name")
        input_type = data.get("type", "text")
        if name and input_type in {"hidden", "text"}:
            self.fields[name] = data.get("value", "")


def _build_mineduc_diversificado_post_body(initial_html: bytes, department_code: str) -> bytes:
    parser = _AspNetFormParser()
    parser.feed(initial_html.decode("utf-8", errors="replace"))
    fields = dict(parser.fields)
    missing = [field for field in REQUIRED_WEBFORMS_FIELDS if field not in fields]
    if missing:
        raise AcquisitionError(f"El formulario MINEDUC no contiene campos WebForms requeridos: {', '.join(missing)}")
    fields.update(
        {
            "_ctl0:ContentPlaceHolder1:cmbDepartamento": department_code,
            "_ctl0:ContentPlaceHolder1:cmbNivel": MINEDUC_DIVERSIFICADO_LEVEL_CODE,
            "_ctl0:ContentPlaceHolder1:cmbSector": "TODOS",
            "_ctl0:ContentPlaceHolder1:ddlplan": "TODOS",
            "_ctl0:ContentPlaceHolder1:ddlModalidad": "TODOS",
            "_ctl0:ContentPlaceHolder1:txtCodEstab": "",
            "_ctl0:ContentPlaceHolder1:txtNomEstab": "",
            "_ctl0:ContentPlaceHolder1:txtDirecEstab": "",
            "_ctl0:ContentPlaceHolder1:IbtnConsultar.x": "15",
            "_ctl0:ContentPlaceHolder1:IbtnConsultar.y": "10",
        }
    )
    return urlencode(fields).encode("utf-8")


def _write_temp_csv(target: Path, content: bytes) -> Path:
    with NamedTemporaryFile("wb", delete=False, dir=target.parent, prefix=f".{target.name}.", suffix=".tmp") as temp_file:
        temp_file.write(content)
        return Path(temp_file.name)


def _reserved_temp_path(target: Path, suffix: str) -> Path:
    with NamedTemporaryFile("wb", delete=False, dir=target.parent, prefix=f".{target.name}.", suffix=suffix) as temp_file:
        path = Path(temp_file.name)
    path.unlink(missing_ok=True)
    return path


def _write_download_and_manifest(target: Path, temp_target: Path, entries: Manifest, manifest_path: Path) -> Manifest:
    backup_target: Path | None = None
    manifest_backup: Path | None = None
    raw_replaced = False
    preserve_target_backup = False
    preserve_manifest_backup = False
    manifest_persist_error: Exception | None = None

    try:
        if manifest_path.exists():
            manifest_backup = _reserved_temp_path(manifest_path, ".manifest.backup")
            try:
                shutil.copy2(manifest_path, manifest_backup)
            except Exception as exc:
                raise AcquisitionError(
                    f"Falló la preparación del backup del manifest; se conservó el artefacto crudo original: {exc}"
                ) from exc

        if target.exists():
            backup_target = _reserved_temp_path(target, ".backup")
            target.replace(backup_target)

        temp_target.replace(target)
        raw_replaced = True
        try:
            return write_manifest(entries, manifest_path)
        except Exception as exc:
            manifest_persist_error = exc
            raise
    except Exception as exc:
        if raw_replaced:
            try:
                _rollback_target_after_manifest_failure(target, backup_target)
                raw_replaced = False
            except AcquisitionError as rollback_error:
                preserve_target_backup = True
                raise rollback_error from exc
            try:
                _rollback_manifest_after_manifest_failure(manifest_path, manifest_backup)
            except AcquisitionError as rollback_error:
                preserve_manifest_backup = True
                raise rollback_error from exc
            if manifest_persist_error is not None:
                raise AcquisitionError(
                    "Falló la persistencia del manifest; se restauró el artefacto crudo original "
                    f"y el manifest previo: {manifest_persist_error}"
                ) from manifest_persist_error
        elif backup_target and backup_target.exists() and not target.exists():
            try:
                backup_target.replace(target)
            except Exception as restore_error:
                preserve_target_backup = True
                raise _manual_recovery_error("artefacto crudo", target, backup_target, restore_error) from restore_error
        raise
    finally:
        if temp_target.exists():
            temp_target.unlink()
        if backup_target and backup_target.exists() and not preserve_target_backup:
            backup_target.unlink()
        if manifest_backup and manifest_backup.exists() and not preserve_manifest_backup:
            manifest_backup.unlink()


def _rollback_target_after_manifest_failure(target: Path, backup_target: Path | None) -> None:
    if backup_target and backup_target.exists():
        try:
            backup_target.replace(target)
        except Exception as exc:
            raise _manual_recovery_error("artefacto crudo", target, backup_target, exc) from exc
    elif target.exists():
        target.unlink()


def _rollback_manifest_after_manifest_failure(manifest_path: Path, manifest_backup: Path | None) -> None:
    if manifest_backup and manifest_backup.exists():
        try:
            manifest_backup.replace(manifest_path)
        except Exception as exc:
            raise _manual_recovery_error("manifest.json", manifest_path, manifest_backup, exc) from exc
    elif manifest_path.exists():
        manifest_path.unlink()


def _manual_recovery_error(artifact_kind: str, target: Path, backup: Path, cause: Exception) -> AcquisitionError:
    return AcquisitionError(
        f"Falló la restauración de {artifact_kind} desde backup; se preservó el backup para "
        f"recuperación manual. destino={target.name}; backup={backup.name}; causa={cause}"
    )


def acquire_or_register_raw(
    raw_dir: Path | str = Path("data/raw"),
    *,
    source_url: str | None = None,
    output_filename: str | None = None,
    manual_files: list[Path | str] | None = None,
    extraction_date: str | None = None,
    version_dataset: str = "v0.1.0",
    cobertura: str = "Alcance disponible registrado",
    alcance_faltante: str | None = None,
    departamento: str | None = None,
    allow_overwrite: bool = False,
    downloader: Callable[[str], bytes] | None = None,
) -> Manifest:
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    extraction_date = extraction_date or date.today().isoformat()
    validate_dataset_version(version_dataset)
    downloader = downloader or _default_downloader
    cobertura_documentada = _format_cobertura(cobertura, alcance_faltante)

    if source_url:
        _validate_source_url(source_url)

    acquisition_error: str | None = None
    if source_url:
        target: Path | None = None
        content: bytes | None = None
        try:
            target = _safe_csv_path(raw_path, output_filename or _filename_from_url(source_url))
            if target.exists() and not allow_overwrite:
                raise RawFileExistsError(f"No se puede sobrescribir CSV crudo existente: {target.name}")
            content = downloader(source_url)
            _validate_downloaded_csv_content(content)
        except RawFileExistsError:
            raise
        except AcquisitionError as exc:
            acquisition_error = str(exc)
        except Exception as exc:  # fallback manual permitido por la spec
            acquisition_error = str(exc)
        if acquisition_error is None and target is not None and content is not None:
            temp_target = _write_temp_csv(target, content)
            try:
                temp_checksum = checksum_sha256(temp_target)
                entries = [
                    _entry(
                        target,
                        raw_path,
                        source_url,
                        extraction_date,
                        version_dataset,
                        cobertura_documentada,
                        departamento,
                        "automatica",
                        checksum=temp_checksum,
                    )
                ]
                return _write_download_and_manifest(target, temp_target, entries, raw_path / "manifest.json")
            finally:
                if temp_target.exists():
                    temp_target.unlink()
        if allow_overwrite and output_filename and target is not None and target.exists() and manual_files is None:
            raise AcquisitionError(acquisition_error or "La descarga MINEDUC no contiene CSV válido.")
    else:
        acquisition_error = "alcance faltante: no se indicó URL oficial MINEDUC"

    files = _manual_csv_files(raw_path, manual_files)
    if not files:
        raise AcquisitionError(f"alcance faltante: no hay CSV crudos manuales para registrar ({acquisition_error}).")

    entries = [
        _entry(
            file,
            raw_path,
            source_url or "manual",
            extraction_date,
            version_dataset,
            cobertura_documentada,
            departamento,
            "manual",
            acquisition_error,
        )
        for file in files
    ]
    return write_manifest(entries, raw_path / "manifest.json")


def capture_mineduc_diversificado_html(
    raw_dir: Path | str = Path("data/raw"),
    *,
    department_code: str,
    department_name: str,
    source_url: str = MINEDUC_BUSCA_ESTABLECIMIENTO_URL,
    output_filename: str | None = None,
    extraction_date: str | None = None,
    version_dataset: str = "v0.1.0",
    allow_overwrite: bool = False,
    fetcher: Callable[[str, bytes | None], bytes] | None = None,
) -> Manifest:
    """Captura el HTML oficial de Busca Establecimiento para diversificado.

    MINEDUC no expone un enlace CSV visible en la página pública. Este helper conserva
    el HTML de resultados como artefacto crudo y lo registra sin etiquetarlo como CSV.
    """

    _validate_source_url(source_url)
    if not re.fullmatch(r"[0-9A-Za-z_-]+", department_code):
        raise AcquisitionError("El código de departamento MINEDUC contiene caracteres no permitidos.")
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    extraction_date = extraction_date or date.today().isoformat()
    validate_dataset_version(version_dataset)
    fetcher = fetcher or _default_form_fetcher
    target_name = output_filename or f"mineduc_busca_establecimiento_diversificado_{department_code}.html"
    target = _safe_raw_artifact_path(raw_path, target_name, suffix=".html")
    if target.exists() and not allow_overwrite:
        raise RawFileExistsError(f"No se puede sobrescribir artefacto crudo existente: {target.name}")

    try:
        initial_html = fetcher(source_url, None)
    except Exception as exc:
        raise AcquisitionError(f"Falló la captura HTML de MINEDUC: {exc}") from exc
    post_body = _build_mineduc_diversificado_post_body(initial_html, department_code)
    try:
        result_html = fetcher(source_url, post_body)
    except Exception as exc:
        raise AcquisitionError(f"Falló la captura HTML de MINEDUC: {exc}") from exc
    _validate_mineduc_search_html_content(result_html)
    temp_target = _write_temp_csv(target, result_html)
    temp_checksum = checksum_sha256(temp_target)
    entries = [
        _entry(
            target,
            raw_path,
            source_url,
            extraction_date,
            version_dataset,
            f"NIVEL ESCOLAR: DIVERSIFICADO; departamento: {department_name}; "
            "CSV directo no disponible en la página pública; artefacto fuente preservado como HTML.",
            department_name,
            "html-form",
            error="sin CSV directo visible en la página oficial",
            checksum=temp_checksum,
        )
    ]
    return _write_download_and_manifest(target, temp_target, entries, raw_path / "manifest.json")


def _entry(
    path: Path,
    raw_dir: Path,
    source_url: str,
    extraction_date: str,
    version_dataset: str,
    cobertura: str,
    departamento: str | None,
    metodo: str,
    error: str | None = None,
    checksum: str | None = None,
) -> ManifestEntry:
    return ManifestEntry(
        archivo=path.relative_to(raw_dir.resolve()).as_posix(),
        fuente_url=source_url,
        fecha_extraccion=extraction_date,
        version_dataset=version_dataset,
        cobertura=cobertura,
        departamento=departamento,
        metodo=metodo,
        checksum_sha256=checksum or checksum_sha256(path),
        error_adquisicion=error,
    )
