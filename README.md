# Proyecto 1 — Calidad de datos de establecimientos educativos

Proceso reproducible para obtener, consolidar, diagnosticar y limpiar los establecimientos educativos de nivel **Diversificado** publicados por el Ministerio de Educación de Guatemala (MINEDUC).

> **Repositorio:** [github.com/Qu3zada22/proyecto1-ds](https://github.com/Qu3zada22/proyecto1-ds)
>
> **Estado:** avance parcial verificable
>
> **Fecha de corte:** 16 de julio de 2026

## Resumen ejecutivo

El proyecto parte de 23 consultas oficiales del MINEDUC conservadas como HTML. A partir de ellas se genera una fuente consolidada nacional, se ejecuta un diagnóstico de calidad y se produce un dataset limpio mediante reglas conservadoras y trazables.

El avance actual incluye:

- procedencia verificable mediante HTML oficiales, manifest y checksums;
- fuente consolidada canónica con 11,867 establecimientos;
- diagnóstico reproducible por variable;
- limpieza inicial de espacios, caracteres invisibles y marcadores inequívocos de ausencia;
- bitácora de transformaciones y comparación antes/después;
- 109 pruebas automatizadas aprobadas;
- planificación explícita del trabajo pendiente y sus responsables.

La salida limpia actual es una **versión parcial**. Todavía no se declara libre de todos los problemas porque faltan decisiones territoriales, revisión de teléfonos, duplicados parciales y validación final integral.

## Resultados actuales

| Resultado | Valor |
|---|---:|
| Registros de la fuente canónica | 11,867 |
| Columnas de la fuente canónica | 20 |
| Códigos únicos | 11,867 |
| Registros del dataset limpio | 11,867 |
| Columnas del dataset limpio | 19 |
| HTML oficiales preservados | 23 |
| Pruebas automatizadas | 109 aprobadas |

La reducción de 20 a 19 columnas se debe a la eliminación trazable de la columna `<NBSP>`, que estaba completamente vacía. No se eliminaron establecimientos.

## Fuente y procedencia

La información proviene del portal oficial de búsqueda de establecimientos del MINEDUC:

- [Búsqueda de establecimientos — MINEDUC](https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/)

No se encontró un CSV oficial descargable directamente. Por eso se conservaron las respuestas HTML por territorio y se construyó un CSV consolidado mediante código.

```text
23 HTML oficiales + data/raw/manifest.json
                    │
                    ▼
data/source/establecimientos_diversificado_mineduc.csv
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
Diagnóstico y tablas   data/processed/establecimientos_diversificado_limpio.csv
                                │
                                ▼
                       Bitácora y reporte de calidad
```

Los HTML no se eliminan después de generar el CSV: son la evidencia que permite reconstruirlo y auditar su origen.

## Archivos principales del avance

| Archivo | Contenido |
|---|---|
| `data/source/establecimientos_diversificado_mineduc.csv` | Fuente consolidada canónica generada desde los HTML. |
| `data/processed/establecimientos_diversificado_limpio.csv` | Dataset limpio preliminar. |
| `data/raw/manifest.json` | Inventario, cobertura y checksums de las fuentes. |
| `docs/fuentes_datos.md` | Explicación detallada de la adquisición y procedencia. |
| `docs/diagnostico.md` | Diagnóstico inicial de calidad. |
| `docs/plan_limpieza.md` | Reglas y riesgos definidos antes de transformar. |
| `docs/planificacion.md` | Matriz autoritativa de requisitos, pendientes y responsables. |
| `docs/reconciliacion_anggie.md` | Comparación con la fuente secundaria del equipo. |
| `outputs/tablas/bitacora_limpieza.csv` | Transformaciones aplicadas y filas afectadas. |
| `outputs/tablas/reporte_calidad_antes_despues.csv` | Comparación preliminar antes/después. |
| `outputs/reportes/migracion_fuente.md` | Evidencia de integridad de la fuente canónica. |

## Reproducibilidad

### Requisitos

- Python 3.11 o superior.
- [`uv`](https://docs.astral.sh/uv/) para administrar el entorno y las dependencias.

### Ejecución

```bash
# Preparar el entorno
uv sync

# Reconstruir el CSV canónico desde los HTML
uv run python scripts/consolidar_crudos.py

# Regenerar el diagnóstico
uv run python scripts/diagnosticar_crudos.py

# Regenerar el dataset limpio y sus reportes
uv run python scripts/limpiar_dataset.py

# Verificar el proyecto
uv run pytest
```

Las transformaciones pertenecen a `src/proyecto1_ds/`; los archivos de `scripts/` son interfaces de línea de comandos. Los CSV y reportes generados no deben editarse manualmente.

## Limpieza aplicada

La primera etapa de limpieza utiliza reglas de bajo riesgo:

1. normalización de espacios y caracteres NBSP;
2. conversión de marcadores inequívocos de ausencia a un vacío consistente;
3. eliminación de la columna `<NBSP>` únicamente porque está completamente vacía;
4. preservación de códigos, teléfonos y otros identificadores como texto;
5. conservación de nombres, direcciones y valores ambiguos cuando no existe evidencia suficiente para corregirlos.

Cada transformación queda registrada en la bitácora. Las decisiones que requieren catálogo oficial o revisión humana permanecen explícitamente pendientes.

## Estado frente a los requisitos

La evaluación detallada se encuentra en [`docs/planificacion.md`](docs/planificacion.md).

| Estado | Requisitos |
|---|---:|
| Completados | 12 |
| Parciales | 11 |
| Faltantes | 5 |
| Inciertos | 1 |
| **Total auditado** | **29** |

## Organización del equipo

| Integrante | Responsabilidad siguiente |
|---|---|
| **Anggie** | Reconciliación de fuentes, candidatos a duplicados parciales, excepciones telefónicas, bitácora y sección de procedencia del Code Book. |
| **Iris** | Catálogo territorial versionado, consistencia departamento–municipio, dominios y documentación de variables derivadas. |
| **Jonathan** | Integración, validación final, reporte completo, documentación del flujo, Code Book Markdown/PDF y auditoría de entrega. |

Cada integrante debe aportar commits identificables y una sección concreta del Code Book.

## Trabajo pendiente

- validar departamentos y municipios con un catálogo oficial versionado;
- revisar candidatos a duplicados parciales sin eliminarlos automáticamente;
- resolver excepciones telefónicas y otros formatos ambiguos;
- ejecutar la validación automática final de toda la rúbrica;
- completar el reporte narrativo de calidad antes/después;
- construir el Code Book de las 19 variables y exportarlo a PDF;
- realizar la auditoría final de entrega y contribuciones del equipo.

## Alcance de esta entrega parcial

Esta entrega demuestra que la adquisición, consolidación, diagnóstico y limpieza conservadora inicial son reproducibles. No presenta todavía el dataset como una versión final sin errores.

Para convertir este README en PDF se puede abrir su vista renderizada en GitHub y usar **Imprimir → Guardar como PDF**. Así se conservan los encabezados, tablas, enlaces y bloques de código sin requerir herramientas adicionales.

## Documentación complementaria

- [Instrucciones del proyecto](docs/instrucciones.md)
- [Fuentes de datos](docs/fuentes_datos.md)
- [Diagnóstico](docs/diagnostico.md)
- [Plan de limpieza](docs/plan_limpieza.md)
- [Planificación y asignaciones](docs/planificacion.md)
- [Reconciliación de la fuente secundaria](docs/reconciliacion_anggie.md)
