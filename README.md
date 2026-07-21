# Proyecto 1 — Limpieza de datos educativos

Este proyecto procesa los establecimientos educativos de nivel Diversificado publicados por el MINEDUC de Guatemala. El pipeline consolida los datos oficiales, diagnostica su calidad, aplica reglas de limpieza trazables y genera el CSV limpio y el Code Book.

## Requisitos

- Python 3.11 o superior.
- [`uv`](https://docs.astral.sh/uv/) para instalar y ejecutar las dependencias.
- Pandoc, Chromium, qpdf, pdfinfo y pdftotext para generar y validar el PDF.

## Cómo ejecutarlo

Desde la raíz del repositorio:

```bash
uv sync
uv run python pipeline_limpieza.py
```

El pipeline genera los principales entregables:

- CSV limpio: `data/processed/establecimientos_diversificado_limpio.csv`
- Code Book: `docs/code_book.md`
- Code Book PDF: `docs/code_book.pdf`

Si no están instaladas las herramientas requeridas para generar el PDF:

```bash
uv run python pipeline_limpieza.py --sin-pdf
```

Para reconstruir también el catálogo territorial desde su fuente fijada —requiere conexión a internet—:

```bash
uv run python pipeline_limpieza.py --regenerar-catalogo
```
