# Diseño: Limpieza del repositorio y plan de entrega

## Enfoque técnico

Aplicar una migración mecánica y verificable del contrato vivo: los 23 HTML y `data/raw/manifest.json` permanecen como procedencia inmutable; la consolidación escribe el CSV canónico en `data/source/`, y diagnóstico/limpieza lo consumen para producir las salidas actuales. Antes de eliminar cualquier elemento se registra inventario y hash; no se editan artefactos bajo `openspec/changes/archive/`.

## Decisiones de arquitectura

| Opción | Compromiso | Decisión y fundamento |
|---|---|---|
| `git mv` + SHA-256 + regeneración | Requiere tres comprobaciones | Elegida: demuestra identidad de bytes, facilita detección de rename y prueba reproducibilidad. Copiar/borrar ofrece menos trazabilidad. |
| Cambiar constantes, flags y guards existentes | Cambio intencional de contrato | Elegida: `DEFAULT_OUTPUT_PATH` pasa a `data/source/...`; entradas `DEFAULT_INTERIM_CSV`/`--interim-csv` se reemplazan por `DEFAULT_SOURCE_CSV`/`--source-csv`. No se añade alias ni capa de rutas obsoleta. |
| Allowlist explícita para limpieza | Requiere inventario previo | Elegida: eliminar solo los dos `.gitkeep`, el cambio Anggie después de preservar evidencia, y cachés ignoradas aprobadas. Se prohíben `git clean` destructivo y glob amplio; `.venv/` queda protegida. |
| PR por unidad entregable | Puede requerir excepción documental | Separar migración mecánica, evidencia/limpieza y planificación. Si la reescritura indivisible de `docs/planificacion.md` excede 400 líneas cambiadas, registrar `size:exception`; no fragmentar el documento en estados contradictorios. |

## Flujo de datos

```text
data/raw/*.html + manifest.json ──consolidar──> data/source/establecimientos_diversificado_mineduc.csv
                                                     ├──diagnosticar──> outputs/tablas/ + docs/diagnostico.md
                                                     └──limpiar──────> data/processed/establecimientos_diversificado_limpio.csv
CSV Anggie (git object, secundario) ──comparación documentada read-only──> docs/reconciliacion_anggie.md
```

## Cambios de archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `data/interim/establecimientos_diversificado_raw_unificado.csv` → `data/source/establecimientos_diversificado_mineduc.csv` | Renombrar | Movimiento byte-idéntico. |
| `src/proyecto1_ds/{consolidation,diagnostics,cleaning}.py` | Modificar | Defaults y semántica de fuente; sin alterar parsers ni escritura atómica. |
| `scripts/{consolidar_crudos,diagnosticar_crudos,limpiar_dataset}.py` | Modificar | Defaults, `--source-csv`, mensajes y guards bajo `data/source/`. |
| `tests/test_{consolidation,diagnostics,cleaning,cleaning_cli}.py` | Modificar | Rutas, contratos y RED de rechazo fuera de `data/source/`. |
| `docs/{fuentes_datos,diagnostico,plan_limpieza,reconciliacion_anggie,planificacion}.md` | Modificar | Referencias vivas; recibo reproducible de Anggie; matriz autoritativa y plan. |
| `openspec/specs/{consolidacion-cruda,diagnostico-calidad-cruda,limpieza-dataset-trazable}/spec.md` | Modificar | Contratos activos; historial archivado intacto. |
| `openspec/changes/anggie-csv-reconciliation/`, `openspec/{specs,changes/archive}/.gitkeep` | Eliminar | Solo después de trasladar evidencia útil. |
| `.atl/`, `.pytest_cache/`, `**/__pycache__/`, `*.egg-info/` | Eliminar localmente | Solo coincidencias inventariadas; conservar `.venv/`. |

## Interfaces y contratos

- Fuente canónica: CSV UTF-8 de 11,867×20, 11,867 códigos, SHA-256 `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`.
- La reconciliación registra ref/objeto Git, ruta, SHA-256, `encoding=utf-8`, `csv.reader(strict=True, skipinitialspace=True)`, conteos y comando exacto; una cifra no reproducida se marca como retirada, no corregida por inferencia.
- `docs/planificacion.md` usa una fila por requisito con: fuente, evidencia, estado, brecha, responsable, dependencia, aceptación y PR. Incluye ruta crítica y contribución verificable de Anggie, Iris y Jonathan.

## Estrategia de pruebas

| Capa | Qué | Enfoque |
|---|---|---|
| Unidad | Defaults, flags y guards `data/source/` | Strict TDD en las cuatro suites afectadas; casos fuera de raíz y symlink fallan sin salidas. |
| Integración | HTML+manifest → canónico → diagnóstico/limpieza | `uv run pytest`; regenerar y comparar tamaño, filas, columnas, códigos y SHA-256. |
| Repositorio | Referencias, protección y rename | Búsqueda excluyendo `archive/`; inventario antes/después; `git diff --summary -M`, `--name-status`, `--check`. |

## Matriz de amenazas

| Frontera | Aplicabilidad | Respuesta segura/fallo | RED planificada |
|---|---|---|---|
| Rutas tipo documentación | N/A: no se clasifica ni ejecuta documentación. | — | — |
| Selección de repositorio | Aplicable: verificaciones Git. | Ejecutar desde la raíz confirmada; fallar si `--show-toplevel` difiere. | CWD ajeno no permite limpieza ni valida el rename. |
| Estado de commit | Aplicable: rename y eliminaciones pueden estar staged/unstaged. | Inspeccionar índice y worktree por separado; fallar ante cambios ajenos en rutas protegidas. | Detectar cambio protegido staged y unstaged antes de borrar. |
| Estado de push | N/A: no hay automatización de push. | — | — |
| Comandos de PR | N/A: se diseña el slicing, no se compone ni ejecuta `gh`. | — | — |

## Migración, entrega y recuperación

PR1: rename + código/tests/specs/docs vivas. PR2: recibo Anggie y limpieza aprobada. PR3: planificación autoritativa; aplicar excepción solo si el diff cohesivo supera 400. Cada PR registra prueba focalizada, suite, diff, rollback y dependencia.

Orden operativo: capturar estado/hashes; mover; actualizar RED y contratos; regenerar; verificar cero referencias vivas antiguas y cero cambios en HTML, manifest, `data/processed/` y `.venv/`; después eliminar allowlist. Para rollback, revertir cada PR; antes de commit, usar el inventario y `git restore` solo sobre rutas del slice. Cachés se regeneran, nunca se restaura evidencia desde ellas.

## Preguntas abiertas

Ninguna bloqueante para este cambio; catálogo territorial, criterio de duplicados y generador PDF pertenecen a entregas posteriores del plan.
