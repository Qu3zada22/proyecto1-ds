# Delta: Limpieza de dataset trazable

## MODIFIED Requirements

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
