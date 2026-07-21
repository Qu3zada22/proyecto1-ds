# Proyecto 1 — Calidad de datos de establecimientos educativos


> **Repositorio:** [github.com/Qu3zada22/proyecto1-ds](https://github.com/Qu3zada22/proyecto1-ds)
>
> **Estado:** avance parcial
>
> **Fecha de corte:** 20 de julio de 2026

## Resumen ejecutivo

El proyecto parte de 23 consultas oficiales del MINEDUC conservadas como HTML. A partir de ellas se genera una fuente consolidada nacional, se ejecuta un diagnóstico de calidad y se produce un dataset limpio mediante reglas conservadoras y trazables.

El avance actual incluye:

- procedencia verificable mediante HTML oficiales, manifest y checksums;
- fuente consolidada canónica con 11,867 establecimientos;
- diagnóstico reproducible por variable;
- normalización de texto y categorías (mayúsculas, caracteres invisibles/NFC y marcadores de ausencia) con bitácora;
- catálogo territorial reproducible desde un espejo/conversión comunitaria fijado, con INE, Censo 2018 como fuente primaria declarada;
- variables derivadas con códigos del catálogo territorial, más corrección trazable de 2 variantes tipográficas;
- detección y triage reproducible de duplicados parciales por similitud (RapidFuzz), sin borrado automático;
- recomendaciones reproducibles para los pendientes de duplicados, teléfonos y territorio, sin aplicar cambios;
- validación final reproducible de siete controles, con 3 `cumple`, 4 `requiere_revision` y 0 `falla`;
- comparación antes/después y reportes de trazabilidad;
- Code Book maestro reproducible en Markdown y PDF para las 21 variables;
- auditoría interna de materiales, hashes, contribuciones y bloqueos;
- planificación explícita del trabajo pendiente y sus responsables.

La salida limpia actual sigue siendo una **versión parcial** y el proyecto permanece **NO APTO PARA CIERRE INSTITUCIONAL**. La aprobación versionada dejó 11 pares como `independiente_confirmado`, sin fusión ni borrado, y aplicó 6 normalizaciones telefónicas exactas. Permanecen 978 pares pendientes (718 `duplicado_probable` + 260 `revisar`), 245 teléfonos sospechosos y 145 filas territoriales. Las recomendaciones restantes no equivalen a aprobación institucional.

## Cinco entregables

| Material exigido | Ubicación | Regeneración o evidencia |
|---|---|---|
| Código fuente del pipeline | [`pipeline_limpieza.py`](pipeline_limpieza.py) | `uv run python pipeline_limpieza.py` ejecuta los CLI existentes desde la consolidación hasta la validación, los reportes y el Code Book. |
| Repositorio | [github.com/Qu3zada22/proyecto1-ds](https://github.com/Qu3zada22/proyecto1-ds) | Contiene código, datos, pruebas, procedencia y documentación versionada. |
| Área de trabajo del Code Book | [`docs/code_book.md`](docs/code_book.md) | `uv run python scripts/generar_code_book.py`, desde las secciones editables en `docs/code_book/`. |
| Documento PDF | [`docs/code_book.pdf`](docs/code_book.pdf) | `uv run python scripts/generar_code_book_pdf.py`, a partir del Markdown generado. |
| Data limpia | [`data/processed/establecimientos_diversificado_limpio.csv`](data/processed/establecimientos_diversificado_limpio.csv) | `uv run python scripts/limpiar_dataset.py`, desde la fuente canónica y el catálogo versionado. |

No existe un Google Docs asociado a esta entrega. La rúbrica acepta Google Docs **o** un archivo Markdown; por ello, `docs/code_book.md` versionado en GitHub es el área de trabajo entregada. La colaboración se acredita con commits publicados, sin reinterpretar su autoría:

- [Anggie: `7bac6048f68a116b30e93a65eedc4dcf87412407`](https://github.com/Qu3zada22/proyecto1-ds/commit/7bac6048f68a116b30e93a65eedc4dcf87412407), sección del Code Book de 17 variables.
- [Iris: `bdf87360b4fa7081dac347f373d6a739dc262c2e`](https://github.com/Qu3zada22/proyecto1-ds/commit/bdf87360b4fa7081dac347f373d6a739dc262c2e), sección de variables territoriales.
- La evidencia real adicional de los tres integrantes está inventariada en [`docs/auditoria_final.md`](docs/auditoria_final.md).

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
| Duplicados (`duplicado_probable` / `independiente` / `revisar` / `independiente_confirmado`) | 718 / 366 / 260 / 11 |
| Inconsistencias territoriales documentadas | 7 |
| Filas en esas parejas, con `decision=revisar` | 145 |
| Teléfonos sospechosos vigentes (no vacíos distintos de 8 dígitos exactos) | 245 |
| Hallazgos telefónicos históricos agregados del diagnóstico inicial | 201 |
| HTML oficiales preservados | 23 |

El dataset limpio parte de 20 columnas, elimina la columna vacía `<NBSP>` (queda en 19) y agrega dos variables derivadas (`departamento_codigo` y `municipio_codigo`), llegando a 21. No se eliminaron establecimientos. Se corrigieron 2 variantes tipográficas en 19 filas; 7 parejas territoriales (145 filas) siguen explícitamente en revisión.

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
| `data/processed/establecimientos_diversificado_limpio.csv` | Dataset limpio y enriquecido con códigos derivados del catálogo. |
| `data/reference/catalogo_territorial.csv` | Catálogo derivado de un espejo comunitario fijado; INE, Censo 2018 es la fuente primaria declarada. |
| `data/raw/manifest.json` | Inventario, cobertura y checksums de las fuentes. |
| `data/decisions/duplicados_aprobados.csv` | Once decisiones explícitas `independiente_confirmado`. |
| `data/decisions/telefonos_aprobados.csv` | Seis normalizaciones telefónicas exactas aprobadas. |
| `docs/fuentes_datos.md` | Explicación detallada de la adquisición y procedencia. |
| `docs/diagnostico.md` | Diagnóstico inicial de calidad. |
| `docs/plan_limpieza.md` | Reglas y riesgos definidos antes de transformar. |
| `docs/planificacion.md` | Matriz autoritativa de requisitos, pendientes y responsables. |
| `docs/code_book.md` | Code Book maestro generado para las 21 variables. |
| `docs/code_book.pdf` | PDF definitivo generado y validado desde el maestro Markdown. |
| `docs/auditoria_final.md` | Recibo interno de auditoría; no sustituye un material exigido. |
| `docs/reconciliacion_anggie.md` | Comparación con la fuente secundaria del equipo. |
| `outputs/tablas/bitacora_limpieza.csv` | Transformaciones aplicadas y filas afectadas. |
| `outputs/tablas/reporte_limpieza_base.csv` | Evidencia intermedia emitida atómicamente por la limpieza. |
| `outputs/tablas/reporte_calidad_antes_despues.csv` | Reporte integral final de exactamente 10 métricas. |
| `outputs/tablas/duplicados_parciales.csv` | Candidatos a duplicado parcial para revisión humana. |
| `outputs/tablas/inconsistencias_territoriales.csv` | Parejas departamento–municipio a revisar contra el catálogo. |
| `outputs/tablas/recomendaciones_duplicados.csv` | Recomendación conservadora para cada uno de los 978 pares pendientes. |
| `outputs/tablas/recomendaciones_telefonos.csv` | Clasificación de los 245 teléfonos todavía sospechosos. |
| `outputs/tablas/recomendaciones_territorio.csv` | Siete aliases auditables que representan 145 filas, sin renombre automático. |
| `outputs/tablas/validacion_final.csv` | Resultado reproducible de los siete controles finales. |
| `outputs/reportes/duplicados_parciales.md` | Método y resumen de la detección de duplicados. |
| `outputs/reportes/validacion_territorial.md` | Método y resumen de la validación territorial. |
| `outputs/reportes/migracion_fuente.md` | Evidencia de integridad de la fuente canónica. |
| `outputs/reportes/revision_pendientes.md` | Resumen legible de reglas, conteos y límites institucionales. |

## Reproducibilidad

### Requisitos

- Python 3.11 o superior.
- [`uv`](https://docs.astral.sh/uv/) para administrar el entorno y las dependencias.
- Pandoc, Chromium, qpdf, pdfinfo y pdftotext para generar y validar el PDF.

### Ejecución

```bash
# Preparar el entorno
uv sync

# Ejecutar el pipeline completo con el catálogo territorial versionado
uv run python pipeline_limpieza.py

# Si se desea reconstruir también el catálogo desde el espejo fijado (requiere red)
uv run python pipeline_limpieza.py --regenerar-catalogo

# Omitir únicamente el PDF si no están instaladas sus herramientas externas
uv run python pipeline_limpieza.py --sin-pdf
```

El orquestador se debe ejecutar desde la raíz del repositorio, se detiene ante el primer error y no duplica lógica de negocio. Regenerar artefactos no resuelve ni aprueba los 978 pares, 245 teléfonos o 145 filas territoriales pendientes.

Los comandos individuales siguen disponibles para reproducir o diagnosticar una etapa concreta:

```bash

# Reconstruir el CSV canónico desde los HTML
uv run python scripts/consolidar_crudos.py

# Regenerar el diagnóstico
uv run python scripts/diagnosticar_crudos.py

# Generar el catálogo territorial reproducible — requerido por la limpieza
uv run python scripts/generar_catalogo_territorial.py

# Regenerar el dataset limpio y enriquecido (normalización + códigos INE)
uv run python scripts/limpiar_dataset.py

# Detectar duplicados parciales (sin borrado automático)
uv run python scripts/detectar_duplicados.py

# Aplicar/confirmar el triage y actualizar la bitácora idempotentemente
uv run python scripts/decidir_duplicados.py

# Validar consistencia departamento–municipio contra el catálogo
uv run python scripts/validar_territorio.py

# Generar recomendaciones sin modificar ni fusionar datasets
uv run python scripts/revisar_pendientes.py

# Ejecutar los siete controles finales
uv run python scripts/validar_dataset.py

# Generar las 10 métricas de rúbrica y el resumen de pendientes
uv run python scripts/generar_reporte_calidad.py

# Ensamblar el Code Book maestro Markdown
uv run python scripts/generar_code_book.py

# Generar y validar el PDF definitivo
uv run python scripts/generar_code_book_pdf.py

```

Las transformaciones pertenecen a `src/proyecto1_ds/`; los archivos de `scripts/` son interfaces de línea de comandos. Los CSV y reportes generados no deben editarse manualmente. La limpieza depende del catálogo territorial, así que ejecútalo antes de `limpiar_dataset.py`.

## Limpieza aplicada

La limpieza utiliza reglas deterministas y trazables:

1. normalización de espacios, NBSP y caracteres invisibles/de control (Unicode NFC);
2. canonización a mayúsculas del texto y las categorías, preservando las tildes;
3. conversión de marcadores inequívocos de ausencia a un vacío consistente;
4. eliminación de la columna `<NBSP>` únicamente porque está completamente vacía;
5. validación territorial contra el catálogo reproducible y corrección trazable de 2 variantes tipográficas;
6. variables derivadas `departamento_codigo` y `municipio_codigo` (códigos INE) para habilitar cruces;
7. preservación de códigos, teléfonos y otros identificadores como texto;
8. conservación de nombres, direcciones y valores ambiguos cuando no existe evidencia suficiente para corregirlos.

Cada transformación queda registrada en la bitácora. La implementación de reglas y triage está completada; 11 pares fueron aprobados como independientes y los 260 ambiguos restantes conservan revisión institucional/manual pendiente.

## Estado frente a los requisitos

La evaluación detallada se encuentra en [`docs/planificacion.md`](docs/planificacion.md).

| Estado | Requisitos |
|---|---:|
| Completados | 23 |
| Parciales | 6 |
| Faltantes | 0 |
| Inciertos | 0 |
| **Total auditado** | **29** |

No quedan requisitos `Faltante`, pero seis permanecen `Parcial`. La automatización no equivale a aceptación: R5e, R5f, R5g, R7, R9 y RE conservan decisiones institucionales pendientes. RT está completado por el historial publicado y las secciones del Code Book.

## Organización del equipo

| Integrante | Responsabilidad siguiente |
|---|---|
| **Anggie** | Reglas y triage implementados; 11 independientes y 6 teléfonos aprobados; faltan 718 probables, 260 ambiguos y 245 teléfonos. |
| **Iris** | Hecho: catálogo reproducible, consistencia departamento–municipio, normalización, códigos derivados y Code Book territorial de 4 variables. |
| **Jonathan** | Validación, reporte, Code Book Markdown/PDF y auditoría interna publicados en la integración `c871bd7`. |

Cada integrante cuenta con commits identificables publicados y una sección concreta del Code Book.

## Trabajo pendiente

- obtener fuente institucional para los 978 pares pendientes; los 11 independientes aprobados permanecen separados;
- revisar institucionalmente los 245 teléfonos restantes; las 6 normalizaciones exactas ya fueron aplicadas;
- aceptar formalmente los aliases de las 145 filas territoriales; el texto MINEDUC permanece sin renombre;

Ya está hecho en el alcance de Iris: catálogo territorial reproducible, normalización, validación departamento–municipio, códigos derivados y documentación de 4 variables. El espejo no es una publicación primaria oficial; INE, Censo 2018 es la fuente primaria declarada.

## Alcance de esta entrega parcial

Esta entrega demuestra que la adquisición, consolidación, diagnóstico y limpieza conservadora inicial son reproducibles. No presenta todavía el dataset como una versión final sin errores.

Para convertir este README en PDF se puede abrir su vista renderizada en GitHub y usar **Imprimir → Guardar como PDF**. Así se conservan los encabezados, tablas, enlaces y bloques de código sin requerir herramientas adicionales.

## Documentación complementaria

- [Instrucciones del proyecto](docs/instrucciones.md)
- [Fuentes de datos](docs/fuentes_datos.md)
- [Diagnóstico](docs/diagnostico.md)
- [Plan de limpieza](docs/plan_limpieza.md)
- [Planificación y asignaciones](docs/planificacion.md)
- [Auditoría interna de entrega](docs/auditoria_final.md)
- [Reconciliación de la fuente secundaria](docs/reconciliacion_anggie.md)
