# Diseño: Plan de limpieza cruda

## Enfoque técnico

El cambio implementará solo un entregable documental: `docs/plan_limpieza.md`. El documento traducirá el diagnóstico crudo vigente en reglas propuestas, sin ejecutar limpieza ni alterar `data/raw/`, `data/interim/`, `outputs/`, scripts o `docs/diagnostico.md`. La estructura debe ser revisable contra el Paso 3 de `docs/instrucciones.md`: problema específico, regla exacta, justificación y riesgo por variable.

## Decisiones de arquitectura

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| Plan descriptivo trazable | Mantiene separación diagnóstico → plan → limpieza; algunas reglas quedan pendientes. | Usar este enfoque porque cumple la spec sin inventar catálogos ni mutar datos. |
| Reglas finales prescriptivas | Acelera una limpieza futura, pero puede declarar inválidos sin evidencia oficial. | Rechazado para dominios territoriales, teléfonos finales y duplicados parciales. |
| Documento por secciones cortas y tablas | Más estructura inicial, menor carga cognitiva para revisión. | Adoptar títulos claros, tabla central y checklist de verificación. |

## Flujo de datos

Solo fluye evidencia hacia documentación:

```text
docs/diagnostico.md ─┐
outputs/tablas/*.csv ├─→ redacción manual trazable ─→ docs/plan_limpieza.md
data/interim/*.csv ──┘             │
                                   └─ no muta fuentes ni outputs
```

## Estructura de `docs/plan_limpieza.md`

1. **Resumen ejecutivo**: declarar que es planificación del Paso 3, no limpieza ejecutada.
2. **Fuentes de evidencia**: listar `docs/diagnostico.md`, `outputs/tablas/resumen_dataset.csv`, `diagnostico_columnas.csv`, `problemas_potenciales.csv`, `dominios_observados.csv`, `duplicados_exactos.csv` y `data/interim/establecimientos_diversificado_raw_unificado.csv`.
3. **Criterios de clasificación**: definir `accionable`, `diferida`, `manual` y `conservar`.
4. **Reglas globales propuestas**: nulos/marcadores de ausencia, texto, tipos como texto, trazabilidad, duplicados.
5. **Plan por variable/problema**: tabla con encabezados obligatorios `Variable`, `Problema`, `Regla propuesta`, `Justificación`, `Riesgo`, `Estado`, `Evidencia`.
6. **Decisiones diferidas y revisión manual**: catálogo territorial, duplicados parciales, teléfonos ambiguos, nombres propios.
7. **Criterios para futura implementación**: qué deberá probar la limpieza posterior.
8. **Alcance excluido**: repetir que no se creó CSV limpio, Code Book final ni reporte antes/después.

## Evidencia por sección

| Sección | Evidencia primaria |
|---------|--------------------|
| Resumen | `docs/diagnostico.md`, `resumen_dataset.csv` |
| Problemas por variable | `problemas_potenciales.csv`, `diagnostico_columnas.csv` |
| Dominios y ejemplos | `dominios_observados.csv` |
| Duplicados | `duplicados_exactos.csv`; fila `duplicados_parciales_diferidos` en `problemas_potenciales.csv` |
| Límites de no limpieza | `docs/diagnostico.md`, specs de consolidación/diagnóstico crudo |

## Contratos de clasificación

- `accionable`: evidencia cuantitativa suficiente, regla determinística, reversible y de bajo riesgo. Ejemplos: registrar `<NBSP>` vacío, planear normalización conservadora de espacios, mapear marcadores de ausencia.
- `diferida`: requiere catálogo oficial, diseño adicional o comparación posterior. Ejemplos: `DEPARTAMENTO`, `MUNICIPIO`, `departamento_origen`, duplicados parciales.
- `manual`: requiere revisión humana por posible pérdida semántica. Ejemplos: teléfonos con separadores/extensiones, nombres de `ESTABLECIMIENTO`, `SUPERVISOR`, `DIRECTOR`.
- `conservar`: sin problema fuerte en diagnóstico actual; no transformar por inercia. Ejemplos: `CODIGO`, `NIVEL`, `SECTOR`, `AREA`, `STATUS`, `MODALIDAD`, `JORNADA`, `PLAN`, `DEPARTAMENTAL`, `archivo_origen`.

## Cambios de archivos

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `docs/plan_limpieza.md` | Crear | Entregable documental futuro; único archivo de producto del apply. |
| `openspec/changes/raw-cleaning-plan/design.md` | Crear | Diseño SDD de este cambio. |

No se modificarán código, datos crudos, datos intermedios, tablas en `outputs/` ni diagnóstico existente.

## Estrategia de verificación

| Capa | Qué verificar | Enfoque |
|------|---------------|---------|
| Documento | Existe `docs/plan_limpieza.md` y declara planificación/no ejecución. | Inspección de archivo. |
| Contrato | Incluye secciones y encabezados obligatorios. | Revisión textual contra esta tabla. |
| Cobertura | Cada variable/problema reportado en `problemas_potenciales.csv` aparece en el plan o queda agrupado con justificación explícita. | Comparar filas de `problemas_potenciales.csv` contra la tabla central del plan. |
| Trazabilidad | Cada regla referencia evidencia concreta. | Buscar rutas de evidencia por fila/sección. |
| No mutación | Solo cambian `docs/plan_limpieza.md` y artefactos SDD. | Inspeccionar diff/status; no regenerar datos. |

## Migración / despliegue

No requiere migración. Rollback: eliminar `docs/plan_limpieza.md` y revertir artefactos SDD del cambio.

## Preguntas abiertas

Ninguna bloqueante.
