# Diagnóstico de datos crudos MINEDUC

Este diagnóstico fue generado por código sobre `data/interim/establecimientos_diversificado_raw_unificado.csv`.

## Resumen

- Filas: 11867
- Columnas: 20
- Duplicados exactos: 0
- Catálogo territorial: no verificable
- Problemas potenciales reportados: 18 (incluye duplicados parciales diferidos)

## Flujo reproducible

El flujo completo conserva la línea de procedencia `adquisición → manifest → consolidación → diagnóstico`:

1. Adquisición: `uv run python scripts/adquirir_datos.py --capture-html --department-code 01 --department-name GUATEMALA --fecha-extraccion 2026-07-14`.
2. Manifest: `data/raw/manifest.json` registra fuente, cobertura, método, checksum y error de adquisición si aplica.
3. Consolidación: `uv run python scripts/consolidar_crudos.py` regenera `data/interim/establecimientos_diversificado_raw_unificado.csv` sin limpieza.
4. Diagnóstico: `uv run python scripts/diagnosticar_crudos.py` regenera estas tablas y este documento.

El comando de adquisición mostrado es un ejemplo para un departamento. La adquisición preservada contiene 23 artefactos HTML departamentales en `data/raw/`; para recapturarla completa, repita el comando para cada código y nombre de departamento, o use los artefactos crudos ya preservados.

## Tablas generadas

- `outputs/tablas/resumen_dataset.csv`
- `outputs/tablas/diagnostico_columnas.csv`
- `outputs/tablas/duplicados_exactos.csv`
- `outputs/tablas/problemas_potenciales.csv`
- `outputs/tablas/dominios_observados.csv`

## Alcance y límites

No se aplicó limpieza, normalización, deduplicación, recodificación, corrección de tipos, eliminación de filas ni corrección de dominios. Los duplicados exactos se reportan sin eliminarlos. Los duplicados parciales quedan diferidos a la fase de limpieza para evitar fusiones o correcciones sin revisión.

## Limitación territorial

No se encontró catálogo oficial de departamentos o municipios en este slice. Por esa razón el diagnóstico documenta dominios territoriales como no verificables y evita declarar valores inválidos sin evidencia suficiente.
