# Plan de limpieza de datos crudos MINEDUC

## Resumen ejecutivo

Este documento corresponde al **Paso 3: Elaboración del Plan de Limpieza** de `docs/instrucciones.md`. Su propósito es convertir el diagnóstico de datos crudos en reglas propuestas por variable antes de modificar cualquier dato.

Este plan es **solo planificación** (Paso 3): no ejecuta limpieza por sí mismo. La ejecución posterior vive en el pipeline (`src/proyecto1_ds/`): normalización y bitácora; catálogo desde un espejo/conversión comunitaria fijado (INE, Censo 2018 como fuente primaria declarada); 2 variantes tipográficas/19 filas corregidas; 7 parejas/145 filas con `decision=revisar`; y triage de 1,355 pares sin fusión automática. Permanecen pendientes la confirmación institucional de 718 `duplicado_probable`, la revisión de 271 pares ambiguos y las excepciones telefónicas/territoriales documentadas.

El dataset diagnosticado contiene 11,867 filas, 20 columnas y 0 duplicados exactos reportados. El diagnóstico identifica 18 problemas potenciales, incluyendo una columna con encabezado no separable (`<NBSP>`), faltantes, texto sospechoso, formatos telefónicos sospechosos, dominios territoriales no verificables y duplicados parciales diferidos.

## Fuentes de evidencia

- `docs/instrucciones.md`: rúbrica del Paso 3 y criterios de limpieza futura.
- `docs/diagnostico.md`: resumen narrativo del diagnóstico crudo y límites de no limpieza.
- `outputs/tablas/resumen_dataset.csv`: tamaño del dataset, duplicados exactos y estado del catálogo territorial.
- `outputs/tablas/diagnostico_columnas.csv`: tipos asignados, faltantes, porcentajes y cantidad de valores únicos por columna.
- `outputs/tablas/problemas_potenciales.csv`: problemas potenciales por variable y conteos asociados.
- `outputs/tablas/dominios_observados.csv`: valores frecuentes observados por variable.
- `outputs/tablas/duplicados_exactos.csv`: evidencia de duplicados exactos reportados.
- `data/source/establecimientos_diversificado_mineduc.csv`: fuente canónica unificada observada por el diagnóstico; este plan no la modifica.

## Criterios de clasificación

- `accionable`: regla propuesta determinística, reversible y de bajo riesgo con evidencia suficiente en el diagnóstico actual. Puede implementarse en una fase futura con pruebas.
- `diferida`: decisión que requiere catálogo oficial, diseño adicional o comparación posterior. No debe presentarse como corrección definitiva todavía.
- `manual`: decisión que requiere revisión humana para evitar pérdida semántica, por ejemplo nombres propios, teléfonos ambiguos o posibles duplicados parciales.
- `conservar`: variable sin problema fuerte reportado por el diagnóstico actual. Se conserva sin transformar por inercia, aunque puede validarse nuevamente en fases posteriores.

## Reglas globales propuestas

1. **Nulos y marcadores de ausencia**: en una futura limpieza, registrar como ausencia los valores vacíos, espacios, `<NBSP>` y marcadores explícitos como `"N/A"`, `"NULL"`, `"-"`, `"."`, `"Sin dato"` o secuencias de guiones solo cuando el contexto confirme que no codifican información útil.
2. **Texto**: aplicar normalización conservadora de espacios iniciales/finales, espacios múltiples y caracteres no separables. Mantener tildes, nombres propios, siglas y puntuación significativa salvo revisión manual.
3. **Tipos**: conservar las variables como texto cuando su formato sea identificador, categoría o valor administrativo. No convertir `CODIGO`, `DISTRITO`, `TELEFONO` ni códigos de archivo a número para evitar pérdida de ceros iniciales o separadores.
4. **Trazabilidad**: toda transformación futura debe registrar variable, problema, regla aplicada, conteo afectado, justificación, riesgo, fecha y fuente de evidencia.
5. **Duplicados**: no eliminar automáticamente. Los duplicados exactos se revisarán contra el reporte actual de 0 casos; los duplicados parciales requieren comparación por similitud y decisión humana antes de fusionar o descartar registros.

## Plan por variable/problema

| Variable | Problema | Regla propuesta | Justificación | Riesgo | Estado | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| `<NBSP>` | Encabezado vacío o compuesto por espacio no separable; columna con 11,867 faltantes y 100.00% de ausencia. | En una futura limpieza, eliminar la columna solo si se confirma que todos sus valores son ausencia y registrar la eliminación en la bitácora de transformaciones. | La columna no aporta contenido observado y fue reportada como encabezado sospechoso y faltante total. | Bajo: eliminar una columna completamente vacía es reversible si se conserva el crudo; riesgo de trazabilidad si no se documenta. | `accionable` | `diagnostico_columnas.csv` filas `<NBSP>`; `problemas_potenciales.csv` filas `encabezado_sospechoso` y `faltantes_detectados`; `dominios_observados.csv` valor vacío con frecuencia 11,867. |
| `DISTRITO` | 532 faltantes (4.48%) y formatos observados heterogéneos como `01-403`, `01-`, `01-99-0153`. | Mantener como texto; convertir espacios y marcadores de ausencia a nulo documentado; diferir validación de patrón hasta definir dominio oficial de distrito. | Tiene ceros iniciales y separadores significativos; convertir a número destruiría estructura. | Medio: validar patrón sin catálogo puede marcar distritos reales como inválidos. | `diferida` | `diagnostico_columnas.csv` fila `DISTRITO`; `problemas_potenciales.csv` fila `faltantes_detectados`; `dominios_observados.csv` valores frecuentes de distrito. |
| `DEPARTAMENTO` | Catálogo territorial no verificable; 23 valores únicos sin faltantes. | Diferir validación y estandarización territorial hasta contar con catálogo oficial; por ahora no declarar inválidos. | El diagnóstico explícitamente no encontró catálogo oficial. | Alto: corregir departamentos por intuición puede introducir errores administrativos. | `diferida` | `docs/diagnostico.md` limitación territorial; `resumen_dataset.csv` `catalogo_territorial=no verificable`; `problemas_potenciales.csv` fila `catalogo_no_verificable`; `dominios_observados.csv` valores de departamento. |
| `MUNICIPIO` | Catálogo territorial no verificable; 352 valores únicos sin faltantes, incluyendo valores como zonas capitalinas. | Diferir validación contra catálogo oficial y revisar consistencia cruzada con `DEPARTAMENTO` en la fase de limpieza. | El valor puede depender de reglas administrativas de MINEDUC y no solo de catálogo geográfico simple. | Alto: reclasificar municipios sin fuente oficial puede crear inconsistencias. | `diferida` | `docs/diagnostico.md`; `problemas_potenciales.csv` fila `catalogo_no_verificable`; `diagnostico_columnas.csv` fila `MUNICIPIO`; `dominios_observados.csv` valores frecuentes. |
| `ESTABLECIMIENTO` | 5 faltantes (0.04%) y 1,396 textos sospechosos con espacios, caracteres no separables o variaciones textuales. | Normalizar espacios y caracteres invisibles de forma conservadora; no unificar nombres ni siglas sin revisión manual. | Los nombres de establecimientos son identificadores semánticos y pueden diferir por tildes, siglas o razón social. | Medio: sobre-normalizar puede fusionar establecimientos distintos o alterar nombres oficiales. | `manual` | `diagnostico_columnas.csv` fila `ESTABLECIMIENTO`; `problemas_potenciales.csv` filas `faltantes_detectados` y `texto_sospechoso`; `dominios_observados.csv` valores como variantes de INED. |
| `DIRECCION` | 81 faltantes (0.68%) y 485 textos sospechosos. | Convertir marcadores de ausencia a nulo documentado y normalizar espacios; preservar abreviaturas, numeración, guiones y puntuación significativa. | Las direcciones admiten abreviaturas y formatos libres; una regla agresiva puede destruir ubicación. | Medio: remover signos o palabras puede perder información de dirección. | `manual` | `diagnostico_columnas.csv` fila `DIRECCION`; `problemas_potenciales.csv` filas `faltantes_detectados` y `texto_sospechoso`; `dominios_observados.csv` valores frecuentes. |
| `TELEFONO` | 946 faltantes; el diagnóstico inicial conserva 201 hallazgos históricos agregados con caracteres no numéricos. El control final detecta 251 sospechosos vigentes: todo valor no vacío debe tener exactamente 8 dígitos, incluidos 50 valores numéricos con longitud distinta. | Mantener como texto; separar limpieza básica de espacios de la revisión manual. No inferir correspondencia registro por registro desde la evidencia histórica agregada. | El teléfono no debe convertirse a número por ceros, extensiones o separadores; los caracteres pueden indicar información útil. | Alto: eliminar caracteres sin revisión puede perder extensiones o múltiples contactos. | `manual` | Diagnóstico histórico: `problemas_potenciales.csv`; control vigente: `validacion_final.csv` y dataset limpio. |
| `SUPERVISOR` | 535 faltantes (4.51%) y 133 textos sospechosos. | Convertir espacios puros a nulo documentado y normalizar espacios; conservar tildes y nombres completos; revisar manualmente variantes de nombres si se requiere deduplicación. | Los nombres propios pueden variar legítimamente por tildes, apellidos o cargos. | Medio: unificar nombres automáticamente puede fusionar personas distintas. | `manual` | `diagnostico_columnas.csv` fila `SUPERVISOR`; `problemas_potenciales.csv` filas `faltantes_detectados` y `texto_sospechoso`; `dominios_observados.csv` valores frecuentes. |
| `DIRECTOR` | 1,830 faltantes (15.42%) y 1,082 textos sospechosos; dominios muestran `<NBSP>`, guiones, punto y `SIN DATO`. | Convertir marcadores claros de ausencia (`<NBSP>`, espacios, guiones solos, punto, `SIN DATO`) a nulo documentado; conservar nombres propios y revisar variantes manualmente. | La evidencia muestra marcadores claros de ausencia, pero también nombres propios que no deben modificarse agresivamente. | Medio: reglas demasiado amplias pueden borrar nombres válidos con guiones o abreviaturas. | `manual` | `diagnostico_columnas.csv` fila `DIRECTOR`; `problemas_potenciales.csv` filas `faltantes_detectados` y `texto_sospechoso`; `dominios_observados.csv` valores frecuentes. |
| `departamento_origen` | Catálogo territorial no verificable; 23 valores únicos usados como procedencia desde el archivo origen. | Conservar como trazabilidad de adquisición; diferir validación territorial contra catálogo oficial y comparar con `DEPARTAMENTO` solo en una fase posterior. | Es una variable de procedencia, no necesariamente una columna de dominio final equivalente a `DEPARTAMENTO`. | Alto: cambiar procedencia puede romper linaje de datos. | `diferida` | `problemas_potenciales.csv` fila `catalogo_no_verificable`; `diagnostico_columnas.csv` fila `departamento_origen`; `dominios_observados.csv` valores de origen. |
| `__fila__` | Duplicados parciales diferidos; el diagnóstico no fusiona ni corrige registros. | En una limpieza futura, calcular similitud por campos clave (`CODIGO`, `ESTABLECIMIENTO`, territorio, jornada/plan) y enviar candidatos a revisión manual antes de fusionar o eliminar. | La rúbrica advierte no eliminar automáticamente; el diagnóstico reporta 0 duplicados exactos. | Alto: fusionar registros parciales puede perder sedes, jornadas o modalidades distintas. | `manual` | `problemas_potenciales.csv` fila `duplicados_parciales_diferidos`; `duplicados_exactos.csv` sin filas de duplicados; `docs/instrucciones.md` Paso 4.g. |
| `CODIGO`, `NIVEL`, `SECTOR`, `AREA`, `STATUS`, `MODALIDAD`, `JORNADA`, `PLAN`, `DEPARTAMENTAL`, `archivo_origen` | Sin problema potencial fuerte reportado en `problemas_potenciales.csv`; no presentan faltantes en `diagnostico_columnas.csv`. | Conservar como texto/categoría; no transformar por inercia. Validar dominios únicamente si aparece catálogo o regla oficial en una fase futura. | No hay evidencia actual suficiente para cambiar estas variables. | Bajo: el principal riesgo es introducir cambios innecesarios. | `conservar` | `diagnostico_columnas.csv` filas de variables conservadas; `dominios_observados.csv` valores observados; `problemas_potenciales.csv` sin filas para estas variables. |

## Cobertura de `problemas_potenciales.csv`

Cada fila de `outputs/tablas/problemas_potenciales.csv` queda cubierta por la tabla central:

- `<NBSP>` `encabezado_sospechoso` y `faltantes_detectados`: cubiertos en la fila `<NBSP>`.
- `DISTRITO` `faltantes_detectados`: cubierto en la fila `DISTRITO`.
- `DEPARTAMENTO` `catalogo_no_verificable`: cubierto en la fila `DEPARTAMENTO`.
- `MUNICIPIO` `catalogo_no_verificable`: cubierto en la fila `MUNICIPIO`.
- `ESTABLECIMIENTO` `faltantes_detectados` y `texto_sospechoso`: cubiertos en la fila `ESTABLECIMIENTO`.
- `DIRECCION` `faltantes_detectados` y `texto_sospechoso`: cubiertos en la fila `DIRECCION`.
- `TELEFONO` `faltantes_detectados`, `formato_sospechoso` y `texto_sospechoso`: cubiertos en la fila `TELEFONO`.
- `SUPERVISOR` `faltantes_detectados` y `texto_sospechoso`: cubiertos en la fila `SUPERVISOR`.
- `DIRECTOR` `faltantes_detectados` y `texto_sospechoso`: cubiertos en la fila `DIRECTOR`.
- `departamento_origen` `catalogo_no_verificable`: cubierto en la fila `departamento_origen`.
- `__fila__` `duplicados_parciales_diferidos`: cubierto en la fila `__fila__`.

## Decisiones diferidas y revisión manual

- **Territorio**: la limitación “catálogo no verificable” describe el diagnóstico inicial. La fase posterior usa un catálogo reproducible, pero conserva 7 parejas/145 filas para revisión humana y no presenta el espejo comunitario como fuente primaria oficial.
- **Duplicados parciales**: quedan en revisión manual; no se fusionan ni eliminan automáticamente.
- **Teléfonos ambiguos**: se revisarán manualmente cuando contengan extensiones, varios números, separadores o texto auxiliar.
- **Texto semántico libre**: `ESTABLECIMIENTO`, `DIRECCION`, `SUPERVISOR` y `DIRECTOR` solo admiten normalización conservadora de espacios; cualquier unificación, recorte o edición semántica requiere revisión humana.

## Criterios para futura implementación

Una fase posterior de limpieza deberá cumplir, como mínimo, estos criterios antes de considerarse implementada:

- Ejecutar transformaciones mediante código reproducible, no edición manual directa del CSV.
- Registrar una bitácora con variable, problema, transformación aplicada, registros afectados, justificación y riesgo.
- Mantener datos crudos inmutables y escribir salidas limpias en una ubicación nueva y trazable.
- Probar que no quedan espacios iniciales/finales ni caracteres no separables en campos donde se aplique normalización.
- Probar que los marcadores de ausencia definidos se convierten de forma consistente a nulos documentados.
- Probar que `CODIGO`, `DISTRITO`, `TELEFONO`, `archivo_origen` y variables categóricas se conservan como texto cuando corresponda.
- Validar dominios territoriales únicamente con catálogo oficial o documentar explícitamente que la validación sigue diferida.
- Documentar cualquier decisión sobre duplicados exactos o parciales con evidencia y revisión humana cuando aplique.

## Alcance excluido

Este documento excluye explícitamente:

- Crear un CSV limpio.
- Crear el Code Book final.
- Crear el reporte comparativo antes/después.
- Mutar `data/raw/`, `data/source/`, `outputs/`, scripts o `docs/diagnostico.md`.
- Afirmar que ya se limpió, deduplicó, normalizó o validó territorialmente el dataset.
