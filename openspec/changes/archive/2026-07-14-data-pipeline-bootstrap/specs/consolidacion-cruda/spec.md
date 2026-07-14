# Especificación: Consolidación cruda

## Propósito

Definir la unión inicial de artefactos crudos en un conjunto intermedio, sin limpieza ni transformaciones correctivas, preservando trazabilidad por registro. Los artefactos fuente pueden ser CSV o, cuando no exista CSV directo, páginas HTML oficiales de resultados MINEDUC preservadas en `data/raw/`.

## Requisitos

### Requisito: Unión sin limpieza

El sistema MUST consolidar los artefactos crudos disponibles hacia `data/interim/` sin recodificar, normalizar, deduplicar, corregir tipos, eliminar filas ni modificar valores fuente. Si existen CSV crudos, los procesa como entrada tabular directa. Si no existe CSV directo y el manifest registra HTML oficial MINEDUC con `metodo: html-form`, el sistema MUST extraer las tablas de resultados desde esos HTML crudos como entrada tabular estructural.

#### Escenario: esquemas compatibles

- DADO que existen CSV crudos o HTML oficiales MINEDUC con tablas de resultados de estructura compatible
- CUANDO se ejecuta la consolidación
- ENTONCES se produce un dataset intermedio unificado
- Y los valores originales permanecen sin cambios correctivos.

#### Escenario: esquemas incompatibles

- DADO que uno o más CSV o tablas extraídas desde HTML tienen columnas incompatibles
- CUANDO se intenta consolidar
- ENTONCES el sistema reporta la incompatibilidad
- Y no inventa coerciones ni limpiezas silenciosas.

### Requisito: Extracción estructural desde HTML oficial

Cuando la fuente preservada sea HTML oficial MINEDUC, el sistema MUST leer `data/raw/*.html`, localizar las tablas de resultados y serializar sus celdas hacia `data/interim/establecimientos_diversificado_raw_unificado.csv` sin limpiar los valores. Extraer celdas de una tabla HTML hacia CSV es consolidación estructural, no limpieza, siempre que preserve el texto fuente de cada celda tal como aparece en el artefacto oficial, salvo el escapado, delimitación y saltos necesarios por la serialización CSV.

#### Escenario: HTML oficial sin CSV directo

- DADO que el manifest registra artefactos HTML oficiales MINEDUC con `metodo: html-form`
- Y no se encontró punto final CSV directo
- CUANDO se ejecuta la consolidación
- ENTONCES el sistema extrae las celdas de las tablas de resultados hacia el CSV intermedio
- Y no corrige, normaliza, deduplica, tipa ni elimina valores.

#### Escenario: HTML sin tabla esperada

- DADO que un artefacto HTML oficial no contiene la tabla de resultados esperada
- CUANDO se intenta consolidar
- ENTONCES el sistema reporta el problema para ese archivo
- Y no genera una salida parcial silenciosa.

### Requisito: Trazabilidad por registro

Cada registro consolidado MUST conservar `archivo_origen` y `departamento_origen`, tanto si proviene de CSV como si proviene de una tabla extraída desde HTML oficial. Si el departamento no puede determinarse con confianza, MUST quedar marcado o reportado como alcance pendiente.

#### Escenario: procedencia completa

- DADO que un registro proviene de un CSV o HTML identificable
- CUANDO se agrega al dataset intermedio
- ENTONCES conserva archivo y departamento de origen.

#### Escenario: departamento ambiguo

- DADO que el departamento no está disponible o es ambiguo
- CUANDO se consolida el registro
- ENTONCES la ambigüedad se conserva para diagnóstico posterior.
