# Delta: Limpieza trazable

## ADDED Requirements

### Requirement: Regresión y escritor seguro

La limpieza MUST poner `ESTABLECIMIENTO` y `DIRECTOR` en mayúsculas y MUST detectar capacidad segura con `os.open` bajo `monkeypatch`.

#### Scenario: rama segura
- DADO soporte seguro con sustitución
- CUANDO se inyecta una carrera
- ENTONCES la rama segura protege.

#### Scenario: plataforma portátil
- DADO capacidad ausente
- CUANDO se escribe
- ENTONCES usa modo portátil.

### Requirement: Catálogo requerido por CLI

El CLI MUST validar el catálogo antes de enriquecer o escribir; fixtures exitosos MUST proveerlo.

#### Scenario: fixture válido
- DADO fixture válido
- CUANDO se ejecuta el CLI
- ENTONCES alcanza resultado o fallo inyectado.

#### Scenario: catálogo ausente
- DADO catálogo ausente
- CUANDO se ejecuta el CLI
- ENTONCES falla sin mutar salidas.

## MODIFIED Requirements

### Requirement: Reporte antes/después

El reporte MUST comparar filas, columnas, faltantes, `<NBSP>`, ausencias y decisiones; MUST registrar 11,867 filas, 20→21 columnas y métricas territoriales.
(Anteriormente: no fijaba 20→21 ni métricas territoriales.)

#### Scenario: comparación generada
- DADO una limpieza completada
- CUANDO se consulta el reporte
- ENTONCES compara métricas y pendientes.

#### Scenario: regeneración autorizada
- DADO catálogo verificado y pruebas verdes
- CUANDO scripts regeneran salidas autorizadas
- ENTONCES registra 20→21 sin mutaciones ajenas.
