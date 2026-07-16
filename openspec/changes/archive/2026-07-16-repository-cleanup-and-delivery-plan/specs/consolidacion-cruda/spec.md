# Delta: Consolidación cruda

## MODIFIED Requirements

### Requirement: Unión sin limpieza

El sistema MUST consolidar sin limpieza en `data/source/establecimientos_diversificado_mineduc.csv`; la migración MUST preservar bytes y contenido.
(Anteriormente: salida en `data/interim/`.)

#### Scenario: migración íntegra
- DADO el CSV anterior
- CUANDO se migra con sus referencias
- ENTONCES origen y destino tienen bytes y SHA-256 idénticos, sin referencias operativas antiguas.

#### Scenario: diferencia detectada
- DADO una diferencia de bytes, contenido o referencias
- CUANDO se valida
- ENTONCES falla y se revierten ruta y referencias.

### Requirement: Extracción estructural desde HTML oficial

El sistema MUST conservar 23 HTML y manifest, y regenerar desde ellos la fuente canónica sin limpieza.
(Anteriormente: escribía en `data/interim/`.)

#### Scenario: reproducción comprobada
- DADO 23 HTML y manifest intactos
- CUANDO se consolida
- ENTONCES genera 11,867×20, 11,867 códigos y SHA-256 `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`.

#### Scenario: procedencia incompleta
- DADO un HTML ausente o discordante
- CUANDO se consolida
- ENTONCES no publica salida parcial e identifica la evidencia inválida.
