# Especificación: Limpieza de dataset trazable

## Propósito

Definir la generación reproducible de un dataset limpio conservador desde el CSV intermedio vigente, con bitácora y reporte antes/después, sin mutar fuentes crudas, intermedias ni diagnósticos existentes.

## Requisitos

### Requisito: Generación de CSV limpio separado

El sistema MUST generar `data/processed/establecimientos_diversificado_limpio.csv` usando como entrada primaria únicamente `data/interim/establecimientos_diversificado_raw_unificado.csv`. El CSV de Anggie MAY usarse solo como evidencia secundaria de validación, nunca como fuente primaria.

#### Escenario: limpieza desde intermedio vigente

- DADO que existe el CSV intermedio vigente
- CUANDO se ejecuta la limpieza trazable
- ENTONCES se produce el CSV limpio en `data/processed/`
- Y conserva filas y columnas no eliminadas según reglas seguras.

#### Escenario: entrada primaria ausente

- DADO que el CSV intermedio no existe o no es legible
- CUANDO se solicita la limpieza
- ENTONCES no se genera dataset limpio parcial
- Y se reporta la causa del fallo.

#### Escenario: entrada vacía o malformada

- DADO un CSV intermedio vacío, con encabezados duplicados o con filas ragged que no coinciden con la cantidad de encabezados
- CUANDO se solicita la limpieza
- ENTONCES el sistema MUST rechazar la entrada como malformada
- Y no debe crear ni actualizar el CSV limpio, la bitácora ni el reporte antes/después de forma parcial.

#### Escenario: entrada solo con encabezados

- DADO un CSV intermedio válido que contiene encabezados pero cero filas de datos
- CUANDO se ejecuta la limpieza trazable
- ENTONCES se genera un CSV limpio solo con encabezados válidos
- Y la bitácora y el reporte antes/después registran `filas=0` y conteos cero sin tratarlo como fallo.

### Requisito: Reglas determinísticas conservadoras

El sistema MUST aplicar solo reglas determinísticas seguras: eliminar la columna `<NBSP>` si está completamente vacía, normalizar NBSP/espacios, convertir marcadores inequívocos de ausencia a vacío/nulo consistente y preservar identificadores, teléfonos, categorías y texto libre como cadenas.

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

El sistema MUST emitir `outputs/tablas/reporte_calidad_antes_despues.csv` con métricas comparables antes y después, incluyendo filas, columnas, faltantes por variable, columna `<NBSP>`, marcadores de ausencia normalizados y decisiones diferidas.

#### Escenario: comparación generada

- DADO una limpieza completada
- CUANDO se consulta el reporte antes/después
- ENTONCES muestra métricas previas y posteriores comparables
- Y distingue limpieza ejecutada de validaciones pendientes.

### Requisito: Atomicidad e idempotencia de salidas

El sistema MUST tratar el CSV limpio, la bitácora y el reporte antes/después como un único conjunto de salida atómico e idempotente. Para una misma entrada, dos ejecuciones MUST producir salidas byte-for-byte idénticas, sin agregar filas duplicadas ni conservar filas obsoletas de ejecuciones anteriores.

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

### Requisito: Protección de fuentes y decisiones diferidas

El sistema MUST NOT mutar `data/raw/`, `data/interim/`, HTML fuente, `docs/diagnostico.md`, `docs/plan_limpieza.md` ni diagnósticos existentes. Duplicados parciales, validación territorial, teléfonos ambiguos y limpieza semántica libre MUST quedar diferidos o manuales.

#### Escenario: artefactos protegidos

- DADO que existen fuentes crudas, intermedias y diagnósticos previos
- CUANDO se ejecuta la limpieza trazable
- ENTONCES esos artefactos permanecen sin cambios
- Y solo se crean o actualizan las salidas limpias permitidas.

#### Escenario: problema no determinístico

- DADO un duplicado parcial, territorio no verificable, teléfono ambiguo o texto semántico dudoso
- CUANDO se evalúa durante la limpieza
- ENTONCES no se corrige automáticamente
- Y queda marcado como diferido o manual en la evidencia.
