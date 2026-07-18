# Delta: Plan de entrega

## MODIFIED Requirements

### Requirement: Planificación autoritativa y contribución

El plan MUST cubrir cada requisito con estado, evidencia, dependencias, aceptación, responsable y asignaciones vigentes. MUST reflejar catálogo, consistencia, dominios y variables de Iris con pendientes abiertos. Code Book territorial, `README.md` y `AGENTS.md` MUST coincidir y MUST NOT declarar cierre.
(Anteriormente: no exigía evidencia territorial actual ni evitaba cierres prematuros.)

#### Scenario: cobertura completa
- DADO requisitos del curso
- CUANDO se valida el plan
- ENTONCES todos tienen esos campos.

#### Scenario: aporte insuficiente
- DADO evidencia incompleta
- CUANDO se valida
- ENTONCES identifica el faltante.

#### Scenario: documentación veraz
- DADO resultados verificados
- CUANDO se documentan
- ENTONCES declara 21 columnas, origen, provisionalidad y 7 pendientes.

## ADDED Requirements

### Requirement: No mutación fuera de alcance

El cambio MUST NOT modificar artefactos Anggie de duplicados, teléfonos, reconciliación o Code Book, ni `README.pdf`, crudos o fuentes.

#### Scenario: protección comprobada
- DADO artefactos protegidos
- CUANDO se regeneran entregables de Iris
- ENTONCES sus bytes permanecen idénticos.

#### Scenario: intento prohibido
- DADO una operación fuera de alcance
- CUANDO se solicita
- ENTONCES falla antes de mutar datos.
