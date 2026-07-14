# Especificación: Adquisición de datos MINEDUC

## Propósito

Definir cómo obtener o registrar datos crudos oficiales de establecimientos educativos de MINEDUC, preservando fuente, alcance, fecha y versión sin aplicar limpieza. Los artefactos crudos preferidos son CSV; cuando no exista punto final CSV directo, se permiten páginas HTML oficiales de resultados MINEDUC preservadas sin modificación.

## Requisitos

### Requisito: Adquisición mixta trazable

El sistema MUST intentar adquirir datos desde la fuente oficial de MINEDUC cuando esté disponible. Si no existe punto final CSV directo, MAY preservar HTML oficial de resultados MINEDUC como artefacto crudo con `metodo: html-form`. Si la adquisición automática falla, MUST reportar el motivo claramente y MAY usar CSV crudos colocados manualmente cuando existan.

#### Escenario: descarga oficial disponible

- DADO que MINEDUC permite obtener datos de establecimientos de nivel diversificado
- CUANDO se ejecuta la adquisición
- ENTONCES se guardan CSV crudos o HTML oficiales de resultados en `data/raw/`
- Y se conserva evidencia de la fuente oficial usada.

#### Escenario: fallback manual permitido

- DADO que la adquisición automática falla o no existe exportación directa
- CUANDO existen CSV crudos descargados manualmente
- ENTONCES el sistema los registra como entrada válida
- Y documenta el fallo automático sin modificar los datos.

#### Escenario: HTML oficial preservado sin CSV directo

- DADO que MINEDUC entrega resultados oficiales por WebForms
- Y no se encontró punto final CSV directo para el alcance solicitado
- CUANDO se captura la fuente oficial disponible
- ENTONCES se preserva el HTML de resultados en `data/raw/`
- Y el manifest registra `metodo: html-form` sin inventar CSV crudo.

#### Escenario: alcance no disponible

- DADO que MINEDUC no publica parte del alcance esperado
- CUANDO se registra la adquisición
- ENTONCES el alcance disponible y el faltante quedan documentados.

### Requisito: Metadatos de fuente y versión

El sistema MUST registrar por lote la URL o fuente, fecha de extracción, cobertura real, departamento cuando aplique, método de adquisición y versión SemVer-like del dataset crudo.

#### Escenario: metadatos completos

- DADO que se incorpora un CSV crudo o un HTML oficial preservado
- CUANDO se registra su linaje
- ENTONCES quedan documentadas fuente, fecha, versión y cobertura.
