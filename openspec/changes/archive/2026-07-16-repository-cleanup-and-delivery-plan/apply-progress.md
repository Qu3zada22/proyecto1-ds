# Progreso acumulado de aplicación: PR1–PR3
**Modo:** Strict TDD | **Entrega:** `auto-chain`, `stacked-to-main` | **Estado:** PR1–PR3 y 12/12 tareas ejecutables completos; los seguimientos futuros 4.1–4.3 permanecen planificados/no implementados fuera de este cambio.

## Tareas completadas
- [x] 1.1 Recibo recuperable en `outputs/reportes/migracion_fuente.md`.
- [x] 1.2 Cuatro suites migradas con guards de ruta, symlink, atomicidad y procedencia.
- [x] 1.3 Renombre byte-idéntico y contratos `data/source/` sin alias obsoleto.
- [x] 1.4 Documentación y specs vivas actualizadas; `archive/` intacto.
- [x] 1.5 Suite, regeneración, identidad, referencias y protegidos comprobados.
- [x] 2.1 Preflight probado para raíz Git, índice/worktree, allowlist y `.venv/`.
- [x] 2.2 Recibo Anggie reproducible desde commit/blob; `12,807` retirado y `12,948` medido.
- [x] 2.3 Allowlist rastreada e ignorada eliminada sin glob amplio ni `git clean`.
- [x] 2.4 Suite, diff, hashes protegidos, `.venv/` y ausencia del cambio activo comprobados.
- [x] 3.1 Matriz autoritativa de 29 requisitos con estado, evidencia, brecha, responsable, dependencia, aceptación y PR.
- [x] 3.2 Ruta crítica y asignaciones de Anggie, Iris y Jonathan con aporte Git y Code Book verificable.
- [x] 3.3 Rutas canónicas fijadas; futuros explícitamente no implementados; README inexistente, por lo que no se creó ni modificó.

## Corrección semántica de cierre

Las referencias 4.1–4.3 se movieron de la lista ejecutable a una hoja de ruta sin casillas. No se marcaron como completas ni se implementó trabajo futuro. `docs/planificacion.md` conserva PR4–PR7 como **Planificado/no implementado**. El informe `verify-report.md` bloqueado se preservó como `verify-attempt-blocked.md` con veredicto **FAIL**, para distinguir el intento histórico de la próxima verificación final.

## Evidencia del ciclo TDD
| Tarea | Archivo/capa | Safety net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|
| 1.1 | Recibo estructural | 63/63 | N/A: inventario previo | Hashes capturados | 23 HTML + manifest + procesado + outputs | Recibo compacto |
| 1.2 | Cuatro suites/unitaria | 63/63 | 3 errores de colección | 7/7 iniciales; 67/67 finales | Externa, symlink, manifest y atomicidad | Casos integrados |
| 1.3 | Cuatro suites/unitaria | 63/63 | Defaults/flags fallaron | 67/67 | Core, tres CLI y sin alias | Nombres consistentes |
| 1.4 | Repositorio | 63/63 | Referencias vivas detectadas | 0 referencias | Código, CLI, pruebas, docs y specs | `archive/` excluido |
| 1.5 | Integración | 67/67 | Checksum/baseline fijados | 101/101 | Regeneración, rename y protegidos | Sin cambio adicional |
| 2.1 | `test_repository_cleanup.py` | 101/101 | Colección falló por preflight ausente | 5/5 | CWD, no permitido, `.venv`, staged y unstaged | Harness local sin lógica del pipeline |
| 2.2 | Recibo Anggie | 101/101 | Faltaban commit, blob, hash, parser y comando | 5/5 | `strict=True` falla; `strict=False` mide el blob | Tabla y comando compactos |
| 2.3 | Estado del repositorio | 101/101 | 1 fallo con tres rastros restaurados | 5/5 | Rastreada e ignorada; preflight valida antes de borrar | Sin script productivo persistente |
| 2.4 | Hashes/diff | 101/101 | El estado previo conservaba allowlist rastreada | 5/5 y suite completa | 23 HTML, manifest, canónico, procesado, outputs, specs y `.venv` | Un solo test de estado final |
| 3.1 | Plan/matriz | 5/5 | Matriz y campos ausentes: 1 fallo | 8/8 | 29 requisitos, cuatro estados y diez campos | Parser limitado a filas Markdown |
| 3.2 | Plan/asignaciones | 5/5 | Sin filas para tres integrantes: 1 fallo | 8/8 | Tres personas, commit, Code Book, aceptación y dependencias | Tabla compacta |
| 3.3 | Plan/terminología | 5/5 | Futuros/rutas incompletos: 1 fallo | 8/8 | Ocho futuros, rutas canónicas y ausencia de rutas obsoletas | Sin README artificial |
| Corrección de metadatos | `tasks.md`/dispatcher | 8/8 | Estado nativo: 12/15, `allComplete: false` | Estado nativo: 12/12, `allComplete: true` | Hoja de ruta sin casillas y plan futuro intacto | Cambio mínimo; sin código, datos ni plan funcional |

## Evidencia de unidad de trabajo PR1
| Evidencia | Resultado exacto |
|---|---|
| Prueba focalizada | `uv run pytest tests/test_consolidation.py tests/test_diagnostics.py tests/test_cleaning.py tests/test_cleaning_cli.py` → `67 passed` |
| Harness real | Consolidar → diagnosticar → limpiar → exit 0; fuente `11867×20`, `11867` códigos, SHA-256 `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f` |
| Repositorio | Suite `101 passed`; rename `100%`; cero referencias vivas; protegidos con hashes baseline |
| Rollback | Renombre, contratos, referencias, cuatro suites, docs/specs vivas y recibo PR1 |

## Evidencia de unidad de trabajo PR2
| Evidencia | Resultado exacto |
|---|---|
| Prueba focalizada | `/home/jonialen/.local/bin/uv run pytest tests/test_repository_cleanup.py` → `5 passed` |
| Harness real | `git show` del blob `2e27f11…` con UTF-8 y `csv.reader(strict=False, skipinitialspace=True)` → `12,948×18`, `11,867` códigos, `1,081` duplicados más allá de la primera aparición; `0/0` códigos exclusivos |
| Suite/repositorio | `/home/jonialen/.local/bin/uv run pytest` → `106 passed`; diff/allowlist/hashes comprobados; pytest regeneró cachés ignoradas aceptables |
| Rollback | Restaurar los tres rastros Git eliminados y revertir solo `docs/reconciliacion_anggie.md`, `tests/test_repository_cleanup.py`, checkboxes y esta sección; los ignorados se regeneran y `.venv/` no se toca |

## Evidencia de unidad de trabajo PR3
| Evidencia | Resultado exacto |
|---|---|
| Prueba focalizada | `/home/jonialen/.local/bin/uv run pytest tests/test_repository_cleanup.py` → `8 passed` |
| Harness real | N/A: unidad exclusivamente documental, sin frontera de ejecución; `git diff --check` y búsqueda determinística de rutas obsoletas terminaron con código 0 |
| Suite/protegidos | `/home/jonialen/.local/bin/uv run pytest` → `109 passed`; hashes de manifest, fuente, procesado y ocho outputs idénticos al baseline |
| Rollback | Revertir solo `docs/planificacion.md`, las tres pruebas de planificación, checkboxes 3.1–3.3 y esta evidencia; PR1/PR2 y artefactos protegidos permanecen |

## Evidencia de unidad correctiva

| Evidencia | Resultado exacto |
|---|---|
| Prueba focalizada | `/home/jonialen/.local/bin/uv run pytest tests/test_repository_cleanup.py` → `8 passed` antes del cambio y `8 passed` después |
| Suite completa | `/home/jonialen/.local/bin/uv run pytest` → `109 passed` |
| Dispatcher nativo | `gentle-ai sdd-status repository-cleanup-and-delivery-plan --cwd /home/jonialen/Documents/uvg/s8/data/proyecto1 --json --instructions` → `12/12`, `pending: 0`, `allComplete: true`, `apply: all_done`; `verify` aún bloqueado por `path-bound compact authority contains a foreign OpenSpec path` |
| Harness real | N/A: corrección exclusiva de metadatos SDD, sin frontera de código, datos o runtime; el dispatcher nativo es la validación operativa aplicable |
| Integridad | `git diff --check` → código 0; `docs/planificacion.md` no fue modificado por esta corrección |
| Rollback | Revertir solo `tasks.md`, esta sección de `apply-progress.md` y el renombre/anotación de `verify-attempt-blocked.md`; PR1–PR3 y `docs/planificacion.md` permanecen |

**Carga real PR1:** 399 líneas autoradas estimadas. **PR2:** 324. **PR3:** 388 líneas (`129` adiciones + `259` eliminaciones) contra el estado final de PR2. **Corrección:** alcance documental mínimo; no implementa PR4–PR7. **Bloqueo externo restante:** resolver la autoridad compacta de revisión ajena antes de la verificación final.
