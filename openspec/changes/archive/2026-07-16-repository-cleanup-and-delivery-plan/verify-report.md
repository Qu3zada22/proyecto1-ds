```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:44be552b270eb5529c73bd06e2fab098a5a98de47fbe690f26553f2d24c1746b
verdict: pass
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 20/20
test_command: /home/jonialen/.local/bin/uv run pytest
test_exit_code: 0
test_output_hash: sha256:6e527a96e72671a8bf7bc1ffa553a1b3adf6755d224e631f061fb24d9bbe7aa0
build_command: /home/jonialen/.local/bin/uv run python -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8')) for root in ('src','scripts','tests') for p in pathlib.Path(root).rglob('*.py')]"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio:** `repository-cleanup-and-delivery-plan`  
**Versión:** N/A  
**Modo:** Strict TDD; verificación final automática; persistencia híbrida  
**Alcance ejecutable:** tareas 1.1–3.3. Los seguimientos 4.1–4.3 son una hoja de ruta sin casillas y permanecen explícitamente **Planificado/no implementado**.

### Preflight autoritativo y revisión

| Comprobación | Resultado |
|---|---|
| Tareas nativas | `12/12`, pendientes `0`, `allComplete: true`, `apply: all_done` |
| Gate | `post-apply` |
| Resultado | ✅ `allow` — authoritative transaction, current repository target, and content-bound artifacts match |
| Linaje | `review-324f9f6beb796ec0`, generación 1 |
| Store/genesis/chain revision | `sha256:b41be1ce9163d35cc080e5255d342c1f74806c5d89cba6fb4917dba494a351b4` |
| Candidate tree | `9d96e85b94ea462ae11ea2b10a9d2d56252c603c` |
| Paths digest | `sha256:2ad74721d14b9e6b8b1066df484b07bb47b1aad4d2745d79322d1171b800ce47` |

El gate dedicado es autoritativo para esta ejecución y permitió continuar. El intento previo se conserva sin cambios en `verify-attempt-blocked.md` como evidencia histórica de la semántica anterior de tareas.

### Completitud

| Métrica | Valor |
|---|---:|
| Tareas ejecutables totales | 12 |
| Tareas completas | 12 |
| Tareas incompletas | 0 |
| Requisitos de la delta | 9 |
| Escenarios de la delta | 20 |
| Seguimientos futuros fuera de alcance | 3, sin casillas |

### Ejecución de build, pruebas y validaciones

| Comando | Resultado | Exit | SHA-256 de salida exacta |
|---|---|---:|---|
| `/home/jonialen/.local/bin/uv run pytest` | `109 passed in 0.32s` | 0 | `6e527a96e72671a8bf7bc1ffa553a1b3adf6755d224e631f061fb24d9bbe7aa0` |
| `/home/jonialen/.local/bin/uv run pytest tests/test_consolidation.py tests/test_diagnostics.py tests/test_cleaning.py tests/test_cleaning_cli.py tests/test_repository_cleanup.py` | `75 passed in 0.21s` | 0 | `55ae52c199dec9c529985270a4d1ab2c3ff548e638dcfbcc8b3118889eafa6ce` |
| Validación AST declarada en el sobre | Sin salida; sintaxis válida en `src/`, `scripts/` y `tests/` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Harness canónico en salidas temporales | 11,867×20; 11,867 códigos; regeneración byte-idéntica; diagnóstico y limpieza ejecutados | 0 | `cc271030412b9ce363655c7806792af8d4171d79393f2e2e87faa3565e6587bb` |
| Harness Anggie desde objeto Git | Identidad, parser y métricas reproducidos | 0 | `ade815e5884a082b9eb91205aedc10c9f779173d2a1d504188561be91ce9e997` |
| Harness del plan | 29 requisitos, diez campos y tres asignaciones verificadas | 0 | `2cd8b8cdcaa92958b41fd0d031c6032f6e75cdf454a41c46208766274aa49149` |
| Harness de protegidos/allowlist | 33/33 hashes, 23 HTML, `.venv/` y tres eliminaciones autorizadas | 0 | `4fc0e93bf8a06d0da4c8da6e08a8f40866ae65ea3acf4f8c623f4439f89611e0` |
| Git summary/name-status/check/status | Rename R100, diff válido y estado inventariado | 0 | `7cab5f381fe7fe41cb82d812f8f24637a7a23856dab6162696259d5c497c5d6f` |

No hay comando de coverage, linter ni type checker configurado en `openspec/config.yaml`; estas dimensiones se omiten sin afectar el veredicto.

### Evidencia sustantiva

| Dimensión | Resultado actual |
|---|---|
| Fuente canónica | SHA-256 `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`; 11,867×20 y 11,867 códigos |
| Reproducibilidad | Los 23 HTML y el manifest regeneraron bytes idénticos en `/tmp`; diagnóstico reportó 11,867 filas, 20 columnas y 0 duplicados exactos |
| Procedencia/protegidos | 33/33 hashes coinciden: HTML, manifest, fuente, procesado y outputs; `.venv/` permanece |
| Migración Git | `R100` desde `data/interim/...` hacia `data/source/establecimientos_diversificado_mineduc.csv` |
| Referencias vivas | Cero usos operativos de `data/interim/`, `DEFAULT_INTERIM_CSV`, `--interim-csv` o `data/clean/`; la única coincidencia es una aserción negativa |
| Allowlist | Solo se retiraron los dos `.gitkeep` y el cambio activo de Anggie; cachés recreables siguen ignoradas |
| Anggie | Commit `6e83a26…`, blob `2e27f11…`, SHA-256 `ca738d5d…`; 12,948×18, 11,867 códigos, 1,081 duplicados adicionales y 0/0 códigos exclusivos |
| Cifra disputada | `12,807` permanece retirada; `12,948` fue reproducida con `strict=False, skipinitialspace=True` |
| Plan autoritativo | 29/29 requisitos con diez campos; estados futuros no se promueven a completados |
| Asignaciones | Anggie, Iris y Jonathan tienen entregable, aceptación, aporte Code Book, evidencia Git y dependencias |

### Matriz de cumplimiento de especificaciones

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Unión sin limpieza | Migración íntegra | Harness de bytes/hash y Git `R100` | ✅ COMPLIANT |
| Unión sin limpieza | Diferencia detectada | Checksum de manifest, atomicidad y rollback probados | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | Reproducción comprobada | Harness real sobre 23 HTML + manifest | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | Procedencia incompleta | Casos de ausencia, checksum, manifest y HTML truncado | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Métricas reproducibles | Harness actual + pruebas de tablas/documento | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Catálogo oficial ausente | Prueba de catálogo no verificable sin inferir inválidos | ✅ COMPLIANT |
| Generación de CSV limpio separado | Limpieza canónica | Harness temporal y CLI por defecto | ✅ COMPLIANT |
| Generación de CSV limpio separado | Entrada ausente o ilegible | Prueba CLI sin parciales ni traceback | ✅ COMPLIANT |
| Generación de CSV limpio separado | Entrada malformada | Pruebas de vacío, ragged, comillas y encabezados duplicados | ✅ COMPLIANT |
| Generación de CSV limpio separado | Solo encabezados | Prueba de encabezados con conteos cero | ✅ COMPLIANT |
| Protección de fuentes y decisiones diferidas | Artefactos protegidos | 33/33 hashes y pruebas de no mutación | ✅ COMPLIANT |
| Protección de fuentes y decisiones diferidas | Decisión no determinística | Caso NBSP con contenido conservado y trazado | ✅ COMPLIANT |
| Limpieza por lista permitida | Eliminación aprobada | Estado Git, allowlist y harness de protegidos | ✅ COMPLIANT |
| Limpieza por lista permitida | Eliminación no prevista | Preflight cubre CWD, `.venv/`, staged y unstaged | ✅ COMPLIANT |
| Reconciliación de Anggie verificable | Evidencia conciliada | Harness actual desde `git show` | ✅ COMPLIANT |
| Reconciliación de Anggie verificable | Medición no reproducible | Retirada de 12,807 y reproducción de 12,948 | ✅ COMPLIANT |
| Planificación autoritativa y contribución | Cobertura completa | 29/29 filas con diez campos no vacíos | ✅ COMPLIANT |
| Planificación autoritativa y contribución | Asignación insuficiente | Prueba exige las tres personas, Git y Code Book | ✅ COMPLIANT |
| Integridad de referencias y recuperación | Referencias consistentes | Búsqueda dirigida, defaults/flags y 109 pruebas | ✅ COMPLIANT |
| Integridad de referencias y recuperación | Fallo y rollback | Atomicidad, identidad del blob y recibos de recuperación | ✅ COMPLIANT |

**Resumen de cumplimiento:** 20/20 escenarios conformes; 9/9 requisitos cubiertos mediante pruebas y harnesses ejecutados actualmente.

### Corrección estática

| Requisito | Estado | Evidencia |
|---|---|---|
| Unión sin limpieza | ✅ Implementado | Fuente canónica byte-idéntica y R100 |
| Extracción estructural | ✅ Implementado | 23 HTML + manifest reproducen el canónico |
| Diagnóstico rúbrica plus | ✅ Implementado | Fuente nueva y métricas regenerables |
| Generación de CSV limpio | ✅ Implementado | Entrada canónica y salida separada en `data/processed/` |
| Protección de fuentes | ✅ Implementado | Hashes, atomicidad y decisiones manuales |
| Limpieza por lista permitida | ✅ Implementado | Preflight y eliminaciones acotadas |
| Reconciliación de Anggie | ✅ Implementado | Recibo completo y medición actual |
| Planificación y contribución | ✅ Implementado | Matriz 29/29 y tres asignaciones verificables |
| Integridad y recuperación | ✅ Implementado | Terminología vigente y rollback documentado/probado |

### Coherencia con el diseño

| Decisión | Seguida | Evidencia |
|---|---|---|
| `git mv` + SHA-256 + regeneración | ✅ Sí | R100, hash completo y bytes regenerados idénticos |
| Reemplazar defaults/flags sin alias | ✅ Sí | `DEFAULT_SOURCE_CSV` y `--source-csv`; alias ausente |
| Allowlist explícita; proteger `.venv/` | ✅ Sí | Tres eliminaciones rastreadas y `.venv/` presente |
| Preservar Anggie antes de retirar el cambio | ✅ Sí | Recibo reproducible desde commit/blob |
| Plan con requisitos, brechas y responsables | ✅ Sí | 29 filas y asignaciones completas |
| Entregas futuras fuera del cambio | ✅ Sí | Hoja de ruta sin casillas y estados planificados/no implementados |
| Unidades PR1→PR2→PR3 | ✅ Sí | Evidencia focalizada, harness y rollback por unidad |

### Cumplimiento TDD

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia TDD reportada | ✅ | Tabla RED/GREEN/TRIANGULATE/REFACTOR presente |
| Tareas con prueba o harness | ✅ | 12/12 tareas ejecutables tienen evidencia asociada |
| RED corroborado | ✅ | Archivos y casos descritos existen; no se revirtió el worktree para recrear RED histórico |
| GREEN actual | ✅ | 75/75 pruebas focalizadas y 109/109 totales |
| Triangulación | ✅ | Rutas, symlinks, atomicidad, procedencia, parser, plan y estados futuros |
| Safety net | ✅ | Baselines 63→67→101→106→109 documentados |

**Cumplimiento TDD:** 6/6 comprobaciones satisfechas.

### Distribución de capas de prueba

| Capa | Pruebas | Archivos | Herramienta |
|---|---:|---:|---|
| Unidad/CLI/repositorio | 109 | 8 | pytest mediante uv |
| Harness de integración real | 4 | N/A | Python + Git sobre datos/artefactos reales |
| E2E configurado | 0 | 0 | No disponible |

### Cobertura de archivos modificados

Análisis omitido: no existe herramienta ni comando de coverage configurado.

### Calidad de aserciones

Se inspeccionaron las cinco suites focalizadas. No se encontraron tautologías, aserciones sin ejecución de producción, bucles fantasma, comprobaciones solo de tipo ni smoke tests sin comportamiento observable.

**Calidad de aserciones:** ✅ Todas las aserciones revisadas verifican comportamiento real.

### Métricas de calidad

**Linter:** ➖ No disponible  
**Type checker:** ➖ No disponible  
**Validación sintáctica AST:** ✅ Sin errores

### Evidencia canónica de verificación

Los bytes exactos entre los marcadores siguientes, incluido el salto final, son el preimage canónico de 1,673 bytes cuyo SHA-256 es el `evidence_revision` del sobre.

<!-- verification-evidence:start -->
```text
schema: gentle-ai.verification-evidence/v1
change: repository-cleanup-and-delivery-plan
scope: final-whole-change
task_progress: 12/12
requirements: 9/9
scenarios: 20/20
test_command: /home/jonialen/.local/bin/uv run pytest
test_exit_code: 0
test_output_hash: sha256:6e527a96e72671a8bf7bc1ffa553a1b3adf6755d224e631f061fb24d9bbe7aa0
focused_test_command: /home/jonialen/.local/bin/uv run pytest tests/test_consolidation.py tests/test_diagnostics.py tests/test_cleaning.py tests/test_cleaning_cli.py tests/test_repository_cleanup.py
focused_test_exit_code: 0
focused_test_output_hash: sha256:55ae52c199dec9c529985270a4d1ab2c3ff548e638dcfbcc8b3118889eafa6ce
build_command: /home/jonialen/.local/bin/uv run python -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8')) for root in ('src','scripts','tests') for p in pathlib.Path(root).rglob('*.py')]"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
pipeline_output_hash: sha256:cc271030412b9ce363655c7806792af8d4171d79393f2e2e87faa3565e6587bb
anggie_output_hash: sha256:ade815e5884a082b9eb91205aedc10c9f779173d2a1d504188561be91ce9e997
plan_output_hash: sha256:2cd8b8cdcaa92958b41fd0d031c6032f6e75cdf454a41c46208766274aa49149
protected_output_hash: sha256:4fc0e93bf8a06d0da4c8da6e08a8f40866ae65ea3acf4f8c623f4439f89611e0
git_output_hash: sha256:7cab5f381fe7fe41cb82d812f8f24637a7a23856dab6162696259d5c497c5d6f
review_gate: post-apply
review_result: allow
review_lineage: review-324f9f6beb796ec0
review_store_revision: sha256:b41be1ce9163d35cc080e5255d342c1f74806c5d89cba6fb4917dba494a351b4
review_candidate_tree: 9d96e85b94ea462ae11ea2b10a9d2d56252c603c
```
<!-- verification-evidence:end -->

### Hallazgos

**CRITICAL:** Ninguno.  
**WARNING:** Ninguno sustantivo.  
**SUGGESTION:** El inventario agregado de `gentle-ai sdd-status` aún reportó una autoridad compacta ajena, mientras el preflight dedicado `review validate --gate post-apply` seleccionó el linaje correcto y devolvió `allow`; conviene sanear ese inventario antes del archivo si el dispatcher continúa mostrando `resolve-review`.

### Veredicto

**PASS**

Las 12 tareas ejecutables cumplen los 9 requisitos y 20 escenarios con evidencia runtime vigente. Los entregables posteriores de Anggie, Iris y Jonathan permanecen correctamente fuera del alcance actual como planificación no implementada.
