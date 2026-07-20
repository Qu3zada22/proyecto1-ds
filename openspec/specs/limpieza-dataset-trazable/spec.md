# Especificación: Limpieza de dataset trazable

## Propósito

Definir la generación reproducible de un dataset limpio conservador desde la fuente canónica vigente, con bitácora y reporte base, sin mutar fuentes crudas, canónicas, diagnósticos ni el reporte integral final.

## Requisitos

### Requirement: Generación de CSV limpio separado

El sistema MUST generar `data/processed/establecimientos_diversificado_limpio.csv` solo desde `data/source/establecimientos_diversificado_mineduc.csv`; alternativas MAY usarse como evidencia.
(Anteriormente: entrada en `data/interim/`.)

#### Scenario: limpieza canónica
- DADO la fuente válida
- CUANDO se limpia
- ENTONCES produce la salida en `data/processed/`.

#### Scenario: entrada ausente o ilegible
- DADO una fuente ausente o ilegible
- CUANDO se limpia
- ENTONCES no altera salidas y reporta la causa.

#### Scenario: entrada malformada
- DADO un CSV vacío, ragged o con encabezados duplicados
- CUANDO se limpia
- ENTONCES se rechaza sin alterar salidas.

#### Scenario: solo encabezados
- DADO un CSV válido sin filas
- CUANDO se limpia
- ENTONCES genera encabezados y conteos cero.

### Requisito: Reglas determinísticas conservadoras

El sistema MUST aplicar solo reglas determinísticas seguras: eliminar la columna `<NBSP>` si está completamente vacía, normalizar NBSP/espacios, convertir marcadores inequívocos de ausencia a vacío/nulo consistente y preservar identificadores, teléfonos, categorías y texto libre como cadenas.

La preservación MUST distinguir diagnóstico de validación: 201 es el conteo histórico agregado del diagnóstico inicial para teléfonos con caracteres no numéricos; 251 es el pendiente operativo vigente bajo la regla vacío o exactamente 8 dígitos, incluidos 50 valores numéricos con longitud distinta. La evidencia histórica agregada MUST NOT usarse para afirmar correspondencia registro por registro.

#### Escenario: reglas seguras aplicadas

- DADO que hay NBSP, espacios sobrantes y marcadores claros de ausencia
- CUANDO se limpia el dataset
- ENTONCES esos valores quedan normalizados de forma consistente
- Y `CODIGO`, `DISTRITO`, `TELEFONO`, `archivo_origen` y categorías siguen como texto.

#### Escenario: columna NBSP con contenido

- DADO que la columna `<NBSP>` contiene algún valor no ausente
- CUANDO se evalúa su eliminación
- ENTONCES la columna MUST NOT eliminarse silenciosamente
- Y la situación queda reportada como no segura.

### Requisito: Preservación de texto libre

El sistema MUST preservar `ESTABLECIMIENTO`, `DIRECCION`, `SUPERVISOR` y `DIRECTOR` casi intactos; solo MAY normalizar espacios/NBSP y ausencias inequívocas sin cambiar nombres, puntuación significativa ni semántica.

#### Escenario: texto libre con formato irregular

- DADO un campo de texto libre con espacios múltiples o NBSP
- CUANDO se limpia el registro
- ENTONCES se normalizan solo esos caracteres
- Y el contenido semántico permanece sin reescritura.

### Requisito: Bitácora de limpieza

El sistema MUST emitir `outputs/tablas/bitacora_limpieza.csv` con, como mínimo, `variable`, `regla`, `filas_afectadas` y `evidencia_fuente` para cada transformación ejecutada o decisión segura relevante.

#### Escenario: transformación registrada

- DADO que una regla modifica valores o elimina una columna segura
- CUANDO finaliza la limpieza
- ENTONCES la bitácora registra variable, regla, conteo afectado y evidencia
- Y la evidencia traza a diagnóstico, plan o CSV intermedio.

### Requisito: Reporte antes/después

El sistema MUST emitir `outputs/tablas/reporte_limpieza_base.csv` con métricas intermedias de limpieza. MUST NOT crear ni sobrescribir `outputs/tablas/reporte_calidad_antes_despues.csv`, reservado al reporte integral final.

El reporte MUST comparar filas, columnas, faltantes, `<NBSP>`, ausencias y decisiones; MUST registrar 11,867 filas, 20→21 columnas y métricas territoriales.
(Anteriormente: no fijaba 20→21 ni métricas territoriales.)

#### Escenario: comparación generada

- DADO una limpieza completada
- CUANDO se consulta el reporte antes/después
- ENTONCES muestra métricas previas y posteriores comparables
- Y distingue limpieza ejecutada de validaciones pendientes.

### Requisito: Atomicidad e idempotencia de salidas

El sistema MUST tratar el CSV limpio, la bitácora y `reporte_limpieza_base.csv` como un único conjunto de salida atómico e idempotente. Para una misma entrada, dos ejecuciones MUST producir salidas byte-for-byte idénticas sin mutar el reporte integral.

#### Escenario: fallo durante escritura multi-salida

- DADO que existen o se están generando el CSV limpio, la bitácora y el reporte antes/después
- CUANDO ocurre un fallo inyectado durante la escritura o reemplazo de cualquiera de las salidas
- ENTONCES el sistema MUST restaurar las salidas previas o eliminar salidas nuevas incompletas
- Y no debe dejar un conjunto parcialmente actualizado.

#### Escenario: dos ejecuciones con la misma entrada

- DADO el mismo CSV intermedio válido y las mismas rutas de salida
- CUANDO se ejecuta la limpieza dos veces consecutivas
- ENTONCES los bytes del CSV limpio, la bitácora y el reporte antes/después MUST ser idénticos entre ejecuciones
- Y la bitácora y el reporte no contienen filas duplicadas ni filas stale de una ejecución previa.

### Requirement: Protección de fuentes y decisiones diferidas

El sistema MUST NOT mutar crudos, manifest, `data/source/`, diagnósticos ni planes; decisiones ambiguas MUST permanecer manuales.
(Anteriormente: protegía `data/interim/`.)

#### Scenario: artefactos protegidos
- DADO fuentes y evidencia
- CUANDO se limpia
- ENTONCES conservan hashes y solo cambian salidas autorizadas.

#### Scenario: decisión no determinística
- DADO un caso ambiguo
- CUANDO se evalúa
- ENTONCES no se autocorrige y queda trazado.
