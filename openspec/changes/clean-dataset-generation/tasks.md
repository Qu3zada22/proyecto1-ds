# Tareas: Generación conservadora de dataset limpio

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Estimated changed lines | 900-2000; domina el CSV generado |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 core → PR 2 CLI → PR 3 salidas |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Contratos RED y core `cleaning.py` | PR 1 | base = `main`; sin datos |
| 2 | CLI, exit codes y guards | PR 2 | base = `main` después de PR 1 |
| 3 | Salidas generadas y verificación | PR 3 | base = `main` después de PR 2; diffs de datos |

## Fase 1: RED — contratos de limpieza

- [x] 1.1 Crear `tests/test_cleaning.py` para NBSP, ausencias, texto preservado y `<NBSP>` vacía/no vacía.
- [x] 1.2 Agregar RED de CSV vacío, header-only, headers duplicados y filas ragged.
- [x] 1.3 Agregar RED de atomicidad multi-salida con fallo inyectado, restauración y cero parciales.
- [x] 1.4 Agregar RED de dos corridas byte-for-byte idénticas para CSV, bitácora y reporte.
- [x] 1.5 Crear `tests/test_cleaning_cli.py` para CLI/API, exit `0/1`, stderr sin traceback y guards.
- [x] 1.6 Agregar RED de no mutación para `data/raw/`, `data/interim/`, HTML fuente y diagnósticos.

## Fase 2: GREEN — módulo core

- [x] 2.1 Crear `src/proyecto1_ds/cleaning.py` con excepciones, `clean_dataset()` y CSV estricto.
- [x] 2.2 Normalizar NBSP/espacios y ausencias inequívocas, preservando texto.
- [x] 2.3 Eliminar `<NBSP>` solo vacía; con contenido, reportar no seguro.
- [x] 2.4 Construir bitácora/reporte estables, header-only con `filas=0` y decisiones diferidas.
- [x] 2.5 Implementar `write_cleaning_outputs()` con temporales, backups, restauración y limpieza de parciales.

## Fase 3: GREEN — CLI e integración

- [x] 3.1 Crear `scripts/limpiar_dataset.py` con `ROOT`, `main()->int`, defaults y errores esperados.
- [x] 3.2 Guardar desde CLI solo en `data/processed/` y `outputs/tablas/`; leer solo `data/interim/`.
- [x] 3.3 Exportar en `src/proyecto1_ds/__init__.py` solo si el API público lo exige; no requerido porque el CLI importa desde `proyecto1_ds.cleaning`.

## Fase 4: REFACTOR, salidas y verificación

- [ ] 4.1 Refactorizar duplicación concreta entre `cleaning.py`, `diagnostics.py` y guards tempranos del CLI en PR3/refactor/final cleanup: lectura CSV estricta, escritura atómica con temporales/backups, formato de invisibles y helpers de reporte; sin mezclar limpieza en `src/proyecto1_ds/diagnostics.py`.
- [ ] 4.2 Ejecutar CLI para generar `data/processed/establecimientos_diversificado_limpio.csv`, `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`.
- [ ] 4.3 Ejecutar `uv run pytest` y verificar idempotencia, atomicidad, edges, exit codes y no mutación.
