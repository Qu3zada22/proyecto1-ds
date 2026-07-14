```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:ac9509b9ac3e7a1aee50f603b7a3662fed48dd7885f1b6b12dfd8114b39cbaaf
verdict: pass
blockers: 0
critical_findings: 0
requirements: 0/0
scenarios: 0/0
test_command: "/home/jonialen/.local/bin/uv run pytest"
test_exit_code: 0
test_output_hash: sha256:59b23ee45e3fb3df6c1225614934fee7546a5296a75cf3d9ceffc683cbfb1fb7
build_command: "not configured"
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Cambio**: `data-pipeline-bootstrap`  
**Proyecto**: `proyecto1-ds`  
**Versión**: N/A  
**Modo**: Strict TDD  
**Fecha**: 2026-07-14  
**Resultado de revisión acotada**: ✅ La validación previa al reemplazo del reporte permitió continuar con lineage `review-3fd2f13a80a0fdf2`; después de persistir este reporte, `gentle-ai sdd-status` marca verificación completa y mantiene archivo bloqueado por `scope-changed` de la revisión.

### Completitud

| Métrica | Valor |
|--------|-------|
| Artefactos revisados | `proposal.md`, `design.md`, `tasks.md`, `apply-progress.md`, 3 delta specs y `openspec/config.yaml` |
| Tareas totales | 46 |
| Tareas completas | 46 |
| Tareas incompletas | 0 |
| Requisitos verificados | 7/7 |
| Escenarios verificados | 15/15 |
| Bloqueadores de verificación restantes | 0 |

### Ejecución de build y pruebas

**Build**: ➖ No configurado en `openspec/config.yaml`; no hay comando de build para este proyecto Python script-first.

```text
build_command: not configured
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

**Tests**: ✅ 63 passed / ❌ 0 failed / ⚠️ 0 skipped

```text
$ /home/jonialen/.local/bin/uv run pytest
============================= test session starts ==============================
platform linux -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/jonialen/Documents/uvg/s8/data/proyecto1
configfile: pyproject.toml
testpaths: tests
collected 63 items

tests/test_acquisition.py ......................                         [ 34%]
tests/test_cli.py ........                                               [ 47%]
tests/test_consolidation.py ...................                          [ 77%]
tests/test_diagnostics.py ..........                                     [ 93%]
tests/test_manifest.py ....                                              [100%]

============================== 63 passed in 0.11s ==============================
test_output_hash: sha256:59b23ee45e3fb3df6c1225614934fee7546a5296a75cf3d9ceffc683cbfb1fb7
```

**Pruebas frescas sin bytecode/cache**: ✅ 63 passed

```text
$ PYTHONDONTWRITEBYTECODE=1 /home/jonialen/.local/bin/uv run pytest -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/jonialen/Documents/uvg/s8/data/proyecto1
configfile: pyproject.toml
testpaths: tests
collected 63 items

tests/test_acquisition.py ......................                         [ 34%]
tests/test_cli.py ........                                               [ 47%]
tests/test_consolidation.py ...................                          [ 77%]
tests/test_diagnostics.py ..........                                     [ 93%]
tests/test_manifest.py ....                                              [100%]

============================== 63 passed in 0.09s ==============================
output_hash: sha256:f71d31e1d4dff35b70f2fe2f4e0b33bdea41f9f3af31657894a980f58f1d00b5
```

**Runtime de consolidación**: ✅ passed

```text
$ /home/jonialen/.local/bin/uv run python scripts/consolidar_crudos.py
Dataset intermedio generado: /home/jonialen/Documents/uvg/s8/data/proyecto1/data/interim/establecimientos_diversificado_raw_unificado.csv
output_hash: sha256:cd1f3d55087146b790b3b4f6dc9d00c96da3a39624ba37809a6a1935563b73ed
```

**Runtime de diagnóstico**: ✅ passed

```text
$ /home/jonialen/.local/bin/uv run python scripts/diagnosticar_crudos.py
Diagnóstico generado: /home/jonialen/Documents/uvg/s8/data/proyecto1/docs/diagnostico.md
output_hash: sha256:71976fa1073bc1b19677c8cec97b754ca1b025d3e53cf54d8ad4ff97f6aec220
```

**Validación de revisión acotada previa al reemplazo del reporte**: ✅ allowed

```text
$ gentle-ai review validate --gate post-apply
schema: gentle-ai.review-gate-result/v1
result: allow
allowed: true
lineage_id: review-3fd2f13a80a0fdf2
generation: 1
store_revision: sha256:5d4ac562a47d7ea063a7e56b7f0fff0029d7f22f931bb22031fc33e4ea9dff80
output_hash: sha256:6f61345f7769451f3abd5696a9810cc15d92e6ef07d794a9f9a36e78f274ac46
```

**Cobertura**: ➖ No disponible. `openspec/config.yaml` no define `coverage_command` y el proyecto no configura `pytest-cov`.

### Cumplimiento TDD

| Check | Resultado | Detalles |
|-------|-----------|----------|
| Evidencia TDD reportada | ✅ | `apply-progress.md` contiene la tabla de evidencia de ciclo TDD. |
| Todas las tareas tienen pruebas o justificación | ✅ | Las tareas de comportamiento enlazan con `tests/test_acquisition.py`, `tests/test_manifest.py`, `tests/test_cli.py`, `tests/test_consolidation.py` y `tests/test_diagnostics.py`; filas de configuración/documentación están justificadas. |
| RED confirmado | ✅ | `apply-progress.md` registra fallas RED por tarea/remediación y los archivos de prueba existen. |
| GREEN confirmado | ✅ | La suite completa pasó ahora: 63/63. |
| Triangulación adecuada | ✅ | Hay casos múltiples para adquisición, fallback, rollback, WebForms, consolidación CSV/HTML, errores de esquema, diagnóstico y límites sin limpieza. |
| Safety Net para archivos modificados | ✅ | `apply-progress.md` registra ejecuciones previas de safety net antes de remediaciones. |

**Cumplimiento TDD**: 6/6 checks aprobados.

---

### Distribución de capas de prueba

| Capa | Pruebas | Archivos | Herramientas |
|------|---------|----------|--------------|
| Unit | 45 | 5 | `pytest` |
| Integración/CLI | 18 | 3 | `pytest`, carga/ejecución de scripts |
| E2E | 0 | 0 | No configurado |
| **Total** | **63** | **5** | |

---

### Cobertura de archivos cambiados

Análisis de cobertura omitido: no hay herramienta de cobertura detectada ni comando configurado.

---

### Calidad de aserciones

**Calidad de aserciones**: ✅ Todas las aserciones inspeccionadas verifican comportamiento real. El caso `assert rows == []` cubre el escenario oficial de cero resultados y tiene pruebas compañeras no vacías; las aserciones sobre temporales/backups validan efectos de rollback después de ejercer rutas productivas.

---

### Métricas de calidad

**Linter**: ➖ No disponible  
**Type Checker**: ➖ No disponible

### Matriz de cumplimiento de especificación

| Requisito | Escenario | Prueba/evidencia runtime | Resultado |
|-----------|-----------|--------------------------|-----------|
| Adquisición mixta trazable | Descarga oficial disponible | `tests/test_acquisition.py::test_descarga_oficial_y_metadatos_completos`; suite aprobada | ✅ COMPLIANT |
| Adquisición mixta trazable | Fallback manual permitido | `test_registra_fallback_manual_con_error_explicito`, `test_registra_fallback_manual_cuando_mineduc_responde_html_invalido`, `test_respuesta_html_mineduc_sin_manual_falla_con_contexto_de_fallback`; suite aprobada | ✅ COMPLIANT |
| Adquisición mixta trazable | HTML oficial preservado sin CSV directo | `test_captura_html_oficial_diversificado_sin_convertirlo_a_csv`; manifest real conserva 23 lotes `html-form` | ✅ COMPLIANT |
| Adquisición mixta trazable | Alcance no disponible | `test_documenta_alcance_disponible_y_faltante`, `test_reporta_alcance_faltante_sin_csv`; suite aprobada | ✅ COMPLIANT |
| Metadatos de fuente y versión | Metadatos completos | `tests/test_manifest.py::test_manifest_escribe_metadatos_y_checksum`; manifest con URL, fecha, versión, cobertura, departamento, método y checksum | ✅ COMPLIANT |
| Unión sin limpieza | Esquemas compatibles | `test_consolida_csv_compatibles_preservando_valores_y_procedencia`; comando real de consolidación aprobado | ✅ COMPLIANT |
| Unión sin limpieza | Esquemas incompatibles | `test_reporta_esquema_incompatible_sin_generar_salida_parcial`; suite aprobada | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | HTML oficial sin CSV directo | `test_extrae_tabla_html_oficial_sin_limpiar_texto_de_celdas`; consolidación real generó 11,867 filas desde 23 HTML oficiales | ✅ COMPLIANT |
| Extracción estructural desde HTML oficial | HTML sin tabla esperada | `test_html_sin_tabla_esperada_reporta_error_y_no_genera_salida`, pruebas de HTML truncado/parcial; suite aprobada | ✅ COMPLIANT |
| Trazabilidad por registro | Procedencia completa | `test_consolida_csv_compatibles_preservando_valores_y_procedencia`; dataset intermedio real contiene `archivo_origen` y `departamento_origen` | ✅ COMPLIANT |
| Trazabilidad por registro | Departamento ambiguo | `test_conserva_departamento_ambiguo_como_pendiente_para_diagnostico`; suite aprobada | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Métricas obligatorias generadas | `test_genera_metricas_obligatorias_sin_modificar_csv_intermedio`; comando real de diagnóstico regeneró tablas y Markdown | ✅ COMPLIANT |
| Diagnóstico rúbrica plus | Catálogo oficial no disponible | `test_reporta_patrones_sospechosos_y_difiere_duplicados_parciales`; diagnóstico documenta catálogo territorial `no verificable` | ✅ COMPLIANT |
| Límites previos a limpieza | Duplicados exactos detectados | `test_genera_metricas_obligatorias_sin_modificar_csv_intermedio`; resumen real reporta duplicados exactos sin eliminar datos | ✅ COMPLIANT |
| Límites previos a limpieza | Duplicados parciales sospechosos | `test_reporta_patrones_sospechosos_y_difiere_duplicados_parciales`; `problemas_potenciales.csv` incluye `duplicados_parciales_diferidos` | ✅ COMPLIANT |

**Resumen de cumplimiento**: 15/15 escenarios compliant.

### Correctitud (evidencia estática)

| Requisito | Estado | Notas |
|-----------|--------|-------|
| Adquisición MINEDUC / HTML crudo cuando no hay CSV directo | ✅ Implementado | `acquisition.py` valida URLs oficiales HTTPS de MINEDUC, captura HTML WebForms con campos de estado requeridos, rechaza HTML/CSV inválidos en la ruta CSV y registra fallback manual cuando corresponde. |
| Manifest, checksum y procedencia | ✅ Implementado | `manifest.py` valida versiones SemVer-like y SHA-256; consolidación verifica checksums antes de leer y añade columnas de linaje. |
| Consolidación a CSV intermedio sin limpieza | ✅ Implementado | `consolidation.py` conserva texto de celdas, compara encabezados normalizados solo para compatibilidad, rechaza filas ragged y escribe de forma atómica en `data/interim`. |
| Diagnóstico reproducible | ✅ Implementado | `diagnostics.py` genera resumen, métricas por columna, duplicados exactos, problemas potenciales, dominios observados y `docs/diagnostico.md`. |
| No generar dataset limpio ni limpiar datos | ✅ Respetado | El alcance de limpieza, deduplicación parcial, normalización categórica y dataset final sigue diferido. |

### Coherencia (diseño)

| Decisión | ¿Seguida? | Notas |
|----------|-----------|-------|
| Python script-first con módulos en `src/proyecto1_ds/` | ✅ Sí | Los CLIs son envoltorios delgados sobre módulos de adquisición, manifest, consolidación y diagnóstico. |
| `data/raw/` como zona cruda inmutable con manifest externo | ✅ Sí | Los artefactos crudos HTML `html-form` permanecen en `data/raw/`; el manifest guarda fuente, fecha, cobertura, versión, método, checksum y contexto de error. |
| Consolidación estructural append-only a `data/interim/` | ✅ Sí | Se extraen tablas HTML oficiales y solo se agregan columnas de linaje. |
| Diagnóstico generado en `outputs/tablas/` y `docs/diagnostico.md` | ✅ Sí | El comando runtime regeneró salidas esperadas. |
| Catálogos faltantes degradan a no verificable | ✅ Sí | El diagnóstico documenta el catálogo territorial como `no verificable` y evita declarar inválidos sin evidencia. |

### Issues encontrados

**CRITICAL**: None  
**WARNING**: None  
**SUGGESTION**: Coverage/linter/type-check no están configurados; considerarlos en una fase posterior si el proyecto requiere métricas estáticas más fuertes.

**Bloqueador externo a verificación**: `gentle-ai sdd-status` reporta `archive: blocked` porque la revisión acotada quedó en `scope-changed` después de reemplazar `verify-report.md`; requiere una nueva lineage o resolución explícita de revisión para archivo.

### Veredicto

PASS

El cambio cumple propuesta, specs, diseño y tareas bajo evidencia runtime fresca; Strict TDD está documentado y validado, las 63 pruebas pasan y las salidas se regeneran por script. No queda bloqueador de verificación; el archivo requiere resolver el `scope-changed` de revisión provocado por la actualización de este reporte.
