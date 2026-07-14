# Apply Progress: Plan de limpieza cruda

## Estado general

- Cambio: `raw-cleaning-plan`
- Modo: Strict TDD activo para cambios de código; **no aplicable** a este lote porque solo se crean/modifican documentos.
- Unidad de trabajo: cambio documental staged de 501 inserciones en PR único, mantenido como paquete atómico y revisado con lentes acotados.
- Alcance staged aplicado: `docs/plan_limpieza.md`, `openspec/changes/raw-cleaning-plan/proposal.md`, `openspec/changes/raw-cleaning-plan/exploration.md`, `openspec/changes/raw-cleaning-plan/design.md`, `openspec/changes/raw-cleaning-plan/specs/plan-limpieza-cruda/spec.md`, `openspec/changes/raw-cleaning-plan/tasks.md` y `openspec/changes/raw-cleaning-plan/apply-progress.md`.
- Alcance excluido respetado: no se modificaron `data/raw/`, `data/interim/`, `outputs/`, scripts/código fuente ni `docs/diagnostico.md`.

## Tareas completadas

- [x] 1.1 Leer `docs/instrucciones.md`, `docs/diagnostico.md` y `outputs/tablas/{resumen_dataset,diagnostico_columnas,problemas_potenciales,dominios_observados,duplicados_exactos}.csv` como fuentes de evidencia.
- [x] 1.2 Mapear cada fila de `outputs/tablas/problemas_potenciales.csv` a una entrada esperada del plan o a una agrupación con justificación explícita.
- [x] 2.1 Crear `docs/plan_limpieza.md` con resumen ejecutivo que declare Paso 3, planificación previa y no limpieza ejecutada.
- [x] 2.2 Añadir fuentes de evidencia, criterios `accionable`/`diferida`/`manual`/`conservar` y reglas globales propuestas para nulos, texto, tipos, trazabilidad y duplicados.
- [x] 2.3 Completar la tabla central con encabezados `Variable`, `Problema`, `Regla propuesta`, `Justificación`, `Riesgo`, `Estado`, `Evidencia`.
- [x] 2.4 Cubrir `<NBSP>`, `DISTRITO`, `DEPARTAMENTO`, `MUNICIPIO`, `ESTABLECIMIENTO`, `DIRECCION`, `TELEFONO`, `SUPERVISOR`, `DIRECTOR`, `departamento_origen` y variables a conservar.
- [x] 2.5 Añadir decisiones diferidas/manuales, criterios para futura implementación y alcance excluido sin afirmar limpieza, deduplicación, normalización ni CSV limpio.
- [x] 3.1 Verificar que `docs/plan_limpieza.md` existe y declara alcance de planificación/no ejecución según la spec.
- [x] 3.2 Comparar `outputs/tablas/problemas_potenciales.csv` contra la tabla central del plan y confirmar cobertura o agrupación justificada.
- [x] 3.3 Revisar que cada regla tenga justificación, riesgo, estado y evidencia trazable a `docs/diagnostico.md`, `outputs/tablas/*.csv` o `data/interim/establecimientos_diversificado_raw_unificado.csv`.
- [x] 3.4 Inspeccionar `git diff --stat` y `git status --short` para confirmar que no cambiaron `data/raw/`, `data/interim/`, `outputs/`, scripts ni `docs/diagnostico.md`.

## Evidencia TDD

| Tarea | RED | GREEN | REFACTOR | Resultado |
| --- | --- | --- | --- | --- |
| 1.1 | No aplicable: lectura documental, sin producción/test de código. | Fuentes leídas e incorporadas al plan. | No aplicable. | Aprobado |
| 1.2 | No aplicable: mapeo documental, sin producción/test de código. | Cobertura documentada para cada fila de `problemas_potenciales.csv`. | No aplicable. | Aprobado |
| 2.1 | No aplicable: creación de documento, sin producción/test de código. | `docs/plan_limpieza.md` declara Paso 3 y no ejecución. | Revisión textual. | Aprobado |
| 2.2 | No aplicable: contenido documental, sin producción/test de código. | Secciones de evidencia, criterios y reglas globales agregadas. | Revisión textual. | Aprobado |
| 2.3 | No aplicable: tabla documental, sin producción/test de código. | Tabla central con encabezados requeridos creada. | Revisión textual. | Aprobado |
| 2.4 | No aplicable: cobertura documental, sin producción/test de código. | Variables requeridas y variables a conservar cubiertas. | Revisión textual. | Aprobado |
| 2.5 | No aplicable: contenido documental, sin producción/test de código. | Decisiones diferidas/manuales, criterios futuros y alcance excluido agregados. | Revisión textual. | Aprobado |
| 3.1 | No aplicable: verificación documental, sin producción/test de código. | Inspección confirma existencia y declaración de planificación. | No aplicable. | Aprobado |
| 3.2 | No aplicable: verificación documental, sin producción/test de código. | Cada fila del CSV de problemas está cubierta directa o agrupadamente. | No aplicable. | Aprobado |
| 3.3 | No aplicable: verificación documental, sin producción/test de código. | Cada fila central incluye justificación, riesgo, estado y evidencia. | No aplicable. | Aprobado |
| 3.4 | No aplicable: seguridad de alcance, sin producción/test de código. | `git diff --stat` y `git status --short` inspeccionados. | No aplicable. | Aprobado |

## Verificación ejecutada

- `/home/jonialen/.local/bin/uv run pytest`: **63 passed**.
- `git diff --cached --stat`: muestra 7 archivos staged y 501 inserciones; todo el lote actual está staged como documentación añadida.
- `git status --short`: muestra siete entradas `A` para `docs/plan_limpieza.md` y los artefactos OpenSpec bajo `openspec/changes/raw-cleaning-plan/`.
- `git status --short -- data/raw data/interim outputs scripts docs/diagnostico.md`: sin salida; no hay cambios en datos crudos, datos intermedios, outputs, scripts ni diagnóstico.

## Alcance de rollback/fix-forward

Rollback, recuperación y fix-forward deben operar sobre el set staged completo: `docs/plan_limpieza.md`, `openspec/changes/raw-cleaning-plan/proposal.md`, `openspec/changes/raw-cleaning-plan/exploration.md`, `openspec/changes/raw-cleaning-plan/design.md`, `openspec/changes/raw-cleaning-plan/specs/plan-limpieza-cruda/spec.md`, `openspec/changes/raw-cleaning-plan/tasks.md`, `openspec/changes/raw-cleaning-plan/apply-progress.md` y las observaciones Engram `sdd/raw-cleaning-plan/*`. No corregir ni retirar solo `docs/plan_limpieza.md`, `tasks.md` o `apply-progress.md`; hacerlo dejaría OpenSpec parcialmente aplicado con `proposal.md`, `exploration.md`, `design.md` o `spec.md` huérfanos.

## Cobertura de problemas potenciales

- `<NBSP>`: cubre `encabezado_sospechoso` y `faltantes_detectados`.
- `DISTRITO`: cubre `faltantes_detectados`.
- `DEPARTAMENTO`: cubre `catalogo_no_verificable`.
- `MUNICIPIO`: cubre `catalogo_no_verificable`.
- `ESTABLECIMIENTO`: cubre `faltantes_detectados` y `texto_sospechoso`.
- `DIRECCION`: cubre `faltantes_detectados` y `texto_sospechoso`.
- `TELEFONO`: cubre `faltantes_detectados`, `formato_sospechoso` y `texto_sospechoso`.
- `SUPERVISOR`: cubre `faltantes_detectados` y `texto_sospechoso`.
- `DIRECTOR`: cubre `faltantes_detectados` y `texto_sospechoso`.
- `departamento_origen`: cubre `catalogo_no_verificable`.
- `__fila__`: cubre `duplicados_parciales_diferidos`.

## Archivos staged del cambio

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `docs/plan_limpieza.md` | Creado | Plan documental de limpieza, sin ejecutar mutaciones. |
| `openspec/changes/raw-cleaning-plan/proposal.md` | Creado | Intención, alcance y recuperación del cambio documental. |
| `openspec/changes/raw-cleaning-plan/exploration.md` | Creado | Exploración previa y restricciones de no mutación. |
| `openspec/changes/raw-cleaning-plan/design.md` | Creado | Diseño documental y trazabilidad esperada. |
| `openspec/changes/raw-cleaning-plan/specs/plan-limpieza-cruda/spec.md` | Creado | Requisitos y escenarios de la capacidad nueva. |
| `openspec/changes/raw-cleaning-plan/tasks.md` | Creado | Tareas completadas y forecast actualizado al tamaño staged real. |
| `openspec/changes/raw-cleaning-plan/apply-progress.md` | Creado | Progreso de apply, evidencia TDD no aplicable y verificación. |

## Desviaciones del diseño

Ninguna. La implementación sigue el diseño documental y mantiene el alcance sin mutación de datos, código, outputs ni diagnóstico.

## Problemas encontrados

Ninguno bloqueante.

## Remediación de legibilidad

- `docs/plan_limpieza.md`: `DIRECCION` cambió de estado `accionable` a `manual` para alinear su riesgo `Medio` con los criterios de clasificación; no se afirma limpieza ejecutada.
- `docs/plan_limpieza.md`: la sección de decisiones manuales ahora incluye `DIRECCION` como texto semántico libre.
- `openspec/changes/raw-cleaning-plan/proposal.md`: el plan de reversión ahora cubre el set staged completo (`docs/plan_limpieza.md`, `proposal.md`, `exploration.md`, `design.md`, `specs/plan-limpieza-cruda/spec.md`, `tasks.md`, `apply-progress.md`) y las observaciones Engram actualizadas del cambio; cualquier rollback o fix-forward debe retirar o actualizar ese mismo conjunto para evitar artefactos OpenSpec huérfanos.
- `openspec/changes/raw-cleaning-plan/apply-progress.md`: el alcance aplicado, el inventario staged y la recuperación/fix-forward ahora enumeran el set documental completo para evitar retirar solo parte del cambio.
- `openspec/changes/raw-cleaning-plan/tasks.md`: el forecast de revisión ahora refleja el staged diff real de 501 inserciones y documenta por qué se mantiene como PR documental único con revisión focalizada.
- `openspec/changes/raw-cleaning-plan/apply-progress.md`: la evidencia de verificación ahora usa el estado staged actual (`git diff --cached --stat` y siete entradas `A`) y reemplaza la explicación obsoleta previa.

### Evidencia TDD de remediación

| Tarea | RED | GREEN | REFACTOR | Resultado |
| --- | --- | --- | --- | --- |
| Remediar consistencia de `DIRECCION` | No aplicable: corrección documental, sin producción/test de código. | Texto actualizado y revisado contra los criterios de clasificación. | Revisión de coherencia textual. | Aprobado |
| Actualizar alcance de reversión | No aplicable: corrección documental, sin producción/test de código. | Plan de reversión actualizado contra el conjunto real de artefactos. | Revisión de concisión y alcance. | Aprobado |
