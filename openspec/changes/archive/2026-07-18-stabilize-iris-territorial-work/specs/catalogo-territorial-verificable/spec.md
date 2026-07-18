# Especificación: Catálogo verificable

## Requirements

### Requirement: Procedencia inmutable

El catálogo MUST registrar pin inmutable, SHA-256 y cadena espejo–fuente primaria INE.

#### Scenario: procedencia válida
- DADO el recurso fijado
- CUANDO se verifica
- ENTONCES pin, checksum y origen coinciden.

#### Scenario: integridad inválida
- DADO pin mutable o alteración
- CUANDO se verifica
- ENTONCES rechaza sin reemplazar el catálogo.

### Requirement: Reemplazo validado

El generador MUST validar esquema, códigos y 22 departamentos/340 municipios antes de reemplazar atómicamente.

#### Scenario: catálogo completo
- DADO un insumo válido
- CUANDO se genera
- ENTONCES se reemplaza atómicamente.

#### Scenario: contenido inválido
- DADO contenido inválido
- CUANDO se genera
- ENTONCES falla y preserva bytes previos.
