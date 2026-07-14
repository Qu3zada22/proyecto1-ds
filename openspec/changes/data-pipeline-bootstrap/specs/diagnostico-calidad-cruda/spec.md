# Especificación: Diagnóstico de calidad cruda

## Propósito

Definir el diagnóstico reproducible previo a limpieza, priorizando `docs/diagnostico.md` y tablas generadas por código.

## Requisitos

### Requisito: Diagnóstico rúbrica plus

El sistema MUST generar métricas de filas, columnas, tipos, faltantes, únicos, duplicados exactos, dominios, formatos y problemas potenciales. También SHOULD reportar patrones sospechosos de texto o dominio cuando sea viable.

#### Escenario: métricas obligatorias generadas

- DADO que existe el dataset intermedio crudo
- CUANDO se ejecuta el diagnóstico
- ENTONCES `docs/diagnostico.md` resume las métricas requeridas
- Y las tablas provienen de código reproducible.

#### Escenario: catálogo oficial no disponible

- DADO que no se encuentra catálogo oficial de departamentos o municipios
- CUANDO se evalúan dominios territoriales
- ENTONCES el diagnóstico documenta la limitación
- Y evita declarar inválidos sin evidencia suficiente.

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
