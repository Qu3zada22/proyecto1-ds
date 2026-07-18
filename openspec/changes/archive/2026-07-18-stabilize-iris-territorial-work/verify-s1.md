# Informe de verificación: S1 — regresiones

**Cambio**: `stabilize-iris-territorial-work`
**Alcance**: únicamente tareas 1.1–1.2
**Persistencia**: híbrida
**Modo**: TDD estricto
**Base del slice**: `bdf87360b4fa7081dac347f373d6a739dc262c2e`

## Completitud

| Métrica | Valor |
|---|---:|
| Tareas S1 totales | 2 |
| Tareas S1 completas | 2 |
| Tareas S1 incompletas | 0 |

Las tareas S2 y S3 permanecen pendientes y se excluyeron deliberadamente de esta verificación focalizada.

## Ejecución

| Evidencia | Comando | Resultado |
|---|---|---|
| Pruebas focalizadas | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py tests/test_repository_cleanup.py -p no:cacheprovider` | exit 0; 48 passed |
| Suite completa | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider` | exit 0; 113 passed |
| Higiene | `git diff --check` | exit 0; salida vacía |
| Reproducción temporal | `clean_dataset → enrich_result → write_cleaning_outputs` en `/tmp/opencode` | exit 0; tres artefactos idénticos |
| Presupuesto | `git diff --numstat` desde la base para archivos S1 | 110 líneas rastreadas; 160 con marcas/progreso; ≤400 |

```yaml
test_command: PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider
test_exit_code: 0
test_output_hash: sha256:305f553dba5053f0201f2d59f3f2c0a49c29d222e6bc589ac2b4fe23332d5373
focused_test_command: PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py tests/test_repository_cleanup.py -p no:cacheprovider
focused_test_exit_code: 0
focused_test_output_hash: sha256:44bd052df633fb274c88be57fab1a9ccd88884c74cea5a2c6934d206ab014a39
build_command: git diff --check
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
reproduction_exit_code: 0
reproduction_output_hash: sha256:c64e1fbf2dbbea864bbc383d2b91d14738522559110b90b1ecf2ced356620992
```

No existe un comando de build, cobertura, linter o type checker configurado en `pyproject.toml`; `git diff --check` se registró como gate de construcción/higiene disponible.

## Cumplimiento de especificación S1

| Requisito | Escenario | Evidencia ejecutada | Resultado |
|---|---|---|---|
| Regresión y escritor seguro | rama segura | `test_capacidad_dir_fd_permanece_detectable_al_sustituir_os_open` y pruebas de carrera con `os.open` sustituido | ✅ COMPLIANT |
| Regresión y escritor seguro | plataforma portátil | `test_write_cleaning_outputs_usa_rama_portatil_sin_capacidad_dir_fd` | ✅ COMPLIANT |
| Catálogo requerido por CLI | fixture válido | pruebas de éxito, salida personalizada y fallo de escritura con `_write_valid_catalog` | ✅ COMPLIANT |
| Catálogo requerido por CLI | catálogo ausente | `test_cli_reporta_catalogo_ausente_con_fuente_valida_sin_escribir_parciales` | ✅ COMPLIANT |

**Resumen de escenarios**: 4/4 escenarios S1 conformes.

## Corrección estática y observable

| Comportamiento | Estado | Evidencia |
|---|---|---|
| `ESTABLECIMIENTO` y `DIRECTOR` en mayúsculas | ✅ | Valores Unicode y bitácora `normalizar_mayusculas` comprobados en runtime. |
| Capacidad `dir_fd` estable bajo monkeypatch | ✅ | `_OS_OPEN_SUPPORTS_DIR_FD` se captura antes de sustituir `os.open`; las carreras confirman ejecución segura. |
| Fallback portátil | ✅ | Fuerza capacidad ausente, prohíbe invocar el escritor seguro y comprueba las tres salidas temporales. |
| CLI con catálogo | ✅ | Los casos que llegan a enriquecimiento crean un catálogo mínimo válido. |
| Catálogo ausente sin parciales | ✅ | Exit 1, error explícito, fuente intacta y cero directorios de salida. |
| Hashes actualizados | ✅ | Reproducción fuera del repositorio generó bytes idénticos para limpio, bitácora y reporte. |

## Coherencia con el diseño

| Decisión S1 | Seguida | Nota |
|---|---|---|
| Slice autónomo de regresiones | ✅ | Solo cambian `cleaning.py` y tres archivos de pruebas, además de artefactos SDD. |
| Pruebas junto con el comportamiento | ✅ | Las tareas 1.1–1.2 incluyen sus regresiones en la misma unidad. |
| Rollback independiente | ✅ | Revertir los cuatro archivos S1 y sus marcas/progreso no elimina trabajo S2/S3. |
| Presupuesto de revisión | ✅ | 110 líneas de código/pruebas; 160 con tareas/progreso, menor que 400. |

## Cumplimiento TDD

| Comprobación | Resultado | Detalle |
|---|---|---|
| Evidencia RED/GREEN reportada | ✅ | `apply-progress.md` registra ambas tareas y el correctivo de catálogo ausente. |
| Archivos de prueba existentes | ✅ | 2/2 tareas tienen pruebas presentes. |
| GREEN confirmado | ✅ | 48/48 focalizadas y 113/113 totales pasan. |
| Triangulación | ✅ | Rama segura/portátil y CLI éxito/fallo/ausencia cubren variantes distintas. |
| Red de seguridad | ✅ | Se documenta la base de 101 aprobadas y 8 fallidas. |
| Calidad de aserciones | ✅ | No se observaron tautologías, ghost loops ni aserciones sin ejecutar producción. |

### Distribución de capas

| Capa | Pruebas | Archivos |
|---|---:|---:|
| Unidad/core | 29 | 1 |
| Integración CLI/repositorio | 19 | 2 |
| E2E | 0 | 0 |
| **Total focalizado** | **48** | **3** |

Cobertura y métricas de calidad omitidas: no hay herramientas configuradas. Esto no bloquea el gate.

## Protecciones e aislamiento

- Hashes protegidos confirmados: manifest `8b72e9…`, fuente `c83ac1…`, duplicados CSV `4b1c6d…`, informe de duplicados `c9feec…` y `README.pdf` `42e322…`.
- Reproducción de solo lectura: limpio `32414c…`, bitácora `fcc202…` y reporte `33a2f9…`, todos `equal=True`; no se modificaron las salidas rastreadas.
- `git diff` contra la base no muestra cambios en implementación S2/S3, artefactos de Anggie, `README.md`, `AGENTS.md`, datos ni `outputs/`.
- `README.pdf` continúa no rastreado y conserva exactamente su hash protegido.

## Hallazgos

**CRITICAL**: ninguno.
**WARNING**: ninguno.
**SUGGESTION**: ninguna.

## Veredicto

**PASS** — las tareas S1 1.1–1.2 cumplen sus cuatro escenarios, pasan pruebas focalizadas y completas, reproducen los hashes sin tocar salidas y respetan aislamiento y presupuesto.
