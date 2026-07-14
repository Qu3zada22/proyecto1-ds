# Proposal: Plan de limpieza cruda

## Intento

Crear una propuesta documental para `docs/plan_limpieza.md` que traduzca el diagnóstico crudo actual en reglas planificadas por variable, antes de modificar datos. El cambio cubre el Paso 3 de la rúbrica CC3084: problema específico, regla exacta, justificación y riesgos.

## Alcance

### Dentro del alcance
- Definir la estructura y criterios de `docs/plan_limpieza.md` usando `docs/diagnostico.md` y `outputs/tablas/*.csv`.
- Exigir tabla por variable con problema, regla candidata, evidencia, justificación, riesgo y estado.
- Separar reglas accionables de decisiones diferidas por falta de catálogo o revisión manual.

### Fuera del alcance
- Mutar `data/raw/`, `data/interim/`, scripts u outputs generados.
- Ejecutar limpieza, validación, deduplicación, reporte antes/después, Code Book final o CSV limpio.

## Capacidades

### Nuevas capacidades
- `plan-limpieza-cruda`: especifica el documento trazable de planificación de limpieza sobre datos crudos diagnosticados.

### Capacidades modificadas
- Ninguna. La adquisición, consolidación y diagnóstico siguen siendo fases sin limpieza.

## Enfoque

Usar un plan descriptivo trazable desde diagnóstico: resumir fuentes, listar reglas globales de nulos/texto/tipos/trazabilidad, y bajar a nivel de variable para `<NBSP>`, `DISTRITO`, `DEPARTAMENTO`, `MUNICIPIO`, `ESTABLECIMIENTO`, `DIRECCION`, `TELEFONO`, `SUPERVISOR`, `DIRECTOR`, `departamento_origen` y variables a conservar sin cambio.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `docs/plan_limpieza.md` | Nuevo | Entregable futuro de planificación. |
| `docs/diagnostico.md` | Referencia | Fuente narrativa; no se reescribe. |
| `outputs/tablas/*.csv` | Referencia | Evidencia cuantitativa; no se regenera. |
| `data/interim/establecimientos_diversificado_raw_unificado.csv` | Sin cambio | Dataset observado; no se modifica. |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Convertir observaciones en reglas definitivas sin catálogo oficial | Media | Marcar dominios territoriales como diferidos. |
| Destruir nombres propios al normalizar texto | Media | Proponer reglas conservadoras y reversibles. |
| Sobrerregular teléfonos con caracteres no numéricos | Media | Documentar revisión antes de estandarizar. |

## Plan de reversión y recuperación

Revertir, recuperar o aplicar fix-forward siempre sobre el set documental staged completo del cambio: `docs/plan_limpieza.md`, `openspec/changes/raw-cleaning-plan/proposal.md`, `openspec/changes/raw-cleaning-plan/exploration.md`, `openspec/changes/raw-cleaning-plan/design.md`, `openspec/changes/raw-cleaning-plan/specs/plan-limpieza-cruda/spec.md`, `openspec/changes/raw-cleaning-plan/tasks.md`, `openspec/changes/raw-cleaning-plan/apply-progress.md` y las observaciones Engram actualizadas para `sdd/raw-cleaning-plan/*`. No retirar ni corregir solo `docs/plan_limpieza.md`, `tasks.md` o `apply-progress.md`: el mismo set completo debe actualizarse o eliminarse para evitar artefactos OpenSpec huérfanos (`proposal.md`, `exploration.md`, `design.md` o `spec.md`). No hay datos ni código que restaurar.

## Dependencias

- Diagnóstico vigente y tablas generadas por código ya existentes.
- Rúbrica en `docs/instrucciones.md`.

## Criterios de éxito

- [ ] La propuesta define `plan-limpieza-cruda` como capacidad nueva.
- [ ] El alcance prohíbe explícitamente mutar datos o producir CSV limpio.
- [ ] La siguiente fase puede escribir specs para `docs/plan_limpieza.md` sin ambigüedad.
