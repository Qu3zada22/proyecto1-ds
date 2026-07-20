# Code Book — Variables diagnóstico y operativas (sección de Anggie)

Esta sección cubre las **17 variables operativas y de trazabilidad** del dataset limpio `data/processed/establecimientos_diversificado_limpio.csv`. Las 4 variables territoriales (`DEPARTAMENTO`, `MUNICIPIO`, `departamento_codigo`, `municipio_codigo`) están documentadas en `variables_territoriales.md` (sección de Iris).

**Metadatos comunes**

- **Fecha exacta de extracción:** 2026-07-14 (captura de los HTML oficiales; ver `data/raw/manifest.json`).
- **Fuente de origen:** MINEDUC — Busca Establecimiento (Diversificado), 23 HTML capturados por departamento.
- **Fuente canónica:** `data/source/establecimientos_diversificado_mineduc.csv` (11,867 filas × 20 columnas).
- **Dataset limpio:** `data/processed/establecimientos_diversificado_limpio.csv` (11,867 filas × 21 columnas).
- **Versión del conjunto limpio:** v0.1.0.
- **Diagnóstico original:** `outputs/tablas/diagnostico_columnas.csv`, `outputs/tablas/problemas_potenciales.csv`.
- **Bitácora de transformaciones:** `outputs/tablas/bitacora_limpieza.csv`.

**Plantilla usada por variable:** descripción · tipo de dato · dominio permitido · valores posibles · faltantes · tratamiento en limpieza · variable derivada · fecha de extracción · fuente · versión.

---

## `CODIGO`

- **Descripción:** Código único asignado por el MINEDUC a cada establecimiento educativo. Identifica de forma unívoca al establecimiento en los sistemas del MINEDUC.
- **Tipo de dato:** Texto (identificador).
- **Dominio permitido:** Cadena con formato `DD-MM-NNNN-SS` (departamento–municipio–correlativo–sector). Preservado como texto para evitar pérdida de ceros u otros separadores.
- **Valores posibles:** 11,867 valores únicos; ej. `01-01-0158-46`, `16-09-0870-46`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; conservado exactamente como aparece en la fuente oficial.
- **Variable derivada:** No.

---

## `DISTRITO`

- **Descripción:** Código de distrito escolar asignado por el MINEDUC para la organización administrativa de la supervisión educativa.
- **Tipo de dato:** Texto (identificador).
- **Dominio permitido:** Cadena con estructura numérica de segmentos separados por guiones; ej. `01-01-0026`.
- **Valores posibles:** 1,682 valores únicos observados.
- **Faltantes:** 532 (4.48%); los registros sin distrito quedaron vacíos en la fuente oficial.
- **Tratamiento en limpieza:** Se normalizó el marcador de ausencia (filas con valor vacío o marcador estándar convertidas a cadena vacía). Sin modificaciones al código en sí.
- **Variable derivada:** No.

---

## `ESTABLECIMIENTO`

- **Descripción:** Nombre oficial del establecimiento educativo según el registro del MINEDUC.
- **Tipo de dato:** Texto libre.
- **Dominio permitido:** Texto en mayúsculas; no existe un vocabulario controlado predefinido.
- **Valores posibles:** 6,668 valores únicos (distintos establecimientos pueden tener el mismo nombre si operan en distintas localidades o jornadas).
- **Faltantes:** 5 (0.04%); anomalías puntuales en la fuente.
- **Tratamiento en limpieza:**
  - Normalización de NBSP, caracteres invisibles y espacios múltiples (1,396 filas afectadas).
  - Canonización a mayúsculas.
  - Marcadores de ausencia convertidos a vacío (5 filas).
- **Variable derivada:** No.

---

## `DIRECCION`

- **Descripción:** Dirección física del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto libre.
- **Dominio permitido:** Texto en mayúsculas; no hay formato estandarizado.
- **Valores posibles:** 7,528 valores únicos.
- **Faltantes:** 81 (0.68%).
- **Tratamiento en limpieza:**
  - Normalización de NBSP, caracteres invisibles y espacios múltiples (485 filas).
  - Canonización a mayúsculas (10 filas).
  - Marcadores de ausencia convertidos a vacío (81 filas).
- **Variable derivada:** No.

---

## `TELEFONO`

- **Descripción:** Número(s) de contacto telefónico del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (número conservado como texto para preservar ceros y separadores).
- **Dominio permitido:** Dígitos; se admiten separadores de múltiples números (`-`, `,`) y texto auxiliar mínimo.
- **Valores posibles:** 6,572 valores únicos (incluyendo vacíos y formatos mixtos).
- **Faltantes:** 946 (7.97%); los establecimientos sin teléfono registrado quedaron vacíos.
- **Tratamiento en limpieza:**
  - Normalización de NBSP y espacios múltiples (8 filas).
  - Marcadores de ausencia convertidos a vacío (946 filas).
- **Excepciones de formato documentadas (201 registros con caracteres no-dígito):**
  - **Múltiples teléfonos separados por `-`**: ej. `24328801-24329098`, `77648506-45419234-41177068`. Representa varios contactos del establecimiento; se conserva como texto íntegro.
  - **Múltiples teléfonos separados por `,`**: ej. `3325732, 2320075, 2307014`. Mismo caso anterior.
  - **Texto auxiliar**: ej. `25763, 26725 Y 21568`. Texto aclaratorio conservado sin modificación.
  - **Extensión de rango abreviada**: ej. `22202870-73` (indica extensiones de un conmutador). Se conserva como texto; no se expande automáticamente.
  - **Valores sospechosos de relleno**: ej. `41724130-00000000` (el segundo segmento es `00000000`). Conservados sin modificación; requieren revisión humana si se usan como llave de contacto.
  - **Decisión documentada**: ninguna de estas excepciones se normaliza automáticamente. El teléfono es información de contacto que puede tener extensiones o múltiples registros legítimos; eliminar caracteres sin contexto implicaría pérdida semántica irreversible.
- **Variable derivada:** No.

---

## `SUPERVISOR`

- **Descripción:** Nombre del supervisor educativo asignado al establecimiento por el MINEDUC.
- **Tipo de dato:** Texto libre (nombre propio).
- **Dominio permitido:** No aplica vocabulario controlado.
- **Valores posibles:** 1,290 valores únicos.
- **Faltantes:** 535 (4.51%).
- **Tratamiento en limpieza:** Sin transformaciones; los nombres propios se conservan tal como aparecen en la fuente oficial para evitar pérdida semántica. La normalización de espacios invisibles se aplicó globalmente.
- **Variable derivada:** No.

---

## `DIRECTOR`

- **Descripción:** Nombre del director del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto libre (nombre propio).
- **Dominio permitido:** No aplica vocabulario controlado.
- **Valores posibles:** 5,572 valores únicos.
- **Faltantes:** 1,830 (15.42%); es la variable con mayor porcentaje de faltantes del dataset.
- **Tratamiento en limpieza:** Sin transformaciones; nombres propios conservados tal como aparecen.
- **Variable derivada:** No.

---

## `NIVEL`

- **Descripción:** Nivel educativo del establecimiento según la clasificación del MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** Un único valor en este dataset.
- **Valores posibles:** `DIVERSIFICADO` (único valor; el dataset cubre exclusivamente este nivel).
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; valor uniforme en todas las filas.
- **Variable derivada:** No.

---

## `SECTOR`

- **Descripción:** Sector de administración del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 4 categorías oficiales del MINEDUC.
- **Valores posibles:** `COOPERATIVA`, `MUNICIPAL`, `OFICIAL`, `PRIVADO`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; vocabulario controlado y sin variantes tipográficas en la fuente.
- **Variable derivada:** No.

---

## `AREA`

- **Descripción:** Clasificación del área geográfica del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 3 categorías.
- **Valores posibles:** `RURAL`, `SIN ESPECIFICAR`, `URBANA`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

---

## `STATUS`

- **Descripción:** Estado operativo del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 5 categorías oficiales.
- **Valores posibles:** `ABIERTA`, `CERRADA DEFINITIVAMENTE`, `CERRADA TEMPORALMENTE`, `TEMPORAL NOMBRAMIENTO`, `TEMPORAL TITULOS`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

---

## `MODALIDAD`

- **Descripción:** Modalidad lingüística del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 2 categorías.
- **Valores posibles:** `BILINGUE`, `MONOLINGUE`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

---

## `JORNADA`

- **Descripción:** Jornada de funcionamiento del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 6 categorías.
- **Valores posibles:** `DOBLE`, `INTERMEDIA`, `MATUTINA`, `NOCTURNA`, `SIN JORNADA`, `VESPERTINA`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

---

## `PLAN`

- **Descripción:** Plan de estudios o modalidad de asistencia del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 13 categorías observadas.
- **Valores posibles:** `A DISTANCIA`, `DIARIO(REGULAR)`, `DOMINICAL`, `FIN DE SEMANA`, `INTERCALADO`, `IRREGULAR`, `MIXTO`, `SABATINO`, `SEMIPRESENCIAL`, `SEMIPRESENCIAL (DOS DÍAS A LA SEMANA)`, `SEMIPRESENCIAL (FIN DE SEMANA)`, `SEMIPRESENCIAL (UN DÍA A LA SEMANA)`, `VIRTUAL A DISTANCIA`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; vocabulario verificado contra catálogo.
- **Variable derivada:** No.

---

## `DEPARTAMENTAL`

- **Descripción:** Nombre de la dirección departamental de educación a la que pertenece el establecimiento. No coincide necesariamente con `DEPARTAMENTO` ya que una dirección departamental puede cubrir subdivisiones geográficas distintas (ej. Guatemala se divide en cuatro regionales).
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 26 valores observados (incluye subdivisiones regionales de Guatemala).
- **Valores posibles:** `ALTA VERAPAZ`, `BAJA VERAPAZ`, `CHIMALTENANGO`, `CHIQUIMULA`, `EL PROGRESO`, `ESCUINTLA`, `GUATEMALA NORTE`, `GUATEMALA OCCIDENTE`, `GUATEMALA ORIENTE`, `GUATEMALA SUR`, `HUEHUETENANGO`, `IZABAL`, `JALAPA`, `JUTIAPA`, `PETÉN`, `QUETZALTENANGO`, `QUICHÉ`, `QUICHÉ NORTE`, `RETALHULEU`, `SACATEPÉQUEZ`, `SAN MARCOS`, `SANTA ROSA`, `SOLOLÁ`, `SUCHITEPÉQUEZ`, `TOTONICAPÁN`, `ZACAPA`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; la división regional de Guatemala (Norte/Sur/Oriente/Occidente) y `QUICHÉ NORTE` son valores oficiales del MINEDUC.
- **Variable derivada:** No.

---

## `archivo_origen`

- **Descripción:** Nombre del archivo HTML de origen del que se extrajo el registro. Variable de trazabilidad añadida durante la consolidación.
- **Tipo de dato:** Texto (nombre de archivo).
- **Dominio permitido:** 23 valores posibles, uno por departamento capturado.
- **Valores posibles:** `mineduc_busca_establecimiento_diversificado_00.html` … `mineduc_busca_establecimiento_diversificado_22.html`.
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; es evidencia de procedencia inmutable.
- **Variable derivada:** **Sí** (añadida durante consolidación en `scripts/consolidar_crudos.py`).
  - **Método:** el script asigna el nombre del HTML procesado a cada fila extraída.
  - **Utilidad:** permite rastrear cualquier registro hasta su fuente HTML original en `data/raw/`.

---

## `departamento_origen`

- **Descripción:** Nombre del departamento según el encabezado del formulario MINEDUC del que se extrajo el registro. Variable de trazabilidad añadida durante la consolidación.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 23 valores posibles.
- **Valores posibles:** Los 22 departamentos de Guatemala más `CIUDAD CAPITAL` (que el MINEDUC lista separado de `GUATEMALA`).
- **Faltantes:** 0 (0%).
- **Tratamiento en limpieza:** Sin modificaciones; es evidencia de procedencia inmutable.
- **Variable derivada:** **Sí** (añadida durante consolidación en `scripts/consolidar_crudos.py`).
  - **Método:** el script extrae el nombre del departamento del título o contexto del HTML y lo asigna a cada fila.
  - **Utilidad:** complementa `archivo_origen` para verificar consistencia entre el departamento registrado en `DEPARTAMENTO` y el HTML de origen.

---

## Métricas de calidad antes/después (resumen Anggie)

| Variable | Faltantes antes | Faltantes después | Filas transformadas | Tipo de transformación |
|---|---|---|---|---|
| `DISTRITO` | 532 | 532 | 532 | Marcadores → vacío |
| `ESTABLECIMIENTO` | 5 | 5 | 1,401 | NBSP + marcadores + mayúsculas |
| `DIRECCION` | 81 | 81 | 576 | NBSP + mayúsculas + marcadores |
| `TELEFONO` | 946 | 946 | 954 | NBSP + marcadores (sin tocar formato) |
| `SUPERVISOR` | 535 | 535 | 0 | Sin transformación |
| `DIRECTOR` | 1,830 | 1,830 | 0 | Sin transformación |
| `NIVEL`–`DEPARTAMENTAL` | 0 | 0 | 0 | Sin transformación |
| `archivo_origen`, `departamento_origen` | 0 | 0 | 0 | Variables de trazabilidad |

Fuente: `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`.

---

## Decisiones de duplicados parciales (resumen Anggie, R5g)

La detección produjo 1,355 pares candidatos. Las reglas aplicadas sin borrado automático son:

| Regla | Condición | Pares | Interpretación |
|---|---|---|---|
| `duplicado_probable` | `confianza == "alta"` (dirección Y teléfono coinciden) | 718 | Evidencia estructural máxima; requieren validación institucional antes de cualquier fusión. |
| `independiente` | `confianza == "media"` Y ambos teléfonos no vacíos Y distintos | 366 | Teléfonos diferentes sugieren establecimientos distintos. |
| `revisar` | Resto (ambiguos: mismo teléfono pero distinta dirección, o teléfonos vacíos) | 271 | Requieren revisión humana. |

Evidencia: `outputs/tablas/duplicados_parciales.csv` · `src/proyecto1_ds/duplicates.py` · `scripts/decidir_duplicados.py`.
