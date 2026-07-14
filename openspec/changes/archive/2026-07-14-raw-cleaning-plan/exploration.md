## Exploration: Plan de limpieza cruda

### Current State
El proyecto ya preserva los datos crudos oficiales de MINEDUC en `data/raw/` y unifica estructuralmente 23 HTML oficiales hacia `data/interim/establecimientos_diversificado_raw_unificado.csv` sin limpieza. El dataset intermedio tiene 11,867 filas y 20 columnas; `docs/diagnostico.md` y `outputs/tablas/*.csv` fueron generados por código y declaran explícitamente que no hubo normalización, deduplicación, recodificación, corrección de tipos, eliminación de filas ni validación territorial concluyente.

Los diagnósticos actuales justifican reglas de limpieza para: encabezado `<NBSP>` completamente vacío; valores faltantes o marcadores de ausencia en `<NBSP>`, `DISTRITO`, `ESTABLECIMIENTO`, `DIRECCION`, `TELEFONO`, `SUPERVISOR` y `DIRECTOR`; texto sospechoso por espacios, espacios múltiples o caracteres no separables en `ESTABLECIMIENTO`, `DIRECCION`, `TELEFONO`, `SUPERVISOR` y `DIRECTOR`; teléfonos no vacíos con caracteres no numéricos; dominios territoriales no verificables en `DEPARTAMENTO`, `MUNICIPIO` y `departamento_origen`; y duplicados parciales que están diferidos por diseño. También conviene planificar reglas de conservación explícita para variables sin problema diagnosticado fuerte (`CODIGO`, `NIVEL`, `SECTOR`, `AREA`, `STATUS`, `MODALIDAD`, `JORNADA`, `PLAN`, `DEPARTAMENTAL`, `archivo_origen`) para evitar transformaciones no justificadas.

### Affected Areas
- `docs/plan_limpieza.md` — entregable principal del cambio; debe definir reglas, justificación, evidencia, riesgo y alcance antes de mutar datos.
- `docs/diagnostico.md` — fuente narrativa de evidencia y límites; debe ser referenciada, no reescrita por este cambio.
- `outputs/tablas/diagnostico_columnas.csv` — fuente cuantitativa para faltantes, unicidad y tipos observados.
- `outputs/tablas/problemas_potenciales.csv` — fuente principal para mapear problema → regla candidata.
- `outputs/tablas/dominios_observados.csv` — evidencia de dominios observados y ejemplos frecuentes; útil para redactar reglas sin convertirlas todavía en catálogos oficiales.
- `outputs/tablas/duplicados_exactos.csv` — evidencia de 0 duplicados exactos; debe informar la regla futura de deduplicación sin ejecutar eliminaciones.
- `data/interim/establecimientos_diversificado_raw_unificado.csv` — dataset de referencia para el plan; no debe modificarse en esta fase.
- `src/proyecto1_ds/diagnostics.py` — define marcadores de ausencia y criterios diagnósticos actuales; puede servir como referencia, pero no debe cambiarse en esta exploración.
- `openspec/specs/diagnostico-calidad-cruda/spec.md` y `openspec/specs/consolidacion-cruda/spec.md` — establecen el límite vigente: diagnóstico y consolidación no limpian datos.

### Approaches
1. **Plan descriptivo trazable desde diagnóstico** — Crear `docs/plan_limpieza.md` como documento de decisión con tabla por variable/problema/regla/justificación/riesgo/estado, usando solo evidencia ya generada.
   - Pros: Mantiene separación entre diagnóstico, planificación e implementación; es fácil de revisar contra la rúbrica; evita tocar datos antes de acordar reglas.
   - Cons: Algunas reglas quedarán como “pendiente de catálogo” o “revisión manual” porque el diagnóstico no prueba todo.
   - Effort: Low

2. **Plan prescriptivo completo con reglas finales** — Definir desde ahora todas las normalizaciones, catálogos, deduplicación parcial y criterios de corrección como si fueran definitivos.
   - Pros: Acelera la futura implementación si todas las suposiciones resultan correctas.
   - Cons: Alto riesgo de inventar dominios válidos, fusionar registros o normalizar nombres propios sin evidencia oficial; puede contradecir la regla de no limpiar “porque sí”.
   - Effort: Medium

3. **Plan mínimo por categorías generales** — Documentar solo reglas globales para nulos, texto y duplicados sin bajar a cada variable afectada.
   - Pros: Rápido y breve.
   - Cons: No cumple bien la planificación del slice 4, que pide tabla por variable con problema, regla, justificación y riesgo; deja poca trazabilidad para validar después.
   - Effort: Low

### Recommendation
Usar el enfoque de plan descriptivo trazable desde diagnóstico. El alcance de este cambio debe limitarse a crear `docs/plan_limpieza.md` con: resumen ejecutivo; fuentes de evidencia; reglas por variable/problema; reglas globales para nulos, texto, tipos y trazabilidad; decisiones explícitamente diferidas; criterios de aceptación para la futura implementación; y riesgos. El documento debe decir claramente que no modifica `data/raw/`, `data/interim/`, scripts ni tablas generadas.

Para la futura implementación se debe diferir: creación del dataset limpio en `data/clean/`; cambios en scripts de limpieza/validación; eliminación o fusión de duplicados parciales; corrección de dominios territoriales sin catálogo oficial; estandarización definitiva de teléfonos; renombrado físico de columnas; imputaciones; eliminación de filas; y generación de reporte antes/después o Code Book final.

### Risks
- Sobre-especificar desde diagnóstico puede convertir observaciones en “verdades” sin catálogo externo, especialmente para departamentos, municipios y departamentales.
- Normalizar nombres de establecimientos, supervisores o directores puede destruir tildes, abreviaturas o variantes legítimas si no se define una regla conservadora.
- Tratar teléfonos no numéricos como inválidos automáticamente puede eliminar extensiones, separadores o múltiples números que aún podrían ser útiles.
- El encabezado `<NBSP>` parece removible por estar 100% vacío, pero debe documentarse como decisión futura para no violar la separación entre plan y mutación.
- Duplicados parciales no pueden resolverse solo con conteo diagnóstico; requieren criterios de similitud y revisión para evitar fusiones incorrectas.

### Ready for Proposal
Yes — el orquestador puede avanzar a `sdd-propose` para crear un cambio enfocado en el entregable documental `docs/plan_limpieza.md`, con alcance explícito de planificación solamente y sin modificar datos, scripts ni outputs generados.
