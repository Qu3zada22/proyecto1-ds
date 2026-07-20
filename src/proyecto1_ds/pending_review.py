"""Recomendaciones reproducibles para pendientes, sin transformar datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
import os
from pathlib import Path
import re
import shutil
from typing import Any
import unicodedata

from proyecto1_ds.duplicates import CANDIDATE_FIELDS, VALID_DECISIONS, detect_partial_duplicates
from proyecto1_ds.territorial import INCONSISTENCY_FIELDS, validate_territorial


DEFAULT_CLEAN_CSV = Path("data/processed/establecimientos_diversificado_limpio.csv")
DEFAULT_CANDIDATES_CSV = Path("outputs/tablas/duplicados_parciales.csv")
DEFAULT_TERRITORY_CSV = Path("outputs/tablas/inconsistencias_territoriales.csv")
DEFAULT_CATALOG_CSV = Path("data/reference/catalogo_territorial.csv")
DEFAULT_TABLES_DIR = Path("outputs/tablas")
DEFAULT_REPORTS_DIR = Path("outputs/reportes")

DUPLICATE_FIELDS = [
    "codigo_a", "codigo_b", "recomendacion", "confianza", "razones", "evidencia_faltante",
]
PHONE_FIELDS = [
    "CODIGO", "valor", "grupo_vigente", "patron", "recomendacion", "propuesta", "razon",
]
TERRITORY_FIELDS = [
    "departamento_mineduc", "municipio_mineduc", "municipio_catalogo", "filas",
    "municipio_codigo_catalogo", "recomendacion", "evidencia_mineduc_codigo", "confianza",
    "nota_no_renombrar",
]

# Tabla de decisión v1. Cada par conserva dos registros porque el nombre identifica una sede
# explícita y la dirección difiere. No se generaliza esta decisión a nombres parecidos.
INDEPENDENT_PAIR_DECISIONS_V1 = {
    ("00-19-0077-46", "00-19-0085-46"): (
        'COLEGIO EDUCATIVO "LICDA. KIMBERLY MAZARIEGOS ENRÍQUEZ NO. 1"',
        'COLEGIO EDUCATIVO "LICDA. KIMBERLY MAZARIEGOS ENRIQUEZ NO. 3"',
    ),
    ("00-18-0149-46", "00-18-0212-46"): ("COLEGIO BELLO AMANECER", "COLEGIO BELLO AMANECER 2"),
    ("01-15-0582-46", "01-15-0623-46"): ("LICEO INTERCULTURAL DE GUATEMALA II", "LICEO INTERCULTURAL DE GUATEMALA"),
    ("01-15-0584-46", "01-15-0803-46"): ("LICEO INTERCULTURAL DE GUATEMALA II", "LICEO INTERCULTURAL DE GUATEMALA"),
    ("22-11-0095-46", "22-11-0096-46"): (
        'INSTITUTO PARTICULAR DE FORMACIÓN Y DESARROLLO PROFESIONAL "INDEFORP"',
        'INSTITUTO PARTICULAR FORMACIÓN Y DESARROLLO PROFESIONAL "INDEFORP II"',
    ),
    ("01-15-0270-46", "01-15-0757-46"): ("LICEO PIERRE DE FERMAT", "LICEO PIERRE DE FERMAT II"),
    ("01-14-0157-46", "01-14-0169-46"): ("LICEO CRISTIANO BETH SHALOM SUR", "LICEO CRISTIANO BETH SHALOM"),
    ("01-08-0737-46", "01-08-0986-46"): (
        'LICEO TECNOLÓGICO DE GUATEMALA "ELOHIM"',
        'LICEO TECNOLOGICO DE GUATEMALA "ELOHIM" NO. 2',
    ),
    ("01-08-0739-46", "01-08-0986-46"): (
        'LICEO TECNOLÓGICO DE GUATEMALA "ELOHIM"',
        'LICEO TECNOLOGICO DE GUATEMALA "ELOHIM" NO. 2',
    ),
    ("00-01-0641-46", "00-01-9594-46"): ("LICEO TECNOLÓGICO MAYA DE GUATEMALA II", "LICEO TECNÓLOGICO MAYA DE GUATEMALA"),
    ("00-01-0646-46", "00-01-9595-46"): ("LICEO TECNOLÓGICO MAYA DE GUATEMALA II", "LICEO TECNÓLOGICO MAYA DE GUATEMALA"),
}

# La clave es la etiqueta preservada por MINEDUC; el valor es el código que debe corroborarse.
TERRITORY_ALIAS_DECISIONS_V1 = {
    ("QUICHE", "IXCAN"): "1420",
    ("QUICHE", "NEBAJ"): "1413",
    ("ALTA VERAPAZ", "LA TINTA"): "1616",
    ("QUETZALTENANGO", "GENOVA COSTA CUCA"): "921",
    ("ALTA VERAPAZ", "LANQUIN"): "1611",
    ("SACATEPEQUEZ", "ALOTENANGO"): "314",
    ("QUETZALTENANGO", "OLINTEPEQUE"): "903",
}


class PendingReviewError(ValueError):
    """Entrada inválida o evidencia que ya no corresponde a los datos vigentes."""


@dataclass(frozen=True)
class PendingReviewOutputs:
    duplicates_path: Path
    phones_path: Path
    territory_path: Path
    report_path: Path


def generate_pending_review(
    clean_csv: Path | str = DEFAULT_CLEAN_CSV,
    candidates_csv: Path | str = DEFAULT_CANDIDATES_CSV,
    territory_csv: Path | str = DEFAULT_TERRITORY_CSV,
    catalog_csv: Path | str = DEFAULT_CATALOG_CSV,
    *,
    tables_dir: Path | str = DEFAULT_TABLES_DIR,
    reports_dir: Path | str = DEFAULT_REPORTS_DIR,
    project_root: Path | str = Path.cwd(),
) -> PendingReviewOutputs:
    """Valida evidencia vigente y publica recomendaciones sin aplicar cambios."""

    clean_path = Path(clean_csv)
    candidates_path = Path(candidates_csv)
    territory_path = Path(territory_csv)
    catalog_path = Path(catalog_csv)
    clean_header, clean_rows = _read_csv(clean_path)
    if len(clean_rows) != 11_867 or len({row.get("CODIGO", "") for row in clean_rows}) != len(clean_rows):
        raise PendingReviewError(f"Dataset limpio stale o con códigos inválidos: {clean_path}")
    required_clean = {"CODIGO", "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "DEPARTAMENTO", "MUNICIPIO", "municipio_codigo"}
    if not required_clean.issubset(clean_header):
        raise PendingReviewError(f"Dataset limpio malformado, faltan columnas: {clean_path}")

    candidate_header, candidate_rows = _read_csv(candidates_path)
    territorial_header, territorial_rows = _read_csv(territory_path)
    catalog_header, catalog_rows = _read_csv(catalog_path)
    if candidate_header != CANDIDATE_FIELDS or territorial_header != INCONSISTENCY_FIELDS:
        raise PendingReviewError("Evidencia malformada: encabezado no canónico")
    if catalog_header != ["departamento_codigo", "departamento", "municipio_codigo", "municipio"]:
        raise PendingReviewError(f"Catálogo malformado: {catalog_path}")
    _validate_lineage(clean_path, candidates_path, candidate_rows, catalog_path, territory_path, territorial_rows)

    by_code = {row["CODIGO"]: row for row in clean_rows}
    duplicate_recommendations = _recommend_duplicates(candidate_rows, by_code)
    phone_recommendations = _recommend_phones(clean_rows)
    territorial_recommendations = _recommend_territory(territorial_rows, clean_rows, catalog_rows)
    _validate_totals(duplicate_recommendations, phone_recommendations, territorial_recommendations)

    tables_root = Path(tables_dir)
    reports_root = Path(reports_dir)
    outputs = PendingReviewOutputs(
        duplicates_path=tables_root / "recomendaciones_duplicados.csv",
        phones_path=tables_root / "recomendaciones_telefonos.csv",
        territory_path=tables_root / "recomendaciones_territorio.csv",
        report_path=reports_root / "revision_pendientes.md",
    )
    contents = {
        outputs.duplicates_path: _csv_bytes(DUPLICATE_FIELDS, duplicate_recommendations),
        outputs.phones_path: _csv_bytes(PHONE_FIELDS, phone_recommendations),
        outputs.territory_path: _csv_bytes(TERRITORY_FIELDS, territorial_recommendations),
        outputs.report_path: _render_report(project_root=Path(project_root)).encode(),
    }
    _replace_outputs(contents)
    return outputs


def _recommend_duplicates(candidates: list[dict[str, str]], by_code: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    pending = [row for row in candidates if row["decision"] in {"duplicado_probable", "revisar"}]
    recommendations: list[dict[str, str]] = []
    for candidate in pending:
        key = tuple(sorted((candidate["codigo_a"], candidate["codigo_b"])))
        record_a, record_b = (by_code.get(code) for code in key)
        if record_a is None or record_b is None:
            raise PendingReviewError(f"Evidencia de duplicados stale: código ausente {key}")
        recommendation = "requiere_fuente_institucional"
        reasons = (
            "La coincidencia local produjo un candidato, pero dos códigos distintos no prueban duplicación registral, "
            "sustitución ni equivalencia. La etiqueta de triage solo define el alcance y no se usa como conclusión."
        )
        missing = "Fichas MINEDUC de ambos códigos con oferta, sede, vigencia y acto de alta, baja, sustitución o equivalencia."
        recommendations.append({
            "codigo_a": key[0], "codigo_b": key[1], "recomendacion": recommendation,
            "confianza": "alta", "razones": reasons, "evidencia_faltante": missing,
        })
    return recommendations


def _recommend_phones(clean_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in clean_rows:
        value = record["TELEFONO"]
        if not value or value.isdigit() and len(value) == 8:
            continue
        group = "numerico_longitud_incorrecta" if value.isdigit() else "no_numerico"
        formatted = re.fullmatch(r"(\d{4})-(\d{4})", value)
        repeated = re.fullmatch(r"(\d{8})-\1", value)
        if formatted:
            pattern, recommendation = "telefono_unico_formateado_4_4", "normalizacion_segura"
            proposal = "".join(formatted.groups())
            reason = "El único separador divide inequívocamente un teléfono de 8 dígitos en 4+4."
        elif repeated:
            pattern, recommendation = "telefono_repetido_identico", "normalizacion_segura"
            proposal = repeated.group(1)
            reason = "Los dos segmentos son el mismo teléfono válido; deduplicarlo no elimina otro contacto."
        elif value.isdigit() and len(value) == 16:
            pattern, recommendation = "posible_concatenacion_de_dos_telefonos", "conservar_y_documentar"
            proposal = f"{value[:8]} | {value[8:]} (solo referencia)"
            reason = "Admite una partición 8+8, pero el original no contiene separador y no debe alterarse."
        elif value.isdigit():
            pattern, recommendation = f"numerico_longitud_{len(value)}", "requiere_fuente_institucional"
            proposal = "Sin transformación automática"
            reason = "La longitud no permite inferir de forma inequívoca un teléfono válido de 8 dígitos."
        else:
            pattern, recommendation = "formato_no_numerico_con_estructura", "conservar_y_documentar"
            proposal = "Conservar íntegro; interpretar con fuente institucional"
            reason = "Separadores o texto pueden preservar múltiples contactos, extensiones o estructura histórica útil."
        rows.append({
            "CODIGO": record["CODIGO"], "valor": value, "grupo_vigente": group, "patron": pattern,
            "recomendacion": recommendation, "propuesta": proposal, "razon": reason,
        })
    return rows


def _recommend_territory(
    inconsistencies: list[dict[str, str]], clean_rows: list[dict[str, str]], catalog_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    catalog = {
        (_normalize(row["departamento"]), row["municipio_codigo"]): row["municipio"]
        for row in catalog_rows
    }
    results: list[dict[str, str]] = []
    found: set[tuple[str, str]] = set()
    for issue in inconsistencies:
        key = (issue["departamento"], issue["municipio"])
        expected_code = TERRITORY_ALIAS_DECISIONS_V1.get(key)
        if expected_code is None or issue["decision"] != "revisar":
            raise PendingReviewError(f"Tabla territorial stale para {key}")
        matching = [row for row in clean_rows if (row["DEPARTAMENTO"], row["MUNICIPIO"]) == key]
        if len(matching) != int(issue["filas"]) or any(row["municipio_codigo"] != expected_code for row in matching):
            raise PendingReviewError(f"Asignación territorial stale para {key}")
        if any(_municipality_code(row["CODIGO"]) != expected_code for row in matching):
            raise PendingReviewError(f"Código MINEDUC no corrobora territorio para {key}")
        catalog_name = catalog.get((_normalize(key[0]), expected_code))
        if catalog_name is None or _normalize(catalog_name) != _normalize(issue["sugerencia_oficial"]):
            raise PendingReviewError(f"Catálogo territorial stale para {key}")
        found.add(key)
        results.append({
            "departamento_mineduc": key[0], "municipio_mineduc": key[1],
            "municipio_catalogo": catalog_name, "filas": issue["filas"],
            "municipio_codigo_catalogo": expected_code,
            "recomendacion": "alias_confirmable_por_catalogo",
            "evidencia_mineduc_codigo": f"Las {issue['filas']} filas MINEDUC usan segmento municipal {expected_code} y el limpio conserva ese código.",
            "confianza": "alta",
            "nota_no_renombrar": "Conservar texto MINEDUC; el alias habilita unión por código, no un renombre automático.",
        })
    if found != set(TERRITORY_ALIAS_DECISIONS_V1):
        raise PendingReviewError("Tabla territorial stale respecto de las siete parejas vigentes")
    return results


def _validate_lineage(
    clean: Path, candidates_path: Path, candidates: list[dict[str, str]], catalog: Path,
    territory_path: Path, territory: list[dict[str, str]],
) -> None:
    expected_candidates = detect_partial_duplicates(clean).candidates
    compared_candidate_fields = CANDIDATE_FIELDS[:-1]
    if [_signature(row, compared_candidate_fields) for row in candidates] != [
        _signature(row, compared_candidate_fields) for row in expected_candidates
    ]:
        raise PendingReviewError(f"Evidencia de duplicados stale: {candidates_path}")
    if any(row["decision"] not in VALID_DECISIONS for row in candidates):
        raise PendingReviewError(f"Decisión de duplicados inválida: {candidates_path}")
    expected_territory = validate_territorial(clean, catalog_csv=catalog).inconsistencies
    if [_signature(row, INCONSISTENCY_FIELDS) for row in territory] != [
        _signature(row, INCONSISTENCY_FIELDS) for row in expected_territory
    ]:
        raise PendingReviewError(f"Evidencia territorial stale: {territory_path}")


def _validate_totals(duplicates: list[dict[str, str]], phones: list[dict[str, str]], territory: list[dict[str, str]]) -> None:
    duplicate_counts = _counts(duplicates)
    phone_counts = _counts(phones)
    if len(duplicates) != 978 or duplicate_counts != {"requiere_fuente_institucional": 978}:
        raise PendingReviewError(f"Conteos de duplicados stale: {duplicate_counts}")
    if len(phones) != 245 or phone_counts != {"conservar_y_documentar": 196, "requiere_fuente_institucional": 49}:
        raise PendingReviewError(f"Conteos telefónicos stale: {phone_counts}")
    if len(territory) != 7 or sum(int(row["filas"]) for row in territory) != 145:
        raise PendingReviewError("Conteos territoriales stale")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            raw = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as exc:
        raise PendingReviewError(f"CSV malformado o ilegible: {path}: {exc}") from exc
    if not raw or not raw[0] or len(raw[0]) != len(set(raw[0])) or any(len(row) != len(raw[0]) for row in raw[1:]):
        raise PendingReviewError(f"CSV malformado: {path}")
    return raw[0], [dict(zip(raw[0], row, strict=True)) for row in raw[1:]]


def _municipality_code(code: str) -> str:
    parts = code.split("-")
    if len(parts) != 4 or not parts[0].isdigit() or not parts[1].isdigit():
        raise PendingReviewError(f"Código MINEDUC malformado: {code}")
    return str(int(parts[0]) * 100 + int(parts[1]))


def _normalize(value: str) -> str:
    return " ".join(
        "".join(char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)).upper().split()
    )


def _signature(row: dict[str, Any], fields: list[str]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in fields)


def _counts(rows: list[dict[str, str]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        result[row["recomendacion"]] = result.get(row["recomendacion"], 0) + 1
    return result


def _csv_bytes(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: _safe_csv_output(row[field]) for field in fields} for row in rows)
    return buffer.getvalue().encode()


def _safe_csv_output(value: str) -> str:
    return "'" + value if value.startswith(("=", "+", "-", "@")) else value


def _replace_outputs(contents: dict[Path, bytes]) -> None:
    staged = {path: path.with_name(f".{path.name}.{os.getpid()}.tmp") for path in contents}
    backups = {path: path.with_name(f".{path.name}.{os.getpid()}.backup") for path in contents}
    existed = {path: path.exists() for path in contents}
    backed_up: set[Path] = set()
    try:
        for path, content in contents.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            staged[path].write_bytes(content)
        for path in contents:
            if existed[path]:
                shutil.copyfile(path, backups[path])
                backed_up.add(path)
        for path in contents:
            staged[path].replace(path)
    except OSError:
        for path in reversed(contents):
            if path in backed_up:
                backups[path].replace(path)
            elif not existed[path]:
                path.unlink(missing_ok=True)
        raise
    finally:
        for path in (*staged.values(), *backups.values()):
            path.unlink(missing_ok=True)


def _render_report(*, project_root: Path) -> str:
    del project_root  # Las rutas documentadas son deliberadamente relativas al repositorio.
    return """# Recomendaciones para revisión pendiente

Estas recomendaciones **no equivalen a aprobación institucional**. No se modificó ni fusionó ningún dataset; las salidas organizan evidencia vigente para revisión.

## Ruta rápida

```bash
uv run python scripts/revisar_pendientes.py
```

## Resultados

| Unidad auditable | Resultado | Límite |
|---|---:|---|
| Duplicados, un par pendiente por fila | 978 | 0 duplicados confirmables localmente; 0 independientes adicionales; 978 requieren fuente institucional. |
| Teléfonos, un establecimiento pendiente por fila | 245 | 0 propuestas seguras restantes; 196 conservar/documentar; 49 requieren fuente institucional. |
| Territorio, una pareja por fila | 7 parejas territoriales (145 filas) | Alias confirmable para unión por código; 0 renombres automáticos. |

## Reglas

- Duplicados: 11 pares aprobados viven en `data/decisions/duplicados_aprobados.csv` y quedan fuera de esta tabla pendiente. La etiqueta de triage no se usa como conclusión.
- Teléfonos: 6 normalizaciones aprobadas viven en `data/decisions/telefonos_aprobados.csv` y ya no aparecen como pendientes. Una cadena de 16 dígitos solo recibe una separación de referencia.
- Confianza: la columna `confianza` expresa confianza en la recomendación conservadora, no la confianza del detector original.
- Territorio: cada etiqueta MINEDUC se conserva; el código municipal del registro debe coincidir con el catálogo y con el segmento del `CODIGO` MINEDUC.

## Evidencia

- `outputs/tablas/recomendaciones_duplicados.csv`
- `outputs/tablas/recomendaciones_telefonos.csv`
- `outputs/tablas/recomendaciones_territorio.csv`

Las decisiones de fusión, sustitución, aceptación telefónica o renombre territorial continúan pendientes de autoridad institucional.
"""
