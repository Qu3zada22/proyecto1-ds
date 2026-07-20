# Recomendaciones para revisión pendiente

Estas recomendaciones **no equivalen a aprobación institucional**. No se modificó ni fusionó ningún dataset; las salidas organizan evidencia vigente para revisión.

## Ruta rápida

```bash
uv run python scripts/revisar_pendientes.py
```

## Resultados

| Unidad auditable | Resultado | Límite |
|---|---:|---|
| Duplicados, un par pendiente por fila | 978 | 0 duplicados confirmables localmente; 0 independientes adicionales; 978 requieren fuente institucional. |
| Teléfonos, un establecimiento pendiente por fila | 245 | 0 propuestas seguras restantes; 196 conservar/documentar; 49 requieren fuente institucional. |
| Territorio, una pareja por fila | 7 parejas territoriales (145 filas) | Alias confirmable para unión por código; 0 renombres automáticos. |

## Reglas

- Duplicados: 11 pares aprobados viven en `data/decisions/duplicados_aprobados.csv` y quedan fuera de esta tabla pendiente. La etiqueta de triage no se usa como conclusión.
- Teléfonos: 6 normalizaciones aprobadas viven en `data/decisions/telefonos_aprobados.csv` y ya no aparecen como pendientes. Una cadena de 16 dígitos solo recibe una separación de referencia.
- Confianza: la columna `confianza` expresa confianza en la recomendación conservadora, no la confianza del detector original.
- Territorio: cada etiqueta MINEDUC se conserva; el código municipal del registro debe coincidir con el catálogo y con el segmento del `CODIGO` MINEDUC.

## Evidencia

- `outputs/tablas/recomendaciones_duplicados.csv`
- `outputs/tablas/recomendaciones_telefonos.csv`
- `outputs/tablas/recomendaciones_territorio.csv`

Las decisiones de fusión, sustitución, aceptación telefónica o renombre territorial continúan pendientes de autoridad institucional.
