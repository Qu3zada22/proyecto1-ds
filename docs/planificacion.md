# Planificación del Proyecto 1: Obtención y Limpieza de Datos

Este documento divide el proyecto en **slices de trabajo**. Cada slice tiene un objetivo claro, entregables verificables y criterios mínimos de aceptación. La idea es avanzar de forma ordenada: primero preservar la data cruda, después diagnosticar, luego planificar la limpieza y finalmente ejecutar, validar y documentar.

## Resumen de slices

| Slice | Fase | Objetivo principal | Entregable principal |
| --- | --- | --- | --- |
| 0 | Preparación | Definir estructura reproducible del proyecto | Carpetas base y convenciones |
| 1 | Obtención | Resguardar datos crudos oficiales del MINEDUC | HTML crudos `html-form` en `data/raw/` |
| 2 | Consolidación inicial | Extraer tablas crudas sin limpiarlas todavía | CSV intermedio en `data/interim/` |
| 3 | Diagnóstico | Medir el estado real de la data cruda con código | `docs/diagnostico.md` y tablas |
| 4 | Plan de limpieza | Definir reglas antes de modificar datos | `docs/plan_limpieza.md` |
| 5 | Limpieza base | Normalizar nulos, tipos y texto | Dataset limpio preliminar |
| 6 | Consistencia y duplicados | Detectar dominios inválidos, duplicados exactos y parciales | Bitácora de decisiones |
| 7 | Validación automática | Probar que el dataset final cumple reglas de calidad | Script/reporte de validación |
| 8 | Reporte comparativo | Demostrar mejora antes vs. después | `docs/reporte_calidad.md` |
| 9 | Code Book | Documentar variables, dominios, fuente y tratamientos | `docs/codebook.md` y PDF |
| 10 | Entrega final | Consolidar archivos finales del proyecto | CSV limpio final y repositorio ordenado |

---

## Slice 0: Preparación del proyecto

### Objetivo

Crear una estructura de trabajo clara, reproducible y fácil de revisar.

### Tareas principales

- Crear carpetas para datos crudos, intermedios, limpios, documentación, scripts y salidas.
- Definir nombres consistentes para archivos.
- Separar claramente datos crudos de datos modificados.
- Acordar que ningún archivo en `data/raw/` debe modificarse manualmente.

### Estructura sugerida

```txt
data/
  raw/
  interim/
  clean/
docs/
  instrucciones.md
  planificacion.md
  diagnostico.md
  plan_limpieza.md
  reporte_calidad.md
  codebook.md
outputs/
  tablas/
  reportes/
src/ o notebooks/
  01_obtencion.py
  02_diagnostico.py
  03_limpieza.py
  04_validacion.py
  05_export_final.py
```

### Criterios de aceptación

- Existe una estructura de carpetas entendible.
- Los datos crudos tienen una ubicación única.
- El proyecto puede ser navegado por otra persona sin explicación verbal.

---

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
- Exportar un CSV intermedio en `data/interim/` sin limpiar ni normalizar valores.

### Entregables

- Dataset unido preliminar, por ejemplo `data/interim/establecimientos_diversificado_raw_unificado.csv`.

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

## Slice 5: Limpieza base

### Objetivo

Aplicar las transformaciones fundamentales para obtener una versión limpia preliminar.

### Tareas principales

- Convertir cadenas vacías, espacios, `N/A`, `NULL`, `-`, `.`, `Sin dato` y equivalentes a valores faltantes consistentes.
- Corregir tipos de datos.
- Normalizar texto: espacios, mayúsculas/minúsculas, tildes y caracteres invisibles.
- Estandarizar nombres de columnas si es necesario.
- Registrar cada transformación en una bitácora.

### Entregables

- Dataset limpio preliminar en `data/interim/` o `data/clean/`.
- Bitácora de transformaciones.

### Criterios de aceptación

- Los textos no tienen espacios al inicio o al final.
- Los tipos de datos son coherentes con el significado de cada variable.
- Los valores faltantes se representan de forma uniforme.

---

## Slice 6: Consistencia, dominios y duplicados

### Objetivo

Resolver problemas más profundos: categorías inconsistentes, valores inválidos, consistencia cruzada y duplicados.

### Tareas principales

- Validar departamentos y municipios contra un catálogo oficial o lista controlada.
- Revisar teléfonos, códigos y campos con formato esperado.
- Detectar duplicados exactos.
- Detectar posibles duplicados parciales usando similitud de cadenas.
- Documentar cada decisión: conservar, corregir, fusionar o descartar.
- Revisar contradicciones entre variables relacionadas.

### Entregables

- Bitácora de duplicados y decisiones.
- Dataset limpio candidato.

### Criterios de aceptación

- No se eliminan duplicados parciales automáticamente sin análisis.
- Las categorías equivalentes quedan unificadas.
- Los valores inválidos detectados en el diagnóstico quedan corregidos o documentados.

---

## Slice 7: Validación automática de calidad

### Objetivo

Comprobar con pruebas automáticas que el dataset limpio cumple los estándares definidos.

### Tareas principales

- Crear validaciones para duplicados exactos.
- Validar ausencia de espacios iniciales/finales.
- Validar formato de teléfonos si existe esa variable.
- Validar departamentos y municipios.
- Validar tipos de datos esperados.
- Validar categorías normalizadas.
- Validar ausencia de valores inválidos detectados previamente.

### Entregables

- Script de validación, por ejemplo `src/04_validacion.py`.
- Reporte de validación en `outputs/reportes/`.

### Criterios de aceptación

- Las pruebas pueden ejecutarse nuevamente desde cero.
- El resultado indica claramente qué pasó y qué falló si hay errores.
- El dataset limpio pasa las reglas críticas de calidad.

---

## Slice 8: Reporte de calidad antes vs. después

### Objetivo

Demostrar cuantitativamente la mejora lograda por la limpieza.

### Tareas principales

- Comparar registros antes y después.
- Comparar variables antes y después.
- Comparar valores faltantes.
- Comparar duplicados exactos y posibles duplicados.
- Comparar formatos inconsistentes.
- Comparar categorías inconsistentes.
- Resumir errores corregidos.

### Entregables

- `docs/reporte_calidad.md`.
- Tabla comparativa antes/después.

### Criterios de aceptación

- El reporte usa métricas calculadas por código.
- Cualquier cambio en número de filas o columnas está justificado.
- La mejora no se describe solo con palabras: se demuestra con números.

---

## Slice 9: Libro de códigos

### Objetivo

Documentar el dataset final para que cualquier persona pueda entenderlo y reutilizarlo.

### Tareas principales

- Describir cada variable.
- Indicar tipo de dato final.
- Indicar dominio permitido.
- Listar valores posibles cuando aplique.
- Documentar tratamiento aplicado durante limpieza.
- Documentar variables derivadas si existen.
- Incluir fecha exacta de extracción.
- Incluir fuente de origen.
- Indicar versión del conjunto limpio.

### Entregables

- `docs/codebook.md`.
- Versión final en PDF.

### Criterios de aceptación

- Cada variable del dataset final aparece en el Code Book.
- El documento explica qué se hizo con cada variable durante la limpieza.
- La fuente, fecha de extracción y versión del dataset están documentadas.

---

## Slice 10: Entrega final

### Objetivo

Preparar los materiales finales solicitados por la rúbrica.

### Tareas principales

- Exportar un único CSV limpio y unificado.
- Revisar que el pipeline pueda ejecutarse de principio a fin.
- Confirmar que el repositorio contiene código, datos, documentación y entregables.
- Generar PDF final del Code Book.
- Revisar contribuciones del equipo en repositorio y documentación.

### Entregables finales

- Código fuente del pipeline en `.py`, `.ipynb`, `.r` o `.rmd`.
- Repositorio completo.
- Libro de códigos en Markdown o Google Docs.
- Libro de códigos en PDF.
- Dataset final limpio en `.csv`.

### Criterios de aceptación

- Existe un archivo único en `data/clean/` listo para análisis.
- El proceso completo es reproducible.
- Los documentos finales explican qué se hizo, por qué se hizo y cómo verificarlo.

---

## Orden recomendado de ejecución

1. Slice 0: Preparación.
2. Slice 1: Obtención.
3. Slice 2: Consolidación inicial.
4. Slice 3: Diagnóstico.
5. Slice 4: Plan de limpieza.
6. Slice 5: Limpieza base.
7. Slice 6: Consistencia y duplicados.
8. Slice 7: Validación automática.
9. Slice 8: Reporte antes/después.
10. Slice 9: Code Book.
11. Slice 10: Entrega final.

## Regla de oro del proyecto

Cada modificación debe poder responder estas preguntas:

1. ¿Qué problema tenía la variable?
2. ¿Cuántos registros estaban afectados?
3. ¿Qué regla se aplicó?
4. ¿Por qué esa regla es razonable?
5. ¿Qué riesgo tiene esa transformación?

Si una limpieza no puede responder eso, todavía no está suficientemente justificada.
