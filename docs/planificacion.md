# Plan actual de cierre del Proyecto 1

Este es el plan autoritativo vigente frente a `docs/instrucciones.md`. Distingue evidencia ya disponible de trabajo futuro: **planificar no equivale a implementar**.

## Contrato y estado ejecutivo

- Fuente canónica: `data/source/establecimientos_diversificado_mineduc.csv`.
- Salida limpia actual: `data/processed/establecimientos_diversificado_limpio.csv`.
- Procedencia inmutable: 23 HTML en `data/raw/` y `data/raw/manifest.json`.
- Territorio: catálogo reproducible desde un **espejo/conversión comunitaria** fijado; la fuente primaria declarada es INE, Censo 2018. El espejo no es una publicación primaria oficial.
- Resultado territorial: 11,867×21; 2 variantes tipográficas (19 filas) corregidas y 7 parejas (145 filas) conservadas con `decision=revisar` y códigos provisionales.
- Trabajo restante: automatización completada; pendientes institucionales: 718 `duplicado_probable`, 260 pares ambiguos, 245 teléfonos sospechosos vigentes y 145 filas territoriales. Los 201 casos telefónicos del diagnóstico inicial son hallazgos históricos agregados y no permiten correspondencia registro por registro.
- Decisiones aprobadas: `data/decisions/duplicados_aprobados.csv` confirma 11 pares independientes sin fusionarlos y `data/decisions/telefonos_aprobados.csv` autoriza 6 normalizaciones exactas ya aplicadas. Las recomendaciones post-decisión conservan 978 pares y 245 teléfonos pendientes.
- Resumen verificable de la matriz: **23 `Completado`, 6 `Parcial`, 0 `Faltante`, 0 `Incierto`**.
- Resultado institucional: **NO APTO PARA CIERRE INSTITUCIONAL**; las recomendaciones no equivalen a aprobación.
- Estados: **Completado** (aceptación demostrada), **Parcial** (hay evidencia, queda brecha), **Faltante** (sin entregable aceptable) e **Incierto** (requiere una decisión o fuente).
- Todo elemento marcado **Planificado/no implementado** permanece fuera del estado actual.

## Matriz de requisitos

| ID | Fuente | Requisito | Estado | Evidencia actual | Brecha | Responsable | Dependencia | Aceptación | Unidad |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Paso 1.1 | Descargar cobertura nacional hasta Diversificado | Completado | 23 HTML + manifest | Ninguna del alcance preservado | Jonathan | MINEDUC | 23 departamentos trazables y hashes válidos | U1 Fuente |
| R2 | Paso 1.2 | Guardar datos crudos en CSV | Completado | CSV canónico 11,867×20 | Ninguna | Jonathan | R1 | Regeneración byte-idéntica desde HTML | U1 Fuente |
| R3a | Paso 2.3a | Filas y columnas por código | Completado | `resumen_dataset.csv` | Ninguna | Anggie | R2 | 11,867×20 reproducible | U2 Diagnóstico |
| R3b | Paso 2.3b | Tipos por variable | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Las 20 variables tienen tipo reportado | U2 Diagnóstico |
| R3c | Paso 2.3c | Faltantes: cantidad y porcentaje | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Conteos y porcentajes para 20 variables | U2 Diagnóstico |
| R3d | Paso 2.3d | Únicos por columna | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Conteo para 20 variables | U2 Diagnóstico |
| R3e | Paso 2.3e | Duplicados exactos | Completado | `duplicados_exactos.csv` | Ninguna | Anggie | R2 | Conteo reproducible: 0 | U2 Diagnóstico |
| R3f | Paso 2.3f | Dominios e inconsistencias | Completado | `dominios_observados.csv`; catálogo reproducible; 7 parejas/145 filas `revisar` | Ninguna para detección | Iris | Espejo fijado; INE, Censo 2018 como fuente primaria declarada | Hallazgos sustentados sin presentar el espejo como publicación primaria | U2 Diagnóstico |
| R3g | Paso 2.3g | Formatos inconsistentes | Completado | `problemas_potenciales.csv` | Ninguna para diagnóstico inicial | Anggie | R2 | Hallazgos y conteos regenerables | U2 Diagnóstico |
| R3h | Paso 2.3h | Problemas potenciales explícitos | Completado | 18 problemas en diagnóstico | Ninguna para diagnóstico inicial | Anggie | R3a–R3g | Tabla y resumen coinciden | U2 Diagnóstico |
| R4a | Paso 3.4a | Problema por variable | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Cada variable/problema está cubierto | U3 Plan |
| R4b | Paso 3.4b | Regla exacta y justificación | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Regla previa a transformación | U3 Plan |
| R4c | Paso 3.4c | Riesgo de cada regla | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Cada regla declara riesgo | U3 Plan |
| R5a | Paso 4.5a | Nulos, vacíos y marcadores | Completado | CSV limpio + bitácora: marcadores inequívocos normalizados | Ninguna para reglas aplicadas | Anggie | Reconciliación | Marcadores resueltos y auditados | U4 Limpieza |
| R5b | Paso 4.5b | Tipos correctos | Completado | `validacion_final.csv`: esquema semántico esperado de 21 variables | Ninguna; identificadores, códigos y teléfonos se preservan como texto | Jonathan | R5a–R5h | Control `tipos_esperados` cumple | U4 Limpieza |
| R5c | Paso 4.5c | Normalización de texto | Completado | Mayúsculas, NBSP, invisibles (NFC) y marcadores normalizados; bitácora | Ninguna para reglas deterministas | Iris | Bitácora | Cero bordes; decisiones trazadas | U4 Limpieza |
| R5d | Paso 4.5d | Categorías consistentes | Completado | Vocabulario controlado verificado; territorio validado contra catálogo INE | Ninguna | Iris | R3f | Variantes justificadas y probadas | U4 Limpieza |
| R5e | Paso 4.5e | Formatos uniformes | Parcial | 6 normalizaciones exactas aprobadas y aplicadas; 245 pendientes: 196 conservar/documentar y 49 requieren fuente | Falta aceptación institucional de los 245 teléfonos restantes | Anggie | Revisión humana | Formatos aceptados o excepciones aprobadas | U4 Limpieza |
| R5f | Paso 4.5f | Valores inválidos | Parcial | 390 hallazgos vigentes: 245 teléfonos + 145 filas territoriales; 7 aliases sin renombrar | Aceptación telefónica y territorial pendiente | Iris | R5e | Territorio trazado; teléfonos quedan pendientes | U4 Limpieza |
| R5g | Paso 4.5g | Duplicados exactos y parciales | Parcial | Exactos=0; 11 `independiente_confirmado`; 978 pendientes: 718 probables + 260 ambiguos | Obtener fuente institucional para los 978 pendientes; 0 fusionados | Anggie | Detección hecha | Cada candidato confirmado institucionalmente; sin fusión automática | U4 Limpieza |
| R5h | Paso 4.5h | Consistencia cruzada | Completado | `validacion_territorial.md`; 329 válidas, 22 por regla y 7 parejas/145 filas `revisar` | Ninguna para el alcance de detección de Iris | Iris | Catálogo reproducible | Pendientes preservados, sin autocorrección inventada | U4 Limpieza |
| R5i | Paso 4.5i | Variables derivadas justificadas | Completado | 4 variables territoriales documentadas; `departamento_codigo` y `municipio_codigo` marcadas como derivadas | Ninguna para la sección de Iris | Iris | Code Book territorial | Método, dominio, provisionalidad y utilidad documentados | U4 Limpieza |
| R6 | Control 6 | Bitácora de transformaciones | Completado | `bitacora_limpieza.csv` + `reporte_limpieza_base.csv`; triage sin fusión | Ninguna para transformaciones ejecutadas; decisiones futuras se agregarán al aprobarse | Anggie | R5 | Una fila por transformación aplicada | U4 Limpieza |
| R7 | Control 7 | Validación automática final | Parcial | Mecanismo completo: exactamente 7 controles; 3 cumple, 4 requieren revisión, 0 falla | Resolver o aceptar institucionalmente los cuatro controles en revisión | Jonathan | R4–R6 | Los siete controles cumplen o tienen excepción formal aceptada | U5 Validación |
| R8 | Control 8 | Comparación antes/después | Completado | `reporte_calidad_antes_despues.csv`: exactamente 10 métricas, con pendientes integrados | Ninguna para el reporte tabular; pendientes operativos siguen abiertos | Jonathan | R7 | Métricas, porcentajes, unidades y evidencia regenerables | U6 Reporte |
| R9 | Cierre 9 | Único conjunto limpio final | Parcial | CSV único 11,867×21, sin adición/eliminación de filas | R5e, R5f, R5g y R7 conservan aceptación institucional pendiente | Jonathan | R5–R8 | Archivo único con controles aceptados; automatización sola no basta | U7 Dataset |
| R10 | Cierre 10 | Code Book completo | Completado | `docs/code_book.md` con 21 variables + `docs/code_book.pdf` reproducible y validado | Ninguna para documentación; no cierra pendientes del dataset | Jonathan | R5–R9 | Markdown y PDF reproducibles, completos y legibles | U8 Code Book |
| RE | Material final | Código, repositorio, área, PDF y CSV | Parcial | Cinco materiales disponibles; auditoría interna documenta hashes y comandos | CSV final sin aceptación institucional mientras R9 siga parcial | Jonathan | R7–R10 | Cinco materiales reproducibles y dataset institucionalmente aceptado | U9 Entrega |
| RT | Trabajo en equipo | Contribución significativa visible | Completado | Historial publicado: Anggie `b8eb3de`/`7bac604`, Iris `b314998`/`bdf8736` y Jonathan `c871bd7`; cada integrante aporta una sección del Code Book | Ninguna | Equipo | Unidades anteriores | Cada persona con commit publicado y sección Code Book | Historial Git |

## Asignaciones y contribución visible

| ID | Persona | Entregable | Aceptación | Aporte Code Book | Evidencia Git | Dependencias |
|---|---|---|---|---|---|---|
| A-Anggie | Anggie | Reglas y triage; 11 independientes y 6 teléfonos aprobados; 978 pares y 245 teléfonos pendientes | Flujo reproducible; decisiones versionadas; sin borrado ni fusión | Code Book: procedencia, métricas y tratamientos — `docs/code_book/variables_anggie.md` | Commits publicados `b8eb3de`, `7bac604` | CSV alterno; diagnóstico; revisión institucional/manual |
| A-Iris | Iris | Catálogo reproducible y consistencia departamento–municipio | 7 parejas/145 filas trazadas como `revisar`; 2 variantes/19 filas justificadas | Code Book territorial completo: dominios, valores y 2 variables derivadas | Commits publicados `b314998`, `bdf8736`; sección propia publicada | Espejo fijado; INE, Censo 2018 como fuente primaria declarada |
| A-Jonathan | Jonathan | Validación, reporte integral, Code Book Markdown/PDF y auditoría interna | Siete controles, 10 métricas y maestro de 21 variables reproducibles | Code Book maestro: ensamblaje, versión y pendientes | Commit de integración publicado `c871bd7` | Entregas de Anggie e Iris |

## Evidencia detallada de fases previas

Las fases siguientes sustentan los estados completados de la matriz; los criterios futuros se controlan exclusivamente mediante la matriz y la ruta crítica.

## Slice 1: Obtención y resguardo de datos

### Objetivo

Resguardar los datos de establecimientos educativos del país hasta nivel **Diversificado** desde la fuente oficial del MINEDUC. No se encontró un endpoint CSV directo; la fuente oficial preservada son artefactos HTML `html-form`.

### Tareas principales

- Capturar los resultados oficiales del formulario MINEDUC por departamento.
- Guardar cada artefacto crudo HTML `html-form` sin editarlo.
- Registrar la fecha exacta de extracción.
- Registrar URL/fuente de origen.
- Evitar modificaciones manuales sobre los archivos descargados.

### Entregables

- Artefactos HTML oficiales en `data/raw/` y `manifest.json` con método, cobertura y checksum.
- Registro de fuente y fecha de extracción en el Code Book o documento auxiliar.

### Criterios de aceptación

- Los artefactos crudos existen y pueden abrirse desde código.
- Se puede explicar de dónde salió cada archivo.
- La data cruda está preservada sin limpieza manual.

---

## Slice 2: Consolidación inicial sin limpieza

### Objetivo

Extraer estructuralmente las tablas de los artefactos crudos en un solo dataset intermedio, sin corregir todavía los problemas de calidad.

### Tareas principales

- Leer los HTML oficiales `html-form` preservados mediante código.
- Revisar que las tablas extraídas compartan estructura compatible.
- Agregar una variable de trazabilidad si hace falta, por ejemplo `archivo_origen` o `departamento_origen`.
- Exportar la fuente canónica en `data/source/` sin limpiar ni normalizar valores.

### Entregables

- Dataset unido preliminar en `data/source/establecimientos_diversificado_mineduc.csv`.

### Criterios de aceptación

- El dataset intermedio contiene todos los registros descargados.
- No se han aplicado reglas de limpieza todavía.
- Existe trazabilidad mínima hacia la fuente original.

---

## Slice 3: Diagnóstico inicial de calidad

### Objetivo

Medir con código qué tan dañada está la data antes de modificarla.

### Tareas principales

- Calcular número de filas y columnas.
- Identificar tipo de dato asignado a cada variable.
- Calcular valores faltantes por variable: cantidad y porcentaje.
- Calcular valores únicos por columna.
- Detectar duplicados exactos.
- Identificar valores fuera de dominio.
- Detectar formatos inconsistentes.
- Documentar problemas potenciales de calidad.

### Entregables

- `docs/diagnostico.md`.
- Tablas generadas por código en `outputs/tablas/`.
- Resumen de problemas por variable.

### Criterios de aceptación

- Todas las métricas exigidas por las instrucciones están calculadas con código.
- El diagnóstico no depende de observaciones manuales sueltas.
- Cada problema importante tiene evidencia cuantitativa.

---

## Slice 4: Plan de limpieza

### Objetivo

Definir la estrategia de limpieza antes de tocar los datos.

### Tareas principales

- Crear una tabla por variable con problema, regla, justificación y riesgo.
- Definir cómo se tratarán valores nulos y vacíos.
- Definir reglas para texto, mayúsculas, tildes, espacios y caracteres especiales.
- Definir dominios válidos para departamentos, municipios, teléfonos, códigos y categorías.
- Definir criterios para duplicados exactos y parciales.

### Entregables

- `docs/plan_limpieza.md`.

### Criterios de aceptación

- Cada transformación futura tiene una justificación previa.
- Los riesgos están documentados.
- No hay limpiezas “porque sí”. Cada regla responde a un problema encontrado.

---

## Artefactos ya implementados (esta iteración)

- **Catálogo territorial reproducible**: `data/reference/catalogo_territorial.csv` (22 departamentos, 340 municipios), generado desde un espejo/conversión comunitaria fijado; INE, Censo 2018 es la fuente primaria declarada.
- **Normalización de texto/categorías** en `src/proyecto1_ds/cleaning.py`: mayúsculas, NBSP, caracteres invisibles (NFC) y marcadores de ausencia, con bitácora.
- **Enriquecimiento territorial** en `src/proyecto1_ds/enrichment.py`: variables derivadas `departamento_codigo` y `municipio_codigo` (códigos INE) y corrección trazable de 2 typos; cableado en `scripts/limpiar_dataset.py`.
- **Detección de duplicados parciales** en `src/proyecto1_ds/duplicates.py` (`scripts/detectar_duplicados.py`): similitud RapidFuzz con corroboración de sede y oferta; salida `outputs/tablas/duplicados_parciales.csv` y `outputs/reportes/duplicados_parciales.md`. Sin borrado automático.
- **Validación territorial** en `src/proyecto1_ds/territorial.py` (`scripts/validar_territorio.py`): consistencia departamento–municipio contra catálogo; salida `outputs/tablas/inconsistencias_territoriales.csv` y `outputs/reportes/validacion_territorial.md`.
- **Recomendaciones de pendientes** en `src/proyecto1_ds/pending_review.py` (`scripts/revisar_pendientes.py`): valida linaje y publica tres tablas más `outputs/reportes/revision_pendientes.md`; no modifica ni fusiona datasets.

## Ruta crítica y unidades de entrega

```text
fuente canónica (hecho) → catálogo territorial (hecho) → normalización + códigos INE (hecho)
→ duplicados: 11 independientes aprobados; confirmar 718 probables + revisar 260 ambiguos
→ validación + reporte + Code Book Markdown/PDF (automatizados y publicados) → aceptación institucional
```

1. **U4 — Limpieza automatizada:** reglas, bitácora y triage reproducibles; quedan confirmaciones institucionales.
2. **U5/U6 — Validación y reporte:** mecanismos completos; cuatro controles conservan `requiere_revision`.
3. **U8 — Code Book:** Markdown y PDF reproducibles con las 21 variables.
4. **U9 — Entrega:** cinco materiales publicados; el CSV espera aceptación institucional.

## Control de cierre

- Ninguna unidad puede declararse completa solo por estar automatizada o descrita aquí.
- Cada aceptación debe apuntar a código, prueba, dato o documento versionado y al commit de su responsable.
- No se modifica la procedencia para resolver una discrepancia; se registra y se revisa.
- La entrega institucional se bloquea mientras R5e, R5f, R5g, R7, R9 o RE no estén **Completado**. R10 y RT completos acreditan documentación y contribución publicada, no la aceptación del dataset.
