# Validación cruzada reproducible del CSV de Anggie

Este recibo conserva la evidencia útil de la rama `scrap-anggie` sin incorporar su CSV al pipeline canónico. Las métricas siguientes se obtuvieron directamente del objeto Git identificado; no dependen de un archivo presente en el worktree.

## Identidad de la evidencia

| Campo | Valor |
|---|---|
| Ref consultada | `scrap-anggie` |
| Commit resuelto | `6e83a26a71d743ce08bbec592821da35df52ceef` |
| Ruta en la rama | `data/raw/establecimientos_diversificado_guatemala.csv` |
| Objeto blob Git | `2e27f11a8fb882594b8434f4d85b2ca75bc43b8a` |
| Tamaño | `8,696,253` bytes |
| SHA-256 del blob | `ca738d5d0628613c8ad5519e15a5f20c4c1e8d536bd4510a2235e893ee3d4fd5` |
| Fuente de contraste | `data/source/establecimientos_diversificado_mineduc.csv` |

## Método reproducible

El blob se obtuvo con el equivalente programático de `git show`, se decodificó con `encoding="utf-8"` y se leyó mediante `csv.reader(..., strict=False, skipinitialspace=True)`. `skipinitialspace=True` es necesario por los espacios previos a campos entrecomillados. Se documenta `strict=False` porque `strict=True` falla reproduciblemente en el registro 5 (línea física 5) con `_csv.Error: ',' expected after '"'`: el archivo contiene espacios entre el cierre de una comilla y la coma siguiente.

Ejecutar desde la raíz Git:

```bash
python - <<'PY'
import csv, hashlib, io, subprocess
from collections import Counter

ref = "scrap-anggie"
path = "data/raw/establecimientos_diversificado_guatemala.csv"
blob = subprocess.check_output(["git", "show", f"{ref}:{path}"])
rows = list(csv.reader(io.StringIO(blob.decode("utf-8"), newline=""), strict=False, skipinitialspace=True))
header, *data = rows
exact = Counter(map(tuple, data))
codes = {row[0].strip() for row in data if row[0].strip()}

with open("data/source/establecimientos_diversificado_mineduc.csv", encoding="utf-8", newline="") as source:
    canonical_rows = list(csv.reader(source, strict=True))
canonical_header, *canonical_data = canonical_rows
code_index = canonical_header.index("CODIGO")
canonical_codes = {row[code_index].strip() for row in canonical_data if row[code_index].strip()}

print("commit", subprocess.check_output(["git", "rev-parse", ref], text=True).strip())
print("blob", subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip())
print("bytes", len(blob), "sha256", hashlib.sha256(blob).hexdigest())
print("anggie", len(data), "x", len(header), "unique_codes", len(codes))
print("unique_exact_rows", len(exact), "duplicates_beyond_first", sum(n - 1 for n in exact.values()))
print("canonical", len(canonical_data), "x", len(canonical_header), "unique_codes", len(canonical_codes))
print("anggie_only", len(codes - canonical_codes), "canonical_only", len(canonical_codes - codes))
PY
```

## Mediciones obtenidas

| Métrica | CSV de Anggie | Fuente canónica |
|---|---:|---:|
| Filas de datos | 12,948 | 11,867 |
| Columnas | 18 | 20 |
| Códigos únicos no vacíos | 11,867 | 11,867 |
| Filas exactas únicas | 11,867 | 11,867 |
| Duplicados exactos más allá de la primera aparición | 1,081 | 0 |
| Códigos exclusivos respecto de la otra fuente | 0 | 0 |

La afirmación previa de **12,807: retirada**. Ese conteo no fue reproducido con el objeto y método documentados. El valor `12,948` sí corresponde a filas de datos analizadas directamente; el encabezado eleva el total de registros CSV a `12,949`.

## Decisión de uso

El CSV de Anggie permanece como evidencia secundaria de validación cruzada. No reemplaza ni alimenta automáticamente la fuente canónica: tiene un esquema distinto, requiere tolerancia de parsing documentada y contiene 1,081 repeticiones exactas. Una reconciliación campo a campo futura deberá conservar procedencia y decisiones humanas sin mutar datos por inferencia.
