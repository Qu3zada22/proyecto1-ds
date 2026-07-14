"""Consolidación cruda sin limpieza de artefactos MINEDUC."""

from __future__ import annotations

import csv
from html.parser import HTMLParser
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from .manifest import Manifest, ManifestEntry, read_manifest


DEFAULT_OUTPUT_PATH = Path("data/interim/establecimientos_diversificado_raw_unificado.csv")
RESULT_TABLE_ID = "_ctl0_ContentPlaceHolder1_dgResultado"
PROVENANCE_COLUMNS = ["archivo_origen", "departamento_origen"]
NO_RESULTS_MARKERS = (
    "no se encontraron registros",
    "no se encontraron resultados",
    "no existen registros",
    "no hay registros",
    "sin resultados",
)


class ConsolidationError(RuntimeError):
    """Error explícito durante la consolidación cruda."""


def consolidate_raw(
    manifest: Manifest | None = None,
    *,
    raw_dir: Path | str = Path("data/raw"),
    manifest_path: Path | str | None = None,
    output_path: Path | str = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Une artefactos crudos compatibles en un CSV intermedio.

    La función solo hace transformación estructural: lee CSV o tablas HTML oficiales,
    alinea columnas compatibles por encabezado normalizado para comparación y agrega
    columnas de procedencia. No corrige ni limpia valores fuente.
    """

    raw_root = Path(raw_dir)
    entries = manifest if manifest is not None else _read_manifest_for_consolidation(Path(manifest_path) if manifest_path else raw_root / "manifest.json")
    if not entries:
        raise ConsolidationError("No hay artefactos crudos registrados en el manifest para consolidar.")

    batches = [_read_entry(entry, raw_root) for entry in entries]
    base_header = batches[0].header
    base_key_to_header = _header_key_map(base_header, batches[0].entry.archivo)
    base_keys = list(base_key_to_header)
    expected_keys = set(base_keys)

    for batch in batches[1:]:
        keys = set(_header_key_map(batch.header, batch.entry.archivo))
        if keys != expected_keys:
            raise ConsolidationError(
                f"columnas incompatibles en {batch.entry.archivo}; "
                f"esperadas={sorted(expected_keys)}; recibidas={sorted(keys)}"
            )

    output_rows: list[dict[str, str]] = []
    for batch in batches:
        row_key_to_header = _header_key_map(batch.header, batch.entry.archivo)
        for row in batch.rows:
            output_row = {header: row[row_key_to_header[key]] for key, header in zip(base_keys, base_header, strict=True)}
            output_row["archivo_origen"] = batch.entry.archivo
            output_row["departamento_origen"] = batch.entry.departamento or "pendiente"
            output_rows.append(output_row)

    destination = Path(output_path)
    _write_csv_atomic(destination, base_header + PROVENANCE_COLUMNS, output_rows)
    return destination


def _read_manifest_for_consolidation(path: Path) -> Manifest:
    try:
        return read_manifest(path)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ConsolidationError(f"Manifest inválido en {path}: {exc}") from exc


def _write_csv_atomic(destination: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with NamedTemporaryFile(
            "w",
            delete=False,
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            temp_path = Path(csv_file.name)
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            csv_file.flush()
        temp_path.replace(destination)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


class _RawBatch:
    def __init__(self, entry: ManifestEntry, header: list[str], rows: list[dict[str, str]]) -> None:
        self.entry = entry
        self.header = header
        self.rows = rows


def _read_entry(entry: ManifestEntry, raw_dir: Path) -> _RawBatch:
    path = _resolve_raw_path(raw_dir, entry.archivo)
    _validate_checksum(entry, path)
    if entry.metodo == "html-form" or path.suffix.lower() == ".html":
        header, rows = _extract_html_result_table(path)
    else:
        header, rows = _read_csv_table(path)
    return _RawBatch(entry, header, rows)


def _resolve_raw_path(raw_dir: Path, archivo: str) -> Path:
    raw_root = raw_dir.resolve()
    path = (raw_root / archivo).resolve()
    if raw_root != path and raw_root not in path.parents:
        raise ConsolidationError(f"Artefacto fuera de data/raw rechazado: {archivo}")
    if not path.exists():
        raise ConsolidationError(f"Artefacto crudo no existe: {archivo}")
    return path


def _read_csv_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, strict=True)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise ConsolidationError(f"CSV sin encabezados: {path.name}") from exc
            if not header:
                raise ConsolidationError(f"CSV sin encabezados: {path.name}")
            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(header):
                    raise ConsolidationError(
                        f"CSV crudo malformado en {path.name}: fila {line_number} "
                        f"tiene {len(row)} columnas; se esperaban {len(header)}."
                    )
                rows.append(dict(zip(header, row, strict=True)))
            return header, rows
    except csv.Error as exc:
        raise ConsolidationError(f"CSV crudo malformado en {path.name}: {exc}") from exc


def _extract_html_result_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    parser = _ResultTableParser()
    html = path.read_text(encoding="utf-8")
    parser.feed(html)
    parser.close()
    parser.validate_complete(path.name)
    if not parser.rows:
        raise ConsolidationError(f"No se encontró tabla oficial de resultados en {path.name}")
    header = parser.rows[0]
    data_rows = parser.rows[1:]
    if not header:
        raise ConsolidationError(f"Tabla oficial de resultados sin encabezados en {path.name}")
    rows = [_row_from_cells(header, cells, path.name) for cells in data_rows if _row_has_real_data(cells)]
    if not rows and not _has_official_no_results_marker(html):
        raise ConsolidationError(
            f"Tabla oficial de resultados sin filas de datos y sin marcador oficial de cero resultados en {path.name}"
        )
    return header, rows


def _validate_checksum(entry: ManifestEntry, path: Path) -> None:
    from .manifest import checksum_sha256

    try:
        actual_checksum = checksum_sha256(path)
    except OSError as exc:
        raise ConsolidationError(f"No se pudo calcular checksum_sha256 de {entry.archivo}: {exc}") from exc
    if actual_checksum != entry.checksum_sha256:
        raise ConsolidationError(
            f"checksum_sha256 no coincide para {entry.archivo}; "
            f"manifest={entry.checksum_sha256}; actual={actual_checksum}"
        )


def _row_has_real_data(cells: list[str]) -> bool:
    return any(cell.strip() for cell in cells)


def _has_official_no_results_marker(html: str) -> bool:
    normalized = " ".join(html.casefold().split())
    return any(marker in normalized for marker in NO_RESULTS_MARKERS)


def _row_from_cells(header: list[str], cells: list[str], filename: str) -> dict[str, str]:
    if len(cells) != len(header):
        raise ConsolidationError(
            f"Fila HTML con cantidad de celdas incompatible en {filename}; "
            f"esperadas={len(header)}; recibidas={len(cells)}"
        )
    return dict(zip(header, cells, strict=True))


class _ResultTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._table_depth = 0
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "table" and self._table_depth == 0 and data.get("id") == RESULT_TABLE_ID:
            self._table_depth = 1
            return
        if self._table_depth == 0:
            return
        if tag == "table":
            self._table_depth += 1
        elif tag == "tr" and self._current_row is None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_cell is None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._table_depth == 0:
            return
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append("".join(self._current_cell))
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = None
        elif tag == "table":
            self._table_depth -= 1

    def validate_complete(self, filename: str) -> None:
        if self._current_cell is not None or self._current_row is not None:
            raise ConsolidationError(f"HTML incompleto: fila abierta en tabla oficial de resultados de {filename}")
        if self._table_depth > 0:
            raise ConsolidationError(f"HTML incompleto: tabla oficial de resultados abierta en {filename}")


def _header_key_map(header: list[str], filename: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for column in header:
        key = _normalize_header(column)
        if key in mapping:
            raise ConsolidationError(f"Encabezado duplicado tras normalización en {filename}: {column!r}")
        mapping[key] = column
    return mapping


def _normalize_header(value: str) -> str:
    return " ".join(value.split()).casefold()
