# Validación cruzada del CSV de Anggie

Este documento registra una comparación técnica entre el CSV disponible en la rama `scrap-anggie` y el dataset intermedio generado por el pipeline actual. El objetivo es conservar trazabilidad de fuentes alternativas y dejar evidencia de revisión cruzada antes de decidir cualquier integración futura.

## Fuentes comparadas

| Fuente | Ubicación | Uso en esta revisión |
|--------|-----------|----------------------|
| CSV de Anggie | `scrap-anggie:data/raw/establecimientos_diversificado_guatemala.csv` | Evidencia secundaria de validación cruzada. |
| Dataset intermedio actual | `data/interim/establecimientos_diversificado_raw_unificado.csv` | Referencia generada desde HTML oficial MINEDUC preservado. |

## Resultado resumido

| Métrica | CSV de Anggie | Dataset intermedio actual |
|---------|---------------|---------------------------|
| Filas observadas | 12,807 | 11,867 |
| Códigos únicos | 11,867 | 11,867 |
| Códigos faltantes entre fuentes | 0 | 0 |
| Duplicados exactos | 1,081 | 0 |
| Departamentos observados | 23 | 23 |

Ambas fuentes cubren los mismos códigos de establecimientos. La diferencia principal es que el CSV de Anggie incluye duplicados exactos y requiere lectura cuidadosa por espacios antes de campos entrecomillados.

## Hallazgos técnicos

- El CSV de Anggie se interpreta mejor usando `skipinitialspace=True`, porque varias filas tienen espacios antes de campos entrecomillados.
- La cobertura por código coincide con el dataset intermedio actual: no se encontraron códigos extra ni faltantes.
- Los duplicados exactos del CSV de Anggie no deben incorporarse automáticamente al dataset principal sin una regla explícita de deduplicación.
- Se observaron diferencias puntuales en algunos campos, por lo que el CSV es útil como referencia de contraste para una reconciliación posterior.

## Decisión de uso

El CSV de Anggie se tratará como **fuente secundaria de validación cruzada**, no como reemplazo automático del pipeline actual. Si una fase posterior decide fusionar diferencias campo a campo, el valor del CSV de Anggie podrá priorizarse cuando exista conflicto, dejando evidencia del cambio aplicado.

## Próximo paso recomendado

Crear una fase posterior de reconciliación que:

1. lea el CSV de Anggie con parámetros explícitos;
2. normalice encabezados para comparación;
3. deduplique filas exactas;
4. compare valores campo a campo contra el dataset intermedio;
5. genere un reporte reproducible de diferencias y decisiones.

Esta revisión no modifica datos crudos, datos intermedios, outputs ni reglas de limpieza.
