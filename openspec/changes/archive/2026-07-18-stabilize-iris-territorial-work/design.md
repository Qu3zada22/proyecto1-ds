# Diseño: Estabilizar el trabajo territorial de Iris

## Enfoque técnico

Corregir regresiones sin ampliar decisiones. El catálogo versionado operará offline; su generador usará un URL `raw` fijado a un commit y verificará SHA-256, JSON, esquema, 22 departamentos, 340 municipios y códigos únicos antes del reemplazo atómico.

Causas raíz: expectativas antiguas de mayúsculas, `dir_fd` acoplado al monkeypatch, fixtures sin catálogo, métrica 20→19 contradictoria y rutas absolutas. Las siete parejas (145 filas) conservarán texto MINEDUC y `decision=revisar`; sus códigos serán provisionales. No se decidirán duplicados ni teléfonos.

## Slices y presupuesto de revisión

Estrategia `auto-chain`: S1 → S2 → S3. El límite de 400 cuenta **todas** las adiciones y eliminaciones Git, incluidos CSV y reportes. Esta decisión reemplaza la exclusión de generados usada en el forecast de `proposal.md`; la propuesta no se modifica.

| Área conceptual | Slice | Unidad / rollback |
|---|---|---|
| Regresiones | S1 | Mayúsculas, capacidad `dir_fd` estable y fixture CLI; revertir código y pruebas S1. |
| Contrato territorial | S2 | Pin/hash, validación, typo/provisional, rutas relativas y par territorial atómico; revertir S2. |
| Regeneración/documentación | S3a/S3b o más | Separar documentos/código de generados cuando sea revisable; revertir hijos en orden inverso. |

Al iniciar cada slice se registra `SLICE_BASE=<commit>` y antes de apply/PR se ejecuta exactamente:

```bash
git diff --numstat "$SLICE_BASE"..HEAD
LINES=$(git diff --numstat "$SLICE_BASE"..HEAD | awk '($1 !~ /^[0-9]+$/)||($2 !~ /^[0-9]+$/){bad=1;next}{n+=$1+$2} END{if(bad) exit 2; print n+0}')
test "$LINES" -le 400
```

El cálculo cubre el slice completo. Un valor no numérico o `LINES>400` bloquea apply: dividir y repetir; nunca omitir archivos.

## Decisiones de arquitectura

| Opción | Tradeoff | Decisión |
|---|---|---|
| Descargar siempre | Deriva con `main` y depende de red. | Rechazada. |
| CSV versionado + pin/hash del espejo | Offline y reproducible; el espejo no prueba procedencia primaria. | Elegida; documentar INE/Censo 2018 y límite de evidencia. |
| Alias únicos | Mezcla corrección con decisión humana. | Separar 2 typos aprobados de 7 mapeos provisionales. |

## Flujo de datos

```text
URL inmutable → SHA/JSON/esquema/conteos → catálogo atómico
                                              ↓
fuente 11,867×20 → limpieza 19 → enriquecimiento 21 → validación 7/145 revisar
                                              ↓                    ↓
                                  CSV/bitácora/métricas    CSV/Markdown relativos
```

Orden: pruebas → catálogo → limpieza → validación → hashes → documentos. No ejecutar `detectar_duplicados.py`.

## Cambios de archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `src/proyecto1_ds/cleaning.py` | Modificar | Desacoplar `dir_fd`; reconciliar métricas. |
| `src/proyecto1_ds/enrichment.py` | Modificar | Validar catálogo; separar correcciones/provisionales; mantener 20→21 y 7/145. |
| `src/proyecto1_ds/territorial.py` | Modificar | Rutas relativas, orden estable y CSV+Markdown transaccionales. |
| `scripts/generar_catalogo_territorial.py` | Modificar | Pin, SHA-256, validaciones y reemplazo atómico. |
| `scripts/{limpiar_dataset,validar_territorio}.py` | Modificar mínimo | Pasar raíz/dependencias explícitas. |
| `tests/test_{cleaning,cleaning_cli,repository_cleanup}.py` | Modificar | Regresiones, fixtures y hashes protegidos/autorizados. |
| `tests/test_territorial_contract.py` | Crear | Catálogo, enriquecimiento, pendientes, determinismo y atomicidad. |
| `data/reference/catalogo_territorial.csv`; `data/processed/establecimientos_diversificado_limpio.csv`; `outputs/tablas/{bitacora_limpieza,reporte_calidad_antes_despues,inconsistencias_territoriales}.csv`; `outputs/reportes/validacion_territorial.md` | Regenerar | Solo mediante CLIs. |
| `docs/code_book/variables_territoriales.md`, `docs/fuentes_datos.md`, `docs/planificacion.md`, `docs/plan_limpieza.md`, `README.md`, `AGENTS.md` | Modificar | Procedencia, 20→21, provisionales, pendientes y comandos. |

## Interfaces y contratos

- Catálogo exacto: `departamento_codigo,departamento,municipio_codigo,municipio`, 340 filas, 22 departamentos y códigos no vacíos/únicos; todo fallo conserva el archivo anterior y retorna 1.
- El consumidor valida el CSV local. Los siete alias asignan código provisional sin cambiar nombres ni `revisar`.
- El reporte serializa rutas POSIX relativas; ejecuciones equivalentes producen bytes idénticos. CSV y Markdown territoriales se publican o restauran juntos.

## Estrategia de pruebas

| Capa | RED esperado |
|---|---|
| Unidad | Mayúsculas; `dir_fd`; hash/esquema/22/340/unicidad; 2 typos frente a 7 provisionales; 7/145. |
| CLI | Fixture; fallo sin parciales; URL/hash inválido no reemplaza; rutas relativas; idempotencia. |
| Repositorio | 11,867×21; métricas coherentes; allowlist y hashes protegidos. |

Comandos: `uv run pytest tests/test_cleaning.py tests/test_cleaning_cli.py`; pruebas territoriales focalizadas; `uv run pytest`; `git diff --check`; `sha256sum`. Permanecen duplicados (`4b1c…`, `c9fe…`), `README.pdf` (`42e322…`), manifest (`8b72…`) y fuente (`c83a…`).

## Gate de regeneración y rollout

Antes de apply, crear un worktree temporal (`TMP=$(mktemp -d); git worktree add "$TMP/repro" HEAD`), ejecutar allí catálogo → limpieza → validación y comparar contenido, hashes y `git -C "$TMP/repro" diff --numstat`. Medir el subconjunto generado con la misma suma.

Si es revisable, S3a contiene código/documentos y S3b generados más sus aserciones de hash inseparables; pueden crearse más slices medidos. Si el diff generado solo supera 400 y no admite división segura por conjunto atómico, **detenerse antes de apply** y exigir aceptación explícita `size:exception`. No proceder silenciosamente.

No hay migración. Cada hijo `auto-chain` se integra tras su predecesor, se mide contra su propio `SLICE_BASE` y se revierte en orden inverso. Los generados se restauran por revert o regeneración con el commit anterior, nunca manualmente.

## Matriz de amenazas

N/A — no se implementa automatización shell, Git/PR ni integración de procesos; los comandos anteriores son gates manuales de entrega.

## Preguntas abiertas

Ninguna.
