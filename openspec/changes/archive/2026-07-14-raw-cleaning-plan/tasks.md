# Tasks: Plan de limpieza cruda

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas cambiadas estimadas | 501 inserciones staged reales (`git diff --cached --stat`) |
| 400-line budget risk | High por tamaño bruto; gestionado como excepción documental acotada |
| Chained PRs recommended | No, después de revisión focalizada del staged diff |
| Suggested split | PR único atómico: `docs/plan_limpieza.md` + artefactos OpenSpec/SDD requeridos |
| Delivery strategy | single PR con manejo de revisión por lentes acotados |
| Chain strategy | no aplicable |

Decision needed before apply: No; el staged diff real ya fue tratado como lote documental único y revisado por alcance.
Chained PRs recommended: No; separar los artefactos dejaría el cambio OpenSpec menos trazable que el paquete atómico actual.
Chain strategy: no aplicable
400-line budget risk: High por 501 inserciones staged; aceptable para revisión porque son 7 archivos documentales añadidos, sin código/datos/outputs, y la revisión se manejó con lentes focalizados de riesgo, resiliencia y legibilidad.

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Crear y verificar `docs/plan_limpieza.md` sin mutar datos/código/outputs | PR 1 | Base main; revisión textual y diff/status incluidos |

## Phase 1: Preparación de evidencia

- [x] 1.1 Leer `docs/instrucciones.md`, `docs/diagnostico.md` y `outputs/tablas/{resumen_dataset,diagnostico_columnas,problemas_potenciales,dominios_observados,duplicados_exactos}.csv` como fuentes de evidencia.
- [x] 1.2 Mapear cada fila de `outputs/tablas/problemas_potenciales.csv` a una entrada esperada del plan o a una agrupación con justificación explícita.

## Phase 2: Redacción del documento

- [x] 2.1 Crear `docs/plan_limpieza.md` con resumen ejecutivo que declare Paso 3, planificación previa y no limpieza ejecutada.
- [x] 2.2 Añadir fuentes de evidencia, criterios `accionable`/`diferida`/`manual`/`conservar` y reglas globales propuestas para nulos, texto, tipos, trazabilidad y duplicados.
- [x] 2.3 Completar la tabla central con encabezados `Variable`, `Problema`, `Regla propuesta`, `Justificación`, `Riesgo`, `Estado`, `Evidencia`.
- [x] 2.4 Cubrir `<NBSP>`, `DISTRITO`, `DEPARTAMENTO`, `MUNICIPIO`, `ESTABLECIMIENTO`, `DIRECCION`, `TELEFONO`, `SUPERVISOR`, `DIRECTOR`, `departamento_origen` y variables a conservar.
- [x] 2.5 Añadir decisiones diferidas/manuales, criterios para futura implementación y alcance excluido sin afirmar limpieza, deduplicación, normalización ni CSV limpio.

## Phase 3: Verificación

- [x] 3.1 Verificar que `docs/plan_limpieza.md` existe y declara alcance de planificación/no ejecución según la spec.
- [x] 3.2 Comparar `outputs/tablas/problemas_potenciales.csv` contra la tabla central del plan y confirmar cobertura o agrupación justificada.
- [x] 3.3 Revisar que cada regla tenga justificación, riesgo, estado y evidencia trazable a `docs/diagnostico.md`, `outputs/tablas/*.csv` o `data/interim/establecimientos_diversificado_raw_unificado.csv`.
- [x] 3.4 Inspeccionar `git diff --stat` y `git status --short` para confirmar que no cambiaron `data/raw/`, `data/interim/`, `outputs/`, scripts ni `docs/diagnostico.md`.
