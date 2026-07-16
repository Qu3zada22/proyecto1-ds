# Delta: Diagnóstico de calidad cruda

## MODIFIED Requirements

### Requirement: Diagnóstico rúbrica plus

El sistema MUST diagnosticar desde `data/source/establecimientos_diversificado_mineduc.csv` filas, columnas, tipos, faltantes, únicos, duplicados, dominios, formatos y problemas; SHOULD reportar patrones sospechosos.
(Anteriormente: consumía `data/interim/`.)

#### Scenario: métricas reproducibles
- DADO la fuente válida
- CUANDO se diagnostica
- ENTONCES documento y tablas se regeneran mediante código.

#### Scenario: catálogo oficial ausente
- DADO que falta el catálogo oficial
- CUANDO se evalúan dominios
- ENTONCES se documenta y no se declaran inválidos sin evidencia.
