## Exploración: limpieza del repositorio y plan de entrega

### Estado actual

El repositorio ya implementa una línea reproducible `HTML oficial MINEDUC → manifest → consolidación → diagnóstico → limpieza conservadora → data/processed`. La consolidación valida los checksum del manifest, extrae las tablas de los 23 HTML y agrega `archivo_origen` y `departamento_origen`; la limpieza escribe el dataset final actual en `data/processed/`.

Se verificó directamente que regenerar el CSV desde `data/raw/` produce bytes idénticos al archivo actual: **11,867 filas, 20 columnas y 11,867 códigos únicos** (`SHA-256 c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`). Por ello, el CSV consolidado es un derivado reproducible y puede promoverse como fuente tabular canónica; los 23 HTML deben conservarse como evidencia oficial y de reproducibilidad.

#### Alcance preciso

- Mover la fuente tabular canónica a `data/source/establecimientos_diversificado_mineduc.csv` y actualizar contratos, CLIs, pruebas y documentación que la referencian.
- Conservar los HTML, el manifest y el CSV limpio en `data/processed/`.
- Eliminar únicamente artefactos prescindibles verificados y el cambio OpenSpec incompleto de Anggie, después de preservar/corregir su evidencia en `docs/reconciliacion_anggie.md`.
- Reemplazar `docs/planificacion.md` por el plan vigente, trazable a todos los requisitos de `docs/instrucciones.md`, con responsables y criterios de aceptación.

#### Fuera de alcance

- Eliminar HTML oficiales, regenerar o alterar datos sin una fase de implementación posterior, o usar el CSV de Anggie como fuente primaria.
- Añadir una arquitectura `src` nueva o capas sin necesidad; los scripts existentes y el paquete mínimo son suficientes.
- Declarar resuelto un duplicado parcial, una regla territorial, teléfono ambiguo o inconsistencia semántica sin evidencia reproducible y revisión humana.
- Propagar la cifra de 12,807 o 12,948 filas atribuida a Anggie sin volver a medir la fuente y documentar el comando/parámetros.

### Áreas afectadas

#### Linaje de datos propuesto

```text
23 HTML oficiales MINEDUC en data/raw/ + manifest.json (inmutables)
  → scripts/consolidar_crudos.py
  → data/source/establecimientos_diversificado_mineduc.csv (canónico, reproducible)
  → scripts/diagnosticar_crudos.py y scripts/limpiar_dataset.py
  → outputs/tablas/*, docs/diagnostico.md
  → data/processed/establecimientos_diversificado_limpio.csv
```

| Área | Impacto y acción requerida |
|---|---|
| `src/proyecto1_ds/consolidation.py` | Cambiar `DEFAULT_OUTPUT_PATH` al CSV canónico en `data/source/`; mantener la extracción estructural y la validación de checksum. |
| `src/proyecto1_ds/diagnostics.py`, `src/proyecto1_ds/cleaning.py` | Cambiar la entrada predeterminada y los guards de `data/interim/` a `data/source/`. |
| `scripts/consolidar_crudos.py`, `scripts/diagnosticar_crudos.py`, `scripts/limpiar_dataset.py` | Actualizar defaults, descripciones y validaciones de rutas. |
| `tests/test_consolidation.py`, `tests/test_diagnostics.py`, `tests/test_cleaning*.py` | Ajustar fixtures/rutas y cubrir que la fuente canónica permanece dentro de `data/source/`. |
| `docs/*.md`, `openspec/specs/*`, archivos OpenSpec archivados | Hay 33 archivos de texto que mencionan el nombre anterior; separar referencias vivas de historial archivado. No reescribir el historial: documentar la migración cuando corresponda. |
| `docs/reconciliacion_anggie.md` | Conservar como evidencia de contribución y corregir sus conteos solo después de una ejecución reproducible. |
| `docs/planificacion.md` | Reemplazar el plan stale (`data/clean/`, slices ya completados) por la fuente de verdad actual con avance, brechas, responsables y criterios. |

#### Matriz de retención y eliminación

| Elemento | Decisión | Motivo y condición |
|---|---|---|
| `data/raw/mineduc_*.html` (23) y `data/raw/manifest.json` | Conservar | Son procedencia oficial, checksum, cobertura y entrada para reproducir el CSV. Eliminarlos rompería el manifest y la consolidación. |
| `data/interim/establecimientos_diversificado_raw_unificado.csv` | Mover/renombrar | Se promoverá, sin cambiar bytes, a `data/source/establecimientos_diversificado_mineduc.csv`. |
| `data/processed/establecimientos_diversificado_limpio.csv` | Conservar | Es la salida limpia vigente y el nombre/directorio ya implementados. |
| `docs/reconciliacion_anggie.md` | Conservar y corregir | Evidencia de contribución; requiere revalidación de los conteos de Anggie antes de editar. |
| `openspec/changes/anggie-csv-reconciliation/` | Eliminar después de preservar evidencia | Es un cambio activo incompleto. Su análisis útil ya debe estar reflejado en la reconciliación corregida y en el nuevo plan. |
| `openspec/changes/archive/.gitkeep`, `openspec/specs/.gitkeep` | Eliminar | Están versionados, pero sus directorios ya contienen 26 y 6 entradas respectivamente. |
| `.atl/`, `.pytest_cache/`, `__pycache__/`, `src/proyecto1_ds.egg-info/` | Eliminar localmente si se desea | `git clean -ndX` los identifica como ignorados y reconstruibles. No forman parte de la entrega. |
| `.venv/` | Decisión operativa antes de eliminar | Es ignorado y reconstruible, pero borrarlo obliga a recrear el entorno. Eliminarlo solo si se acepta esa interrupción inmediata. |

### Mapa de brechas frente a los requisitos de `docs/`

| Requisito del curso | Evidencia actual | Brecha y entregable de cierre |
|---|---|---|
| Obtención, resguardo y unión | HTML oficiales, manifest, consolidación y CSV reproducible | Promover el CSV canónico y explicar claramente HTML→CSV en README/Code Book. |
| Diagnóstico por código | `docs/diagnostico.md` y tablas en `outputs/tablas/` | Mantenerlo apuntando a `data/source/` tras el movimiento. |
| Plan de limpieza | `docs/plan_limpieza.md` | Actualizar `docs/planificacion.md` como plan vigente; no duplicar ni contradecir el plan de reglas. |
| Limpieza profunda y bitácora | Limpieza conservadora, bitácora y reporte parcial | Completar reglas pendientes basadas en evidencia: territorial, teléfonos/formato, categorías y consistencia cruzada. |
| Duplicados exactos y parciales | Exactos: 0; parciales: diferidos | Generar candidatos por similitud, revisión humana y bitácora de decisión; no eliminar automáticamente. |
| Validación automática final | Pruebas de la limpieza conservadora | Implementar validación del conjunto final para todos los checks del curso, con reporte reproducible de aprobados, diferidos y fallos. |
| Informe antes/después completo | `reporte_calidad_antes_despues.csv` parcial | Crear `docs/reporte_calidad.md` con todas las métricas exigidas, conteos y justificación de cambios. |
| Catálogo y consistencia territorial | Marcado como no verificable | Incorporar catálogo oficial versionado/documentado, reglas departamento–municipio–origen y excepciones justificadas. |
| Code Book Markdown y PDF | Ausente | Crear `docs/codebook.md` y PDF con variable, tipo, dominio, valores, tratamiento, derivadas, fecha, fuente y versión. |
| Repositorio navegable y contribuciones visibles | Falta README; Iris/Anggie no tienen evidencia final suficiente | README de ejecución/reproducibilidad y secciones/commits atribuibles de los tres integrantes, también en Code Book. |

### Enfoques

1. **Migración mínima, trazable y por unidades de trabajo** — Renombrar el CSV como dato generado, adaptar solo referencias vivas y cerrar las brechas del curso en slices independientes.
   - Ventajas: conserva procedencia, reduce complejidad, evita reescritura de historial y permite revisar cada entrega.
   - Desventajas: requiere clasificar las referencias históricas y coordinar tres entregables.
   - Esfuerzo: Medio.

2. **Reorganización amplia del pipeline y datos** — Rediseñar carpetas, mover crudos, intermedios y scripts antes de completar las brechas.
   - Ventajas: podría uniformar nombres visualmente.
   - Desventajas: rompe contratos, aumenta el radio de cambio y contradice la preferencia por simplicidad sin aportar requisitos del curso.
   - Esfuerzo: Alto.

### Asignaciones propuestas y criterios de aceptación

| Responsable | Entregable concreto | Criterios de aceptación |
|---|---|---|
| **Anggie** | Reconciliación corregida y reporte completo de calidad. | Reejecuta la comparación contra su CSV con ruta, hash, parser y conteos reproducibles; corrige `docs/reconciliacion_anggie.md` sin afirmar 12,807/12,948 sin evidencia; entrega `docs/reporte_calidad.md` con las diez métricas del curso y justificaciones. |
| **Iris** | Catálogo territorial, revisión de duplicados parciales y consistencia cruzada. | Versiona/documenta la fuente y fecha del catálogo; genera reglas y resultados para departamento–municipio–origen; produce candidatos de similitud, decisión humana por caso y bitácora; no elimina ni fusiona automáticamente. |
| **Jonathan** | Migración de fuente canónica, validación final, README y ensamblaje del Code Book/PDF. | El CSV en `data/source/` se regenera byte a byte desde los 23 HTML; referencias vivas, tests y guards pasan; validación cubre la lista del curso o marca una excepción fundamentada; README permite reproducir el pipeline; Code Book/PDF contiene todos los metadatos y acredita a los tres integrantes. |

La responsabilidad de ensamblaje no sustituye contribuciones: Anggie e Iris deben aportar contenido verificable a `docs/reconciliacion_anggie.md`, reporte, catálogo/bitácora y Code Book para que su participación sea visible.

#### Slices de entrega recomendados (presupuesto de 400 líneas)

| Orden | Unidad de trabajo / PR | Dependencia y presupuesto |
|---|---|---|
| 1 | Limpieza local aprobada + eliminación de `.gitkeep` redundantes + retiro del cambio OpenSpec incompleto, después de preservar evidencia | Independiente; bajo. La eliminación de `.venv` queda fuera salvo aceptación explícita. |
| 2 | Promoción del CSV y actualización de contratos vivos, scripts y pruebas | Base para los demás. El rename/dato generado se registra como movimiento/snapshot y no se cuenta como líneas autoradas; si el diff de código+tests supera 400, dividir CLI/consolidación de diagnóstico/limpieza. |
| 3 | Reconciliación reproducible de Anggie + informe de calidad | Depende de la ruta canónica; objetivo ≤400 líneas autoradas. |
| 4 | Catálogo territorial, duplicados parciales, consistencia y validación final | Depende de 2; probable alto riesgo. Aplicar `auto-chain`: separar catálogo/reglas de candidatos+validación. |
| 5 | README, Code Book Markdown/PDF y actualización de planificación | Depende de resultados validados; separar PDF generado del Markdown autorado y mantener el PR ≤400 líneas autoradas. |

Para cada slice: prueba focalizada, resultado exacto, escenario de ejecución o `N/A`, límite de rollback y diagrama de dependencia en los PR encadenados. Si un slice no puede dividirse sin romper el entregable, solicitar una excepción de tamaño explícita; no mezclar trabajo no relacionado para llenar un PR.

### Recomendación

Adoptar el **enfoque mínimo, trazable y por unidades de trabajo**. El movimiento a `data/source/` reconoce el papel real del CSV sin borrar la evidencia oficial que lo sustenta. `data/processed/` debe ser el estándar para la salida limpia porque es la implementación vigente; las menciones a `data/clean/` en la planificación son obsoletas y las instrucciones del curso no imponen ese directorio.

Antes de aplicar, crear una propuesta que fije la migración de contratos vivos, el plan autoritativo y las condiciones de cierre de cada responsable. Luego especificar y diseñar los cambios con pruebas antes de modificar datos o código.

### Riesgos

- Actualizar solo el nombre del archivo sin cambiar los guards de ruta dejaría CLIs funcionalmente incompatibles.
- Reescribir documentos OpenSpec archivados para cambiar rutas destruiría la fidelidad histórica; deben conservarse como historial.
- Un catálogo territorial no oficial, sin versión o sin excepciones puede introducir falsos inválidos.
- Los candidatos de duplicados parciales pueden representar sedes, jornadas o modalidades distintas; requieren decisión documentada.
- El PDF puede ser un artefacto generado grande; debe verificarse contra el Markdown fuente y tratarse aparte del presupuesto autorado.
- Borrar `.venv/` sin coordinación deteriora el flujo inmediato, aunque sea reconstruible.

### Decisiones aún necesarias

1. Confirmar si la limpieza local incluye `.venv/` ahora o si se conserva hasta terminar la entrega.
2. Aprobar la fuente oficial/versionada para el catálogo territorial y cómo registrar excepciones administrativas.
3. Acordar la herramienta reproducible para generar el PDF del Code Book.
4. Definir el criterio de disposición para cada duplicado parcial revisado (conservar, fusionar o excluir) y quién lo aprueba.

### Listo para propuesta

Sí. La propuesta debe formalizar el cambio de contrato hacia `data/source/`, conservar HTML/manifest como procedencia, retirar únicamente candidatos seguros, establecer `docs/planificacion.md` como plan vigente y convertir las asignaciones anteriores en requisitos verificables y PRs encadenados cuando excedan el presupuesto de 400 líneas.
