# Code Book maestro — Establecimientos educativos de nivel Diversificado

Este documento reúne las 21 variables del dataset limpio en su orden canónico. Se genera desde `docs/code_book/variables_anggie.md` y `docs/code_book/variables_territoriales.md`; no debe editarse manualmente.

- **Fuente canónica:** `data/source/establecimientos_diversificado_mineduc.csv`.
- **Dataset documentado:** `data/processed/establecimientos_diversificado_limpio.csv`.
- **Linaje:** HTML oficiales MINEDUC + manifest → fuente canónica → limpieza/enriquecimiento → dataset limpio.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Contribuciones:** Anggie documenta 17 variables; Iris documenta 4 variables territoriales; Jonathan ensambla el maestro.
- **Pendientes:** 718 pares `duplicado_probable` requieren confirmación, 271 pares requieren revisión, 251 teléfonos sospechosos vigentes y 145 filas territoriales permanecen pendientes.
- **Referencia histórica telefónica:** el diagnóstico inicial conserva 201 hallazgos históricos agregados por caracteres no numéricos; además, el control vigente detecta 50 teléfonos numéricos vigentes con longitud distinta de 8. La evidencia histórica agregada no establece correspondencia registro por registro.
- **PDF reproducible:** `uv run python scripts/generar_code_book_pdf.py` genera `docs/code_book.pdf`.

## Cómo leer este documento

Los conteos de nulos corresponden al dataset limpio. `revisar` indica evidencia preservada, no un error corregido. Las secciones fuente continúan siendo la autoridad editable de cada responsable.

## `CODIGO`

- **Descripción:** Código único asignado por el MINEDUC a cada establecimiento educativo. Identifica de forma unívoca al establecimiento en los sistemas del MINEDUC.
- **Tipo de dato:** Texto (identificador).
- **Dominio permitido:** Cadena con formato `DD-MM-NNNN-SS` (departamento–municipio–correlativo–sector). Preservado como texto para evitar pérdida de ceros u otros separadores.
- **Valores posibles:** 11,867 valores únicos; ej. `01-01-0158-46`, `16-09-0870-46`.

- **Tratamiento en limpieza:** Sin modificaciones; conservado exactamente como aparece en la fuente oficial.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `DISTRITO`

- **Descripción:** Código de distrito escolar asignado por el MINEDUC para la organización administrativa de la supervisión educativa.
- **Tipo de dato:** Texto (identificador).
- **Dominio permitido:** Cadena con estructura numérica de segmentos separados por guiones; ej. `01-01-0026`.
- **Valores posibles:** 1,682 valores únicos observados.

- **Tratamiento en limpieza:** Se normalizó el marcador de ausencia (filas con valor vacío o marcador estándar convertidas a cadena vacía). Sin modificaciones al código en sí.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 532 (4.48%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `DEPARTAMENTO`

- **Descripción:** Departamento administrativo del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** Los 22 departamentos oficiales de Guatemala, más el valor especial `CIUDAD CAPITAL` que el MINEDUC usa para el municipio de Guatemala.
- **Valores posibles:** 23 valores observados: `ALTA VERAPAZ`, `BAJA VERAPAZ`, `CHIMALTENANGO`, `CHIQUIMULA`, `CIUDAD CAPITAL`, `EL PROGRESO`, `ESCUINTLA`, `GUATEMALA`, `HUEHUETENANGO`, `IZABAL`, `JALAPA`, `JUTIAPA`, `PETEN`, `QUETZALTENANGO`, `QUICHE`, `RETALHULEU`, `SACATEPEQUEZ`, `SAN MARCOS`, `SANTA ROSA`, `SOLOLA`, `SUCHITEPEQUEZ`, `TOTONICAPAN`, `ZACAPA`.
- **Tratamiento en limpieza:** Canonización a mayúsculas y normalización de espacios, NBSP y caracteres invisibles. El nombre original del MINEDUC se conserva (incluido `CIUDAD CAPITAL`); su consistencia se valida contra el catálogo INE sin alterar el valor.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y catálogo territorial reproducible; ver la sección canónica de Iris.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Iris.

---

## `MUNICIPIO`

- **Descripción:** Municipio del establecimiento según el MINEDUC. Para `CIUDAD CAPITAL`, el valor corresponde a la zona de la ciudad de Guatemala (`ZONA N`).
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** Municipios oficiales de Guatemala pertenecientes a su departamento; para `CIUDAD CAPITAL`, zonas capitalinas.
- **Valores posibles:** Alrededor de 352 valores observados (incluye zonas capitalinas). El dominio oficial se define en `data/reference/catalogo_territorial.csv` (340 municipios).
- **Tratamiento en limpieza:**
  - Canonización a mayúsculas y normalización de espacios/NBSP/invisibles.
  - Corrección trazable de 2 typos contra el catálogo oficial: `PACHALUN` → `PACHALUM` y `SAN MIGUEL PANAM` → `SAN MIGUEL PANAN` (bitácora `outputs/tablas/bitacora_limpieza.csv`).
  - 7 nombres cortos se conservan sin declararlos resueltos (p. ej. `NEBAJ`); abarcan 145 filas, usan códigos provisionales y mantienen `decision=revisar` en `outputs/tablas/inconsistencias_territoriales.csv`.
  - Validación de consistencia cruzada departamento–municipio contra el catálogo INE.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y catálogo territorial reproducible; ver la sección canónica de Iris.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Iris.

---

## `departamento_codigo`

- **Descripción:** Código oficial INE del departamento. Se agrega para habilitar cruces con otras fuentes oficiales (censo, geografía, presupuesto).
- **Tipo de dato:** Texto (código numérico conservado como texto).
- **Dominio permitido:** Códigos oficiales INE de departamento, del `1` al `22`.
- **Valores posibles:** `1` Guatemala, `2` El Progreso, `3` Sacatepéquez, `4` Chimaltenango, `5` Escuintla, `6` Santa Rosa, `7` Sololá, `8` Totonicapán, `9` Quetzaltenango, `10` Suchitepéquez, `11` Retalhuleu, `12` San Marcos, `13` Huehuetenango, `14` Quiché, `15` Baja Verapaz, `16` Alta Verapaz, `17` Petén, `18` Izabal, `19` Zacapa, `20` Chiquimula, `21` Jalapa, `22` Jutiapa.
- **Tratamiento en limpieza:** Asignado por unión con el catálogo INE tras normalizar el nombre del departamento (mayúsculas y sin tildes). `CIUDAD CAPITAL` se mapea a Guatemala (`1`) mediante regla documentada.
- **Variable derivada:** **Sí.**
  - **Método de cálculo:** normalización del valor de `DEPARTAMENTO` + búsqueda exacta en `data/reference/catalogo_territorial.csv` (módulo `src/proyecto1_ds/enrichment.py`).
  - **Utilidad:** llave de unión estable con cualquier dataset oficial de Guatemala; los nombres varían, el código no.
  - **Cobertura:** 11,867 de 11,867 filas (100%).

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y catálogo territorial reproducible; ver la sección canónica de Iris.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Iris.

---

## `municipio_codigo`

- **Descripción:** Código oficial INE del municipio. Se agrega para habilitar cruces con otras fuentes oficiales.
- **Tipo de dato:** Texto (código numérico conservado como texto para preservar su estructura).
- **Dominio permitido:** Códigos oficiales INE de municipio (3 a 4 dígitos; los primeros dígitos corresponden al departamento).
- **Valores posibles:** Códigos del catálogo oficial (rango `101`–`2217`); p. ej. `101` = Guatemala/Guatemala, `901` = Quetzaltenango/Quetzaltenango.
- **Tratamiento en limpieza:** Asignado por unión con el catálogo tras corregir 2 variantes tipográficas. Los 7 nombres cortos reciben código provisional sin cambiar el texto MINEDUC ni su estado `revisar`; también se aplica la regla `CIUDAD CAPITAL` → municipio de Guatemala.
- **Variable derivada:** **Sí.**
  - **Método de cálculo:** normalización de la pareja (`DEPARTAMENTO`, `MUNICIPIO`) + búsqueda en el catálogo, con tabla de reconciliación documentada en `src/proyecto1_ds/enrichment.py`.
  - **Utilidad:** identifica de forma única cada municipio para análisis y uniones; robusto frente a variantes de escritura.
  - **Cobertura:** 11,867 de 11,867 filas (100%); 145 asignaciones son provisionales y no equivalen a validación oficial del nombre.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y catálogo territorial reproducible; ver la sección canónica de Iris.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Iris.

---

## `ESTABLECIMIENTO`

- **Descripción:** Nombre oficial del establecimiento educativo según el registro del MINEDUC.
- **Tipo de dato:** Texto libre.
- **Dominio permitido:** Texto en mayúsculas; no existe un vocabulario controlado predefinido.
- **Valores posibles:** 6,668 valores únicos (distintos establecimientos pueden tener el mismo nombre si operan en distintas localidades o jornadas).

- **Tratamiento en limpieza:**
  - Normalización de NBSP, caracteres invisibles y espacios múltiples (1,396 filas afectadas).
  - Canonización a mayúsculas.
  - Marcadores de ausencia convertidos a vacío (5 filas).
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 5 (0.04%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `DIRECCION`

- **Descripción:** Dirección física del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto libre.
- **Dominio permitido:** Texto en mayúsculas; no hay formato estandarizado.
- **Valores posibles:** 7,528 valores únicos.

- **Tratamiento en limpieza:**
  - Normalización de NBSP, caracteres invisibles y espacios múltiples (485 filas).
  - Canonización a mayúsculas (10 filas).
  - Marcadores de ausencia convertidos a vacío (81 filas).
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 81 (0.68%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `TELEFONO`

- **Descripción:** Número(s) de contacto telefónico del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (número conservado como texto para preservar ceros y separadores).
- **Dominio permitido:** Para el control final, vacío o exactamente 8 dígitos. Los separadores y textos auxiliares se preservan como evidencia, pero clasifican el valor como sospechoso vigente.
- **Valores posibles:** 6,572 valores únicos (incluyendo vacíos y formatos mixtos).

- **Tratamiento en limpieza:**
  - Normalización de NBSP y espacios múltiples (8 filas).
  - Marcadores de ausencia convertidos a vacío (946 filas).
- **Referencia histórica del diagnóstico inicial:** 201 hallazgos agregados con caracteres no-dígito. No identifica necesariamente las mismas filas del control vigente.
- **Pendiente operativo vigente:** 251 teléfonos sospechosos bajo la regla estricta; incluye además 50 valores numéricos con longitud distinta de 8. La evidencia histórica agregada no permite establecer correspondencia registro por registro.
  - **Múltiples teléfonos separados por `-`**: ej. `24328801-24329098`, `77648506-45419234-41177068`. Representa varios contactos del establecimiento; se conserva como texto íntegro.
  - **Múltiples teléfonos separados por `,`**: ej. `3325732, 2320075, 2307014`. Mismo caso anterior.
  - **Texto auxiliar**: ej. `25763, 26725 Y 21568`. Texto aclaratorio conservado sin modificación.
  - **Extensión de rango abreviada**: ej. `22202870-73` (indica extensiones de un conmutador). Se conserva como texto; no se expande automáticamente.
  - **Valores sospechosos de relleno**: ej. `41724130-00000000` (el segundo segmento es `00000000`). Conservados sin modificación; requieren revisión humana si se usan como llave de contacto.
  - **Decisión documentada**: ninguna de estas excepciones se normaliza automáticamente. El teléfono es información de contacto que puede tener extensiones o múltiples registros legítimos; eliminar caracteres sin contexto implicaría pérdida semántica irreversible.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 946 (7.97%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `SUPERVISOR`

- **Descripción:** Nombre del supervisor educativo asignado al establecimiento por el MINEDUC.
- **Tipo de dato:** Texto libre (nombre propio).
- **Dominio permitido:** No aplica vocabulario controlado.
- **Valores posibles:** 1,290 valores únicos.

- **Tratamiento en limpieza:** Se normalizaron espacios, NBSP y caracteres invisibles en 133 filas, y marcadores inequívocos de ausencia en 535 filas. La comparación directa por `CODIGO` entre fuente y limpio confirma 668 filas modificadas; no se alteró el contenido semántico de los nombres.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 535 (4.51%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `DIRECTOR`

- **Descripción:** Nombre del director del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto libre (nombre propio).
- **Dominio permitido:** No aplica vocabulario controlado.
- **Valores posibles:** 5,572 valores únicos.

- **Tratamiento en limpieza:** Se normalizaron espacios, NBSP y caracteres invisibles en 1,082 filas, y marcadores inequívocos de ausencia en 1,830 filas. La comparación directa por `CODIGO` entre fuente y limpio confirma 2,912 filas modificadas; no se alteró el contenido semántico de los nombres.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 1830 (15.42%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `NIVEL`

- **Descripción:** Nivel educativo del establecimiento según la clasificación del MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** Un único valor en este dataset.
- **Valores posibles:** `DIVERSIFICADO` (único valor; el dataset cubre exclusivamente este nivel).

- **Tratamiento en limpieza:** Sin modificaciones; valor uniforme en todas las filas.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `SECTOR`

- **Descripción:** Sector de administración del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 4 categorías oficiales del MINEDUC.
- **Valores posibles:** `COOPERATIVA`, `MUNICIPAL`, `OFICIAL`, `PRIVADO`.

- **Tratamiento en limpieza:** Sin modificaciones; vocabulario controlado y sin variantes tipográficas en la fuente.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `AREA`

- **Descripción:** Clasificación del área geográfica del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 3 categorías.
- **Valores posibles:** `RURAL`, `SIN ESPECIFICAR`, `URBANA`.

- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `STATUS`

- **Descripción:** Estado operativo del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 5 categorías oficiales.
- **Valores posibles:** `ABIERTA`, `CERRADA DEFINITIVAMENTE`, `CERRADA TEMPORALMENTE`, `TEMPORAL NOMBRAMIENTO`, `TEMPORAL TITULOS`.

- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `MODALIDAD`

- **Descripción:** Modalidad lingüística del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 2 categorías.
- **Valores posibles:** `BILINGUE`, `MONOLINGUE`.

- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `JORNADA`

- **Descripción:** Jornada de funcionamiento del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 6 categorías.
- **Valores posibles:** `DOBLE`, `INTERMEDIA`, `MATUTINA`, `NOCTURNA`, `SIN JORNADA`, `VESPERTINA`.

- **Tratamiento en limpieza:** Sin modificaciones.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `PLAN`

- **Descripción:** Plan de estudios o modalidad de asistencia del establecimiento.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 13 categorías observadas.
- **Valores posibles:** `A DISTANCIA`, `DIARIO(REGULAR)`, `DOMINICAL`, `FIN DE SEMANA`, `INTERCALADO`, `IRREGULAR`, `MIXTO`, `SABATINO`, `SEMIPRESENCIAL`, `SEMIPRESENCIAL (DOS DÍAS A LA SEMANA)`, `SEMIPRESENCIAL (FIN DE SEMANA)`, `SEMIPRESENCIAL (UN DÍA A LA SEMANA)`, `VIRTUAL A DISTANCIA`.

- **Tratamiento en limpieza:** Sin modificaciones; vocabulario verificado contra catálogo.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `DEPARTAMENTAL`

- **Descripción:** Nombre de la dirección departamental de educación a la que pertenece el establecimiento. No coincide necesariamente con `DEPARTAMENTO` ya que una dirección departamental puede cubrir subdivisiones geográficas distintas (ej. Guatemala se divide en cuatro regionales).
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 26 valores observados (incluye subdivisiones regionales de Guatemala).
- **Valores posibles:** `ALTA VERAPAZ`, `BAJA VERAPAZ`, `CHIMALTENANGO`, `CHIQUIMULA`, `EL PROGRESO`, `ESCUINTLA`, `GUATEMALA NORTE`, `GUATEMALA OCCIDENTE`, `GUATEMALA ORIENTE`, `GUATEMALA SUR`, `HUEHUETENANGO`, `IZABAL`, `JALAPA`, `JUTIAPA`, `PETÉN`, `QUETZALTENANGO`, `QUICHÉ`, `QUICHÉ NORTE`, `RETALHULEU`, `SACATEPÉQUEZ`, `SAN MARCOS`, `SANTA ROSA`, `SOLOLÁ`, `SUCHITEPÉQUEZ`, `TOTONICAPÁN`, `ZACAPA`.

- **Tratamiento en limpieza:** Sin modificaciones; la división regional de Guatemala (Norte/Sur/Oriente/Occidente) y `QUICHÉ NORTE` son valores oficiales del MINEDUC.
- **Variable derivada:** No.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `archivo_origen`

- **Descripción:** Nombre del archivo HTML de origen del que se extrajo el registro. Variable de trazabilidad añadida durante la consolidación.
- **Tipo de dato:** Texto (nombre de archivo).
- **Dominio permitido:** 23 valores posibles, uno por departamento capturado.
- **Valores posibles:** `mineduc_busca_establecimiento_diversificado_00.html` … `mineduc_busca_establecimiento_diversificado_22.html`.

- **Tratamiento en limpieza:** Sin modificaciones; es evidencia de procedencia inmutable.
- **Variable derivada:** **Sí** (añadida durante consolidación en `scripts/consolidar_crudos.py`).
  - **Método:** el script asigna el nombre del HTML procesado a cada fila extraída.
  - **Utilidad:** permite rastrear cualquier registro hasta su fuente HTML original en `data/raw/`.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## `departamento_origen`

- **Descripción:** Nombre del departamento según el encabezado del formulario MINEDUC del que se extrajo el registro. Variable de trazabilidad añadida durante la consolidación.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** 23 valores posibles.
- **Valores posibles:** Los 22 departamentos de Guatemala más `CIUDAD CAPITAL` (que el MINEDUC lista separado de `GUATEMALA`).

- **Tratamiento en limpieza:** Sin modificaciones; es evidencia de procedencia inmutable.
- **Variable derivada:** **Sí** (añadida durante consolidación en `scripts/consolidar_crudos.py`).
  - **Método:** el script extrae el nombre del departamento del título o contexto del HTML y lo asigna a cada fila.
  - **Utilidad:** complementa `archivo_origen` para verificar consistencia entre el departamento registrado en `DEPARTAMENTO` y el HTML de origen.

- **Nulos/NA en el dataset limpio:** 0 (0.00%).
- **Fuente/procedencia:** MINEDUC y evidencias de diagnóstico/limpieza; ver la sección canónica de Anggie.
- **Fecha exacta de extracción:** 2026-07-14.
- **Versión del conjunto limpio:** v0.1.0.
- **Responsable de la sección:** Anggie.

---

## Evidencia transversal y trabajo pendiente

- Duplicados: `outputs/tablas/duplicados_parciales.csv` conserva 718 pares `duplicado_probable` por confirmar y 271 pares `revisar`.
- Teléfonos vigentes: el control estricto sobre el limpio conserva 251 sospechosos; todo valor no vacío debe tener exactamente 8 dígitos.
- Referencia histórica: `outputs/tablas/problemas_potenciales.csv` conserva 201 hallazgos agregados del diagnóstico inicial por caracteres no numéricos; el limpio también contiene 50 valores numéricos con longitud distinta de 8, sin inferir correspondencia registro por registro.
- Territorio: `outputs/tablas/inconsistencias_territoriales.csv` conserva 145 filas `revisar`.
- La auditoría de entrega se conserva como recibo interno en `docs/auditoria_final.md`; no sustituye ninguno de los cinco materiales exigidos.
