# Proyecto 1 — Calidad de datos de establecimientos educativos


> **Repositorio:** [github.com/Qu3zada22/proyecto1-ds](https://github.com/Qu3zada22/proyecto1-ds)
>
> **Estado:** avance parcial
>
> **Fecha de corte:** 16 de julio de 2026

## Resumen ejecutivo

El proyecto parte de 23 consultas oficiales del MINEDUC conservadas como HTML. A partir de ellas se genera una fuente consolidada nacional, se ejecuta un diagnóstico de calidad y se produce un dataset limpio mediante reglas conservadoras y trazables.

El avance actual incluye:

- procedencia verificable mediante HTML oficiales, manifest y checksums;
- fuente consolidada canónica con 11,867 establecimientos;
- diagnóstico reproducible por variable;
- normalización de texto y categorías (mayúsculas, caracteres invisibles/NFC y marcadores de ausencia) con bitácora;
- catálogo territorial oficial (INE, Censo 2018) versionado y validación de consistencia departamento–municipio;
- variables derivadas con códigos oficiales INE de departamento y municipio, más corrección trazable de 2 typos;
- detección de duplicados parciales por similitud (RapidFuzz), sin borrado automático;
- comparación antes/después y reportes de trazabilidad;
- planificación explícita del trabajo pendiente y sus responsables.

La salida limpia actual sigue siendo una **versión parcial**. Todavía no se declara libre de todos los problemas porque faltan la revisión humana de los duplicados candidatos, las excepciones telefónicas, la validación automática final y el Code Book.

## Resultados actuales

| Resultado | Valor |
|---|---:|
| Registros de la fuente canónica | 11,867 |
| Columnas de la fuente canónica | 20 |
| Códigos únicos | 11,867 |
| Registros del dataset limpio | 11,867 |
| Columnas del dataset limpio | 21 |
| Municipios del catálogo oficial (INE) | 340 |
| Candidatos a duplicado parcial (para revisión) | 1,355 |
| Inconsistencias territoriales documentadas | 7 |
| HTML oficiales preservados | 23 |

El dataset limpio parte de 20 columnas, elimina la columna vacía `<NBSP>` (queda en 19) y agrega dos variables derivadas (`departamento_codigo` y `municipio_codigo`), llegando a 21. No se eliminaron establecimientos.

## Fuente y procedencia

La información proviene del portal oficial de búsqueda de establecimientos del MINEDUC:

- [Búsqueda de establecimientos — MINEDUC](https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/)

No se encontró un CSV oficial descargable directamente. Por eso se conservaron las respuestas HTML por territorio y se construyó un CSV consolidado mediante código.

```text
23 HTML oficiales + data/raw/manifest.json        data/reference/catalogo_territorial.csv (INE)
                    │                                             │
                    ▼                                             │
data/source/establecimientos_diversificado_mineduc.csv           │
                    │                                             │
          ┌─────────┴─────────┐                                  │
          ▼                   ▼                                  ▼
Diagnóstico y tablas   data/processed/establecimientos_diversificado_limpio.csv
                                │
                ┌───────────────┼───────────────────┐
                ▼               ▼                   ▼
     Bitácora y reporte   Duplicados parciales   Validación territorial
       antes/después       (candidatos)          (inconsistencias)
```

Los HTML no se eliminan después de generar el CSV: son la evidencia que permite reconstruirlo y auditar su origen.

## Archivos principales del avance

| Archivo | Contenido |
|---|---|
| `data/source/establecimientos_diversificado_mineduc.csv` | Fuente consolidada canónica generada desde los HTML. |
| `data/processed/establecimientos_diversificado_limpio.csv` | Dataset limpio y enriquecido con códigos oficiales. |
| `data/reference/catalogo_territorial.csv` | Catálogo territorial oficial (INE, Censo 2018): departamentos y municipios con códigos. |
| `data/raw/manifest.json` | Inventario, cobertura y checksums de las fuentes. |
| `docs/fuentes_datos.md` | Explicación detallada de la adquisición y procedencia. |
| `docs/diagnostico.md` | Diagnóstico inicial de calidad. |
| `docs/plan_limpieza.md` | Reglas y riesgos definidos antes de transformar. |
| `docs/planificacion.md` | Matriz autoritativa de requisitos, pendientes y responsables. |
| `docs/reconciliacion_anggie.md` | Comparación con la fuente secundaria del equipo. |
| `outputs/tablas/bitacora_limpieza.csv` | Transformaciones aplicadas y filas afectadas. |
| `outputs/tablas/reporte_calidad_antes_despues.csv` | Comparación antes/después. |
| `outputs/tablas/duplicados_parciales.csv` | Candidatos a duplicado parcial para revisión humana. |
| `outputs/tablas/inconsistencias_territoriales.csv` | Parejas departamento–municipio a revisar contra el catálogo. |
| `outputs/reportes/duplicados_parciales.md` | Método y resumen de la detección de duplicados. |
| `outputs/reportes/validacion_territorial.md` | Método y resumen de la validación territorial. |
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

# Generar el catálogo territorial oficial (INE) — requerido por la limpieza
uv run python scripts/generar_catalogo_territorial.py

# Regenerar el dataset limpio y enriquecido (normalización + códigos INE)
uv run python scripts/limpiar_dataset.py

# Detectar duplicados parciales (sin borrado automático)
uv run python scripts/detectar_duplicados.py

# Validar consistencia departamento–municipio contra el catálogo
uv run python scripts/validar_territorio.py
```

Las transformaciones pertenecen a `src/proyecto1_ds/`; los archivos de `scripts/` son interfaces de línea de comandos. Los CSV y reportes generados no deben editarse manualmente. La limpieza depende del catálogo territorial, así que ejecútalo antes de `limpiar_dataset.py`.

## Limpieza aplicada

La limpieza utiliza reglas deterministas y trazables:

1. normalización de espacios, NBSP y caracteres invisibles/de control (Unicode NFC);
2. canonización a mayúsculas del texto y las categorías, preservando las tildes;
3. conversión de marcadores inequívocos de ausencia a un vacío consistente;
4. eliminación de la columna `<NBSP>` únicamente porque está completamente vacía;
5. validación territorial contra el catálogo oficial y corrección trazable de 2 typos de municipio;
6. variables derivadas `departamento_codigo` y `municipio_codigo` (códigos INE) para habilitar cruces;
7. preservación de códigos, teléfonos y otros identificadores como texto;
8. conservación de nombres, direcciones y valores ambiguos cuando no existe evidencia suficiente para corregirlos.

Cada transformación queda registrada en la bitácora. Las decisiones que requieren revisión humana (duplicados candidatos, teléfonos) permanecen explícitamente pendientes.

## Estado frente a los requisitos

La evaluación detallada se encuentra en [`docs/planificacion.md`](docs/planificacion.md).

| Estado | Requisitos |
|---|---:|
| Completados | 16 |
| Parciales | 10 |
| Faltantes | 3 |
| Inciertos | 0 |
| **Total auditado** | **29** |

Los tres faltantes son la validación automática final (7 controles), el Code Book (+PDF) y el ensamblaje del material de entrega.

## Organización del equipo

| Integrante | Responsabilidad siguiente |
|---|---|
| **Anggie** | Reconciliación de fuentes, candidatos a duplicados parciales, excepciones telefónicas, bitácora y sección de procedencia del Code Book. |
| **Iris** | Hecho: catálogo territorial INE versionado, consistencia departamento–municipio, dominios, normalización de texto/categorías, códigos oficiales y detección de duplicados. Sigue: documentar sus variables (incl. derivadas) en el Code Book. |
| **Jonathan** | Integración, validación final, reporte completo, documentación del flujo, Code Book Markdown/PDF y auditoría de entrega. |

Cada integrante debe aportar commits identificables y una sección concreta del Code Book.

## Trabajo pendiente

- revisar los candidatos a duplicados parciales y registrar la decisión de cada caso;
- resolver excepciones telefónicas y otros formatos ambiguos;
- ejecutar la validación automática final de toda la rúbrica (7 controles);
- completar el reporte narrativo de calidad antes/después (10 métricas);
- construir el Code Book de las 21 variables y exportarlo a PDF;
- realizar la auditoría final de entrega y contribuciones del equipo.

Ya está hecho: catálogo territorial oficial, normalización de texto/categorías, validación departamento–municipio, códigos oficiales INE como variables derivadas y detección de duplicados parciales.

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
