```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6194cef893236a837d9815a006c7390c5af68adf1c8a53073d6fca0fe360f475
verdict: pass
blockers: 0
critical_findings: 0
requirements: 2/2
scenarios: 4/4
test_command: /home/jonialen/.local/bin/uv run pytest
test_exit_code: 0
test_output_hash: sha256:6c4756e628407e89e397b821e59028c53438f3f807bd3e06c8e23baf9c93a77f
build_command: /home/jonialen/.local/bin/uv run python -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8')) for root in ('src','scripts','tests') for p in pathlib.Path(root).rglob('*.py')]"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio:** `repository-cleanup-and-delivery-plan`  
**Slice:** PR2, tareas 2.1–2.4 — evidencia Anggie y limpieza por lista permitida  
**Modo:** Strict TDD; ejecución automática; persistencia híbrida  
**Naturaleza:** verificación parcial de PR2. PR3 y las entregas posteriores permanecen fuera de alcance.

### Completitud

| Métrica | Valor |
|---|---:|
| Tareas PR2 totales | 4 |
| Tareas PR2 completas | 4 |
| Tareas PR2 incompletas | 0 |
| Tareas posteriores fuera de alcance | 6 |

### Ejecución de build, pruebas y validaciones

| Comando | Resultado | Exit | SHA-256 de salida exacta |
|---|---|---:|---|
| `/home/jonialen/.local/bin/uv run pytest tests/test_repository_cleanup.py` | `5 passed in 0.07s` | 0 | `cc10b56b1fea68b9150cb21a1f008f468d1cd9af061e89d8ca5aab8b6c30a57f` |
| `/home/jonialen/.local/bin/uv run pytest` | `106 passed in 0.22s` | 0 | `6c4756e628407e89e397b821e59028c53438f3f807bd3e06c8e23baf9c93a77f` |
| Validación AST declarada en el sobre | Sintaxis válida en `src/`, `scripts/` y `tests/`; sin salida | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Harness reproducible de Anggie | Commit/blob/hash y métricas coincidentes | 0 | `ade815e5884a082b9eb91205aedc10c9f779173d2a1d504188561be91ce9e997` |
| Comprobación `strict=True` sobre Anggie | Falla reproducida: `Error ',' expected after '"'` | 0 | `014bfd6cd614e9793715aab3ed445db2693d883b691867ee699b627a1716c353` |
| Harness de preservación y allowlist | 33/33 hashes; tres eliminaciones rastreadas exactas | 0 | `d62edc7753e5db98d95d6b5cb3bf9b9d0fc5b6ab18498965ac34abe1f3e11118` |

No existe herramienta ni umbral de cobertura configurado. Tampoco hay linter ni type checker configurados; estas dimensiones se omiten sin afectar el veredicto.

### Evidencia de Anggie

| Comprobación | Resultado reproducido |
|---|---|
| Ref y commit | `scrap-anggie` → `6e83a26a71d743ce08bbec592821da35df52ceef` |
| Ruta y blob | `data/raw/establecimientos_diversificado_guatemala.csv` → `2e27f11a8fb882594b8434f4d85b2ca75bc43b8a` |
| Tamaño y SHA-256 | `8,696,253` bytes; `ca738d5d0628613c8ad5519e15a5f20c4c1e8d536bd4510a2235e893ee3d4fd5` |
| Parser documentado | UTF-8, `csv.reader(strict=False, skipinitialspace=True)` |
| Métricas Anggie | 12,948×18; 11,867 códigos; 11,867 filas exactas únicas; 1,081 duplicados más allá de la primera aparición |
| Contraste canónico | 11,867×20; 11,867 códigos; 0 códigos exclusivos en ambas direcciones |
| Corrección/retirada | `12,807` está explícitamente retirada; `12,948` queda medida y reproducida. `strict=True` falla como documentado. |

### Limpieza, allowlist y preservación

| Comprobación | Resultado |
|---|---|
| Eliminaciones rastreadas | Exactamente 3: `openspec/specs/.gitkeep`, `openspec/changes/archive/.gitkeep` y `openspec/changes/anggie-csv-reconciliation/exploration.md` |
| Cambio activo incompleto | `openspec/changes/anggie-csv-reconciliation/` no existe en el worktree |
| Política ignorada | `.atl/` y `*.egg-info/` ausentes; `.pytest_cache/` y `__pycache__/` fueron recreados por pytest y continúan ignorados |
| Entorno protegido | `.venv/` existe y continúa ignorado; no aparece entre las eliminaciones |
| Procedencia y datos | 33/33 hashes del recibo coinciden: 23 HTML, manifest, fuente canónica, procesado y siete outputs |
| Specs activas | Las cinco specs activas existen; no hay eliminación ni reescritura de `archive/` fuera del `.gitkeep` autorizado |
| Evidencia PR1 | Persisten `verify-pr1.md`, `outputs/reportes/migracion_fuente.md`, el rename R100 y la suite completa en verde |
| Deriva hacia PR3 | No detectada: `docs/planificacion.md` conserva su estructura previa y solo contiene cuatro reemplazos mecánicos de rutas de PR1; las tareas 3.1–3.3 siguen pendientes |
| Higiene del diff | `git diff --check` finaliza con exit 0 |

El texto histórico `32/32` de `verify-pr1.md` se conserva sin edición. El recibo actual contiene 33 artefactos protegidos al contar también el manifest; la comprobación actual es 33/33 y la diferencia de etiqueta histórica no representa pérdida ni mutación.

### Matriz de cumplimiento de especificaciones del slice

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Limpieza por lista permitida | Eliminación aprobada | Prueba focalizada, `git ls-files --deleted`, estado ignorado y harness de 33 hashes | ✅ COMPLIANT |
| Limpieza por lista permitida | Eliminación no prevista | `test_preflight_rechaza_cwd_ajeno_y_objetivos_no_permitidos` y casos staged/unstaged | ✅ COMPLIANT |
| Reconciliación de Anggie verificable | Evidencia conciliada | Harness real desde `git show` con identidad, parser y métricas exactas | ✅ COMPLIANT |
| Reconciliación de Anggie verificable | Medición no reproducible | Retirada explícita de 12,807 y reproducción de 12,948; fallo de parser estricto corroborado | ✅ COMPLIANT |

**Resumen de cumplimiento del slice:** 4/4 escenarios conformes; 2/2 requisitos cubiertos.

### Corrección estática

| Requisito | Estado | Evidencia |
|---|---|---|
| Limpieza por lista permitida | ✅ Implementado | Preflight cubre raíz Git, allowlist, `.venv/` y protegidos staged/unstaged; estado final limitado a tres eliminaciones rastreadas |
| Reconciliación de Anggie verificable | ✅ Implementado | Recibo conserva identidad completa, comando ejecutable, parser tolerante justificado, métricas y retirada de la cifra no reproducida |

### Coherencia con el diseño

| Decisión | Seguida | Evidencia |
|---|---|---|
| Allowlist explícita sin `git clean` ni glob amplio | ✅ Sí | Tres eliminaciones rastreadas exactas; cachés ignoradas acotadas |
| Preservar `.venv/` y artefactos protegidos | ✅ Sí | `.venv/` presente y 33/33 hashes coincidentes |
| Preservar evidencia antes de retirar Anggie | ✅ Sí | Recibo reproducible desde commit/blob antes de ausencia del cambio activo |
| PR2 autónomo, ≤400 líneas y sin PR3 | ✅ Sí | Progreso registra 324 líneas; planificación no fue reescrita |
| Mantener PR1 verificable | ✅ Sí | Rename R100, recibo, verificación histórica y 106/106 pruebas preservados |

### Cumplimiento TDD

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia TDD reportada | ✅ | Tabla RED/GREEN/TRIANGULATE/REFACTOR presente en `apply-progress.md` |
| Tareas PR2 con evidencia | ✅ | 4/4 tareas documentadas y asociadas a `tests/test_repository_cleanup.py` y harnesses reales |
| RED corroborable | ✅ | Archivo nuevo presente; el progreso registra ausencia de preflight, recibo incompleto y allowlist restaurada durante RED |
| GREEN actual | ✅ | 5/5 focalizadas y 106/106 totales |
| Triangulación | ✅ | CWD, ruta no permitida, `.venv/`, índice, worktree, parser estricto/tolerante, métricas y estado final |
| Safety net | ✅ | 101/101 reportado antes de PR2 |

El estado RED histórico no se recreó porque implicaría modificar o revertir el worktree. La evidencia histórica se contrastó con el archivo de pruebas, los harnesses reproducibles y el GREEN actual.

### Distribución de capas de prueba

| Capa | Casos | Archivos | Herramienta |
|---|---:|---:|---|
| Repositorio/unidad | 5 | 1 | pytest mediante uv |
| Integración adicional | 2 harnesses | N/A | Python + Git sobre evidencia real |
| E2E | 0 | 0 | No configurada |

### Cobertura de archivos modificados

Análisis omitido: no existe herramienta ni comando de coverage configurado.

### Calidad de aserciones

Se inspeccionó `tests/test_repository_cleanup.py`. Las aserciones ejercitan el preflight, el recibo y el estado real del repositorio con colecciones fijas no vacías; no se encontraron tautologías, bucles fantasma, checks únicamente de tipo ni pruebas smoke.

**Calidad de aserciones:** ✅ Todas las aserciones revisadas verifican comportamiento observable.

### Métricas de calidad

**Linter:** ➖ No disponible  
**Type checker:** ➖ No disponible  
**Validación sintáctica AST:** ✅ Sin errores

### Hallazgos

**CRITICAL:** Ninguno.  
**WARNING:** Ninguno.  
**SUGGESTION:** Ninguna.

### Veredicto PR2

**PASS**

Las tareas 2.1–2.4 cumplen la reconciliación reproducible de Anggie, la eliminación rastreada exacta, la política de limpieza ignorada, la preservación de artefactos y el límite de alcance del slice. La evidencia de PR1 permanece válida; PR3 continúa pendiente y fuera de alcance.
