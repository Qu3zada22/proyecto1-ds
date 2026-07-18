# Validación territorial (departamento–municipio)

Generado por código sobre `C:/Users/irisa/Documents/Trabajos_UVG/Semestre 8/DataScience/Proyecto1-ds/data/processed/establecimientos_diversificado_limpio.csv` contra el catálogo oficial `C:/Users/irisa/Documents/Trabajos_UVG/Semestre 8/DataScience/Proyecto1-ds/data/reference/catalogo_territorial.csv` (INE, Censo 2018).

## Método

- Los nombres se comparan normalizando mayúsculas y tildes.
- Regla documentada: `CIUDAD CAPITAL` se trata como el municipio de Guatemala; las `ZONA N` son sus zonas.
- Cada pareja no reconocida se clasifica y se sugiere el nombre oficial más parecido (RapidFuzz).
- **No se corrige ningún valor**: cada inconsistencia queda con `decision = revisar`.

## Tipos de inconsistencia

- `departamento_invalido`: el departamento no existe en el catálogo.
- `municipio_en_otro_departamento`: el municipio existe, pero pertenece a otro departamento.
- `municipio_desconocido`: el municipio no aparece en ese departamento; se sugiere el más parecido.

## Resumen

- Parejas distintas evaluadas: 358
- Parejas válidas: 329
- Parejas por regla CIUDAD CAPITAL: 22
- Parejas inconsistentes: 7
- Filas afectadas: 145

## Salida

- `outputs/tablas/inconsistencias_territoriales.csv`: una pareja por fila, con tipo, sugerencia y decisión pendiente.

La decisión final requiere revisión humana; este reporte solo entrega evidencia trazable.
