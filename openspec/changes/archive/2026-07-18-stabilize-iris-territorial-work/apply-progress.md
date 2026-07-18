# Progreso de implementación: estabilizar trabajo territorial de Iris

## Estado acumulado

- Modo: TDD estricto
- Estrategia: `auto-chain`, `stacked-to-main`
- Slice actual: S3a/S3b — regeneración autorizada y verdad documental
- Estado de fase S1: `success` tras correctivo del gatekeeper
- Estado de fase S2: `success`
- Estado de fase S3: `success`
- Base del slice: `bdf87360b4fa7081dac347f373d6a739dc262c2e`
- Completadas: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3
- Pendientes: ninguna dentro de este cambio; permanecen los entregables externos de Anggie y la integración final de Jonathan

## Cambios S1

- Se alinearon las expectativas con la regla observable de mayúsculas para `ESTABLECIMIENTO` y `DIRECTOR`; una prueba explícita verifica valores y bitácora.
- La capacidad segura `dir_fd` se captura antes de sustituciones de `os.open`, por lo que las pruebas de carrera ejercitan la rama segura en plataformas compatibles; la rama portátil tiene prueba propia.
- Los casos CLI que deben llegar a escritura reciben un catálogo territorial mínimo válido; una regresión observable prueba que una fuente válida sin catálogo falla identificándolo y sin escribir parciales.
- Los hashes del limpio, bitácora y reporte se actualizaron solo después de reproducir sus bytes actuales en un directorio temporal con el código y catálogo rastreados. No se regeneró ni editó ninguna salida real.

## Evidencia del ciclo TDD

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | Triangulación | Refactor |
|---|---|---|---|---|---|---|---|
| 1.1 | `tests/test_cleaning.py` | Unidad | Base: 101 pasan, 8 fallan | 3 fallos focalizados probaron detección y carreras `dir_fd` | 47/47 focalizadas | Rama segura sustituida + rama portátil sin capacidad; mayúsculas y bitácora | Constante de capacidad separada de la función sustituible |
| 1.2 | `tests/test_cleaning_cli.py`, `tests/test_repository_cleanup.py` | CLI/repositorio | Base: 3 fallos CLI y 1 hash obsoleto | Gatekeeper RED: faltaba distinguir fuente válida con catálogo ausente | 11/11 CLI; 8/8 repositorio | Éxito default, salida personalizada, fallo inyectado, entrada ausente y catálogo ausente | Fixture mínimo compartido; implementación sin cambios en el correctivo |
| 2.1 | `tests/test_territorial_contract.py` | Unidad/CLI | Base: 113 pasan | 7 fallos: API, pin/procedencia, fallos no destructivos, provisionales y 7/145 | 7/7 territoriales | Éxito 22/340 y fallos de checksum/esquema/conteo; 2 typos y 7 aliases provisionales | Generación validada extraída de `main`; mensaje de evidencia honesto |
| 2.2 | `tests/test_territorial_contract.py` | Unidad/runtime | Base territorial RED compartida | Rutas absolutas y publicación separada fallaron el contrato nuevo | 7/7 territoriales; 15/15 con repositorio | Dos raíces equivalentes y rollback al fallar el segundo reemplazo | Rutas lógicas y publicación conjunta encapsuladas |
| 3.1 | Harness temporal y comparación Git | Runtime/repositorio | 120/120 pruebas antes de mutar | Salidas rastreadas tenían rutas absolutas y bitácora anterior; `GEN_LINES=4` | Segunda reproducción confirmó conjunto atómico revisable | Catálogo/limpio/calidad/inconsistencias idénticos; bitácora y reporte territorial cambiaban de forma explicable | Worktrees aislados eliminan riesgo sobre el árbol real |
| 3.2 | `tests/test_repository_cleanup.py`, `tests/test_territorial_contract.py` | Repositorio/runtime | 120/120 antes de S3 | 2 fallos probaron hash/20→19 obsoletos; 1 fallo probó lenguaje de procedencia ausente | 16/16 focalizadas; 122/122 completas | 11,867×21, 20→21, 7/145 `revisar`, rutas relativas y hashes exactos | Métrica de columnas se actualiza al enriquecer; reporte distingue espejo y fuente primaria |
| 3.3 | `tests/test_repository_cleanup.py` | Documental | 9/9 pruebas de repositorio tras regeneración | 1 fallo probó ausencia de procedencia, 21 variables, 7/145 y estados del equipo | 1/1 documental; 10/10 repositorio | Plan, README, AGENTS y Code Book coinciden; Anggie/Jonathan siguen pendientes | Documentos condensados alrededor de evidencia y responsabilidades |

## Evidencia de unidad de trabajo

| Evidencia | Resultado |
|---|---|
| Prueba focalizada | `uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py tests/test_repository_cleanup.py` → exit 0, 48 passed |
| Regresión correctiva | `uv run pytest tests/test_cleaning_cli.py::test_cli_reporta_catalogo_ausente_con_fuente_valida_sin_escribir_parciales` → exit 0, 1 passed; implementación existente ya satisfacía el contrato |
| Harness de runtime | `uv run pytest tests/test_cleaning_cli.py::test_cli_limpia_fuente_default_y_escribe_salidas_permitidas` → exit 0, 1 passed; ejecuta CLI con catálogo temporal y tres escrituras |
| Suite completa | `uv run pytest` → exit 0, 113 passed |
| Higiene del diff | `git diff --check` → exit 0, sin errores |
| Presupuesto S1 | 160 líneas cambiadas: 110 código/pruebas + 4 marcas de tareas + 46 de apply-progress; menor que 400 |
| Reproducibilidad de hashes | Harness temporal de `clean_dataset` → `enrich_result` → `write_cleaning_outputs`: limpio `32414c…`, bitácora `fcc202…`, reporte `33a2f9…`; los tres `equal=True` contra archivos rastreados |
| Rollback | Revertir `src/proyecto1_ds/cleaning.py`, `tests/test_cleaning.py`, `tests/test_cleaning_cli.py`, `tests/test_repository_cleanup.py` y las marcas/progreso S1; no afecta S2/S3 ni generados |

## Cambios y evidencia S2

- El espejo comunitario quedó fijado al commit `05b3fce5d7ad57ee09d429b58ee9be17dd117d7a`, URL `raw` inmutable y SHA-256 `e94f891411281b1c77f12a1c46fa424d62d033d7b7021318585065b3e5c57455`; el código aclara que es espejo/conversión y que el INE/Censo 2018 es la fuente primaria declarada, no evidencia primaria descargada directamente.
- Antes del reemplazo se validan checksum, JSON/esquema, valores no vacíos, códigos únicos, 22 departamentos y 340 municipios. Las pruebas de checksum, esquema y conteo prueban que los bytes previos permanecen intactos.
- Dos typos producen evidencia separada; siete aliases conservan texto MINEDUC, reciben códigos provisionales trazables y siguen como 7 parejas/145 filas con `decision=revisar`.
- El informe usa rutas POSIX lógicas relativas y bytes idénticos entre raíces. CSV y Markdown se preparan y publican como par con restauración ante fallo.

| Evidencia S2 | Resultado |
|---|---|
| Prueba focalizada | `uv run pytest tests/test_territorial_contract.py tests/test_repository_cleanup.py` → exit 0, 15 passed |
| Harness runtime | Descarga fijada → catálogo temporal → limpieza/enriquecimiento → validación temporal → exit 0; 11,867×21 y 7/145 `revisar` |
| Suite y diff | `uv run pytest` → exit 0, 120 passed; `git diff --check` → exit 0 |
| Presupuesto | S2 código/pruebas: 278 líneas; diff ejecutable acumulado S1+S2: 388 líneas, ≤400 |
| Procedencia reproducida | Payload `e94f8914…`; catálogo temporal `64b86ba…`, byte a byte igual al catálogo rastreado |
| Rollback S2 | Revertir `scripts/generar_catalogo_territorial.py`, `scripts/validar_territorio.py`, `src/proyecto1_ds/{enrichment,territorial}.py`, `tests/test_territorial_contract.py` y marcas/progreso S2; S1 y salidas reales permanecen |

## Protecciones verificadas

P conserva exactamente manifest `8b72e9…`, fuente `c83ac1…`, duplicados CSV `4b1c6d…`, informe de duplicados `c9feec…` y `README.pdf` `42e322…`. No cambiaron `data/raw/**`, `data/source/**`, datos/salidas generados, decisiones telefónicas o reconciliación.

## Desviaciones e incidencias

Ninguna desviación de comportamiento. La corrección de hashes obsoletos se adelantó dentro de S1 por instrucción explícita y únicamente después de prueba reproducible de solo lectura; las salidas permanecieron intactas hasta el gate autorizado de S3. S2 y S3 quedaron implementados.

## Preflight y medición S3 antes de mutar salidas reales

- Suite inicial: `uv run pytest` → 120 passed.
- Worktree aislado: `/tmp/opencode/iris-s3-preflight.0pGzSv/repro`, construido desde `HEAD` más el diff de código S1/S2.
- Orden ejecutado: catálogo → limpieza → validación. Comparación previa contra el árbol real: catálogo, limpio, reporte de calidad e inconsistencias byte-idénticos; bitácora y reporte territorial diferían.
- `git diff --numstat` generado inicial: bitácora `1+1`, reporte territorial `1+1`; `GEN_LINES=4`, por debajo de 400. El catálogo fue byte-idéntico (`64b86b…`).
- Tras corregir el reporte 20→21 y el lenguaje de procedencia, el conjunto final medido fue bitácora `1+1`, calidad `1+1`, reporte territorial `1+1`: 6 líneas. Dos ejecuciones equivalentes conservaron los mismos hashes.

## Slices S3 reales

| Slice | Límite y contenido | Líneas S3 | Rollback |
|---|---|---:|---|
| S3a | Pruebas/ajuste mínimo + regenerados autorizados y hashes | 73 | Revertir `enrichment.py`, redacción de `territorial.py`, pruebas S3 y tres salidas cambiadas; regenerar con el código previo |
| S3b | Seis documentos + marcas/progreso SDD | 133 | Revertir solo documentos y metadatos SDD; no toca datos ni lógica |

El cálculo S3a compara la instantánea S2 previa: producción 10, pruebas 57 y generados 6. S3b suma el numstat documental (82) y 51 líneas de tareas/progreso. Ambos slices son autónomos y ≤400; no se requiere `size:exception`.

## Evidencia de unidad de trabajo S3

| Evidencia | Resultado |
|---|---|
| Prueba focalizada S3a | `uv run pytest tests/test_territorial_contract.py tests/test_repository_cleanup.py` → exit 0, 16 passed |
| Harness runtime S3a | `uv run python scripts/generar_catalogo_territorial.py && uv run python scripts/limpiar_dataset.py && uv run python scripts/validar_territorio.py` → exit 0; 11,867×21, 20→21, 7 parejas/145 filas `revisar` |
| Prueba focalizada S3b | prueba documental específica → exit 0, 1 passed; archivo de repositorio completo → 10 passed dentro de suite |
| Suite completa | `uv run pytest` → exit 0, 122 passed |
| Idempotencia | Segunda ejecución real produjo catálogo `64b86b…`, limpio `32414c…`, bitácora `2f8031…`, calidad `d915a0…`, inconsistencias `961565…`, reporte territorial `3620b8…` |
| Rutas relativas | Reporte territorial contiene solo rutas POSIX del repositorio; prueba entre dos raíces pasa |
| Protecciones | Manifest `8b72e9…`, fuente `c83ac1…`, duplicados CSV `4b1c6d…`, informe `c9feec…`, `README.pdf` `42e322…` |
| Higiene | `git diff --check` → exit 0 |
| Rollback | S3a y S3b se revierten independientemente y en orden inverso; ningún rollback requiere tocar artefactos de Anggie |

## Estado final de alcance

S3 corrige la verdad 20→21, documenta 7 parejas/145 filas `revisar`, 2 variantes/19 filas, procedencia del espejo y cuatro variables territoriales completas de Iris. Anggie permanece `pendiente/no implementado` para decisiones de duplicados, teléfonos y su Code Book. La integración final de Jonathan permanece pendiente; el proyecto no se declara cerrado.
