# Especificación: Plan de entrega restante

## Propósito

Controlar la limpieza y entrega trazable de CC3084.

## Requisitos

### Requirement: Limpieza por lista permitida

La limpieza MUST preservar `.venv/` y procedencia; MAY eliminar solo `.atl/`, `.pytest_cache/`, `__pycache__/`, `*.egg-info/`, ambos `.gitkeep` redundantes y el cambio de Anggie tras preservar evidencia.

#### Scenario: eliminación aprobada
- DADO inventario, hashes y recuperación probada
- CUANDO se limpia
- ENTONCES elimina exclusivamente elementos de esa lista permitida.

#### Scenario: eliminación no prevista
- DADO una ruta no permitida, incluida `.venv/`
- CUANDO se intenta eliminar
- ENTONCES MUST fallar sin eliminación alguna.

### Requirement: Reconciliación de Anggie verificable

El cierre de `anggie-csv-reconciliation` MUST preservar ruta, hash, parser y mediciones antes de retirar el cambio incompleto; MUST corregir cifras no reproducibles sin canonizar su CSV.

#### Scenario: evidencia conciliada
- DADO el CSV accesible
- CUANDO se remide reproduciblemente
- ENTONCES conteos y diferencias publicados coinciden.

#### Scenario: medición no reproducible
- DADO cifras no reproducibles, incluidas 12,807 o 12,948
- CUANDO se cierra
- ENTONCES se corrigen y preserva la discrepancia.

### Requirement: Planificación autoritativa y contribución

`docs/planificacion.md` MUST cubrir cada requisito de `docs/instrucciones.md` con estado, evidencia, dependencias, aceptación y responsable. MUST asignar: Anggie, reconciliación/métricas y procedencia del Code Book; Iris, catálogo/consistencia territorial y dominios del Code Book; Jonathan, migración/guards/validación y ensamblaje Markdown/PDF del Code Book. Cada aporte MUST ser identificable en el repositorio.

El plan MUST cubrir cada requisito con estado, evidencia, dependencias, aceptación, responsable y asignaciones vigentes. MUST reflejar catálogo, consistencia, dominios y variables de Iris con pendientes abiertos. Code Book territorial, `README.md` y `AGENTS.md` MUST coincidir y MUST NOT declarar cierre.
(Anteriormente: no exigía evidencia territorial actual ni evitaba cierres prematuros.)

#### Scenario: cobertura completa
- DADO los requisitos del curso
- CUANDO se valida el plan
- ENTONCES cada uno posee todos los campos.

#### Scenario: asignación insuficiente
- DADO un integrante sin ambos aportes
- CUANDO se valida
- ENTONCES falla e identifica el faltante.

#### Scenario: documentación veraz
- DADO resultados verificados
- CUANDO se documentan
- ENTONCES declara 21 columnas, origen, provisionalidad y 7 pendientes.

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

### Requirement: Integridad de referencias y recuperación

Código, CLI, pruebas, docs y specs MUST usar `data/source/` como fuente y `data/processed/` como salida; pruebas MUST detectar referencias obsoletas y rollback MUST revertir todo conjuntamente.

#### Scenario: referencias consistentes
- DADO la migración
- CUANDO se prueban referencias
- ENTONCES no quedan rutas obsoletas y las pruebas pasan.

#### Scenario: fallo y rollback
- DADO una prueba fallida
- CUANDO se revierte
- ENTONCES restaura todo sin perder HTML, manifest ni evidencia.
