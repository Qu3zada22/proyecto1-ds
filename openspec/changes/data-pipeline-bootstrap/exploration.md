## Exploración: Bootstrap del primer pipeline ejecutable de datos

### Estado actual
El repositorio está primero orientado a documentación. Contiene las instrucciones del curso en `docs/instrucciones.md`, la planificación por slices en `docs/planificacion.md` y metadatos OpenSpec/SDD en `openspec/config.yaml`. Todavía no existe stack Python, R, notebook, manifiesto de paquetes, CI, test runner, directorio de datos ni pipeline ejecutable. El curso exige obtener datos de MINEDUC, preservar CSV crudos, generar un diagnóstico inicial mediante código, definir un plan de limpieza antes de transformar datos, agregar validación automática posteriormente, crear un Libro de Códigos y entregar un CSV final limpio y unificado.

### Áreas afectadas
- `pyproject.toml` — definiría el primer stack ejecutable en Python, dependencias y herramientas de pruebas/formato.
- `src/proyecto1_ds/` — contendría módulos reutilizables para obtención, consolidación y diagnóstico.
- `scripts/` — expondría puntos de entrada ejecutables para obtención, consolidación y diagnóstico.
- `data/raw/` — almacenaría CSV crudos inmutables y metadatos de fuente; sin ediciones manuales.
- `data/interim/` — almacenaría el dataset unificado previo a limpieza, producido desde archivos crudos.
- `outputs/tables/` — almacenaría tablas diagnósticas generadas por código y requeridas por la rúbrica.
- `docs/diagnostico.md` — resumiría hallazgos diagnósticos generados por código, sin proponer transformaciones todavía.
- `docs/codebook.md` o `docs/data_sources.md` — empezaría a registrar fecha de extracción, URL fuente y linaje del dataset.
- `tests/` — quedaría disponible cuando exista el stack, habilitando TDD estricto para comportamiento del pipeline y helpers de calidad de datos.

### Enfoques
1. **Pipeline Python script-first** — Crear un proyecto Python pequeño con `pandas`, capa de scripts/CLI y `pytest` para checks ejecutables.
   - Pros: Mejor ajuste para reproducibilidad, activación futura de TDD estricto, salidas generadas por scripts, manejo de dependencias y automatización; permite manejar descarga web si MINEDUC requiere HTTP/sesiones.
   - Contras: Requiere crear scaffolding del proyecto antes del análisis; el equipo debe ejecutar herramientas Python consistentemente.
   - Esfuerzo: Medio

2. **Flujo notebook-first** — Usar uno o más notebooks `.ipynb` para obtención, consolidación y diagnóstico.
   - Pros: Rápido para exploración visual y revisión de clase; facilita narrar hallazgos en línea.
   - Contras: Más débil como fuente de verdad para reproducibilidad, pruebas, revisión de diffs y re-ejecución; TDD estricto queda incómodo.
   - Esfuerzo: Bajo

3. **Flujo R/Rmd** — Usar scripts R o R Markdown con tidyverse para obtención, consolidación y diagnóstico.
   - Pros: Buena ergonomía tabular/de reportes y formato aceptable para el curso.
   - Contras: El repositorio no tiene convenciones R; Python encaja mejor con `pytest` y posible automatización/descarga web.
   - Esfuerzo: Medio

### Recomendación
Usar un bootstrap Python script-first, dejando notebooks como opción posterior solo para presentación. El primer slice ejecutable debe crear la estructura mínima ejecutable: configuración de dependencias/pruebas, carpetas de datos crudos inmutables, formato de manifiesto/metadatos de fuente, punto de entrada de obtención que descargue o registre CSV de MINEDUC adquiridos manualmente, paso de consolidación que únicamente una archivos crudos con columnas de procedencia y paso de diagnóstico que genere métricas previas a la limpieza. La limpieza queda explícitamente fuera de alcance: no recortar espacios, recodificar, corregir tipos, deduplicar, arreglar dominios, normalizar categorías ni eliminar filas.

### Riesgos
- La mecánica de descarga de MINEDUC es desconocida: la fuente puede ser dinámica, basada en formularios, dependiente de sesión, bloqueada o sin exportación directa a CSV.
- La disponibilidad y el alcance de datos no están resueltos: el equipo debe confirmar cómo obtener todos los establecimientos con `NIVEL ESCOLAR: DIVERSIFICADO` en todo el país.
- Podrían ser necesarias descargas manuales; si ocurre, el pipeline debe separar metadatos de adquisición de la preservación de archivos crudos y documentar pasos exactos.
- Codificación, delimitadores, nombres de columnas y compatibilidad de esquema pueden variar entre exportaciones departamentales.
- La inmutabilidad de datos crudos debe aplicarse primero por convención; los checks automáticos solo podrán agregarse cuando exista stack ejecutable.
- Se quiere TDD estricto, pero no puede aplicarse hasta que el bootstrap introduzca un comando de pruebas.

### Listo para propuesta
Sí. La propuesta debe acotar `data-pipeline-bootstrap` como el primer slice ejecutable: establecer un esqueleto Python para obtención/consolidación/diagnóstico, preservar datos crudos de forma inmutable, generar salidas diagnósticas previas a limpieza y diferir todas las decisiones de limpieza a un cambio posterior de plan de limpieza cuando los datos reales estén disponibles.
