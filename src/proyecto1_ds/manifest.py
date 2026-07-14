"""Lectura y escritura del manifest de datos crudos."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from tempfile import NamedTemporaryFile

VERSION_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
MANIFEST_PATH = Path("data/raw/manifest.json")


def validate_dataset_version(version: str) -> str:
    if not VERSION_PATTERN.match(version):
        raise ValueError("version_dataset debe usar formato vMAJOR.MINOR.PATCH")
    return version


def next_dataset_version(current: str, change: str) -> str:
    validate_dataset_version(current)
    major, minor, patch = map(int, VERSION_PATTERN.match(current).groups())  # type: ignore[union-attr]
    if change in {"metadata", "metadatos", "patch"}:
        patch += 1
    elif change in {"dataset", "files", "fecha", "cobertura", "minor"}:
        minor += 1
        patch = 0
    elif change in {"major", "incompatible"}:
        major += 1
        minor = patch = 0
    else:
        raise ValueError("change debe ser metadata, dataset o major")
    return f"v{major}.{minor}.{patch}"


def checksum_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class ManifestEntry:
    archivo: str
    fuente_url: str
    fecha_extraccion: str
    version_dataset: str
    cobertura: str
    departamento: str | None
    metodo: str
    checksum_sha256: str
    error_adquisicion: str | None = None

    def __post_init__(self) -> None:
        validate_dataset_version(self.version_dataset)
        required = {
            "archivo": self.archivo,
            "fuente_url": self.fuente_url,
            "fecha_extraccion": self.fecha_extraccion,
            "cobertura": self.cobertura,
            "metodo": self.metodo,
            "checksum_sha256": self.checksum_sha256,
        }
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise ValueError(f"Campos obligatorios faltantes en manifest: {', '.join(missing)}")
        if not re.fullmatch(r"[0-9a-f]{64}", self.checksum_sha256):
            raise ValueError("checksum_sha256 debe ser hexadecimal SHA-256")

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> "ManifestEntry":
        return cls(**data)


Manifest = list[ManifestEntry]


def read_manifest(path: Path = MANIFEST_PATH) -> Manifest:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["lotes"] if isinstance(data, dict) else data
    return [ManifestEntry.from_dict(row) for row in rows]


def write_manifest(entries: Manifest, path: Path = MANIFEST_PATH) -> Manifest:
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = {entry.archivo: entry for entry in read_manifest(path)}
    for entry in entries:
        merged[entry.archivo] = entry
    updated_entries = [merged[archivo] for archivo in sorted(merged)]
    payload = {"lotes": [entry.to_dict() for entry in updated_entries]}
    _write_text_atomic(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return updated_entries


def _write_text_atomic(path: Path, content: str) -> None:
    temp_path: Path | None = None
    try:
        with NamedTemporaryFile("w", delete=False, dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", encoding="utf-8") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            temp_path = Path(temp_file.name)
        temp_path.replace(path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
