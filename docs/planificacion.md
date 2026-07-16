# Plan actual de cierre del Proyecto 1

Este es el plan autoritativo vigente frente a `docs/instrucciones.md`. Distingue evidencia ya disponible de trabajo futuro: **planificar no equivale a implementar**.

## Contrato y estado ejecutivo

- Fuente canónica: `data/source/establecimientos_diversificado_mineduc.csv`.
- Salida limpia actual: `data/processed/establecimientos_diversificado_limpio.csv`.
- Procedencia inmutable: 23 HTML en `data/raw/` y `data/raw/manifest.json`.
- Estados: **Completado** (aceptación demostrada), **Parcial** (hay evidencia, queda brecha), **Faltante** (sin entregable aceptable) e **Incierto** (requiere una decisión o fuente).
- Todo elemento marcado **Planificado/no implementado** permanece fuera del estado actual.

## Matriz de requisitos

| ID | Fuente | Requisito | Estado | Evidencia actual | Brecha | Responsable | Dependencia | Aceptación | PR |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Paso 1.1 | Descargar cobertura nacional hasta Diversificado | Completado | 23 HTML + manifest | Ninguna del alcance preservado | Jonathan | MINEDUC | 23 departamentos trazables y hashes válidos | PR1 |
| R2 | Paso 1.2 | Guardar datos crudos en CSV | Completado | CSV canónico 11,867×20 | Ninguna | Jonathan | R1 | Regeneración byte-idéntica desde HTML | PR1 |
| R3a | Paso 2.3a | Filas y columnas por código | Completado | `resumen_dataset.csv` | Ninguna | Anggie | R2 | 11,867×20 reproducible | Hecho |
| R3b | Paso 2.3b | Tipos por variable | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Las 20 variables tienen tipo reportado | Hecho |
| R3c | Paso 2.3c | Faltantes: cantidad y porcentaje | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Conteos y porcentajes para 20 variables | Hecho |
| R3d | Paso 2.3d | Únicos por columna | Completado | `diagnostico_columnas.csv` | Ninguna | Anggie | R2 | Conteo para 20 variables | Hecho |
| R3e | Paso 2.3e | Duplicados exactos | Completado | `duplicados_exactos.csv` | Ninguna | Anggie | R2 | Conteo reproducible: 0 | Hecho |
| R3f | Paso 2.3f | Dominios e inconsistencias | Parcial | `dominios_observados.csv` | Falta catálogo oficial territorial | Iris | Catálogo versionado | Inválidos sustentados, no inferidos | PR4 |
| R3g | Paso 2.3g | Formatos inconsistentes | Completado | `problemas_potenciales.csv` | Ninguna para diagnóstico inicial | Anggie | R2 | Hallazgos y conteos regenerables | Hecho |
| R3h | Paso 2.3h | Problemas potenciales explícitos | Completado | 18 problemas en diagnóstico | Ninguna para diagnóstico inicial | Anggie | R3a–R3g | Tabla y resumen coinciden | Hecho |
| R4a | Paso 3.4a | Problema por variable | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Cada variable/problema está cubierto | Hecho |
| R4b | Paso 3.4b | Regla exacta y justificación | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Regla previa a transformación | Hecho |
| R4c | Paso 3.4c | Riesgo de cada regla | Completado | `docs/plan_limpieza.md` | Ninguna | Jonathan | R3 | Cada regla declara riesgo | Hecho |
| R5a | Paso 4.5a | Nulos, vacíos y marcadores | Parcial | CSV limpio + bitácora | Faltan excepciones finales | Anggie | Reconciliación | Marcadores resueltos y auditados | PR5 |
| R5b | Paso 4.5b | Tipos correctos | Parcial | Limpieza conservadora | Falta validación final de tipos | Jonathan | R5a–R5h | Tipos esperados pasan pruebas | PR6 |
| R5c | Paso 4.5c | Normalización de texto | Parcial | Espacios/NBSP normalizados | Falta revisión semántica final | Anggie | Bitácora | Cero bordes; decisiones trazadas | PR5 |
| R5d | Paso 4.5d | Categorías consistentes | Parcial | Categorías conservadas | Falta catálogo y resolución territorial | Iris | R3f | Variantes justificadas y probadas | PR4 |
| R5e | Paso 4.5e | Formatos uniformes | Parcial | Formatos diagnosticados | Faltan excepciones telefónicas | Anggie | Revisión humana | Teléfonos/códigos con regla y excepciones | PR5 |
| R5f | Paso 4.5f | Valores inválidos | Parcial | Casos potenciales reportados | Falta catálogo y revisión telefónica | Iris | R3f, R5e | Cero inválidos conocidos o excepción | PR5 |
| R5g | Paso 4.5g | Duplicados exactos y parciales | Faltante | Exactos=0; parciales diferidos | Falta reconciliación y bitácora manual | Anggie | CSV alterno accesible | Candidatos revisados; sin borrado automático | PR5 |
| R5h | Paso 4.5h | Consistencia cruzada | Faltante | Limitación documentada | Falta departamento–municipio oficial | Iris | Catálogo versionado | Todas las parejas válidas o exceptuadas | PR4 |
| R5i | Paso 4.5i | Variables derivadas justificadas | Incierto | No se declararon derivadas finales | Decidir necesidad y documentarla | Iris | Esquema final | Code Book declara derivadas o “ninguna” | PR7 |
| R6 | Control 6 | Bitácora de transformaciones | Parcial | `bitacora_limpieza.csv` | Falta incorporar decisiones futuras | Anggie | R5 | Una fila por transformación/decisión | PR5 |
| R7 | Control 7 | Validación automática final | Faltante | Pruebas del pipeline, no cierre completo | Falta validación final de toda la rúbrica | Jonathan | R4–R6 | Suite prueba siete controles y emite reporte | PR6 |
| R8 | Control 8 | Comparación antes/después | Parcial | CSV comparativo preliminar | Falta reporte de calidad completo | Jonathan | R7 | Diez métricas justificadas y regenerables | PR6 |
| R9 | Cierre 9 | Único conjunto limpio final | Parcial | CSV limpio actual 11,867×19 | Decisiones territoriales/duplicados pendientes | Jonathan | R5–R8 | Archivo único pasa validación final | PR7 |
| R10 | Cierre 10 | Code Book completo | Faltante | Sin Markdown/PDF final | Faltan metadatos por variable y ensamblaje | Jonathan | R5–R9 | 19 variables + procedencia + versión; PDF reproducible | PR7 |
| RE | Material final | Código, repositorio, área, PDF y CSV | Faltante | Código/repositorio/CSV parciales | Faltan Code Book, README y auditoría de entrega | Jonathan | R7–R10 | Cinco materiales enlazados y reproducibles | PR7 |
| RT | Trabajo en equipo | Contribución significativa visible | Parcial | Historial Git y docs existentes | Falta cierre verificable por integrante | Equipo | Asignaciones siguientes | Cada persona: commit identificable + sección Code Book | PR4–PR7 |

## Asignaciones y contribución visible

| ID | Persona | Entregable | Aceptación | Aporte Code Book | Evidencia Git | Dependencias |
|---|---|---|---|---|---|---|
| A-Anggie | Anggie | Reconciliación, métricas, duplicados parciales y excepciones telefónicas | Comando reproducible; bitácora sin borrado automático; excepciones justificadas | Code Book: procedencia, métricas y tratamientos | Uno o más commit identificables que modifiquen evidencia y su sección | CSV alterno; diagnóstico; revisión humana |
| A-Iris | Iris | Catálogo territorial y consistencia departamento–municipio | Fuente oficial versionada; validación legible por máquina; excepciones trazadas | Code Book: dominios, valores posibles y variables derivadas | Uno o más commit identificables que modifiquen catálogo/validación y su sección | Fuente oficial; esquema final |
| A-Jonathan | Jonathan | Integración, validación final, reporte, README, Markdown/PDF y auditoría | Suite verde; reporte completo; PDF reproducible; checklist de entrega | Code Book: ensamblaje, versión y tratamientos finales | Uno o más commit identificables que modifiquen integración y su sección | Entregas de Anggie e Iris |

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

## Ruta crítica y próximos PR

```text
fuente canónica (hecho) → catálogo territorial → reconciliación/duplicados y teléfonos
→ validación final → reporte de calidad completo → Code Book Markdown/PDF → README → auditoría de entrega
```

1. **PR4 — Planificado/no implementado:** Iris entrega catálogo territorial, consistencia cruzada y dominios del Code Book.
2. **PR5 — Planificado/no implementado:** Anggie cierra reconciliación de fuente, duplicados parciales, excepciones telefónicas, métricas, bitácora y procedencia.
3. **PR6 — Planificado/no implementado:** Jonathan integra validación final y reporte de calidad completo.
4. **PR7 — Planificado/no implementado:** equipo cierra dataset; Jonathan ensambla Code Book Markdown/PDF, README y auditoría de entrega.

## Control de cierre

- Ningún PR futuro puede declararse completo solo por estar descrito aquí.
- Cada aceptación debe apuntar a código, prueba, dato o documento versionado y al commit de su responsable.
- No se modifica la procedencia para resolver una discrepancia; se registra y se revisa.
- La entrega se bloquea mientras R7, R10, RE o RT no estén **Completado**.
