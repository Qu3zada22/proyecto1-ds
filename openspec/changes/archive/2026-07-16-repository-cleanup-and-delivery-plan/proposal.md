# Propuesta: Limpieza del repositorio y plan de entrega

## Intención

Fijar el linaje `HTML MINEDUC + manifest → CSV canónico → data/processed/` y una planificación autoritativa para cerrar CC3084 sin perder procedencia.

## Alcance

### Incluido
- Mover sin alterar bytes el consolidado a `data/source/establecimientos_diversificado_mineduc.csv`; migrar referencias vivas en código, CLI, pruebas, docs y specs.
- Conservar los 23 HTML, manifest, `data/processed/` y evidencia de Anggie; corregir métricas solo reproduciblemente.
- Retirar ambos `.gitkeep` y, tras preservar evidencia, `openspec/changes/anggie-csv-reconciliation/`. Limpiar `.atl/`, `.pytest_cache/`, `__pycache__/` y `*.egg-info/`; conservar `.venv/`.
- Reescribir `docs/planificacion.md` con estado por requisito, brechas, dependencias, responsables y aceptación.

### Fuera de alcance
- Implementar todos los pendientes: el plan los divide en cambios/PR posteriores.
- Borrar procedencia/historial, canonizar el CSV de Anggie o añadir capas innecesarias.

## Capacidades

### Nuevas
- `plan-entrega-restante`: estado, asignación, dependencia y aceptación trazables a `docs/instrucciones.md`.

### Modificadas
- `consolidacion-cruda`: salida canónica reproducible en `data/source/`.
- `diagnostico-calidad-cruda`: entrada canónica desde `data/source/`.
- `limpieza-dataset-trazable`: entrada desde `data/source/`, salida en `data/processed/`; alternativas solo como evidencia.

## Enfoque

Migración mínima en unidades ≤400 líneas autoradas; `auto-chain` dividirá las mayores. Ruta crítica: fuente → catálogo territorial → reconciliación/duplicados → validación → reporte → Code Book Markdown/PDF → README → auditoría.

| Responsable | Entrega y aceptación |
|---|---|
| Anggie | Reconciliación reproducible (ruta, hash, parser, conteos) y reporte de diez métricas. No afirmar 12,807/12,948 sin remedir. |
| Iris | Catálogo oficial versionado, consistencia territorial y candidatos parciales con decisión humana/bitácora. |
| Jonathan | Migración byte-idéntica, pruebas/guards, validación, README, ensamblaje Code Book/PDF y auditoría. |

Cada integrante aportará commits y contenido identificable.

## Áreas afectadas

Datos; contratos en `src/`, scripts y pruebas; documentación y OpenSpec activo.

## Riesgos

| Riesgo | Nivel | Mitigación |
|---|---|---|
| Referencias inconsistentes | Alto | Inventario, pruebas y regeneración byte-idéntica |
| Pérdida de evidencia | Alto | Preservar antes de borrar; respetar historial |
| Territorio/duplicados erróneos | Medio | Fuente versionada y revisión humana |

## Recuperación

Revertir movimiento/referencias juntos y restaurar eliminaciones con Git. Antes de borrar, registrar inventario/hashes y preservar evidencia. Los ignorados se regeneran; `.venv/` permanece.

## Dependencias

- Catálogo oficial versionado, CSV de Anggie accesible y generador PDF reproducible.

## Criterios de éxito

- [ ] Los 23 HTML/manifest quedan intactos y regeneran 11,867×20, 11,867 códigos, SHA-256 `c83ac119…ed82f`.
- [ ] Cero referencias vivas anteriores; pruebas/CLI usan `data/source/`; salida en `data/processed/`.
- [ ] La planificación cubre requisitos, brechas, ruta crítica, asignaciones, aceptación, dependencias y contribuciones visibles.
- [ ] Solo se elimina lo autorizado tras inventario, preservación y prueba de recuperación.
