# Especificación: Territorio trazable

## Requirements

### Requirement: Pendientes y códigos

El sistema MUST conservar 7 parejas/145 filas en `revisar`; MAY codificarlas provisionalmente con regla, evidencia y pendiente.

#### Scenario: pareja conocida
- DADO pareja ambigua conocida
- CUANDO se enriquece
- ENTONCES preserva texto, `revisar` y trazabilidad.

#### Scenario: similitud insuficiente
- DADO una coincidencia sin evidencia
- CUANDO se valida
- ENTONCES no autocorrige ni declara validez.

### Requirement: Informe determinístico

El informe MUST usar rutas relativas y MUST ser byte-estable para entradas equivalentes.

#### Scenario: raíces distintas
- DADO entradas equivalentes
- CUANDO se informa
- ENTONCES produce bytes idénticos.

#### Scenario: ruta absoluta
- DADO una ruta absoluta
- CUANDO se renderiza
- ENTONCES no expone prefijos del equipo.
