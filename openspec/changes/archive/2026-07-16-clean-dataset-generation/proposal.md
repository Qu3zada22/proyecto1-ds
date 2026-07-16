# Propuesta: Generación conservadora de dataset limpio

## Intención

Implementar el primer slice real de limpieza del dataset MINEDUC a partir de `docs/plan_limpieza.md`. No es el universo final de limpieza: solo ejecuta reglas determinísticas seguras, preserva procedencia y evita sobre-limpieza semántica.

## Alcance

### Incluido
- Generar `data/processed/establecimientos_diversificado_limpio.csv` desde `data/interim/establecimientos_diversificado_raw_unificado.csv`.
- Aplicar reglas conservadoras: nulos claros, espacios/NBSP, eliminación segura de columna `<NBSP>` vacía y conservación de identificadores/categorías como texto.
- Generar `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`.

### Excluido
- Validación territorial final, catálogo oficial y consistencia departamento/municipio.
- Deduplicación parcial, fusión de registros o edición semántica de nombres, direcciones, supervisores y directores.
- Usar el CSV de Anggie como entrada primaria; queda solo como evidencia secundaria de validación.

## Capacidades

### Capacidades nuevas
- `limpieza-dataset-trazable`: ejecución reproducible de limpieza determinística con dataset limpio, bitácora y reporte antes/después.

### Capacidades modificadas
- Ninguna.

## Enfoque

Agregar un módulo/CLI de limpieza con TDD estricto en implementación posterior. La entrada será solo el CSV intermedio crudo; las salidas serán artefactos nuevos. Las columnas de texto libre se preservan casi intactas: solo normalización conservadora de espacios y marcadores inequívocos de ausencia.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `src/proyecto1_ds/cleaning.py` | Nuevo | Reglas determinísticas, bitácora y métricas. |
| `scripts/limpiar_dataset.py` | Nuevo | CLI reproducible de limpieza. |
| `tests/test_cleaning.py` | Nuevo | Pruebas TDD de reglas y límites. |
| `data/processed/` | Nuevo | CSV limpio generado. |
| `outputs/tablas/` | Modificado | Nuevas tablas de bitácora y reporte; no reescribe diagnósticos existentes. |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Mutar `data/raw/` o `data/interim/` | Baja | Pruebas de rutas y escritura solo en salidas nuevas. |
| Sobre-limpiar texto libre | Media | Reglas limitadas a espacios/NBSP y nulos inequívocos. |
| Perder ceros o separadores en códigos | Media | Tratar identificadores, teléfonos y categorías como texto. |

## Plan de reversión

Eliminar el módulo/CLI y borrar únicamente los artefactos nuevos en `data/processed/` y `outputs/tablas/`. `data/raw/`, `data/interim/`, HTML fuente y diagnósticos existentes permanecen intactos.

## Dependencias

- `docs/plan_limpieza.md` y dataset intermedio crudo vigente.
- `uv run pytest` para TDD/verify posterior.

## Criterios de éxito

- [ ] Se genera CSV limpio separado sin mutar fuentes crudas/intermedias.
- [ ] La bitácora registra columna, regla, conteo, justificación y evidencia.
- [ ] El reporte antes/después distingue limpieza ejecutada de decisiones diferidas.
- [ ] Las pruebas prueban límites de no deduplicación, no validación territorial y preservación textual.
