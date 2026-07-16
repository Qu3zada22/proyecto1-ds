# Especificación: Plan de limpieza cruda

## Propósito

Definir el entregable documental `docs/plan_limpieza.md` para planificar, sin ejecutar, reglas de limpieza trazables desde el diagnóstico crudo vigente y la rúbrica CC3084.

## Requisitos

### Requisito: Documento de planificación obligatorio

El sistema MUST producir `docs/plan_limpieza.md` como documento de planificación previo a cualquier mutación de datos. El documento MUST declarar que corresponde al Paso 3 de `docs/instrucciones.md` y que no representa limpieza ejecutada.

#### Escenario: documento presente

- DADO que existe la propuesta de plan de limpieza cruda
- CUANDO se revise el entregable de planificación
- ENTONCES `docs/plan_limpieza.md` existe
- Y declara alcance de planificación, no ejecución.

#### Escenario: documento ausente

- DADO que no existe `docs/plan_limpieza.md`
- CUANDO se valide la capacidad
- ENTONCES el cambio no cumple el requisito.

### Requisito: Trazabilidad por variable y problema

`docs/plan_limpieza.md` MUST incluir una tabla por variable o problema diagnosticado con: variable, problema, regla propuesta, justificación, riesgo, estado y evidencia. La evidencia MUST trazar a `docs/diagnostico.md`, `outputs/tablas/diagnostico_columnas.csv`, `outputs/tablas/problemas_potenciales.csv`, `outputs/tablas/dominios_observados.csv`, `outputs/tablas/duplicados_exactos.csv` o `data/source/establecimientos_diversificado_mineduc.csv`.

#### Escenario: variable diagnosticada

- DADO que el diagnóstico reporta problemas en una variable
- CUANDO se lea su fila del plan
- ENTONCES se muestran problema, regla, justificación, riesgo, estado y evidencia trazable.

#### Escenario: variable sin problema fuerte

- DADO que una variable debe conservarse sin cambio por falta de evidencia de problema
- CUANDO se lea el plan
- ENTONCES su estado documenta conservación explícita o revisión diferida.

### Requisito: Separación de decisiones accionables y diferidas

El plan MUST separar reglas accionables de decisiones diferidas, manuales o dependientes de catálogo. Dominios territoriales, duplicados parciales, estandarización final de teléfonos y decisiones que requieran catálogo oficial o revisión humana MUST quedar marcadas como diferidas o manuales cuando la evidencia actual no sea concluyente.

#### Escenario: regla accionable

- DADO que una observación tiene evidencia suficiente y bajo riesgo
- CUANDO se clasifica en el plan
- ENTONCES aparece como accionable con justificación y riesgo.

#### Escenario: evidencia insuficiente

- DADO que una decisión requiere catálogo oficial o revisión manual
- CUANDO se clasifica en el plan
- ENTONCES aparece como diferida, manual o dependiente de catálogo
- Y no se presenta como corrección definitiva.

### Requisito: No ejecución de limpieza ni mutación de datos

El plan MUST NOT modificar `data/raw/`, `data/source/`, `outputs/`, scripts ni documentos diagnósticos. También MUST NOT afirmar que se limpió, deduplicó, normalizó, validó territorialmente o generó un dataset limpio.

#### Escenario: revisión de alcance

- DADO que solo se está escribiendo el plan
- CUANDO se inspeccionan artefactos fuera de la spec
- ENTONCES no hay cambios en datos, código, outputs ni diagnóstico.

#### Escenario: lenguaje de ejecución indebido

- DADO que el documento usa lenguaje de limpieza ya ejecutada
- CUANDO se valide el plan
- ENTONCES el requisito falla porque debe usar lenguaje de regla propuesta o decisión pendiente.
