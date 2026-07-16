# Apply progress: clean-dataset-generation

## Slice actual

- PR: 1 / stacked-to-main.
- Alcance: librería core de limpieza + pruebas unitarias.
- Fuera de alcance en este slice: CLI `scripts/limpiar_dataset.py`, generación de salidas reales en `data/processed/` y `outputs/tablas/`, mutación de fuentes `data/raw/`, `data/interim/`, HTML, diagnósticos o plan.
- Nota de consistencia: el forecast de `tasks.md` fue corregido para reflejar `stacked-to-main`, estrategia elegida por el usuario.

## Tareas completadas

- [x] 1.1 Crear `tests/test_cleaning.py` para NBSP, ausencias, texto preservado y `<NBSP>` vacía/no vacía.
- [x] 1.2 Agregar RED de CSV vacío, header-only, headers duplicados y filas ragged.
- [x] 1.3 Agregar RED de atomicidad multi-salida con fallo inyectado, restauración y cero parciales.
- [x] 1.4 Agregar RED de dos corridas byte-for-byte idénticas para CSV, bitácora y reporte.
- [x] 1.6 Agregar RED de no mutación para `data/raw/`, `data/interim/`, HTML fuente y diagnósticos.
- [x] 2.1 Crear `src/proyecto1_ds/cleaning.py` con excepciones, `clean_dataset()` y CSV estricto.
- [x] 2.2 Normalizar NBSP/espacios y ausencias inequívocas, preservando texto.
- [x] 2.3 Eliminar `<NBSP>` solo vacía; con contenido, reportar no seguro.
- [x] 2.4 Construir bitácora/reporte estables, header-only con `filas=0` y decisiones diferidas.
- [x] 2.5 Implementar `write_cleaning_outputs()` con temporales, backups, restauración y limpieza de parciales.
- [x] Remediación PR1: exigir `project_root` para cualquier ruta personalizada de `write_cleaning_outputs()` y validar antes de `mkdir`/escritura.

## TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 1.1 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ Import de `proyecto1_ds.cleaning` falló antes de implementar | ✅ `tests/test_cleaning.py` pasó | ✅ NBSP vacía y NBSP con contenido | ✅ Helpers de fixture reutilizables |
| 1.2 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ Casos malformados/header-only escritos primero | ✅ `tests/test_cleaning.py` pasó | ✅ Empty, duplicados, ragged, quote abierto y header-only | ✅ Validación CSV estricta aislada |
| 1.3 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ Fallo inyectado en `Path.replace` escrito primero | ✅ `tests/test_cleaning.py` pasó | ✅ Restauración de tres salidas + cero temporales/backups | ✅ Escritura atómica extraída |
| 1.4 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ Comparación byte-for-byte escrita primero | ✅ `tests/test_cleaning.py` pasó | ✅ Segunda corrida sobre archivos stale | ✅ CSV con orden estable y sin timestamps |
| 1.6 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ Protección de fuentes escrita primero | ✅ `tests/test_cleaning.py` pasó | ✅ raw, interim, HTML, diagnóstico y plan protegidos | ✅ Escritura limitada a rutas recibidas por API |
| 2.1-2.5 | `tests/test_cleaning.py` | Unit | N/A (new) | ✅ RED global: `ModuleNotFoundError` para `cleaning.py` inexistente | ✅ `tests/test_cleaning.py` y suite completa pasan | ✅ Reglas, errores, atomicidad, idempotencia y no mutación | ✅ Separación core sin tocar `diagnostics.py` |
| Remediación PR1: temporal de writer fallido | `tests/test_cleaning.py` | Unit | ✅ 6/6 baseline | ✅ Test agregado falla con `.reporte_calidad_antes_despues.csv.*.tmp` residual | ✅ `tests/test_cleaning.py` pasó con 7/7 | ✅ Falla durante escritura de temp antes de registro, además de fallo durante replace existente | ✅ `_report_row` usa argumentos keyword-only y `tasks.md` concreta follow-up de duplicación |
| Remediación PR1: guard de rutas de salida | `tests/test_cleaning.py` | Unit | ✅ 7/7 baseline | ✅ Test agregado falla con `TypeError: unexpected keyword argument 'project_root'` | ✅ `tests/test_cleaning.py` pasó con 9/9 | ✅ Rechaza traversal fuera de `data/processed/`, rechaza tablas fuera de `outputs/tablas/`, acepta rutas válidas bajo `project_root` y resuelve defaults bajo la raíz del repo | ✅ Validación de raíces extraída antes de crear directorios/escribir salidas |
| Remediación PR1: rutas personalizadas requieren `project_root` | `tests/test_cleaning.py` | Unit | ✅ 9/9 baseline | ✅ Test agregado falla porque se ejecuta `mkdir` para rutas personalizadas sin `project_root` | ✅ `tests/test_cleaning.py` pasó con 10/10 | ✅ Cubre ruta CSV personalizada, directorio de tablas personalizado y ambas rutas personalizadas sin `project_root`; conserva rechazo con `project_root` fuera de raíces permitidas | ✅ `_output_guard_root()` ahora siempre devuelve raíz validable o lanza `CleaningOutputError` antes de crear directorios/escribir |

## Tests ejecutados

- RED: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → falla esperada por `ModuleNotFoundError: No module named 'proyecto1_ds.cleaning'`.
- GREEN: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 6 passed.
- Verificación de slice: `/home/jonialen/.local/bin/uv run pytest` → 69 passed.
- Baseline remediación: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 6 passed.
- RED remediación: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 1 failed, 6 passed; quedó un `.tmp` de reporte cuando el writer falló después de crearlo y antes de registrarlo para cleanup.
- GREEN remediación: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 7 passed.
- Verificación remediación: `/home/jonialen/.local/bin/uv run pytest` → 70 passed.
- Baseline guard de rutas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 7 passed.
- RED guard de rutas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 1 failed, 7 passed; `write_cleaning_outputs()` aún no aceptaba `project_root`.
- GREEN guard de rutas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 9 passed.
- Verificación guard de rutas: `/home/jonialen/.local/bin/uv run pytest` → 72 passed.
- Baseline remediación rutas personalizadas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 9 passed.
- RED remediación rutas personalizadas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 1 failed, 9 passed; el flujo intentaba `mkdir` cuando había rutas personalizadas sin `project_root`.
- GREEN remediación rutas personalizadas: `/home/jonialen/.local/bin/uv run pytest tests/test_cleaning.py` → 10 passed.
- Verificación remediación rutas personalizadas: `/home/jonialen/.local/bin/uv run pytest` → 73 passed.
- Verificación de artefactos protegidos: `git status --short -- data/raw data/interim data/processed outputs docs` → sin cambios.

## Archivos cambiados

| Archivo | Acción | Descripción |
|---|---|---|
| `src/proyecto1_ds/cleaning.py` | Creado/modificado | Motor core de limpieza conservadora; remediación registra cada temporal antes de invocar el writer para limpiar residuos si la escritura crea el `.tmp` y luego falla; agrega contrato `project_root` obligatorio para rutas personalizadas y valida que salidas queden bajo `data/processed/` y `outputs/tablas/` antes de crear directorios o escribir. |
| `tests/test_cleaning.py` | Creado/modificado | Pruebas unitarias TDD para reglas seguras, errores, atomicidad, idempotencia y no mutación; agregado caso de fallo durante escritura de temp sin residuos `.tmp`, guard contra traversal/rutas fuera de raíz y rechazo temprano de rutas personalizadas sin `project_root`. |
| `openspec/changes/clean-dataset-generation/tasks.md` | Modificado | Marcadas como completadas las tareas PR1 del core y concretado el follow-up 4.1 de duplicación con `diagnostics.py`. |
| `openspec/changes/clean-dataset-generation/apply-progress.md` | Creado/modificado | Evidencia de slice, TDD, pruebas, pendientes y remediación PR1. |

## Salidas generadas

Ninguna salida real del proyecto fue generada. Las escrituras se probaron solo en `tmp_path` de pytest.

## Pendientes

- [ ] 1.5 Crear `tests/test_cleaning_cli.py` para CLI/API, exit `0/1`, stderr sin traceback y guards.
- [ ] 3.1 Crear `scripts/limpiar_dataset.py` con `ROOT`, `main()->int`, defaults y errores esperados.
- [ ] 3.2 Guardar desde CLI solo en `data/processed/` y `outputs/tablas/`; leer solo `data/interim/`.
- [ ] 3.3 Exportar en `src/proyecto1_ds/__init__.py` solo si el API público lo exige.
- [ ] 4.1 Refactorizar duplicación concreta entre `cleaning.py` y `diagnostics.py` después de PR1: lectura CSV estricta, escritura atómica con temporales/backups, formato de invisibles y helpers de reporte; sin mezclar limpieza en `src/proyecto1_ds/diagnostics.py`.
- [ ] 4.2 Ejecutar CLI para generar `data/processed/establecimientos_diversificado_limpio.csv`, `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`.
- [ ] 4.3 Ejecutar `uv run pytest` y verificar idempotencia, atomicidad, edges, exit codes y no mutación.

## Issues / desviaciones

- No se implementó CLI por límite explícito de PR1.
- No se generaron archivos reales en `data/processed/` ni `outputs/tablas/` por límite explícito de PR1.
- La inconsistencia documental de estrategia de cadena fue corregida: `tasks.md`, prompt y Engram indican `stacked-to-main`.
- Remediación PR1: se corrigió el residuo `.tmp` cuando el writer crea un temporal y falla antes de que el código anterior lo registrara para cleanup.
- Remediación PR1: `write_cleaning_outputs()` ahora acepta `project_root`; con raíz explícita (o rutas por defecto) rechaza salidas fuera de `data/processed/` y `outputs/tablas/` antes de crear directorios/escribir.
- Remediación PR1: `write_cleaning_outputs()` ahora rechaza cualquier ruta personalizada sin `project_root` antes de crear directorios o escribir; los tests con `tmp_path` pasan raíz explícita y escriben solo bajo `tmp_path/data/processed/` y `tmp_path/outputs/tablas/`.
- Readability PR1: no se extrajo helper compartido con `diagnostics.py` en este slice; el follow-up 4.1 ahora lista duplicaciones concretas para una refactorización posterior.
