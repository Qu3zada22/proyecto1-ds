# Tareas: Estabilizar el trabajo territorial de Iris

## Pronóstico de carga de revisión

| Campo | Valor |
|---|---|
| Líneas cambiadas estimadas | 800–1,600, incluidos generados |
| Riesgo del límite de 400 | Alto |
| PR encadenados | Sí; S1 → S2 → S3 dinámico |
| Estrategia | `auto-chain`, `stacked-to-main` |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Unidades sugeridas

| Unidad | Meta/PR | Prueba focalizada | Harness | Rollback |
|---|---|---|---|---|
| S1 | Restaurar 8 fallos/PR1 | `uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py` | CLI con catálogo fixture | Revertir código/pruebas S1 |
| S2 | Contrato territorial/PR2 | `uv run pytest tests/test_territorial_contract.py tests/test_repository_cleanup.py` | catálogo → limpieza → validación temporal | Revertir S2 |
| S3a…n | Regeneración y documentación/PR3+ | `uv run pytest && git diff --check` | worktree temporal inferior | Revertir hijos inversamente/regenerar desde commit previo |

**Protección P:** SHA-256 de `data/raw/manifest.json`=`8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07`, fuente=`c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`, duplicados CSV=`4b1c6d6aa7d720872b88e3a5ddcd5402657dede539518fe9a330f541593954c6`, informe=`c9feec7bc2b09fc449439f87781a920539dae668d79c95eca060f2ce3ea93398`, `README.pdf`=`42e3227ede19d0c7f12da930db0bff01ef0adbcbc4e69efe9150ac06fefba2e1`.

## Fase 1: S1 — regresiones

- [x] 1.1 RED/GREEN en `tests/test_cleaning.py`, `src/proyecto1_ds/cleaning.py`: fijar mayúsculas de `ESTABLECIMIENTO`/`DIRECTOR` y capacidad `dir_fd` sustituible; ejecutar prueba focalizada y aceptar 8 fallos restaurados. Verificar P; rollback: revertir ambos archivos.
- [x] 1.2 RED/GREEN en `tests/test_cleaning_cli.py` y fixtures: aportar catálogo válido, probar ausencia sin mutación y limitar hashes autorizados a regeneraciones posteriores; ejecutar prueba focalizada. Aceptar ramas real/inyectada; verificar P; rollback: revertir fixtures.

## Fase 2: S2 — contrato territorial

- [x] 2.1 RED/GREEN en `tests/test_territorial_contract.py`, `scripts/generar_catalogo_territorial.py`, `src/proyecto1_ds/enrichment.py`: pin/URL raw, hash, esquema, unicidad, 22/340, atomicidad, 2 typos y 7 parejas/145 filas `revisar` con códigos provisionales. Ejecutar prueba territorial; aceptar catálogo previo intacto al fallar; verificar P; rollback S2.
- [x] 2.2 RED/GREEN en `tests/test_territorial_contract.py`, `src/proyecto1_ds/territorial.py`, `scripts/{limpiar_dataset,validar_territorio}.py`: rutas POSIX relativas, bytes determinísticos y publicación/restauración conjunta CSV+Markdown. Ejecutar prueba territorial; aceptar 11,867×21 sin outputs Anggie; verificar P; rollback S2.

## Fase 3: S3 dinámico — regeneración y documentación

- [x] 3.1 RED/GREEN temporal sobre archivos generados autorizados: medir antes de tocar el árbol real; aceptar equivalencia/idempotencia y `GEN_LINES≤400`. Verificar P; rollback: eliminar worktree, sin ejecutar `detectar_duplicados.py`.

```bash
TMP=$(mktemp -d); git worktree add "$TMP/repro" HEAD
(cd "$TMP/repro"&&uv run python scripts/generar_catalogo_territorial.py&&uv run python scripts/limpiar_dataset.py&&uv run python scripts/validar_territorio.py)
git -C "$TMP/repro" diff --numstat -- data/reference/catalogo_territorial.csv data/processed/establecimientos_diversificado_limpio.csv outputs/tablas/bitacora_limpieza.csv outputs/tablas/reporte_calidad_antes_despues.csv outputs/tablas/inconsistencias_territoriales.csv outputs/reportes/validacion_territorial.md
GEN_LINES=$(git -C "$TMP/repro" diff --numstat -- data/reference/catalogo_territorial.csv data/processed/establecimientos_diversificado_limpio.csv outputs/tablas/bitacora_limpieza.csv outputs/tablas/reporte_calidad_antes_despues.csv outputs/tablas/inconsistencias_territoriales.csv outputs/reportes/validacion_territorial.md | awk '($1 !~ /^[0-9]+$/)||($2 !~ /^[0-9]+$/){bad=1;next}{n+=$1+$2} END{if(bad) exit 2; print n+0}')
test "$GEN_LINES" -le 400
```

- [x] 3.2 RED/GREEN en generados autorizados y `tests/test_repository_cleanup.py`: regenerar catálogo → limpieza → validación, fijar hashes solo ahora y probar 11,867×21/20→21/7–145. Ejecutar suite; aceptar allowlist y P; rollback: revertir/regenerar desde base.
- [x] 3.3 RED/GREEN documental en `docs/code_book/variables_territoriales.md`, `docs/{fuentes_datos,planificacion,plan_limpieza}.md`, `README.md`, `AGENTS.md`: documentar evidencia, provisionalidad y pendientes sin cerrar proyecto ni tareas Anggie. Ejecutar suite/diff-check; aceptar coherencia; verificar P; rollback: revertir documentos.

## Gate exacto por slice

```bash
git diff --numstat "$SLICE_BASE"..HEAD
LINES=$(git diff --numstat "$SLICE_BASE"..HEAD | awk '($1 !~ /^[0-9]+$/)||($2 !~ /^[0-9]+$/){bad=1;next}{n+=$1+$2} END{if(bad) exit 2; print n+0}')
test "$LINES" -le 400
```

Dividir S3 dinámicamente y repetir el gate. Si un conjunto generado atómico supera 400, detener apply; `size:exception` requiere aprobación explícita.
