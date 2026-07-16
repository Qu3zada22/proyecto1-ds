# Especificación: Diagnóstico de calidad cruda

## Propósito

Definir el diagnóstico reproducible previo a limpieza, priorizando `docs/diagnostico.md` y tablas generadas por código.

## Requisitos

### Requirement: Diagnóstico rúbrica plus

El sistema MUST diagnosticar desde `data/source/establecimientos_diversificado_mineduc.csv` filas, columnas, tipos, faltantes, únicos, duplicados, dominios, formatos y problemas; SHOULD reportar patrones sospechosos.
(Anteriormente: consumía `data/interim/`.)

#### Scenario: métricas reproducibles
- DADO la fuente válida
- CUANDO se diagnostica
- ENTONCES documento y tablas se regeneran mediante código.

#### Scenario: catálogo oficial ausente
- DADO que falta el catálogo oficial
- CUANDO se evalúan dominios
- ENTONCES se documenta y no se declaran inválidos sin evidencia.

### Requisito: Límites previos a limpieza

El sistema MUST NOT limpiar, corregir, fusionar ni eliminar datos durante el diagnóstico. Los duplicados parciales MUST quedar diferidos a la fase de limpieza; este slice MAY reportar solo duplicados exactos.

#### Escenario: duplicados exactos detectados

- DADO que existen filas idénticas en el dataset crudo
- CUANDO se calculan duplicados
- ENTONCES se reporta su cantidad exacta sin eliminarlas.

#### Escenario: duplicados parciales sospechosos

- DADO que hay registros parecidos pero no idénticos
- CUANDO se redacta el diagnóstico
- ENTONCES se documenta que el análisis parcial queda diferido.
