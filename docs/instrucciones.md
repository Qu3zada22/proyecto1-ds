# 🚀 CC3084 - Data Science

### Facultad de Ingeniería | 

Departamento de Ciencias de la Computación 

Universidad del Valle de Guatemala 

📅 **Semestre II-2026** 

---

📊 Proyecto 1: Obtención y Limpieza de los Datos 

> 💡 **¿Por qué es clave este proyecto?** > Los tipos y las fuentes de datos en las organizaciones reales son caóticos y diversos. El primer gran trabajo de un científico de datos es acceder a estas fuentes y preparar el terreno. Saltarse este paso o hacerlo mal implica un riesgo altísimo de llegar a resultados totalmente erróneos. Con este proyecto aprenderás a utilizar herramientas de acceso y limpieza de datos, haciéndolo de la forma más transparente y profesional posible.
> 
> 

### 🎯 Competencias a Desarrollar

* 🛠️ **Obtención efectiva:** Utiliza las herramientas a su disposición para extraer datos desde fuentes específicas.


* ✨ **Limpieza experta:** Modifica los datos crudos ejecutando procesos que le allanen el camino al analista de datos.


* 🧬 **Transparencia total:** Diseña un proceso de limpieza reproducible y verificable por cualquiera.


* 📖 **Documentación robusta:** Elabora un "Code Book" (Libro de Códigos) detallado con todos los metadatos necesarios para el análisis.



---

📝 Actividades del Proyecto 

### 📥 Paso 1: Descarga y Resguardo de Datos

1. Descargue los datos de los establecimientos educativos de todo el país que cubran hasta el nivel diversificado (**NIVEL ESCOLAR: DIVERSIFICADO**).


* 🌐 **Fuente oficial:** [MINEDUC - Busca Establecimiento](http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO GE/) 




2. Guarde los datos crudos en archivos con formato `.csv`.



### 🔍 Paso 2: Diagnóstico Inicial (¿Qué tan dañada está la data?)

3. Elabore un diagnóstico del conjunto de datos crudos. Este análisis debe estar respaldado obligatoriamente por **tablas y estadísticas generadas mediante código**, incluyendo como mínimo:


* 
**a.** Número total de registros (filas) y variables (columnas).


* 
**b.** Tipo de dato asignado a cada variable.


* 
**c.** Cantidad y porcentaje exacto de valores faltantes por variable.


* 
**d.** Cantidad de valores únicos por columna.


* 
**e.** Cantidad de registros que sean duplicados exactos.


* 
**f.** Variables con valores fuera de dominio o inconsistentes.


* 
**g.** Variables con formatos inconsistentes.


* 
**h.** Identificación explícita de problemas potenciales de calidad.





### 🗺️ Paso 3: Elaboración del Plan de Limpieza

4. Antes de modificar cualquier dato, deberá estructurar una estrategia especificando para cada variable:


* 
**a.** Problemas específicos encontrados.


* 
**b.** Regla exacta que utilizará para corregirlos y la justificación de por qué funcionará.


* 
**c.** Riesgos asociados a dicha transformación.





### 🧼 Paso 4: Ejecución de la Limpieza Profunda

5. Realice todas las operaciones necesarias para obtener un conjunto de datos consistente, reproducible y listo para el análisis. Revise minuciosamente los siguientes aspectos cuando apliquen:


* a. Valores Nulos y Vacíos: Explique cómo trató los `NA`, valores faltantes, cadenas vacías, espacios en blanco y textos como `"N/A"`, `"NULL"`, `"-"`, `"."`, `"Sin dato"`, etc.


* b. Tipos de Datos Correctos: Asegúrese de corregir números almacenados como texto, fechas guardadas como cadenas o variables categóricas mal codificadas.


* c. Normalización de Texto: Limpie de raíz espacios iniciales/finales, espacios múltiples, uso inconsistente de mayúsculas/minúsculas, tildes, caracteres especiales, signos de puntuación innecesarios y caracteres invisibles.


* **d. Consistencia de Categorías:** Justifique cualquier unificación. Detecte problemas de escritura (ej: *Guatemala*, *GUATEMALA*, *Guatemla*, *Guatemala.*) y estandarícelos.


* e. Uniformidad de Formatos: Verifique formatos consistentes en teléfonos, códigos, direcciones y nombres.


* f. Valores Inválidos: Identifique datos fuera del dominio esperado (departamentos inexistentes, municipios inválidos, teléfonos con letras o menos dígitos, códigos imposibles).


* g. Tratamiento de Duplicados: * Busque tanto duplicados exactos como parciales. Para los parciales, se sugiere usar similitud de cadenas (Levenshtein, Jaro-Winkler, Rapid Fuzz o equivalentes).


* ⚠️ *¡No elimine automáticamente!* Analice cada caso y documente la decisión tomada.




* h. Consistencia Cruzada: Revise que los valores de distintas variables no se contradigan entre sí y documente los hallazgos.


* i. Variables Derivadas: Si crea nuevas variables, justifique su creación, método de cálculo y utilidad (deben ir en el Libro de Códigos).





---

## 📊 Tablas de Control y Reportes

### 📋 6. Registro de Transformaciones

Cada cambio aplicado debe quedar perfectamente asentado en la siguiente bitácora para garantizar la reproducibilidad absoluta:

| Variable | Problema Detectado | Transformación Aplicada | Registros Afectados | Justificación |
| --- | --- | --- | --- | --- |
| *Ej: Teléfono* | *Contiene letras* | *Filtro Regex para dejar solo dígitos* | *42 filas* | *Alinear al dominio numérico válido* |



### 🧪 7. Validación del Conjunto Limpio

Al finalizar, ejecute pruebas automáticas para comprobar que el dataset cumple con los estándares de calidad establecidos:

* [ ] Cero registros duplicados exactos.


* [ ] Cero espacios en blanco al inicio o al final de los textos.


* [ ] Teléfonos con un formato completamente consistente.


* [ ] Nombres de departamentos y municipios validados contra el catálogo oficial.


* [ ] Todas las variables con el tipo de dato correcto y esperado.


* [ ] Cero categorías duplicadas por culpa de errores de escritura.


* [ ] Ningún valor inválido de los detectados en el diagnóstico inicial.



### 📈 8. Informe de Calidad de los Datos (Antes vs. Después)

Compare el estado del dataset mediante la siguiente tabla estructurada:

| Métrica | Antes | Después | Guía de Llenado / Justificación |
| --- | --- | --- | --- |
| **Registros** |  |  | Número total de filas. Justifique si varió (ej. borrado de duplicados).

 |
| **Variables** |  |  | Número total de columnas. Explique si agregó derivadas o quitó vacías.

 |
| **Valores faltantes** |  |  | Número y % total de celdas vacías (`NA`, `NULL`, vacíos).

 |
| **Variables con NA** |  |  | Cantidad de columnas que tienen al menos un valor faltante.

 |
| **Duplicados exactos** |  |  | Cantidad de filas 100% idénticas en todas sus columnas.

 |
| **Posibles duplicados** |  |  | Detectados por similitud. Indique cuántos se corrigieron/fusionaron.

 |
| **Variables con formato inconsistente** |  |  | Cantidad de columnas con fallas de espacios, mayúsculas, fechas, etc.

 |
| **Variables con tipo incorrecto** |  |  | Cantidad de variables con tipo de dato erróneo (ej. texto en vez de número).

 |
| **Categorías inconsistentes** |  |  | Variaciones de escritura que significan lo mismo.

 |
| **Errores corregidos** |  |  | Total numérico de correcciones o un resumen por tipo de error.

 |



---

## 📁 Cierre y Entregables Finales

### 💎 9. Generación del Conjunto Limpio

Deberá consolidar un **único conjunto de datos** con la información unificada de todos los departamentos, asegurando estructura consistente, tipos correctos, nombres descriptivos, formato uniforme y ausencia total de errores.

### 📖 10. Libro de Códigos (Code Book)

Cada variable del dataset final debe documentarse incluyendo de forma obligatoria:

* 
**a.** Descripción de la variable.


* 
**b.** Tipo de dato.


* 
**c.** Dominio permitido.


* 
**d.** Valores posibles.


* 
**e.** Tratamiento aplicado durante la fase de limpieza.


* 
**f.** Documentación de variables derivadas (si existen).


* 
**g.** Fecha exacta de extracción.


* 
**h.** Fuente de origen de los datos.


* 
**i.** Versión del conjunto limpio.



Nota: Todo el proceso de principio a fin debe ser 100% reproducible.

---

💯 Ponderación y Evaluación (Rúbrica) 

* 
**5 puntos:** Obtención, documentación y unión inicial de los datos.


* 
**15 puntos:** Análisis detallado y diagnóstico del estado de los datos crudos usando código.


* 
**10 puntos:** Plan de limpieza estructurado (problema, solución propuesta y sus riesgos).


* 
**30 puntos:** Calidad de la limpieza general y destreza para detectar duplicados exactos y parciales.


* 
**10 puntos:** Implementación de pruebas automatizadas de calidad de datos.


* 
**10 puntos:** Capacidad de demostrar la mejora cuantitativa mediante el reporte comparativo.


* 
**10 puntos:** Libro de códigos bien organizado, comprensible y con todos los metadatos y fuentes requeridos.


* 
**10 puntos:** Generación exitosa del archivo final único, limpio y listo para analítica.



> 🚨 **Alerta de Trabajo en Equipo:** Todos los integrantes del grupo deben registrar contribuciones significativas en el repositorio y en el Code Book. No se asignará nota a quien no demuestre participación activa.
> 
> 

---

📦 Material Final a Entregarse 

1. 
**Código Fuente:** Archivo legible en `.r`, `.rmd`, `.ipynb` o `.py` con todo el pipeline de código documentado.


2. 
**Repositorio:** Enlace al repositorio del proyecto con el código, los datos y el libro de códigos.


3. 
**Área de Trabajo:** Enlace al Google Docs o archivo Markdown donde desarrollaron el Libro de Códigos.


4. 
**Documento PDF:** Archivo definitivo en formato `.pdf` con el Libro de Códigos limpio.


5. 
**Data Limpia:** Archivo en formato `.csv` que contenga el dataset final unificado.
