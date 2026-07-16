## Exploración: reconciliación del CSV de Anggie con el pipeline MINEDUC

### Estado actual
El pipeline vigente está organizado como una línea reproducible `adquisición → manifest → consolidación → diagnóstico`. La adquisición (`src/proyecto1_ds/acquisition.py`, `scripts/adquirir_datos.py`) preserva 23 HTML oficiales MINEDUC por departamento en `data/raw/` con manifest, checksum, fecha, cobertura y `metodo: html-form`. La consolidación (`src/proyecto1_ds/consolidation.py`, `scripts/consolidar_crudos.py`) extrae la tabla oficial de esos HTML o lee CSV crudos registrados, valida checksum, exige esquemas compatibles y escribe `data/interim/establecimientos_diversificado_raw_unificado.csv` sin limpiar valores. El diagnóstico (`src/proyecto1_ds/diagnostics.py`, `scripts/diagnosticar_crudos.py`) lee el CSV intermedio, reporta métricas, faltantes, dominios, duplicados exactos y problemas potenciales sin mutar datos.

Las pruebas existentes cubren adquisición oficial/manual, captura HTML WebForms, protección contra sobrescrituras, manifest, consolidación CSV/HTML, rechazo de CSV ragged, checksum, escrituras atómicas, diagnóstico read-only y restricciones de CLI. Las specs vigentes en `openspec/specs/` permiten CSV crudos, pero priorizan trazabilidad y no limpieza; cuando no hay CSV directo reproducible, el HTML oficial preservado es fuente cruda válida.

El CSV de Anggie en `scrap-anggie:data/raw/establecimientos_diversificado_guatemala.csv` no debería reemplazar directamente el pipeline actual: contiene los mismos 11,867 códigos únicos que el intermedio vigente, pero agrega 1,081 duplicados exactos y requiere parsing con `skipinitialspace=True` para interpretar correctamente comillas precedidas por espacios. Bajo parsing CSV estándar sin `skipinitialspace`, aparecen filas con longitud variable y direcciones entrecomilladas mal interpretadas.

### Áreas afectadas
- `src/proyecto1_ds/acquisition.py` — si se incorpora, debe registrar el CSV como fuente manual/secundaria con checksum, método y cobertura explícita, sin presentarlo como descarga oficial reproducible si no se prueba su origen.
- `src/proyecto1_ds/consolidation.py` — hoy usa `csv.reader(..., strict=True)` sin `skipinitialspace`; una importación del CSV de Anggie necesitaría un lector específico o una fase separada de reconciliación para no cambiar semántica del consolidador oficial.
- `src/proyecto1_ds/diagnostics.py` — podría ampliarse con métricas de reconciliación: códigos comunes, duplicados por fuente, diferencias por campo y evidencia de procedencia.
- `scripts/` — probablemente haría falta un CLI nuevo de reconciliación o un modo explícito, en vez de mezclarlo con consolidación cruda.
- `tests/` — se necesitarían fixtures con comillas precedidas por espacios, filas duplicadas, diferencias por campo, códigos coincidentes y protección contra reemplazo silencioso.
- `docs/fuentes_datos.md` — debe documentar que el CSV de Anggie es evidencia secundaria/manual salvo que se confirme el flujo oficial de exportación.
- `docs/diagnostico.md`, `docs/plan_limpieza.md`, `outputs/tablas/` — si se implementa después, deben actualizarse solo mediante código para reflejar reconciliación, duplicados y diferencias sin afirmar limpieza ejecutada.
- `openspec/specs/` — requeriría una nueva capacidad o delta spec de reconciliación de fuentes, distinta de adquisición/consolidación/diagnóstico existentes.

### Enfoques
1. **Evidencia secundaria reconciliada** — Registrar el CSV de Anggie como artefacto manual/secundario y producir un reporte de comparación contra el intermedio oficial vigente, sin alimentar automáticamente el dataset principal.
   - Pros: conserva la fuente oficial actual, evita contaminar el intermedio con duplicados, aprovecha el CSV para auditar diferencias y fortalece trazabilidad.
   - Cons: requiere nuevo reporte/CLI y reglas claras para diferencias por campo.
   - Esfuerzo: Medio

2. **Importación como crudo adicional en consolidación** — Agregar el CSV al manifest y modificar consolidación para leerlo con `skipinitialspace=True`, normalizar encabezados y unirlo al intermedio.
   - Pros: reutiliza parte del flujo existente y deja todo bajo manifest/checksum.
   - Cons: duplicaría registros, mezclaría fuentes con granularidad distinta, introduciría parsing especial en una fase que promete no limpiar y puede alterar métricas diagnósticas.
   - Esfuerzo: Medio/Alto

3. **Reemplazo del HTML oficial por el CSV de Anggie** — Usar el CSV de Anggie como fuente primaria del dataset intermedio.
   - Pros: archivo tabular único, más fácil de inspeccionar manualmente.
   - Cons: pierde procedencia oficial reproducible ya preservada, introduce 1,081 duplicados exactos, depende de parsing especial y no resuelve las 53 diferencias de campo reportadas.
   - Esfuerzo: Bajo técnicamente, Alto en riesgo

### Recomendación
Tratar el CSV de Anggie como **evidencia secundaria/manual para reconciliación**, no como reemplazo ni como entrada automática del intermedio principal. La implementación futura debería crear una capacidad separada de reconciliación que lea el CSV con parámetros explícitos (`skipinitialspace=True`, encabezados y valores comparables documentados), calcule duplicados, códigos comunes, diferencias por campo y genere salidas de auditoría. Solo después de revisar las diferencias se debería decidir si alguna corrección pertenece a una fase de limpieza o a una recaptura oficial.

### Riesgos
- `skipinitialspace=True` es necesario para no romper direcciones con comillas precedidas por espacios; aplicarlo globalmente en consolidación puede cambiar la interpretación de otros CSV crudos.
- Los 1,081 duplicados exactos del CSV de Anggie inflarían filas y métricas si se incorporan al intermedio sin deduplicación explícita.
- Las diferencias por campo pueden ser simples espacios colapsados, pero las 53 diferencias sustantivas reportadas requieren revisión, no reemplazo masivo.
- Si no se documenta procedencia, el CSV puede parecer oficial aunque no esté probado como exportación reproducible desde MINEDUC.
- Reconciliar comparando valores normalizados puede confundirse con limpieza; debe quedar como auditoría, no mutación de datos.
- Cambiar outputs vigentes sin versionar la fuente rompería reproducibilidad de `docs/diagnostico.md` y `docs/plan_limpieza.md`.

### Listo para propuesta
Sí. La propuesta debería pedir una capacidad nueva de reconciliación read-only: registrar el CSV de Anggie como evidencia secundaria, generar reporte comparativo reproducible y mantener el dataset intermedio oficial intacto hasta que haya decisión humana sobre duplicados y diferencias.

## Contrato de resultado

- `status`: `success`
- `executive_summary`: El CSV de Anggie coincide en cobertura de códigos con el intermedio actual, pero no debe reemplazarlo: requiere parsing especial, trae duplicados exactos y necesita auditoría de diferencias con procedencia clara.
- `artifacts`: `openspec/changes/anggie-csv-reconciliation/exploration.md`
- `next_recommended`: Crear propuesta SDD para una reconciliación read-only con reporte comparativo, fixtures de parsing y documentación de procedencia.
- `risks`: parsing CSV, duplicados, diferencias de campo, procedencia manual, reproducibilidad y posible mezcla indebida entre auditoría y limpieza.
- `skill_resolution`: Ejecutado como `sdd-explore` executor; no se modificó código ni datos existentes.
