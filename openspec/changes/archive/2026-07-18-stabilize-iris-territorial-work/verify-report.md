```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:150587e76567ac779e909f397377cc9682ce21404138dab87683593f59ca9cb4
verdict: pass
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 19/19
test_command: PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider
test_exit_code: 0
test_output_hash: sha256:d118988c6f54a2c17f167034e3a58139f88076bde83db38d2c1dd637eff13852
build_command: git diff --check
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

# Informe de verificación final

## Verification Report

**Cambio**: `stabilize-iris-territorial-work`  
**Versión**: N/A  
**Persistencia**: híbrida  
**Modo**: TDD estricto  
**Alcance**: cambio completo, 7/7 tareas

### Veredicto ejecutivo

**PASS**. La verificación independiente posterior a la corrección confirma los 9 requisitos y 19 escenarios, incluidas las seis variantes de catálogo inválido de `R3-001`. La suite completa pasa con 128/128 pruebas; la regeneración real permanece idempotente; los hashes protegidos permanecen; el alcance territorial de Iris está completo y los entregables de Anggie y la integración final de Jonathan continúan pendientes.

### Completitud

| Métrica | Valor |
|---|---:|
| Tareas totales | 7 |
| Tareas completas | 7 |
| Tareas incompletas | 0 |
| Requisitos verificados | 9 |
| Escenarios verificados | 19 |

### Ejecución de build, pruebas y runtime

| Evidencia | Comando | Exit | Resultado | SHA-256 de salida exacta |
|---|---|---:|---|---|
| Suite completa posterior a corrección | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider` | 0 | 128 passed, 0 failed, 0 skipped | `d118988c6f54a2c17f167034e3a58139f88076bde83db38d2c1dd637eff13852` |
| Foco `R3-001` + catálogo válido | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_cleaning_cli.py -k "catalogo_invalido or limpia_fuente_default_y_escribe_salidas_permitidas" -p no:cacheprovider` | 0 | 7 passed, 10 deselected | `5daeee43e6714ed13da3ef2f8890d352e41441bb5610e3bd817fd0b549869c75` |
| Build/higiene disponible | `git diff --check` | 0 | salida vacía | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Regeneración e idempotencia posterior a corrección | catálogo → limpieza → validación, ejecutado dos veces y comparado con el estado previo | 0 | tres snapshots de seis artefactos idénticos; protegidos idénticos | `d2bfe30bbc9b7dbf3f66ae7d51cf0289739c600a51492a7591a33f5182f7dfe9` |

```yaml
test_command: PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider
test_exit_code: 0
test_output_hash: sha256:d118988c6f54a2c17f167034e3a58139f88076bde83db38d2c1dd637eff13852
focused_test_command: PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_cleaning_cli.py -k "catalogo_invalido or limpia_fuente_default_y_escribe_salidas_permitidas" -p no:cacheprovider
focused_test_exit_code: 0
focused_test_output_hash: sha256:5daeee43e6714ed13da3ef2f8890d352e41441bb5610e3bd817fd0b549869c75
build_command: git diff --check
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
runtime_exit_code: 0
runtime_output_hash: sha256:d2bfe30bbc9b7dbf3f66ae7d51cf0289739c600a51492a7591a33f5182f7dfe9
```

La evidencia final previa queda preservada como historial: suite 122/122 `sha256:9fe2e6dc…` e idempotencia `sha256:398ae07e…`. Los valores del sobre anterior no se reutilizan como prueba posterior a la corrección.

No hay comando adicional de build, cobertura, linter o verificador de tipos configurado en `openspec/config.yaml`. `git diff --check` es el gate de build/higiene disponible.

### Matriz de cumplimiento

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Regresión y escritor seguro | rama segura | `test_capacidad_dir_fd_permanece_detectable_al_sustituir_os_open` y pruebas de carreras atómicas de `test_cleaning.py` | ✅ COMPLIANT |
| Regresión y escritor seguro | plataforma portátil | `test_write_cleaning_outputs_usa_rama_portatil_sin_capacidad_dir_fd` | ✅ COMPLIANT |
| Catálogo requerido por CLI | fixture válido | prueba CLI de éxito y foco `R3-001`: catálogo válido aceptado; catálogos solo-encabezado, esquema inválido, cobertura incompleta, código vacío, código duplicado y departamento ambiguo rechazados antes de escribir | ✅ COMPLIANT |
| Catálogo requerido por CLI | catálogo ausente | `test_cli_reporta_catalogo_ausente_con_fuente_valida_sin_escribir_parciales` | ✅ COMPLIANT |
| Reporte antes/después | comparación generada | `test_salidas_limpias_y_territoriales_reflejan_el_contrato_actual` | ✅ COMPLIANT |
| Reporte antes/después | regeneración autorizada | pipeline real ejecutado dos veces; 20→21 y hashes protegidos comprobados | ✅ COMPLIANT |
| Procedencia inmutable | procedencia válida | `test_generador_usa_espejo_inmutable_y_publica_catalogo_validado`; ejecución real del recurso fijado | ✅ COMPLIANT |
| Procedencia inmutable | integridad inválida | caso `checksum` de `test_generador_preserva_catalogo_previo_ante_entrada_invalida` | ✅ COMPLIANT |
| Reemplazo validado | catálogo completo | prueba del generador y runtime: 22 departamentos, 340 municipios y 340 códigos únicos | ✅ COMPLIANT |
| Reemplazo validado | contenido inválido | casos `schema` y `count`; preservación de bytes previos | ✅ COMPLIANT |
| Pendientes y códigos | pareja conocida | `test_enriquecimiento_separa_dos_typos_de_siete_codigos_provisionales` y prueba 7/145 | ✅ COMPLIANT |
| Pendientes y códigos | similitud insuficiente | siete nombres quedan sin autocorrección y el reporte conserva `decision=revisar` | ✅ COMPLIANT |
| Informe determinístico | raíces distintas | `test_reporte_es_byte_estable_entre_raices_y_publicacion_es_conjunta` | ✅ COMPLIANT |
| Informe determinístico | ruta absoluta | la misma prueba excluye los prefijos absolutos del equipo | ✅ COMPLIANT |
| Planificación autoritativa | cobertura completa | `test_plan_cubre_todos_los_requisitos_con_campos_verificables` | ✅ COMPLIANT |
| Planificación autoritativa | aporte insuficiente | `test_plan_mantiene_entregables_futuros_y_rutas_canonicas` | ✅ COMPLIANT |
| Planificación autoritativa | documentación veraz | `test_documentacion_refleja_el_cierre_territorial_sin_cerrar_el_proyecto` | ✅ COMPLIANT |
| No mutación fuera de alcance | protección comprobada | pruebas de hashes/repositorio más hashes runtime de duplicados, reconciliación, crudos, fuente y `README.pdf` | ✅ COMPLIANT |
| No mutación fuera de alcance | intento prohibido | `test_preflight_rechaza_cwd_ajeno_y_objetivos_no_permitidos` y casos staged/unstaged protegidos | ✅ COMPLIANT |

**Resumen de cumplimiento**: **19/19 escenarios conformes**.

### Cierre posterior a corrección de `R3-001`

`_load_catalog_codes` valida el esquema exacto de cuatro columnas, registros no vacíos, códigos y nombres no blancos, consistencia bidireccional de departamentos y unicidad de municipios/códigos. `enrich_result` verifica además que el catálogo cubra cada pareja normalizada de la fuente antes de construir o publicar resultados. La regresión parametrizada ejecutó seis rechazos y comprobó que la fuente y las tres salidas preexistentes conservaran exactamente sus bytes; el séptimo caso confirmó que el catálogo válido sigue funcionando.

### Correctitud estática y observable

| Contrato | Estado | Evidencia |
|---|---|---|
| S1: mayúsculas y `dir_fd` | ✅ Implementado | Valores, bitácora, rama segura y fallback portátil pasan en runtime. |
| Pin/hash/procedencia | ✅ Implementado | Revisión `05b3fce5d7ad57ee09d429b58ee9be17dd117d7a`, payload `e94f8914…`; el espejo se distingue de INE/Censo 2018. |
| Catálogo | ✅ Implementado | 340 filas, 22 departamentos, 340 códigos municipales únicos; reemplazo atómico tras validar. |
| Territorio | ✅ Implementado | 2 typos/19 filas separados de 7 mapeos provisionales/145 filas que conservan `revisar`. |
| Reporte territorial | ✅ Implementado | Rutas POSIX relativas, bytes estables y publicación/restauración conjunta CSV+Markdown. |
| Dataset y métricas | ✅ Implementado | 11,867 filas; 20→21 columnas; seis artefactos regenerados con hashes esperados. |
| Documentación | ✅ Implementado | Plan, README, AGENTS y Code Book territorial coinciden sin declarar cierre total. |

### Hashes finales e idempotencia

Las ejecuciones previa, primera y segunda produjeron exactamente los mismos hashes:

| Artefacto autorizado | SHA-256 |
|---|---|
| `data/reference/catalogo_territorial.csv` | `64b86ba51f813d0ce6806a3a948af34e5d5a5ad8425ed62f0e0e1d72a53387f2` |
| `data/processed/establecimientos_diversificado_limpio.csv` | `32414cc3bf68744923ef8d51758e0c863713d6fd3a39b449f37ac04923fb6a8c` |
| `outputs/tablas/bitacora_limpieza.csv` | `2f803138594fa619aff34392b1efa25d9e7a723668da0e76381dfd9b82add4d2` |
| `outputs/tablas/reporte_calidad_antes_despues.csv` | `d915a0c77a3dd4d4f85e9cdb1555c2de732080aaefb102f37d57b6d0fc99c09c` |
| `outputs/tablas/inconsistencias_territoriales.csv` | `961565cc3bbf6ea18cd9b012525ce47acada935e88ed37fb4ceb5e50854b48fd` |
| `outputs/reportes/validacion_territorial.md` | `3620b867483bb442d0d2ea28d083325a1ecc4c2985a0c722658fb1363a5b0724` |

### Protección de Anggie, fuentes y PDF

| Artefacto protegido | Evidencia final | Estado |
|---|---|---|
| `data/raw/manifest.json` | `8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07` | ✅ idéntico |
| fuente canónica | `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f` | ✅ idéntica |
| `duplicados_parciales.csv` | `4b1c6d6aa7d720872b88e3a5ddcd5402657dede539518fe9a330f541593954c6` | ✅ idéntico, sin diff |
| `duplicados_parciales.md` | `c9feec7bc2b09fc449439f87781a920539dae668d79c95eca060f2ce3ea93398` | ✅ idéntico, sin diff |
| `docs/reconciliacion_anggie.md` | `5c8384936a9c2f58eecf423d284d4aa11015cec85816cf470d5503f804c35fbf` | ✅ sin diff |
| `README.pdf` | `42e3227ede19d0c7f12da930db0bff01ef0adbcbc4e69efe9150ac06fefba2e1` | ✅ intacto; continúa no rastreado |

No existe artefacto telefónico ni sección Code Book de Anggie modificada por este cambio. `docs/planificacion.md` y `README.md` mantienen **pendiente/no implementado**: decisiones de 1,355 candidatos a duplicado parcial, excepciones telefónicas y sección propia del Code Book de Anggie. La reconciliación conserva sus bytes y el pipeline de verificación no ejecutó `detectar_duplicados.py`.

### Veracidad del plan y cierre acotado de Iris

`docs/planificacion.md` marca como hechos únicamente catálogo, consistencia departamento–municipio, normalización, códigos derivados y Code Book territorial de cuatro variables de Iris. Mantiene parciales R5a, R5b, R5e, R5f, R5g, R6, R8, R9 y RT; mantiene faltantes R7, R10 y RE; declara pendiente la integración final de Jonathan y bloquea la entrega mientras R7, R10, RE o RT no estén completos. Por tanto, **no declara terminado el proyecto**.

### Presupuesto y unidades de trabajo

| Slice | Líneas preservadas en evidencia | Límite | Estado |
|---|---:|---:|---|
| S1 | 160 | 400 | ✅ |
| S2 | 278 | 400 | ✅ |
| S3a | 73 | 400 | ✅ |
| S3b | 133 | 400 | ✅ |

La estrategia `auto-chain`, `stacked-to-main` divide el cambio completo en unidades de comportamiento con pruebas/documentación y rollback propios. Ningún slice requiere `size:exception`. La medición histórica está preservada en `apply-progress.md`, `verify-s1.md` y `verify-s2.md`; el árbol actual acumula los slices porque, por instrucción, no se crearon commits ni PR.

### TDD Compliance

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia TDD reportada | ✅ | `apply-progress.md` registra RED, GREEN, triangulación, red de seguridad y refactor para 7/7 tareas. |
| Todas las tareas tienen prueba/harness | ✅ | 7/7. |
| RED respaldado por archivos existentes | ✅ | 4 archivos de prueba y harness temporal presentes/documentados. |
| GREEN confirmado | ✅ | 128/128 pruebas pasan; pipeline real pasa dos veces después de la corrección. |
| Triangulación adecuada | ✅ | éxito/fallos, ramas segura/portátil, checksum/esquema/conteo, dos raíces, rollback y documentación. |
| Red de seguridad | ✅ | bases de 101/109/113/120 pruebas preservadas en el progreso. |

**Cumplimiento TDD**: 6/6 comprobaciones conformes.

### Distribución de capas del cambio

| Capa | Pruebas recolectadas | Archivos | Herramienta |
|---|---:|---:|---|
| Unidad/core | 34 | 2 | pytest |
| Integración CLI/repositorio/runtime | 29 | 3 | pytest |
| E2E | 0 | 0 | no configurada |
| **Total relacionado** | **63** | **4** | |

La suite completa contiene 128 pruebas. Los conteos anteriores clasifican los 63 casos recolectados en los cuatro archivos creados o modificados por este cambio; `test_territorial_contract.py` contiene casos de ambas capas.

### Changed File Coverage

Análisis de cobertura omitido: no hay herramienta ni comando de cobertura configurado.

### Assertion Quality

**Calidad de aserciones**: ✅ las pruebas relacionadas ejercitan código o artefactos reales y comprueban valores, bytes, cardinalidades, errores y rollback. No se encontraron tautologías, bucles fantasma, aserciones huérfanas ni pruebas de humo sin comportamiento.

### Quality Metrics

**Linter**: ➖ No disponible  
**Type checker**: ➖ No disponible  
**Higiene Git**: ✅ `git diff --check` sin errores

### Coherencia con el diseño

| Decisión | Seguida | Evidencia |
|---|---|---|
| Catálogo offline reproducible con pin/hash | ✅ | descarga fijada, validación previa y catálogo byte-idéntico |
| Separar 2 typos de 7 provisionales | ✅ | código, bitácora, CSV y pruebas coinciden |
| Rutas relativas y par territorial transaccional | ✅ | prueba entre raíces y rollback del segundo reemplazo |
| Orden catálogo → limpieza → validación | ✅ | ejecutado dos veces en ese orden |
| No ejecutar duplicados ni decidir teléfonos | ✅ | artefactos sin diff/hash idéntico y pendientes documentados |
| Slices revisables y reversibles | ✅ | S1/S2/S3a/S3b bajo 400, con rollback delimitado |

### Hallazgos

**CRITICAL**: ninguno.  
**WARNING**: ninguno.  
**SUGGESTION**: `README.pdf` permanece deliberadamente no rastreado; conservarlo fuera de cualquier staging accidental mientras siga siendo un artefacto protegido externo al cambio.

### Contexto del recibo de revisión

El recibo nativo `review-cd2692dfd5ad50ea` está en estado terminal `approved`: árbol final `db114b6052a515fb05f258b86868a5a42ff19dee`, revisión `sha256:980dee68457d568571c810347f752e59f361940a1f73e363cd854362f5bcfb1b`, `fix_delta_hash` `sha256:d26d05344c031b23817ed3f4cb590ae3bd025063a43962c317d3f3a743e41cbb` y hallazgo resuelto `R3-001`. `R2-001` sobre `README.pdf` permanece como seguimiento informativo preexistente y fuera del alcance, no como bloqueo.

### Veredicto

**PASS** — 7/7 tareas, 9/9 requisitos y 19/19 escenarios conformes; `R3-001` resuelto con 7/7 pruebas focalizadas; 128/128 pruebas verdes; regeneración byte-idéntica e idempotente; alcance de Iris completo; tareas de duplicados/teléfonos/reconciliación/Code Book de Anggie pendientes y sin cambios; fuentes y `README.pdf` intactos.

### Siguiente paso

Archivar el cambio SDD. No mezclar este cierre territorial con los entregables todavía pendientes de Anggie ni con la integración final de Jonathan.
