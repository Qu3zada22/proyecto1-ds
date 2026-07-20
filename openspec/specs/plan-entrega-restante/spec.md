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

### Requirement: Validación final reproducible

El sistema MUST evaluar exactamente los siete controles del paso 7 y publicar `outputs/tablas/validacion_final.csv` con estado `cumple`, `requiere_revision` o `falla`, conteo con unidad y evidencia portable. MUST conservar como revisión 718 duplicados probables, 260 ambiguos, 245 teléfonos sospechosos vigentes y 145 filas territoriales; MUST registrar 11 independientes y 6 teléfonos aprobados. MUST distinguir los 245 vigentes del conteo histórico agregado de 201 y MUST NOT inferir correspondencia registro por registro.

#### Scenario: validación con pendientes conocidos
- DADO el dataset limpio y las evidencias vigentes
- CUANDO se ejecuta `scripts/validar_dataset.py`
- ENTONCES genera siete filas deterministas sin presentar pendientes como éxito.

#### Scenario: entrada inválida
- DADO un insumo ausente o malformado y una salida previa
- CUANDO se valida
- ENTONCES falla sin alterar los bytes de la salida previa.

### Requirement: Reporte integral antes/después

El sistema MUST publicar exactamente las diez métricas del paso 8 una sola vez, con unidades, porcentajes y evidencia portable. MUST distinguir filas, celdas, variables, pares y pendientes, sin sumar correcciones superpuestas como un total artificial. Fuente y limpio MUST contener registros y conservar igual cardinalidad; una diferencia de filas MUST fallar.

La limpieza MUST publicar su evidencia intermedia en `reporte_limpieza_base.csv` y MUST NOT sobrescribir el reporte integral. La validación MUST recomputar duplicados y territorio desde el limpio mediante los módulos existentes y rechazar evidencia stale. Las decisiones MUST pertenecer al dominio cerrado automático/manual; ninguna decisión fusiona o elimina filas.

#### Scenario: reporte real reproducible
- DADO fuente, limpio, diagnóstico, bitácora, duplicados, territorio y validación
- CUANDO se ejecuta `scripts/generar_reporte_calidad.py`
- ENTONCES genera exactamente diez filas e integra 978 pares, 245 teléfonos sospechosos vigentes y 145 filas pendientes; 201 permanece etiquetado como diagnóstico histórico agregado.

#### Scenario: evidencia inválida
- DADO un insumo ausente o malformado y un reporte previo
- CUANDO se genera
- ENTONCES falla sin alterar el reporte previo.

### Requirement: Code Book maestro Markdown/PDF

El sistema MUST ensamblar `docs/code_book.md` desde las secciones canónicas de Anggie e Iris, con exactamente 21 variables y un dataset no vacío. MUST exigir campos con contenido, rechazar rutas absolutas, derivar fecha/versión coincidentes y publicar un solo conteo autoritativo de faltantes desde el limpio. MUST generar `docs/code_book.pdf` de forma atómica y byte-idéntica, con tamaño carta, páginas, texto extraíble y un solo título.

#### Scenario: ensamblado reproducible
- DADO ambas secciones válidas y el dataset limpio
- CUANDO se ejecuta `scripts/generar_code_book.py`
- ENTONCES publica atómicamente 21 variables sin ocultar 978 pares, 245 teléfonos sospechosos vigentes ni 145 filas pendientes, y conserva 201 como referencia histórica agregada.

#### Scenario: fuente inválida
- DADO una fuente ausente, incompleta, duplicada o desordenada y un maestro previo
- CUANDO se ensambla
- ENTONCES falla sin alterar el maestro previo.

#### Scenario: PDF reproducible
- DADO el maestro y la hoja de estilo válidos, con las cinco herramientas disponibles
- CUANDO se ejecuta `scripts/generar_code_book_pdf.py` dos veces
- ENTONCES publica un PDF byte-idéntico, no vacío, tamaño carta, con páginas, texto y un solo título.

#### Scenario: PDF inválido o herramienta ausente
- DADO un PDF previo y un fallo operativo o validación negativa
- CUANDO se intenta generar
- ENTONCES falla sin alterar el PDF previo.

### Requirement: Auditoría interna honesta

`docs/auditoria_final.md` MUST registrar hashes, comandos, cinco materiales, contribuciones Git reales y bloqueos manuales. MUST presentarse como recibo interno y MUST NOT declarar el dataset sin errores ni la entrega plenamente apta mientras R5e, R5f, R5g, R7, R9, RE o RT sigan parciales.

El PDF MUST contener el SHA-256 del Markdown usado para renderizarlo. Su CLI MUST restringir `--output` a `docs/*.pdf`, usar timeout finito y normalizar fallos operativos sin destruir la salida previa.
