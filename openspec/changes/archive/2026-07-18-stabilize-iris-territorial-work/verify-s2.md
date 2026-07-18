# Informe de verificación S2

## Verification Report

**Cambio**: `stabilize-iris-territorial-work`

**Alcance**: únicamente S2 — tareas 2.1 y 2.2

**Persistencia**: híbrida

**Modo**: TDD estricto

**Veredicto**: **PASS**

S3 permanece pendiente y fuera de este gate. Este informe no declara completado el cambio completo.

### Completitud

| Métrica | Valor |
|---|---:|
| Tareas S2 totales | 2 |
| Tareas S2 completas | 2 |
| Tareas S2 incompletas | 0 |
| Requisitos S2 verificados | 4 |
| Escenarios S2 verificados | 8 |

### Ejecución: pruebas, build e higiene

| Evidencia | Comando | Exit | Resultado | SHA-256 de salida exacta |
|---|---|---:|---|---|
| Pruebas focalizadas | `uv run pytest tests/test_territorial_contract.py tests/test_repository_cleanup.py` | 0 | 15 passed | `2666c9ebde7c72e2e921469947e5e162fc1dec6922826f788e363c606591877b` |
| Suite completa | `uv run pytest` | 0 | 120 passed | `02eb1a0937c0d3c86b68e8456b281ea636785c0038d62dd99c784f3278ebfb0a` |
| Build/higiene disponible | `git diff --check` | 0 | Sin salida ni errores | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Reproducción del catálogo y dataset | harness Python temporal de descarga fijada, generación y validación | 0 | Catálogo idéntico; `11867×21`; `7/145 revisar` | `1935ff15dea4ebaaea06c2bd1261d9b7a0edb75ed84c0555d554956f5c0d21a5` |
| Presupuesto | medición `git diff --numstat` más prueba S2 nueva | 0 | S2=278; acumulado ejecutable S1+S2=388; ambos ≤400 | `270480ae57132010db4385b86d973afd8807408476c4d0cacab5c142d0548977` |

No existe comando de build adicional, cobertura, linter ni verificador de tipos configurado en `openspec/config.yaml`; esas dimensiones se omiten sin afectar el gate.

### Matriz de cumplimiento de especificaciones

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Procedencia inmutable | Procedencia válida | `test_generador_usa_espejo_inmutable_y_publica_catalogo_validado`; harness remoto fijado | ✅ COMPLIANT |
| Procedencia inmutable | Integridad inválida | parametrización `checksum` de `test_generador_preserva_catalogo_previo_ante_entrada_invalida` | ✅ COMPLIANT |
| Reemplazo validado | Catálogo completo | prueba del generador + reproducción real de esquema, unicidad, 22/340 y bytes | ✅ COMPLIANT |
| Reemplazo validado | Contenido inválido | parametrizaciones `schema` y `count`; bytes previos preservados | ✅ COMPLIANT |
| Pendientes y códigos | Pareja conocida | `test_enriquecimiento_separa_dos_typos_de_siete_codigos_provisionales` y `test_reporte_conserva_siete_parejas_y_145_filas_pendientes` | ✅ COMPLIANT |
| Pendientes y códigos | Similitud insuficiente | reporte territorial mantiene inconsistencias en `revisar` sin autocorrección | ✅ COMPLIANT |
| Informe determinístico | Raíces distintas | `test_reporte_es_byte_estable_entre_raices_y_publicacion_es_conjunta` | ✅ COMPLIANT |
| Informe determinístico | Ruta absoluta | la misma prueba verifica ausencia del prefijo temporal absoluto | ✅ COMPLIANT |

**Resumen de cumplimiento**: 8/8 escenarios S2 conformes.

### Correctitud estática y runtime

| Contrato | Estado | Evidencia |
|---|---|---|
| Pin y URL inmutables | ✅ | Revisión `05b3fce5d7ad57ee09d429b58ee9be17dd117d7a`; URL `raw` contiene la revisión y no usa `/main/`. |
| Cadena de procedencia | ✅ | El código distingue espejo/conversión comunitaria de la fuente primaria declarada INE, Censo 2018. |
| Hash del payload | ✅ | `e94f891411281b1c77f12a1c46fa424d62d033d7b7021318585065b3e5c57455`, verificado contra descarga actual fijada. |
| Catálogo reproducido | ✅ | SHA-256 `64b86ba51f813d0ce6806a3a948af34e5d5a5ad8425ed62f0e0e1d72a53387f2`, idéntico byte a byte al catálogo rastreado. |
| Esquema, códigos y cardinalidad | ✅ | Columnas exactas; códigos no vacíos; códigos municipales únicos; 22 departamentos y 340 municipios. |
| Fallo atómico del catálogo | ✅ | Checksum, esquema y conteo inválidos fallan antes del reemplazo y conservan bytes previos. |
| Typos frente a provisionales | ✅ | Dos correcciones de nombre separadas de siete aliases con código provisional. |
| Pendientes reales | ✅ | Dataset `11867×21`; siete parejas y 145 filas conservan `decision=revisar`. |
| Reporte relativo y determinístico | ✅ | Rutas POSIX lógicas, sin prefijos del equipo y bytes iguales entre raíces equivalentes. |
| Publicación y rollback pareados | ✅ | CSV y Markdown se preparan juntos; un fallo en el segundo reemplazo restaura ambos bytes previos. |

### Coherencia con el diseño

| Decisión | Estado | Nota |
|---|---|---|
| Catálogo offline reproducible con espejo fijado y hash | ✅ | Implementado sin presentar el espejo como descarga primaria del INE. |
| Separar dos typos aprobados de siete mapeos provisionales | ✅ | Los nombres MINEDUC de los siete casos no se corrigen automáticamente. |
| Informe relativo y par territorial transaccional | ✅ | Implementación y prueba de rollback coinciden con el diseño. |
| Slice autónomo y reversible | ✅ | Rollback S2 está delimitado a generador, validador CLI, enriquecimiento, territorio y prueba contractual; S1 queda intacto. |

### Cumplimiento TDD

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia TDD reportada | ✅ | Presente para 2.1 y 2.2 en `apply-progress.md`. |
| Todas las tareas tienen pruebas | ✅ | 2/2 usan `tests/test_territorial_contract.py`; protección de repositorio se ejecuta conjuntamente. |
| RED respaldado | ✅ | El artefacto registra siete fallos iniciales y fallos de rutas/publicación; los archivos de prueba existen. |
| GREEN confirmado | ✅ | 7/7 territoriales, 15/15 focalizadas y 120/120 completas pasan ahora. |
| Triangulación adecuada | ✅ | Éxito y fallos de checksum/esquema/conteo; dos raíces; fallo del segundo reemplazo. |
| Red de seguridad | ✅ | Base de 113 pruebas reportada; suite actual completa verde. |

### Distribución de capas

| Capa | Pruebas recolectadas | Archivos |
|---|---:|---:|
| Unidad/CLI | 5 | 1 |
| Integración de archivos/repositorio | 10 | 2 |
| E2E | 0 | 0 |
| **Total focalizado** | **15** | **2** |

### Calidad de aserciones

✅ Las aserciones focalizadas ejercitan código de producción y comprueban valores, bytes, excepciones, cardinalidades, decisiones y rollback. No se encontraron tautologías, bucles fantasma ni pruebas de humo sin comportamiento.

### Aislamiento y protecciones

`git diff` confirma que no se modificaron rutas reales bajo `data/raw/`, `data/source/`, `data/reference/`, `data/processed/`, `outputs/`, `docs/`, `README.md` ni `AGENTS.md`. `README.pdf` continúa sin mutación con SHA-256 `42e3227ede19d0c7f12da930db0bff01ef0adbcbc4e69efe9150ac06fefba2e1`.

Protecciones adicionales verificadas:

- manifest: `8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07`;
- fuente canónica: `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`;
- duplicados parciales CSV: `4b1c6d6aa7d720872b88e3a5ddcd5402657dede539518fe9a330f541593954c6`;
- informe de duplicados: `c9feec7bc2b09fc449439f87781a920539dae668d79c95eca060f2ce3ea93398`;
- reconciliación de Anggie sin diff; no se ejecutó ni alteró lógica de duplicados, teléfonos o reconciliación;
- no hay mutaciones de implementación o entregables S3.

### Presupuesto y rollback

- S2 código/pruebas: **278 líneas**.
- Diff ejecutable acumulado S1+S2: **388 líneas**.
- Límite: **400 líneas**.
- Gate: **PASS**.
- Rollback pareado: revertir `scripts/generar_catalogo_territorial.py`, `scripts/validar_territorio.py`, `src/proyecto1_ds/enrichment.py`, `src/proyecto1_ds/territorial.py` y `tests/test_territorial_contract.py`; no requiere tocar S1, datos ni salidas reales.

### Hallazgos

**CRITICAL**: Ninguno.

**WARNING**: Ninguno.

**SUGGESTION**: Ninguna dentro del alcance S2.

### Veredicto

**PASS** — las tareas S2 2.1 y 2.2 cumplen sus ocho escenarios con evidencia runtime, suite completa verde, aislamiento comprobado, rollback pareado y presupuesto inferior a 400 líneas.

### Sobre estricto de evidencia

```yaml
test_command: uv run pytest
test_exit_code: 0
test_output_hash: sha256:02eb1a0937c0d3c86b68e8456b281ea636785c0038d62dd99c784f3278ebfb0a
build_command: git diff --check
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
