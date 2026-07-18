# Propuesta: Estabilizar el trabajo territorial de Iris

## Intención

Cerrar el alcance de Iris con pruebas, procedencia reproducible y documentación honesta, sin resolver ambigüedades ni invadir entregables de Anggie. Debe recuperar las 109 pruebas y mantener 11,867 filas y 20→21 columnas.

## Alcance

### Incluido
- Restaurar 109 pruebas y agregar pruebas de comportamiento para normalización, catálogo, enriquecimiento y validación territorial.
- Fijar el espejo del catálogo a una revisión inmutable; validar SHA-256, esquema, 22 departamentos y 340 municipios, diferenciando espejo y fuente primaria.
- Mantener 7 parejas (145 filas) como `revisar`, con códigos provisionales trazables y sin resolución inventada.
- Emitir solo rutas relativas determinísticas en el informe territorial; regenerar, tras pruebas verdes, únicamente salidas limpias/territoriales afectadas y métricas 20→21.
- Actualizar Code Book territorial, plan, `README.md` y `AGENTS.md` sin declarar terminado el proyecto.

### Excluido
- Decisiones o cambios en duplicados parciales, teléfonos, reconciliación o sección Code Book de Anggie.
- Mutación de `README.pdf` o declaración final de todo el proyecto.

## Capacidades

### Nuevas
- `catalogo-territorial-verificable`: pin, procedencia y validación previa al reemplazo atómico.
- `validacion-enriquecimiento-territorial`: códigos derivados trazables, pendientes y reportes determinísticos.

### Modificadas
- `limpieza-dataset-trazable`: normalización esperada, dependencia del catálogo y métricas 20→21.
- `plan-entrega-restante`: evidencia y estado exacto del aporte territorial de Iris.

## Enfoque y slices

Estrategia `auto-chain`, stacked-to-main, máximo 400 líneas de autoría por PR:
1. Regresiones de limpieza y fixtures CLI (180–260).
2. Contrato reproducible de catálogo/territorio (260–380).
3. Regeneración autorizada, hashes y documentación (180–320; generados fuera del presupuesto de autoría).

## Áreas afectadas

| Área | Impacto |
|---|---|
| `src/proyecto1_ds/{cleaning,enrichment,territorial}.py`, `scripts/` | Modificado |
| `tests/` | Modificado/nuevo |
| `data/processed/`, `data/reference/`, `outputs/` territoriales | Regenerado/verificado |
| `docs/`, `README.md`, `AGENTS.md` | Modificado |

## Protección, riesgos y rollback

Hashes inmutables: `data/raw/manifest.json` `8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07`; fuente canónica `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f`; duplicados CSV `4b1c6d6aa7d720872b88e3a5ddcd5402657dede539518fe9a330f541593954c6`, informe `c9feec7bc2b09fc449439f87781a920539dae668d79c95eca060f2ce3ea93398`; `README.pdf` `42e3227ede19d0c7f12da930db0bff01ef0adbcbc4e69efe9150ac06fefba2e1`. También se protegen `data/raw/**`, `data/source/**` y artefactos/decisiones de Anggie.

Riesgo alto: confundir códigos provisionales o espejo con validación oficial. Se mitiga con estados explícitos, pruebas y recibos. Rollback por slice: revertir código, pruebas y documentos; regenerar atómicamente las salidas autorizadas desde el estado previo. Nunca editar datos manualmente.

## Dependencias

- Catálogo fijado y `uv`; TDD estricto antes de regenerar.

## Criterios de aceptación

- [ ] `uv run pytest`: las 109 pruebas existentes y las nuevas pasan; `git diff --check` queda limpio.
- [ ] Catálogo rechaza pin/checksum/esquema/conteos inválidos y documenta espejo versus fuente primaria.
- [ ] Las 7 parejas siguen `revisar`; códigos provisionales y rutas relativas son trazables y byte-estables.
- [ ] Solo cambian salidas autorizadas; hashes protegidos permanecen; dataset conserva 11,867 filas y 21 columnas.
- [ ] Cada slice respeta 400 líneas de autoría y puede verificarse/revertirse independientemente.
