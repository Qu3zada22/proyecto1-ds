# Tareas: Bootstrap del pipeline de diagnóstico

## Pronóstico de carga de revisión (Review Workload Forecast)

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 700-1,000 |
| Riesgo del presupuesto de 400 líneas | High |
| PRs encadenados recomendados | Yes |
| División sugerida | PR 1 entorno/adquisición → PR 2 consolidación → PR 3 diagnóstico |
| Estrategia de entrega | auto-chain si alto riesgo |
| Estrategia de cadena | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Objetivo | PR probable | Notas |
|------|----------|-------------|-------|
| 1 | Base Python, fixtures, manifest y adquisición trazable | PR 1 → main | Incluye `pyproject.toml`, `tests/fixtures/raw/`, `src/proyecto1_ds/manifest.py`, `src/proyecto1_ds/acquisition.py`. |
| 2 | Consolidación cruda sin limpieza | PR 2 → main después de PR 1 | Depende de PR 1; incluye `src/proyecto1_ds/consolidation.py`, parser de tablas HTML oficiales preservadas y `scripts/consolidar_crudos.py`. |
| 3 | Diagnóstico reproducible y salidas | PR 3 → main después de PR 2 | Depende de PR 2; incluye `src/proyecto1_ds/diagnostics.py`, scripts, `outputs/tablas/`, `docs/diagnostico.md`. |

## Fase 1: Entorno y pruebas base

- [x] 1.1 Crear `pyproject.toml` con dependencias mínimas, grupo `dev` de `uv` con `pytest` y comando objetivo `uv run pytest`.
- [x] 1.2 Crear `src/proyecto1_ds/` y `tests/fixtures/raw/` con CSV mínimos: compatible, incompatible y departamento ambiguo.
- [x] 1.3 RED: crear pruebas para SemVer-like, checksum, no sobrescritura y registro de fallback manual.

## Fase 2: Manifest y adquisición

- [x] 2.1 Implementar `src/proyecto1_ds/manifest.py` para leer/escribir `data/raw/manifest.json` con campos exigidos.
- [x] 2.2 Implementar `src/proyecto1_ds/acquisition.py` con `acquire_or_register_raw()`, rechazo de URL no MINEDUC y error explícito.
- [x] 2.3 Crear `scripts/adquirir_datos.py` como CLI delgado que no modifique CSV crudos existentes sin confirmación.
- [x] 2.4 GREEN: pasar escenarios de descarga disponible, fallback manual, alcance faltante y metadatos completos.

### Remediación PR 1 / unidad 1

- [x] R1 Cubrir el CLI público `scripts/adquirir_datos.py`: parser, código de salida, `stderr`, `--confirm-overwrite` y restricción de `--raw-dir`.
- [x] R2 Probar que el alcance disponible y faltante queda documentado en el manifest.
- [x] R3 Convertir archivos manuales faltantes en `AcquisitionError` claro, sin traceback.
- [x] R4 Endurecer adquisición PR 1: HTTPS obligatorio para MINEDUC, merge determinístico de manifest, rechazo de descargas vacías/HTML y escritura temporal antes de reemplazo confirmado.
- [x] R5 Eliminar artefactos locales `*.egg-info/` y dejar la regla en `.gitignore` sin ignorar `uv.lock`.
- [x] R6 Remediar rollback de sobrescritura confirmada cuando falla la persistencia del manifest, restaurando el CSV crudo original y limpiando temporales.
- [x] R7 Investigar la página real de MINEDUC, preservar artefactos HTML oficiales de diversificado por departamento en `data/raw/` y documentar que no se encontró CSV directo.
- [x] R8 Endurecer confiabilidad pre-PR2: escritura atómica de `manifest.json`, restauración del manifest previo ante fallos de persistencia, validación WebForms y recaptura HTML reproducible por CLI.
- [x] R9 Remediar rollback incompleto cuando falla el backup del manifest después de preparar una sobrescritura cruda, preservando crudo y manifest originales.
- [x] R10 Remediar rollback no destructivo cuando falla la restauración desde backup, preservando backups para recuperación manual y reportando contexto claro.

## Fase 3: Consolidación cruda

- [x] 3.1 RED: probar esquema compatible, esquema incompatible, procedencia completa, departamento ambiguo y parser de tablas HTML oficiales preservadas.
- [x] 3.2 Implementar `src/proyecto1_ds/consolidation.py` para comparar encabezados normalizados y aceptar CSV crudos o HTML `html-form`, extrayendo celdas sin alterar valores fuente.
- [x] 3.3 Generar `data/interim/establecimientos_diversificado_raw_unificado.csv` con `archivo_origen` y `departamento_origen` para registros provenientes de CSV o HTML.
- [x] 3.4 Crear `scripts/consolidar_crudos.py` y verificar que no genera salida cuando hay columnas incompatibles o HTML sin tabla esperada.

### Remediación PR 2 / unidad 2

- [x] R11 Excluir filas estructurales HTML sin datos reales, incluyendo footers con solo `&nbsp;`, sin limpiar valores legítimos de registros.
- [x] R12 Validar `checksum_sha256` del manifest antes de leer cada artefacto crudo para consolidación.
- [x] R13 Escribir el CSV intermedio de forma atómica mediante temporal en `data/interim` y reemplazo solo al completar la escritura.
- [x] R14 Restringir el `--output-file` del CLI público a la frontera `data/interim` del proyecto.
- [x] R15 Normalizar errores esperados de manifest JSON/esquema como `ConsolidationError` con mensaje amigable del CLI.
- [x] R16 Documentar el manejo explícito de campos WebForms públicos (`__VIEWSTATE`, `__EVENTVALIDATION`) preservados en HTML crudo.
- [x] R17 Remediar HTML de tabla de resultados malformado/truncado: fallar con `ConsolidationError` ante filas/tablas abiertas y aceptar tablas sin datos solo con marcador oficial explícito de cero resultados.

## Fase 4: Diagnóstico y documentación generada

- [x] 4.1 RED: probar métricas de filas, columnas, tipos, faltantes, únicos, duplicados exactos y catálogo no verificable.
- [x] 4.2 Implementar `src/proyecto1_ds/diagnostics.py` con diagnóstico read-only sobre `data/interim/`.
- [x] 4.3 Crear `scripts/diagnosticar_crudos.py` para escribir tablas en `outputs/tablas/` y `docs/diagnostico.md`.
- [x] 4.4 Verificar flujo fixture completo: adquisición → consolidación → diagnóstico, sin limpieza ni duplicados parciales.

### Remediación PR 3 / unidad 3

- [x] R18 Hacer determinístico `docs/diagnostico.md` usando rutas repo-relativas en lugar de rutas absolutas locales.
- [x] R19 Generar `outputs/tablas/dominios_observados.csv` con valores observados y frecuencias top-N por columna sin limpiar los datos fuente.
- [x] R20 Rechazar CSV intermedio malformado o truncado: vacío, encabezados duplicados, columnas sobrantes o columnas faltantes.
- [x] R21 Escribir salidas diagnósticas con flujo atómico/fix-forward mediante temporales, reemplazo conjunto y preservación/restauración de salidas previas ante fallos.
- [x] R22 Alinear el conteo de problemas potenciales con todas las filas de la tabla, incluyendo `duplicados_parciales_diferidos` de forma explícita.
- [x] R23 Restringir `--interim-csv` del CLI público a la frontera `data/interim` del proyecto.
- [x] R24 Mostrar nombres de columna invisibles/NBSP en tablas generadas mediante `columna_mostrada`, preservando `columna` cruda sin renombrar.
- [x] R25 Rechazar CSV truncado con campo entrecomillado abierto mediante `DiagnosticCsvError`, preservando el comportamiento válido del dataset real.

### Remediación final 4R / bloqueadores de revisión

- [x] R26 Rechazar CSV crudos con filas ragged (columnas sobrantes o faltantes) antes de escribir la salida consolidada.
- [x] R27 Registrar fallback manual cuando MINEDUC responde HTML/CSV inválido y existen CSV manuales; fallar con contexto claro cuando no existen.
- [x] R28 Restringir `--raw-dir` y `--manifest` del CLI de consolidación a la frontera `data/raw` del proyecto.
- [x] R29 Reportar fallos de restauración del rollback diagnóstico y preservar backups para recuperación manual.
- [x] R30 Actualizar documentación para usar comandos portables `uv run ...` y eliminar referencia stale a PR 2.
- [x] R31 Documentar el flujo reproducible adquisición → manifest → consolidación → diagnóstico con comandos de regeneración.
