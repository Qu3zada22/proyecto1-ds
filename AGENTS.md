# Guía para agentes del Proyecto 1

Este archivo es la fuente canónica de contexto para asistentes de desarrollo. `CLAUDE.md` y `CODEX.md` deben enlazar a este documento para evitar instrucciones duplicadas o contradictorias.

## Objetivo del repositorio

Construir un proceso reproducible para obtener, diagnosticar, limpiar y validar los establecimientos educativos de nivel **Diversificado** publicados por el MINEDUC de Guatemala.

El proyecto conserva la procedencia completa: los HTML oficiales son evidencia inmutable, el CSV de `data/source/` es la fuente consolidada canónica y el CSV de `data/processed/` es la salida limpia actual.

## Ruta rápida

```bash
# Instalar/sincronizar dependencias
uv sync

# Ejecutar todas las pruebas
uv run pytest

# Regenerar la fuente consolidada desde los HTML
uv run python scripts/consolidar_crudos.py

# Regenerar diagnóstico
uv run python scripts/diagnosticar_crudos.py

# Generar el catálogo territorial reproducible (requerido por la limpieza)
uv run python scripts/generar_catalogo_territorial.py

# Regenerar dataset limpio y enriquecido (normalización + códigos INE)
uv run python scripts/limpiar_dataset.py

# Detectar duplicados parciales y validar territorio (sin corrección automática)
uv run python scripts/detectar_duplicados.py
uv run python scripts/validar_territorio.py
```

Antes de entregar cambios, la suite completa debe pasar y `git diff --check` no debe reportar errores nuevos.

## Linaje de datos

```text
23 HTML oficiales + data/raw/manifest.json     data/reference/catalogo_territorial.csv (INE)
                    │                                          │
                    ▼                                          │
data/source/establecimientos_diversificado_mineduc.csv        │
                    │                                          │
          ┌─────────┴─────────┐                               │
          ▼                   ▼                               ▼
docs/diagnostico.md   data/processed/establecimientos_diversificado_limpio.csv
outputs/tablas/       outputs/tablas/bitacora_limpieza.csv
                      outputs/tablas/reporte_calidad_antes_despues.csv
                      outputs/tablas/duplicados_parciales.csv
                      outputs/tablas/inconsistencias_territoriales.csv
```

Datos de referencia vigentes:

- Fuente canónica: 11,867 filas, 20 columnas y 11,867 códigos únicos.
- Dataset limpio actual: 11,867 filas y 21 columnas (incluye `departamento_codigo` y `municipio_codigo`).
- Catálogo territorial: `data/reference/catalogo_territorial.csv` (22 departamentos, 340 municipios), derivado de un espejo/conversión comunitaria fijado; INE, Censo 2018 es la fuente primaria declarada, no el espejo.
- Territorio pendiente: 7 parejas/145 filas conservan `decision=revisar`; 2 variantes tipográficas abarcan 19 filas.
- Los 23 HTML y el manifest deben permanecer disponibles para reconstrucción y auditoría.

## Estructura principal

| Ruta | Responsabilidad |
|---|---|
| `data/raw/` | HTML oficiales y manifest; evidencia inmutable. |
| `data/source/` | CSV consolidado canónico generado desde los HTML. |
| `data/processed/` | Dataset limpio y enriquecido; nunca reemplaza la fuente. |
| `data/reference/` | Catálogo territorial oficial (INE) versionado; base de la validación territorial. |
| `src/proyecto1_ds/` | Lógica de adquisición, consolidación, diagnóstico, limpieza, enriquecimiento, duplicados y territorio. |
| `scripts/` | Interfaces CLI del pipeline. |
| `tests/` | Contratos y regresiones con pytest. |
| `outputs/tablas/` | Evidencia tabular generada por diagnóstico y limpieza. |
| `outputs/reportes/` | Recibos y reportes de trazabilidad. |
| `docs/instrucciones.md` | Requisitos originales del curso. |
| `docs/planificacion.md` | Estado autoritativo, brechas, responsables y aceptación. |
| `openspec/specs/` | Comportamiento vigente especificado. |
| `openspec/changes/archive/` | Historial SDD; no es código muerto. |

## Reglas obligatorias

1. No editar manualmente archivos de `data/raw/`, `data/source/`, `data/processed/` ni `outputs/`.
2. Toda transformación de datos debe realizarse mediante código reproducible.
3. No borrar los HTML oficiales ni `manifest.json`; son la procedencia del CSV canónico.
4. No sustituir la fuente canónica por el CSV alternativo de Anggie. Ese archivo es evidencia secundaria de reconciliación.
5. Preservar códigos, teléfonos y demás identificadores como texto cuando corresponda.
6. No corregir territorios, teléfonos, duplicados parciales o texto libre sin una regla aprobada y evidencia trazable.
7. Actualizar pruebas, documentación y especificaciones cuando cambie una ruta o contrato público.
8. No declarar como completado un entregable que solo esté planificado.
9. Usar español neutral/profesional en entregables del curso; usar nombres técnicos claros y consistentes en el código.
10. No hacer commit o push de cachés, `.venv/`, bytecode, temporales, backups ni credenciales.

## Convenciones de implementación

- Python `>=3.11`, dependencias administradas con `uv`. Dependencia de runtime: `rapidfuzz` (similitud de cadenas).
- Tests con `pytest`; preferir comportamiento observable sobre detalles internos.
- Mantener los CLI delgados; la lógica pertenece en `src/proyecto1_ds/`.
- Conservar escrituras atómicas y guards de rutas existentes.
- Los cambios en código deben seguir TDD: prueba fallida, implementación mínima y suite verde.
- Mantener cambios y commits como unidades revisables; incluir pruebas y documentación relacionadas.
- Commits convencionales, sin atribución automática ni líneas `Co-Authored-By` generadas por IA.

## Trabajo pendiente y responsables

`docs/planificacion.md` es la autoridad. Resumen actual:

| Responsable | Próximos entregables |
|---|---|
| Anggie | Pendiente/no implementado: decisiones de duplicados parciales, excepciones telefónicas y su sección del Code Book. |
| Iris | Hecho: catálogo reproducible, consistencia territorial, normalización, códigos derivados y Code Book territorial de 4 variables. |
| Jonathan | Integración final pendiente: validación, reporte completo, README, ensamblaje del Code Book Markdown/PDF y auditoría. |

Cada integrante debe aportar commits identificables y una sección concreta del Code Book. Los entregables futuros continúan como **planificados/no implementados** hasta que exista evidencia de aceptación.

## Verificación antes de cerrar trabajo

- [ ] `uv run pytest` pasa completamente.
- [ ] Los HTML, manifest, CSV canónico, CSV limpio y outputs protegidos no cambiaron accidentalmente.
- [ ] Los archivos generados se regeneraron mediante sus scripts, no mediante edición manual.
- [ ] Las rutas documentadas coinciden con `data/source/` y `data/processed/`.
- [ ] `docs/planificacion.md` refleja el estado real.
- [ ] No hay secretos, cachés ni temporales en el diff.
- [ ] El cambio tiene criterio de rollback cuando mueve o elimina archivos.

## Lecturas recomendadas

1. `docs/instrucciones.md` — rúbrica y entregables exigidos.
2. `docs/planificacion.md` — qué está hecho y qué falta.
3. `docs/fuentes_datos.md` — procedencia y extracción.
4. `docs/plan_limpieza.md` — reglas conservadoras.
5. `docs/reconciliacion_anggie.md` — comparación con la fuente secundaria.
