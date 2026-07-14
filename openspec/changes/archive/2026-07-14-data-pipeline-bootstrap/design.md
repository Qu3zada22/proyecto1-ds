# Diseño: Bootstrap del pipeline de diagnóstico

## Enfoque técnico

Se diseñará un bootstrap Python script-first, reproducible y pequeño, para cubrir adquisición, manifest de datos crudos, consolidación sin limpieza y diagnóstico previo a transformación. El repositorio actual ya preserva artefactos HTML oficiales de resultados MINEDUC porque no se encontró punto final CSV directo. El diseño permite que PR 2 consolide CSV crudos o, cuando el manifest indique `metodo: html-form`, extraiga estructuralmente las tablas desde `data/raw/*.html` hacia el CSV intermedio sin limpiar valores fuente. El flujo satisface las specs `adquisicion-datos-mineduc`, `consolidacion-cruda` y `diagnostico-calidad-cruda`.

## Decisiones de arquitectura

| Decisión | Opción elegida | Alternativas consideradas | Justificación |
|---|---|---|---|
| Ejecución | Scripts Python delgados sobre módulos en `src/proyecto1_ds/` | Notebook-first o R/Rmd | Python facilita reproducibilidad, pruebas con `pytest` y automatización de descarga; los scripts mantienen entradas claras para el equipo. |
| Datos crudos | `data/raw/` como zona inmutable por convención, manifest externo y controles de no sobrescritura para CSV o HTML oficial preservado | Editar CSV/HTML o agregar metadatos dentro de cada artefacto | La rúbrica exige resguardar crudos; el manifest documenta fuente sin alterar archivos originales y los controles reducen riesgo de pérdida de evidencia. |
| Consolidación | Unión append-only a `data/interim/establecimientos_diversificado_raw_unificado.csv`, leyendo CSV o extrayendo tablas desde HTML oficial cuando no hay CSV directo | Normalizar columnas o coercionar tipos | La especificación prohíbe limpieza; extraer celdas de HTML a CSV es una operación estructural y solo se agregan `archivo_origen` y `departamento_origen` como linaje operativo. |
| Diagnóstico | Lectura de `data/interim/` y generación de tablas en `outputs/tablas/` más `docs/diagnostico.md` | Diagnóstico manual en Markdown | La rúbrica exige tablas y estadísticas generadas por código. |
| Catálogos oficiales | Usarlos si existen; si faltan, registrar limitación | Declarar inválidos sin catálogo | Evita falsos positivos cuando no hay evidencia oficial suficiente. |

## Flujo de datos

```text
MINEDUC WebForms / CSV manuales
        │
        ▼
scripts/adquirir_datos.py ──→ data/raw/*.csv o data/raw/*.html + data/raw/manifest.json
        │
        ▼
scripts/consolidar_crudos.py ──→ extracción estructural de tablas HTML si aplica
        │
        ▼
data/interim/establecimientos_diversificado_raw_unificado.csv
        │                              │
        ▼                              ▼
scripts/diagnosticar_crudos.py ──→ outputs/tablas/ ──→ docs/diagnostico.md
```

La adquisición intenta fuente oficial. Si no hay punto final CSV directo, preserva HTML oficial de resultados WebForms con `metodo: html-form`; si falla la adquisición, registra el error y acepta CSV manuales existentes. La consolidación no modifica valores fuente: para CSV lee filas tabulares; para HTML localiza la tabla de resultados, extrae el texto de cada celda y lo serializa a CSV sin limpieza, salvo escapado y delimitación requeridos por el formato CSV. En ambos casos solo añade columnas de procedencia. `archivo_origen` debe salir del manifest o del nombre real del archivo. `departamento_origen` debe priorizar el manifest; solo puede inferirse desde nombre/ruta cuando el nombre contiene una coincidencia exacta con un departamento oficial normalizado y no contiene más de una coincidencia posible. Si no cumple esa regla verificable, debe marcarse como `pendiente`/`ambiguo` y reportarse. El diagnóstico es read-only sobre `data/interim/` y no cambia en esta enmienda.

## Cambios de archivos

| Archivo | Acción futura | Descripción |
|---|---|---|
| `pyproject.toml` | Crear | Stack Python, dependencias y `pytest`. |
| `src/proyecto1_ds/acquisition.py` | Crear | Descarga/registro de CSV y errores de fuente. |
| `src/proyecto1_ds/manifest.py` | Crear | Lectura/escritura de metadatos crudos. |
| `src/proyecto1_ds/consolidation.py` | Crear | Validación de esquemas compatibles, extracción estructural de tablas HTML oficiales y unión sin limpieza. |
| `src/proyecto1_ds/diagnostics.py` | Crear | Métricas de calidad cruda y tablas. |
| `scripts/adquirir_datos.py` | Crear | Punto de entrada de adquisición. |
| `scripts/consolidar_crudos.py` | Crear | Punto de entrada de consolidación. |
| `scripts/diagnosticar_crudos.py` | Crear | Punto de entrada de diagnóstico. |
| `data/raw/`, `data/interim/`, `outputs/tablas/` | Crear | Zonas de datos crudos CSV/HTML, intermedios y salidas generadas. |
| `docs/diagnostico.md` | Crear | Informe diagnóstico generado desde código. |

## Interfaces / contratos

`data/raw/manifest.json` contendrá una lista por lote: `archivo`, `fuente_url`, `fecha_extraccion`, `version_dataset`, `cobertura`, `departamento`, `metodo`, `checksum_sha256` y `error_adquisicion` opcional. `metodo` puede indicar CSV directo/manual o `html-form` para HTML oficial MINEDUC preservado. `version_dataset` usa formato `vMAJOR.MINOR.PATCH`: inicia en `v0.1.0`; incrementa `PATCH` si solo cambian metadatos no estructurales, `MINOR` si cambia el conjunto de archivos/fecha de extracción/cobertura, y `MAJOR` queda reservado para cambios incompatibles futuros en estructura del dataset limpio.

Contratos principales: `acquire_or_register_raw() -> Manifest`, `consolidate_raw(manifest) -> Path`, `generate_diagnostics(interim_csv) -> DiagnosticReport`. La consolidación debe aceptar entradas CSV o HTML oficial `html-form`; para HTML, el parser extrae tablas de resultados desde `data/raw/*.html` y conserva el texto de celdas sin limpieza antes de serializarlo en `data/interim/establecimientos_diversificado_raw_unificado.csv`. Los errores deben ser explícitos: scraping fallido no bloquea si hay CSV manuales o HTML oficial preservado; ausencia total de artefactos crudos bloquea consolidación; HTML sin tabla esperada bloquea o reporta el archivo sin salida parcial silenciosa; esquemas incompatibles bloquean salida unificada; catálogo oficial faltante degrada dominios a “no verificable”.

Compatibilidad de esquema significa que todos los CSV o tablas HTML extraídas a consolidar tienen el mismo conjunto de columnas normalizado solo para comparación de encabezados, sin cambiar datos fuente: se permite distinto orden de columnas, pero no columnas faltantes/sobrantes sin reporte explícito. Si hay incompatibilidad, no se genera el CSV unificado.

Controles de seguridad/reproducibilidad: los scripts deben leer/escribir datos solo dentro de `data/raw/`, `data/interim/`, `outputs/tablas/` y `docs/diagnostico.md`; no deben sobrescribir CSV crudos existentes sin confirmación explícita; deben calcular checksum de archivos crudos registrados; y cualquier URL automática debe corresponder a la fuente oficial MINEDUC o quedar rechazada/documentada.

## Estrategia de pruebas

| Capa | Qué probar | Enfoque |
|---|---|---|
| Unit | Manifest, detección de CSV/HTML, parser de tabla HTML oficial, no sobrescritura, checksum, esquema compatible, métricas | Activar TDD estricto al crear `pyproject.toml` con `pytest`; fixtures mínimos en `tests/fixtures/raw/`. |
| Integración | Raw → interim → tablas/diagnóstico | Fixtures CSV y HTML mínimos con dos departamentos, un caso compatible y un caso incompatible. |
| E2E | Ejecución de scripts en orden | Comando objetivo posterior al bootstrap: `pytest` más ejecución de scripts sobre fixtures. |

## Migración / despliegue

No requiere migración de datos. El rollout es aditivo: crear estructura, registrar crudos, consolidar y diagnosticar. No se limpia ni se reemplaza data fuente.

## Preguntas abiertas

- [x] Confirmar URL/exportación real de MINEDUC: se preservaron resultados WebForms oficiales como HTML y no se encontró punto final CSV directo.
- [ ] Confirmar catálogo oficial disponible para departamentos/municipios.
