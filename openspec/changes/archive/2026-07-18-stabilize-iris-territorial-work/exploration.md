## Exploration: Estabilizar el trabajo territorial de Iris

### Current State
Los commits `a2ecc37`, `b314998` y `bdf8736` integraron normalización, enriquecimiento y documentación territorial. El dataset limpio ya tiene 11,867 filas y 21 columnas; sin embargo, `uv run pytest` arroja 101 aprobadas y 8 fallidas. No hay pruebas dedicadas para catálogo, enriquecimiento ni validación territorial. Las 7 parejas territoriales pendientes abarcan 145 filas y permanecen con `decision=revisar`; no se deben convertir en correcciones inventadas.

**Límite de aceptación de Iris.** Corregir la compatibilidad de normalización/escritura y sus pruebas, hacer reproducible y verificable la procedencia del catálogo, validar/enriquecer territorio y sus variables derivadas, regenerar únicamente salidas territoriales/de limpieza afectadas y corregir sus documentos, Code Book territorial y afirmaciones de Iris en planificación/README. Las excepciones territoriales deben quedar trazadas y explícitamente pendientes cuando no haya decisión humana.

**No objetivos.** No decidir los 1,355 candidatos de duplicado, no modificar `duplicados_parciales.*`, no implementar excepciones telefónicas, no reconciliar la fuente secundaria ni editar la sección de procedencia del Code Book de Anggie. Tampoco tocar `README.pdf` no rastreado. Las pruebas de alcance solo podrán demostrar que estos artefactos/decisiones no se mutan.

**Causas de los 8 fallos.**

| Fallo | Causa raíz | Corrección acotada |
|---|---|---|
| 2 aserciones de limpieza/escritura | `UPPERCASE_TEXT_COLUMNS` ahora canoniza `ESTABLECIMIENTO` y `DIRECTOR`; las expectativas antiguas preservan capitalización de título. | Actualizar las expectativas y añadir una prueba específica de la regla de mayúsculas. |
| 2 pruebas de carrera de temporales | Al monkeypatchear `cleaning.os.open`, `_secure_fd_writes_supported()` deja de reconocerlo en `os.supports_dir_fd` y usa el escritor portátil; la inyección nunca prueba la rama segura. | Detectar la capacidad por plataforma/constantes, o inyectar la capacidad; mantener la rama `dir_fd` bajo prueba. |
| 3 pruebas del CLI | `limpiar_dataset.py` llama `enrich_result` y exige `data/reference/catalogo_territorial.csv` antes de escribir; los fixtures temporales no lo crean. | Añadir un catálogo mínimo válido a los fixtures de los casos exitosos y del caso que debe alcanzar el error de escritura. |
| 1 hash de repositorio | El test de limpieza protegía hashes anteriores de CSV limpio, bitácora y reporte; Iris regeneró los tres al añadir códigos INE. | Actualizar el contrato de hashes únicamente después de regeneración reproducible y verificar los valores nuevos. |

La métrica generada está desactualizada: `reporte_calidad_antes_despues.csv` aún indica 20→19 y territorio pendiente, aunque el resultado enriquecido es 20→21 y añade métricas de códigos. `validacion_territorial.md` serializa rutas absolutas de Windows porque renderiza `Path.as_posix()` sobre rutas absolutas, por lo que no es byte-estable entre equipos.

### Affected Areas
- `src/proyecto1_ds/cleaning.py` — contrato de mayúsculas, detección de escritor seguro y estado de territorio en el reporte base.
- `scripts/limpiar_dataset.py` — dependencia explícita del catálogo para el enriquecimiento.
- `src/proyecto1_ds/enrichment.py` — códigos derivados, dos typos ya trazados y mapeos de alias que requieren estado de evidencia claro.
- `src/proyecto1_ds/territorial.py` y `scripts/validar_territorio.py` — validación, salidas deterministas y renderizado de rutas relativas.
- `scripts/generar_catalogo_territorial.py` y `data/reference/catalogo_territorial.csv` — la URL `main` de un repositorio personal no fija una versión, checksum ni fuente primaria verificable.
- `tests/test_cleaning.py`, `tests/test_cleaning_cli.py`, `tests/test_repository_cleanup.py` — regresiones conocidas y hashes protegidos; agregar `tests/test_territorial.py` y/o `tests/test_enrichment.py` para comportamiento de Iris.
- `data/processed/establecimientos_diversificado_limpio.csv`, `outputs/tablas/bitacora_limpieza.csv`, `outputs/tablas/reporte_calidad_antes_despues.csv`, `outputs/tablas/inconsistencias_territoriales.csv`, `outputs/reportes/validacion_territorial.md` — salidas generadas que se regeneran solo mediante scripts tras pruebas verdes.
- `docs/code_book/variables_territoriales.md`, `docs/planificacion.md`, `README.md`, `AGENTS.md` y, si corresponde, `docs/plan_limpieza.md` — deben reflejar 21 columnas, alcance territorial real, catálogo verificable y pendientes explícitos.

### Approaches
1. **Catálogo versionado con pin criptográfico** — conservar el CSV versionado y descargar desde una revisión inmutable (commit SHA o release), validando SHA-256, esquema, 22 departamentos y 340 municipios antes del reemplazo atómico.
   - Pros: reproducible sin depender de `main`; detecta alteración o fuente incorrecta; cambio contenido.
   - Cons: sigue siendo un espejo de terceros y exige documentar la fuente primaria/fecha/licencia.
   - Effort: Medium.

2. **Catálogo oficial archivado en el repositorio con recibo de procedencia** — tratar el CSV actual como referencia congelada y añadir metadatos de descarga, URL oficial/archivo, fecha, versión y SHA-256; el generador solo verifica o reconstruye desde un insumo versionado.
   - Pros: máxima repetibilidad offline y auditoría de la entrega; elimina dependencia de red durante limpieza.
   - Cons: requiere conseguir y evaluar la fuente primaria exacta; puede aumentar el número de artefactos de referencia.
   - Effort: Medium/High.

3. **Dejar la URL mutable actual** — regenerar directamente desde `main`.
   - Pros: mínimo cambio inmediato.
   - Cons: no es reproducible ni permite afirmar procedencia oficial verificable; puede cambiar el catálogo sin revisión.
   - Effort: Low.

### Recommendation
Adoptar el enfoque 1 ahora: fijar una revisión inmutable del insumo, incluir metadatos y SHA-256 esperados, validar esquema/conteos/códigos antes de escribir y describir honestamente el espejo frente a la fuente primaria. Si se obtiene un archivo oficial estable, evolucionar al enfoque 2 sin cambiar el contrato de consumo del CSV.

Para las 7 parejas (`IXCAN`, `NEBAJ`, `LA TINTA`, `GENOVA COSTA CUCA`, `LANQUIN`, `ALOTENANGO`, `OLINTEPEQUE`), la decisión de este cambio es **conservar el texto MINEDUC, mantener `decision=revisar` y registrar el mapeo usado para código como excepción pendiente de confirmación humana**. No se deben renombrar ni considerar “válidas” solo por similitud. Los dos typos ya implementados deben conservar evidencia separada y pruebas de trazabilidad. El informe y Code Book no deben afirmar “cero pendientes”, “7 alias válidos” ni 100% de cobertura sin indicar estas excepciones.

**Slices de trabajo (estrategia `auto-chain`, presupuesto 400 líneas).**

1. **PR/commit 1 — regresión de limpieza y catálogo en CLI** (estimado 180–260 líneas): pruebas RED para mayúsculas, capacidad `dir_fd` monkeypatcheada y fixtures de catálogo; implementación mínima; `uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py`. Rollback: `cleaning.py` y esas pruebas.
2. **PR/commit 2 — contrato territorial reproducible** (estimado 260–380 líneas): pruebas nuevas para catálogo fijado/checksum, validación/enriquecimiento, 7 pendientes, rutas relativas y ausencia de mutación de duplicados; endurecer generador/enriquecimiento/validador. Verificar pruebas focalizadas y ejecución temporal de los tres CLIs. Rollback: módulos/scripts territoriales y pruebas nuevas.
3. **PR/commit 3 — regeneración y documentación honesta** (estimado 180–320 líneas de autoría; CSV generados excluidos del presupuesto de autoría pero incluidos en identidad): regenerar solo las salidas permitidas, actualizar hashes, Code Book territorial, plan, README y AGENTS. Verificar `uv run pytest`, `git diff --check` y hashes/recibos. Rollback: regenerar desde el commit previo y revertir documentación asociada.

Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High

**Rutas protegidas y rollback.** Permanecen inmutables `data/raw/**`, `data/source/**`, `data/raw/manifest.json`, decisiones/log de reconciliación de Anggie, excepciones telefónicas, `outputs/tablas/duplicados_parciales.csv`, `outputs/reportes/duplicados_parciales.md` y `README.pdf`. Los tres artefactos de limpieza solo pueden cambiar por regeneración atómica tras fijar el catálogo y deben tener hashes actualizados en el mismo slice. Un rollback revierte código/pruebas/documentos de cada slice y vuelve a generar las salidas desde el estado anterior; nunca se editan CSV/outputs manualmente.

### Risks
- Los alias actuales asignan códigos a las 145 filas mientras la validación aún las etiqueta `revisar`; sin separar “código derivado provisional” de “decisión humana”, la documentación puede sobreafirmar validez.
- El checksum por sí solo no prueba que el espejo sea la fuente primaria INE; se debe declarar con precisión la cadena de procedencia.
- Cambiar hashes antes de regenerar todos los artefactos relacionados podría congelar métricas contradictorias.
- Corregir el informe de duplicados o sus candidatos excedería el límite de Iris/Anggie aunque comparta el defecto de rutas absolutas.

### Ready for Proposal
Sí. La propuesta debe fijar el límite de Iris, exigir TDD para regresiones y módulos territoriales, adoptar catálogo con revisión inmutable más checksum, conservar explícitas las 7 decisiones pendientes y prohibir toda mutación o declaración de finalización del trabajo de Anggie.
