# Tareas: Limpieza del repositorio y plan de entrega

## Pronóstico de carga de revisión

| Campo | Valor |
|---|---|
| Líneas autoradas estimadas | 700–1,050 |
| Líneas no autoradas | Renombre CSV byte-idéntico: ~11,868; generadas: 0 |
| Riesgo del presupuesto de 400 líneas | Alto |
| PR encadenadas | Sí: PR1 → PR2 → PR3 hacia `main` |
| Estrategia de entrega | `auto-chain` |
| Estrategia de cadena | `stacked-to-main` |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Unidades de trabajo sugeridas

| Unidad | Meta | PR | Prueba focalizada | Harness real | Límite de rollback |
|---|---|---|---|---|---|
| 1 | Migración canónica | PR1 | `uv run pytest tests/test_{consolidation,diagnostics,cleaning,cleaning_cli}.py` | Consolidar→diagnosticar→limpiar | Renombre, contratos y referencias |
| 2 | Anggie y allowlist | PR2 | `uv run pytest tests/test_repository_cleanup.py` | Preflight + inventario | Recibo y eliminaciones permitidas |
| 3 | Plan autoritativo | PR3 | Matriz vs. `docs/instrucciones.md` | `git diff --check` | Plan y terminología aprobada |

## Fase 1: PR1 — Migración de fuente canónica

- [x] 1.1 Registrar en `outputs/reportes/migracion_fuente.md` inventario/SHA-256 de CSV, 23 HTML, manifest, procesado y outputs; aceptación: baseline recuperable.
- [x] 1.2 RED: adaptar cuatro suites a `data/source/`; rechazar ruta externa/symlink sin salidas y detectar bytes distintos, procedencia incompleta o referencias antiguas.
- [x] 1.3 GREEN: mover con `git mv` a `data/source/establecimientos_diversificado_mineduc.csv`; actualizar tres módulos y CLI, sin alias obsoleto.
- [x] 1.4 Actualizar `docs/{fuentes_datos,diagnostico,plan_limpieza}.md` y tres specs activas; preservar `archive/`.
- [x] 1.5 Evidenciar suite, 11,867×20, 11,867 códigos, SHA-256 completo, cero referencias vivas y rename `-M`; protegidos idénticos.

## Fase 2: PR2 — Limpieza permitida y evidencia Anggie

- [x] 2.1 RED: crear `tests/test_repository_cleanup.py`; fallar fuera de raíz Git, ante cambios protegidos staged/unstaged u objetivo no permitido, incluida `.venv/`.
- [x] 2.2 Preservar en `docs/reconciliacion_anggie.md` ref/objeto, ruta, hash, parser, comando y conteos; reproducir 12,807/12,948 o retirar la afirmación exacta.
- [x] 2.3 Tras preflight/recuperación, eliminar solo dos `.gitkeep`, cambio Anggie y cachés inventariadas aprobadas; nunca glob amplio ni `git clean`.
- [x] 2.4 Evidenciar prueba, diff/inventario y preservación de HTML, manifest, `.venv/`, canónico, procesado, outputs y specs activas.

## Fase 3: PR3 — Plan autoritativo inmediato

- [x] 3.1 Reescribir `docs/planificacion.md`: una fila/requisito con fuente, evidencia, estado, brecha, responsable, dependencia, aceptación y PR; marcar futuro «planificado/no implementado».
- [x] 3.2 Registrar ruta crítica; exigir por persona commit identificable y sección Code Book. Aceptación: ninguna carece de ambos.
- [x] 3.3 Actualizar README/procedencia solo ante ruta/terminología obsoleta aprobada; nunca declarar futuros completos.

## Hoja de ruta posterior — Fuera del alcance ejecutable de este cambio

Estas referencias conservan el plan de entrega, pero no son tareas ejecutables ni completadas por este cambio. Su estado autoritativo permanece **Planificado/no implementado** en `docs/planificacion.md`.

- **Seguimiento 4.1 — Anggie:** reconciliación reproducible, reporte/bitácora de duplicados parciales, excepciones telefónicas y procedencia/Code Book; evidencia futura en `outputs/` y `docs/codebook.md`.
- **Seguimiento 4.2 — Iris:** catálogo territorial, consistencia departamento–municipio, borrador Code Book de todas las variables y validaciones legibles por máquina cuando proceda.
- **Seguimiento 4.3 — Jonathan:** integración, CLI/reporte final, reporte de calidad, README/E2E, merge/PDF Code Book y auditoría; indicar dependencias, aceptación y rutas.
