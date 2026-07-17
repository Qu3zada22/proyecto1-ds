# Duplicados parciales (candidatos)

Generado por código sobre `C:/Users/irisa/Documents/Trabajos_UVG/Semestre 8/DataScience/Proyecto1-ds/data/processed/establecimientos_diversificado_limpio.csv` mediante similitud de cadenas (RapidFuzz).

## Método

- Bloqueo por `DEPARTAMENTO` + `MUNICIPIO`: solo se comparan establecimientos de la misma localidad.
- Similitud de nombres con `token_sort_ratio`; umbral de nombre: 90.0.
- Corroboración de sede: además del nombre, el par debe coincidir en dirección (similitud >= 88.0) o en teléfono.
- Corroboración de oferta: el par debe coincidir en `SECTOR`, `MODALIDAD`, `JORNADA` y `PLAN`. Si difieren, es la misma sede con distinta jornada o plan (oferta legítima), no un duplicado.
- `confianza = alta` cuando coinciden dirección y teléfono; `media` cuando solo una corrobora.
- **No se elimina ni fusiona ningún registro**: cada candidato queda con `decision = revisar`.

## Resumen

- Bloques evaluados: 358
- Comparaciones realizadas: 1039023
- Candidatos a duplicado parcial: 1355
- Confianza alta: 718
- Confianza media: 637
- Variantes de misma sede con distinta oferta (no duplicados): 7046

## Salida

- `outputs/tablas/duplicados_parciales.csv`: un par candidato por fila, con sus similitudes y la decisión pendiente.

La decisión final de cada par requiere revisión humana; este reporte solo entrega evidencia trazable.
