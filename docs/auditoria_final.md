# Auditoría final de entrega

**RECIBO INTERNO.** Este documento no es un sexto material exigido por el curso. Registra cómo verificar los cinco materiales, la contribución del equipo y los bloqueos que la automatización no puede resolver.

**Resultado actual: NO APTO PARA CIERRE INSTITUCIONAL.** Se aprobaron 11 pares independientes y 6 normalizaciones telefónicas exactas, pero 978 pares, 245 teléfonos y 145 filas territoriales siguen pendientes; R5e, R5f, R5g, R7, R9 y RE permanecen parciales. Los 201 hallazgos históricos agregados son solo una referencia y no permiten correspondencia registro por registro.

## Materiales exigidos

| Material | Ruta o referencia | Hash/evidencia | Estado |
|---|---|---|---|
| Código fuente | `src/proyecto1_ds/`, `scripts/` | Suite completa: 218 pruebas; `git diff --check` sin errores | Publicado en `c871bd7`. |
| Repositorio | [github.com/Qu3zada22/proyecto1-ds](https://github.com/Qu3zada22/proyecto1-ds) | HEAD local/remoto `c871bd787ecc3cea6b9c29064b0414ae38f71f4f` | Disponible; integración publicada. |
| Área de trabajo | `docs/code_book.md` | SHA-256 `c18e1caa2a5825bd695e9c550b5e94cf2a5f18d77a3055df80f2c45b9b4de7b9` | Completo: 21 variables. |
| Documento PDF | `docs/code_book.pdf` | SHA-256 `acc66d84ed15d28352c10407c3295f76d00014c1a0c5eeb21dd0e3729a5bc327` | Completo: 13 páginas carta, texto extraíble, un título y hash del Markdown. |
| Data limpia | `data/processed/establecimientos_diversificado_limpio.csv` | SHA-256 `86e411c5f6f11f2af67b2d1dddf199f17ddc5a7fd9b429347bb38dde9e17d521` | Disponible; aceptación institucional pendiente. |

## Evidencia automatizada

| Control | Resultado |
|---|---|
| Matriz | 23 `Completado`, 6 `Parcial`, 0 `Faltante`, 0 `Incierto`. |
| Pruebas | 218 pruebas pasan sin caché ni bytecode. |
| Validación | Exactamente 7 controles: 3 `cumple`, 4 `requiere_revision`, 0 `falla`. |
| Reporte | Exactamente 10 métricas de rúbrica; no agrega una undécima fila artificial. |
| Regeneración | Esta remediación regeneró por CLI exactamente 4 artefactos finales: validación, reporte integral, Code Book Markdown y PDF. |
| PDF | qpdf válido; 13 páginas `letter`; texto extraíble; un título; 17 secciones Anggie y 4 Iris. |
| Contratos | Limpieza publica `reporte_limpieza_base.csv`; el integral se conserva hasta su generador final. |
| Linaje | Validación recomputa duplicados y territorio; el diagnóstico se identifica como histórico de la fuente. |
| Reporte base | SHA-256 `9e97b1f6d7007e90b8a40ffa14466f01ad1a9b4df199fb6c6606c400210b4475`. |

## Contribuciones Git reales

| Integrante | Commits comprobados | Aporte visible |
|---|---|---|
| Anggie | `b8eb3de`, `7bac604`, `b8bf54e` | Triage, 17 variables del Code Book y actualización documental. |
| Iris (`AleWWH1104`) | `a2ecc37`, `b314998`, `bdf8736` | Normalización, territorio/códigos y 4 variables territoriales. |
| Jonathan (`jonialen`) | `6dab5c4`, `1811f3d`, `e7103a1`, `c8bbf3f`, `c871bd7` | Limpieza base, CLI, fuente canónica e integración final de artefactos reproducibles. |

**RT satisfecho.** Anggie, Iris y Jonathan tienen commits identificables publicados y aportes visibles en las secciones del Code Book; `c871bd7` acredita la integración final de Jonathan.

## Bloqueos manuales

| Requisito | Pendiente no automatizable |
|---|---|
| R5e | Aceptar o resolver 245 teléfonos sospechosos vigentes; 6 reglas exactas ya fueron aplicadas y 201 sigue siendo histórico agregado. |
| R5f | Aceptar o resolver 145 filas territoriales con códigos provisionales, además del pendiente telefónico. |
| R5g | Confirmar 718 pares `duplicado_probable` y revisar 260 ambiguos; 11 independientes ya fueron aprobados sin fusión. |
| R7 | Resolver o aceptar formalmente los cuatro controles en `requiere_revision`. |
| R9 | Aceptar institucionalmente el CSV como dataset final; automatización y archivo único no bastan. |
| RE | Reevaluar los cinco materiales cuando R9 tenga aceptación institucional. |

## Comandos de reproducción

```bash
uv sync
uv run python scripts/detectar_duplicados.py
uv run python scripts/decidir_duplicados.py
uv run python scripts/validar_territorio.py
uv run python scripts/validar_dataset.py
uv run python scripts/generar_reporte_calidad.py
uv run python scripts/generar_code_book.py
uv run python scripts/generar_code_book_pdf.py
PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider
qpdf --check docs/code_book.pdf
pdfinfo docs/code_book.pdf
pdftotext docs/code_book.pdf -
sha256sum docs/code_book.md docs/code_book.pdf data/processed/establecimientos_diversificado_limpio.csv
git diff --check
git ls-remote origin HEAD
```

El catálogo y el dataset limpio no se regeneraron durante este cierre porque ningún cambio afectó sus reglas o insumos. Los outputs posteriores sí se regeneraron exclusivamente mediante sus CLI.
