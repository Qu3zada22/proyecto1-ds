# Code Book — Variables territoriales (sección de Iris)

Esta sección de Iris está completa para las **4 variables territoriales** del dataset limpio `data/processed/establecimientos_diversificado_limpio.csv`. Jonathan mantiene la integración final pendiente del Code Book de 21 variables (Markdown/PDF).

**Metadatos comunes a estas variables**

- **Fecha exacta de extracción:** 2026-07-14 (captura de los HTML oficiales; ver `data/raw/manifest.json`).
- **Fuente de origen (valores base):** MINEDUC — [Busca Establecimiento](https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/).
- **Procedencia de códigos:** `data/reference/catalogo_territorial.csv` se reproduce desde un **espejo/conversión comunitaria** fijado; la fuente primaria declarada es INE, Censo 2018. El espejo no constituye una publicación primaria oficial.
- **Estado de revisión:** 7 parejas (145 filas) conservan `decision=revisar`; sus códigos son provisionales. Las 2 variantes tipográficas corregidas abarcan 19 filas.
- **Versión del conjunto limpio:** v0.1.0.

**Plantilla usada por variable** (para que las demás secciones del equipo calcen): descripción · tipo de dato · dominio permitido · valores posibles · tratamiento en limpieza · variable derivada · fecha de extracción · fuente · versión.

---

## `DEPARTAMENTO`

- **Descripción:** Departamento administrativo del establecimiento según el MINEDUC.
- **Tipo de dato:** Texto (categórico).
- **Dominio permitido:** Los 22 departamentos oficiales de Guatemala, más el valor especial `CIUDAD CAPITAL` que el MINEDUC usa para el municipio de Guatemala.
- **Valores posibles:** 23 valores observados: `ALTA VERAPAZ`, `BAJA VERAPAZ`, `CHIMALTENANGO`, `CHIQUIMULA`, `CIUDAD CAPITAL`, `EL PROGRESO`, `ESCUINTLA`, `GUATEMALA`, `HUEHUETENANGO`, `IZABAL`, `JALAPA`, `JUTIAPA`, `PETEN`, `QUETZALTENANGO`, `QUICHE`, `RETALHULEU`, `SACATEPEQUEZ`, `SAN MARCOS`, `SANTA ROSA`, `SOLOLA`, `SUCHITEPEQUEZ`, `TOTONICAPAN`, `ZACAPA`.
- **Tratamiento en limpieza:** Canonización a mayúsculas y normalización de espacios, NBSP y caracteres invisibles. El nombre original del MINEDUC se conserva (incluido `CIUDAD CAPITAL`); su consistencia se valida contra el catálogo INE sin alterar el valor.
- **Variable derivada:** No.

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
