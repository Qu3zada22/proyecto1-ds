# Propuesta: Bootstrap del pipeline de diagnóstico

## Intención

Crear el primer slice ejecutable del proyecto CC3084: obtener o registrar datos crudos de MINEDUC, consolidarlos sin limpieza y generar un diagnóstico inicial reproducible. El resultado prioritario es `docs/diagnostico.md` con métricas generadas por código.

## Alcance

### Incluye
- Bootstrap Python script-first mínimo para adquisición, consolidación cruda y diagnóstico.
- Estrategia mixta de adquisición: intentar scraping simple si MINEDUC lo permite; si falla, reportar el fallo claramente y usar fallback manual cuando ya existan CSV crudos.
- Preservación de CSV crudos en `data/raw/` con fuente, fecha de extracción, versión SemVer-like y alcance real disponible.
- Consolidación previa a limpieza en `data/interim/`, preservando `archivo_origen` y `departamento_origen` por registro.
- Diagnóstico “rúbrica plus”: filas/columnas, tipos, faltantes, únicos, duplicados exactos, dominios, formatos y patrones sospechosos de texto/dominio cuando sea viable.

### Fuera de alcance
- Limpieza, normalización, corrección de tipos, recodificación, deduplicación, eliminación de filas o corrección de dominios.
- Análisis/corrección de duplicados parciales; solo se documentará que queda diferido.
- Plan de limpieza, validación final, reporte antes/después, Code Book final y CSV limpio final.

## Capacidades

### Nuevas
- `adquisicion-datos-mineduc`: obtención/registro reproducible de CSV crudos y metadatos de fuente.
- `consolidacion-cruda`: unión sin limpieza con trazabilidad por archivo y departamento.
- `diagnostico-calidad-cruda`: generación de métricas y tablas diagnósticas previas a transformación.

### Modificadas
- Ninguna; no existen specs vigentes en `openspec/specs/`.

## Enfoque

Usar scripts pequeños y reproducibles. La cobertura será la realmente disponible desde MINEDUC y deberá documentar cualquier alcance no disponible. Para dominios territoriales, preferir catálogos oficiales de departamentos/municipios si están accesibles. TDD estricto queda deseado, pero no exigible hasta que exista stack ejecutable y comando de pruebas.

## Áreas afectadas

| Área | Impacto | Descripción |
|---|---|---|
| `pyproject.toml` | Nuevo | Dependencias y comandos futuros. |
| `src/proyecto1_ds/`, `scripts/` | Nuevo | Lógica y entradas ejecutables. |
| `data/raw/`, `data/interim/` | Nuevo | Datos crudos e intermedios. |
| `outputs/tablas/` | Nuevo | Tablas diagnósticas generadas. |
| `docs/diagnostico.md` | Nuevo | Entregable diagnóstico prioritario. |

## Riesgos

| Riesgo | Prob. | Mitigación |
|---|---|---|
| MINEDUC bloquea scraping o no exporta CSV. | Media | Reportar fallo y permitir fallback manual trazable. |
| Cobertura nacional incompleta. | Media | Documentar disponibilidad real y faltantes. |
| Esquemas CSV incompatibles. | Media | Diagnosticar diferencias sin corregir datos. |

## Plan de reversión

Revertir los commits del bootstrap y regenerar salidas desde CSV crudos. Como la limpieza está fuera de alcance, no habrá transformaciones destructivas sobre datos fuente.

## Dependencias

- Acceso real a MINEDUC o CSV crudos descargados manualmente.
- Catálogos oficiales de departamentos/municipios si están disponibles.
- Definición posterior del stack y comando de pruebas para habilitar TDD estricto.

## Criterios de éxito

- [ ] `docs/diagnostico.md` existe y sus tablas provienen de código.
- [ ] Cada registro consolidado conserva archivo y departamento de origen.
- [ ] La versión del dataset y fecha de extracción están documentadas.
- [ ] La limpieza queda explícitamente diferida.
