```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:925e61ce44c366425fc492018cddf2e23f46099fc9e8b03396106daf52e29364
verdict: pass
blockers: 0
critical_findings: 0
requirements: 6/6
scenarios: 14/14
test_command: /home/jonialen/.local/bin/uv run pytest
test_exit_code: 0
test_output_hash: sha256:e9b96c4acd164a3bda194f06a3c59319d5bd6275e8edbb92814943496910d0f3
build_command: /home/jonialen/.local/bin/uv run python -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8')) for root in ('src','scripts') for p in pathlib.Path(root).rglob('*.py')]"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Informe de verificación

**Cambio:** `repository-cleanup-and-delivery-plan`  
**Slice:** PR1, tareas 1.1–1.5 — migración de fuente canónica y referencias vigentes  
**Modo:** Strict TDD; ejecución automática; persistencia híbrida  
**Naturaleza del informe:** verificación parcial de una unidad de entrega. No sustituye la verificación final del cambio completo. PR2 y PR3 permanecen intencionalmente pendientes y se excluyen del veredicto.

### Completitud

| Métrica | Valor |
|---|---:|
| Tareas PR1 totales | 5 |
| Tareas PR1 completas | 5 |
| Tareas PR1 incompletas | 0 |
| Tareas posteriores fuera de alcance | 10 |

### Ejecución de build, pruebas y validaciones

| Comando | Salida principal | Exit | SHA-256 de salida exacta |
|---|---|---:|---|
| `/home/jonialen/.local/bin/uv run pytest` | `101 passed in 0.15s` | 0 | `e9b96c4acd164a3bda194f06a3c59319d5bd6275e8edbb92814943496910d0f3` |
| `/home/jonialen/.local/bin/uv run pytest tests/test_consolidation.py tests/test_diagnostics.py tests/test_cleaning.py tests/test_cleaning_cli.py` | `67 passed in 0.11s` | 0 | `0418a3ddafebc488d94daf7cc50a9e4b19f57375a376ed55b18037421b31f1f1` |
| Validación AST declarada en el sobre | Sin salida; sintaxis válida en `src/` y `scripts/` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Harness Python read-only con salidas temporales | `11867×20`, 11,867 códigos, hash esperado, regeneración idéntica y flujo consolidar→diagnosticar→limpiar | 0 | `b9905dc4cdb7bfb350420688489e5d12de058116874ca0dc05956c9b7b9c20b2` |
| `{ git diff HEAD --summary -M; git diff HEAD --name-status -M; git diff --check; }` | Rename `R100`; `git diff --check` sin errores | 0 | `15f5f9875568fe411edb63eeff3491cbe36b9a520a85ca7326e9f33280659ef8` |

No existe comando de coverage configurado en `openspec/config.yaml`; el análisis de cobertura se omite sin afectar el veredicto. Tampoco existen linter ni type checker configurados.

### Evidencia de migración y preservación

| Comprobación | Resultado |
|---|---|
| CSV canónico | SHA-256 `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f` |
| Forma y contenido | 11,867 filas, 20 columnas y 11,867 códigos únicos |
| Identidad con origen anterior | El blob `HEAD:data/interim/establecimientos_diversificado_raw_unificado.csv` es byte-idéntico al destino |
| Evidencia Git | `R100 data/interim/... -> data/source/establecimientos_diversificado_mineduc.csv` |
| Reproducibilidad | Los 23 HTML y el manifest regeneran un archivo byte-idéntico en un directorio temporal |
| Referencias operativas antiguas | 0 coincidencias en `src/`, `scripts/`, `tests/`, `docs/` y `openspec/specs/` para la ruta anterior, `DEFAULT_INTERIM_CSV` o `--interim-csv` |
| Referencias actuales | Defaults y CLI usan `data/source/establecimientos_diversificado_mineduc.csv` y `--source-csv`; limpieza conserva `data/processed/` |
| Artefactos protegidos | 32/32 hashes del recibo coinciden: 23 HTML, manifest, procesado y siete CSV de `outputs/tablas/` |
| Preservación adicional | `.venv/`, cambio de Anggie y `openspec/changes/archive/` existen y no presentan diff frente a `HEAD` |

Las referencias antiguas que permanecen en archivos archivados, el cambio de Anggie, artefactos de planificación del cambio y el recibo de migración son evidencia histórica, no referencias operativas.

### Matriz de cumplimiento de especificaciones del slice

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Unión sin limpieza | Migración íntegra | Harness de identidad de blob/hash + `R100` | ✅ COMPLIANT |
| Unión sin limpieza | Diferencia detectada | `test_valida_checksum_del_manifest_antes_de_consolidar`; pruebas de escritura atómica | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | Reproducción comprobada | Harness real sobre 23 HTML + manifest | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | Procedencia incompleta | Casos de checksum, manifest inválido, HTML truncado y ausencia de salida parcial | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Métricas reproducibles | `test_escribe_tablas_y_diagnostico_markdown_generados_por_codigo` + harness real | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Catálogo oficial ausente | `test_reporta_patrones_sospechosos_y_difiere_duplicados_parciales` | ✅ COMPLIANT |
| Generación de CSV limpio separado | Limpieza canónica | CLI por defecto + harness real temporal | ✅ COMPLIANT |
| Generación de CSV limpio separado | Entrada ausente o ilegible | `test_cli_reporta_entrada_ausente_sin_traceback_ni_parciales` | ✅ COMPLIANT |
| Generación de CSV limpio separado | Entrada malformada | `test_rechaza_csv_malformado_y_permite_csv_solo_con_encabezados` | ✅ COMPLIANT |
| Generación de CSV limpio separado | Solo encabezados | Caso de encabezados sin filas en la misma prueba | ✅ COMPLIANT |
| Protección de fuentes y decisiones diferidas | Artefactos protegidos | Prueba de no mutación + validación de 32 hashes | ✅ COMPLIANT |
| Protección de fuentes y decisiones diferidas | Decisión no determinística | `test_conserva_columna_nbsp_con_contenido_y_reporta_decision_no_segura` | ✅ COMPLIANT |
| Integridad de referencias y recuperación | Referencias consistentes | Pruebas de defaults/flags, búsqueda dirigida y suite completa | ✅ COMPLIANT |
| Integridad de referencias y recuperación | Fallo y rollback | Pruebas atómicas + identidad del blob Git anterior + recibo recuperable | ✅ COMPLIANT |

**Resumen de cumplimiento del slice:** 14/14 escenarios conformes; 6/6 requisitos cubiertos.

### Corrección estática

| Requisito | Estado | Evidencia |
|---|---|---|
| Unión sin limpieza | ✅ Implementado | Destino canónico y rename byte-idéntico |
| Extracción estructural | ✅ Implementado | Parser y manifest sin cambios conductuales; salida nueva reproducible |
| Diagnóstico rúbrica plus | ✅ Implementado | `DEFAULT_SOURCE_CSV` y `--source-csv` vigentes |
| Generación de CSV limpio | ✅ Implementado | Fuente canónica y salida procesada separadas |
| Protección de fuentes | ✅ Implementado | Guards, atomicidad y hashes preservados |
| Integridad de referencias y recuperación | ✅ Implementado | Cero referencias operativas antiguas y rollback recuperable desde Git |

### Coherencia con el diseño

| Decisión | Seguida | Evidencia |
|---|---|---|
| `git mv` + SHA-256 + regeneración | ✅ Sí | R100, hash completo y regeneración byte-idéntica |
| Reemplazar defaults/flags sin alias | ✅ Sí | `DEFAULT_SOURCE_CSV`/`--source-csv`; alias anterior ausente |
| Preservar procedencia y salidas | ✅ Sí | 32/32 hashes y diff protegido limpio |
| Mantener historial archivado | ✅ Sí | `archive/` preservado sin cambios |
| PR1 como unidad autónoma y reversible | ✅ Sí | 315 líneas tracked autoradas, pruebas focalizadas y límite de rollback documentado |

### Cumplimiento TDD

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia TDD reportada | ✅ | Tabla RED/GREEN/TRIANGULATE/REFACTOR presente en `apply-progress.md` |
| Evidencia para tareas PR1 | ✅ | 5/5 tareas documentadas; 1.1 es inventario sin conducta nueva |
| Archivos de prueba presentes | ✅ | 4/4 suites declaradas existen |
| GREEN actual confirmado | ✅ | 67/67 focalizadas y 101/101 totales |
| Triangulación | ✅ | Defaults, rutas externas, symlinks, manifest incompleto, malformación y atomicidad |
| Safety net | ✅ | 63/63 reportado antes de la ampliación; 101/101 actual |

El estado RED histórico no se recreó porque requeriría revertir implementación, lo cual está prohibido para esta verificación read-only; se corroboró mediante el diff, la existencia de las pruebas y el GREEN actual.

### Distribución de capas de prueba

| Capa | Pruebas | Archivos | Herramienta |
|---|---:|---:|---|
| Unidad/CLI | 67 | 4 | pytest mediante uv |
| Integración configurada | 0 | 0 | No configurada |
| E2E | 0 | 0 | No configurada |
| Harness real adicional | 1 flujo | N/A | Python sobre datos reales y salidas temporales |

### Cobertura de archivos modificados

Análisis omitido: no hay herramienta ni comando de coverage configurado.

### Calidad de aserciones

Se inspeccionaron las cuatro suites modificadas. No se encontraron tautologías, aserciones sin llamadas a producción, bucles fantasma, checks únicamente de tipo ni pruebas smoke sin comportamiento verificable.

**Calidad de aserciones:** ✅ Todas las aserciones revisadas verifican comportamiento observable.

### Métricas de calidad

**Linter:** ➖ No disponible  
**Type checker:** ➖ No disponible  
**Validación sintáctica AST:** ✅ Sin errores

### Hallazgos

**CRITICAL:** Ninguno.  
**WARNING:** Ninguno.  
**SUGGESTION:** Ninguna.

### Veredicto PR1

**PASS**

Las tareas 1.1–1.5 cumplen el contrato de migración canónica, reproducibilidad, actualización de referencias y preservación. Las tareas de PR2 y PR3 permanecen fuera de alcance y no alteran este veredicto parcial.
