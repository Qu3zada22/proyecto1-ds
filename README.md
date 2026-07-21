# Proyecto 1 — Calidad de datos de establecimientos educativos


- [Anggie: `7bac6048f68a116b30e93a65eedc4dcf87412407`](https://github.com/Qu3zada22/proyecto1-ds/commit/7bac6048f68a116b30e93a65eedc4dcf87412407), sección del Code Book de 17 variables.
- [Iris: `bdf87360b4fa7081dac347f373d6a739dc262c2e`](https://github.com/Qu3zada22/proyecto1-ds/commit/bdf87360b4fa7081dac347f373d6a739dc262c2e), sección de variables territoriales.
- La evidencia real adicional de los tres integrantes está inventariada en [`docs/auditoria_final.md`](docs/auditoria_final.md).


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
