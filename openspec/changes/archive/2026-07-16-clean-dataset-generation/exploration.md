## Exploración: ejecución de limpieza del dataset MINEDUC

### Estado actual
El proyecto ya tiene una línea reproducible `adquisición → manifest → consolidación → diagnóstico → plan de limpieza`. La adquisición (`src/proyecto1_ds/acquisition.py`, `scripts/adquirir_datos.py`) preserva 23 HTML oficiales MINEDUC en `data/raw/` y registra manifest con fuente, fecha, método, departamento, versión y checksum. La consolidación (`src/proyecto1_ds/consolidation.py`, `scripts/consolidar_crudos.py`) extrae tablas oficiales o CSV registrados hacia `data/interim/establecimientos_diversificado_raw_unificado.csv` sin limpiar valores y agrega `archivo_origen`/`departamento_origen`. El diagnóstico (`src/proyecto1_ds/diagnostics.py`, `scripts/diagnosticar_crudos.py`) genera métricas y tablas en `outputs/tablas/` más `docs/diagnostico.md`, también sin mutar el intermedio.

Las specs vigentes en `openspec/specs/` cubren adquisición trazable, consolidación cruda, diagnóstico de calidad cruda y plan de limpieza. Todas refuerzan una separación fuerte: `data/raw/` es inmutable, `data/interim/` conserva el dataset unificado sin limpieza, y la fase nueva debe crear artefactos limpios separados. `docs/plan_limpieza.md` propone reglas, pero declara explícitamente que todavía no ejecuta limpieza ni genera dataset limpio.

Reglas seguras para automatizar ahora: eliminar la columna `<NBSP>` solo si está completamente vacía; convertir marcadores claros de ausencia y espacios puros a nulos documentados; normalizar espacios iniciales/finales, espacios múltiples y NBSP en texto; conservar identificadores/categorías como texto; generar bitácora de transformaciones y reporte antes/después. Reglas a diferir o dejar manuales: validación territorial contra catálogo oficial, deduplicación parcial/fusión, estandarización agresiva de teléfonos, unificación semántica de nombres propios, direcciones, supervisores y directores.

### Áreas afectadas
- `src/proyecto1_ds/cleaning.py` — módulo nuevo probable para reglas determinísticas, bitácora, dataset limpio y métricas antes/después.
- `scripts/limpiar_dataset.py` — CLI nuevo probable para leer `data/interim/establecimientos_diversificado_raw_unificado.csv` y escribir salidas limpias sin tocar crudos/intermedios.
- `tests/test_cleaning.py` — pruebas TDD para nulos, espacios/NBSP, eliminación segura de columna vacía, preservación de tipos texto, no deduplicación automática y bitácora.
- `tests/test_cli.py` o `tests/test_cleaning_cli.py` — restricciones de rutas: entrada solo desde `data/interim/`, salida limpia solo bajo `data/processed/` y tablas bajo `outputs/tablas/`.
- `data/processed/` — ubicación recomendada para `establecimientos_diversificado_limpio.csv`, separada de `data/raw/` y `data/interim/`.
- `outputs/tablas/` — ubicación recomendada para `bitacora_limpieza.csv`, `reporte_calidad_antes_despues.csv` y, si aplica, `duplicados_parciales_candidatos.csv` como evidencia, no como mutación automática.
- `docs/` — probable actualización generada o manual de `docs/reporte_limpieza.md` y posterior `docs/codebook.md`; `docs/diagnostico.md` y `docs/plan_limpieza.md` no deberían reescribirse en el primer slice salvo que la spec lo exija.
- `openspec/specs/` — necesita una nueva capacidad/delta de ejecución de limpieza profunda trazable.

### Enfoques
1. **Slice incremental determinístico** — Crear limpieza reproducible mínima: nulos documentados, espacios/NBSP, eliminación de columna `<NBSP>` vacía, preservación de tipos texto, bitácora y reporte antes/después básico.
   - Pros: bajo riesgo, cabe en el presupuesto de 400 líneas, cumple el núcleo del Paso 4 sin invadir decisiones manuales, es fácil de cubrir con TDD.
   - Cons: no resuelve catálogo territorial, teléfonos complejos ni duplicados parciales; requiere declarar explícitamente esas limitaciones.
   - Esfuerzo: Medio

2. **Limpieza profunda completa en un solo cambio** — Implementar reglas determinísticas, validación territorial, deduplicación parcial, teléfonos, reporte final y codebook juntos.
   - Pros: aproxima más el entregable final del curso en una sola fase.
   - Cons: supera probablemente el presupuesto de revisión, mezcla decisiones automáticas y humanas, requiere catálogo oficial no disponible y aumenta riesgo de sobre-limpieza.
   - Esfuerzo: Alto

3. **Solo generar reporte/candidatos sin dataset limpio** — Mantener la fase read-only y producir candidatos de limpieza o duplicados sin escribir `data/processed/`.
   - Pros: riesgo mínimo y útil para revisión humana.
   - Cons: no cumple el objetivo actual de producir un conjunto limpio; posterga demasiado el Paso 4.
   - Esfuerzo: Bajo/Medio

### Recomendación
Implementar el **slice incremental determinístico**. La propuesta debería definir un cambio pequeño que agregue un módulo/CLI de limpieza con salidas nuevas: `data/processed/establecimientos_diversificado_limpio.csv`, `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`. La limpieza debe ser idempotente, atómica y trazable; no debe modificar `data/raw/`, `data/interim/`, `docs/diagnostico.md` ni `docs/plan_limpieza.md`. Duplicados parciales, catálogo territorial y ediciones semánticas deben quedar como evidencia/candidatos o decisiones diferidas.

### Riesgos
- Mutar accidentalmente `data/raw/` o `data/interim/` rompería el linaje oficial y la reproducibilidad.
- Sobre-limpiar campos semánticos (`ESTABLECIMIENTO`, `DIRECCION`, `SUPERVISOR`, `DIRECTOR`) puede alterar nombres oficiales o fusionar entidades distintas.
- Convertir `CODIGO`, `DISTRITO`, `TELEFONO` o `archivo_origen` a numérico puede perder ceros, separadores o procedencia.
- Eliminar duplicados parciales automáticamente contradice la rúbrica y puede perder jornadas, sedes o modalidades distintas.
- Validar territorios sin catálogo oficial puede marcar como inválidos valores administrativos legítimos.
- El reporte antes/después y el Code Book necesitan distinguir limpieza ejecutada de decisiones diferidas para no prometer calidad no verificada.

### Listo para propuesta
Sí. El orquestador debería proponer una capacidad de limpieza ejecutable y trazable, acotada a reglas determinísticas seguras, con TDD estricto y salidas nuevas en `data/processed/` y `outputs/tablas/`. Debe dejar explícitamente fuera del primer slice la deduplicación parcial automática, la validación territorial final y la normalización semántica agresiva.

## Contrato de resultado

- `status`: `success`
- `executive_summary`: El pipeline actual ya preserva fuente oficial, intermedio crudo y diagnóstico; el siguiente cambio debe ejecutar solo limpieza determinística segura, escribir un dataset limpio separado y registrar bitácora/reporte antes-después sin tocar raw/interim.
- `artifacts`: `openspec/changes/clean-dataset-generation/exploration.md`
- `next_recommended`: Crear propuesta SDD para un slice incremental de limpieza con `data/processed/establecimientos_diversificado_limpio.csv`, bitácora, reporte antes/después y pruebas TDD.
- `risks`: mutación accidental de raw/interim, sobre-limpieza semántica, pérdida de tipos texto, deduplicación parcial indebida, validación territorial sin catálogo y expectativas del Code Book.
- `skill_resolution`: Ejecutado como `sdd-explore` executor; se inspeccionó código real y solo se creó el artifact de exploración solicitado.
