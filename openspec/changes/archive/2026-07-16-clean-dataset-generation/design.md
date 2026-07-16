# Diseño: Generación conservadora de dataset limpio

## Enfoque técnico

Agregar un slice determinístico y trazable después de la consolidación/diagnóstico existentes. La entrada única será `data/interim/establecimientos_diversificado_raw_unificado.csv`; la limpieza escribirá solo `data/processed/establecimientos_diversificado_limpio.csv`, `outputs/tablas/bitacora_limpieza.csv` y `outputs/tablas/reporte_calidad_antes_despues.csv`. Debe seguir contratos concretos ya presentes: CLI delgado con `ROOT` y `main()->int` como `scripts/diagnosticar_crudos.py`, lectura CSV estricta como `diagnostics._read_csv`, guards por raíz como `_resolve_interim_csv`, y commit multi-salida con temporales/backups como `diagnostics._write_outputs_atomically`.

## Decisiones de arquitectura

| Decisión | Opción | Alternativas consideradas | Rationale |
|---|---|---|---|
| Módulo de limpieza | Crear `src/proyecto1_ds/cleaning.py` con `clean_dataset()` y `write_cleaning_outputs()` | Mezclar reglas en `diagnostics.py` | Mantiene diagnóstico read-only y separa “medir” de “transformar”. |
| CLI público | Crear `scripts/limpiar_dataset.py` | Ejecutar limpieza solo desde tests/imports | El proyecto usa CLIs delgados (`diagnosticar_crudos.py`, `consolidar_crudos.py`) como contrato reproducible. |
| Atomicidad multi-salida | Un solo commit lógico para CSV limpio + bitácora + reporte | Escribir cada archivo de forma independiente | Evita artefactos mezclados si falla una escritura; adapta el patrón de backups/restauración de `diagnostics._write_outputs_atomically`. |
| Determinismo | Salidas byte-for-byte idénticas para misma entrada | Incluir timestamps, rutas absolutas o filas no ordenadas | Permite idempotencia verificable y evita filas duplicadas/stale en bitácora/reporte. |
| Alcance conservador | Automatizar solo reglas seguras | Resolver territorio, teléfonos o duplicados parciales | Evita decisiones semánticas sin catálogo/revisión humana. |

## Flujo de datos

```text
data/interim/establecimientos_diversificado_raw_unificado.csv
  └─ scripts/limpiar_dataset.py
      └─ proyecto1_ds.cleaning
          ├─ normaliza NBSP/espacios y ausencias claras
          ├─ elimina columna <NBSP> solo si está vacía
          ├─ conserva identificadores/categorías como str
          └─ escribe salidas atómicas
              ├─ data/processed/establecimientos_diversificado_limpio.csv
              ├─ outputs/tablas/bitacora_limpieza.csv
              └─ outputs/tablas/reporte_calidad_antes_despues.csv
```

## Cambios de archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `src/proyecto1_ds/cleaning.py` | Crear | Reglas, lectura estricta, métricas antes/después, bitácora y escritura atómica. |
| `scripts/limpiar_dataset.py` | Crear | CLI con defaults del proyecto y guards de rutas. |
| `tests/test_cleaning.py` | Crear | Unit tests TDD para reglas y límites. |
| `tests/test_cleaning_cli.py` | Crear | Tests del CLI, errores sin traceback y restricciones de rutas. |

## Interfaces / contratos

- Entrada: CSV UTF-8 tabular estricto en `data/interim/establecimientos_diversificado_raw_unificado.csv`; no se acepta entrada fuera de `data/interim/` desde CLI.
- CSV limpio: mismas filas; columnas originales salvo eliminación segura de encabezado NBSP (`"\xa0"`) cuando todos sus valores sean ausentes. Todos los valores se escriben como texto.
- Ausencias: normalizar a cadena vacía en CSV para `""`, espacios, NBSP, `N/A`, `NA`, `NULL`, `None`, `-`, `.`, `Sin dato`, `----` cuando el valor completo coincide tras `strip/casefold`.
- Espacios: reemplazar NBSP por espacio normal, aplicar `strip()` y colapsar espacios internos múltiples; no cambiar tildes, puntuación significativa, nombres, direcciones ni teléfonos ambiguos.
- `bitacora_limpieza.csv`: columnas `variable`, `regla`, `filas_afectadas`, `justificacion`, `riesgo`, `evidencia_fuente`.
- `reporte_calidad_antes_despues.csv`: columnas `metrica`, `variable`, `antes`, `despues`, `estado`, `nota`; debe incluir filas/columnas, faltantes por variable, columna `<NBSP>`, marcadores normalizados y decisiones diferidas.
- Entrada malformada: CSV vacío, encabezados duplicados o filas ragged MUST fallar sin salidas parciales. CSV solo con encabezado es válido: genera CSV limpio solo con encabezado, bitácora/reporte con `filas=0` y conteos cero.
- Atomicidad: `write_cleaning_outputs()` MUST escribir primero temporales en los directorios destino, respaldar salidas previas, reemplazar las tres salidas y restaurar/eliminar destinos si cualquier paso falla. Si la restauración falla, MUST lanzar `CleaningOutputError` con contexto y preservar backups para recuperación manual.
- Idempotencia: dos ejecuciones con la misma entrada MUST producir bytes idénticos en las tres salidas; no se permiten timestamps, PIDs, rutas absolutas ni append. Bitácora y reporte se reescriben completos con orden estable.

Ejemplo API:

```python
result = clean_dataset(Path("data/interim/establecimientos_diversificado_raw_unificado.csv"))
write_cleaning_outputs(result)
```

Ejemplo CLI:

```bash
uv run python scripts/limpiar_dataset.py \
  --interim-csv data/interim/establecimientos_diversificado_raw_unificado.csv \
  --output-file data/processed/establecimientos_diversificado_limpio.csv \
  --tables-dir outputs/tablas
```

Exit codes: `0` solo cuando las tres salidas quedan comprometidas; `1` para errores esperados de entrada, rutas o escritura, en `stderr` sin traceback.

## Estrategia de pruebas

| Capa | Qué probar | Enfoque |
|---|---|---|
| Unit | NBSP/espacios, ausencias, columna NBSP vacía/no vacía, strings preservados | RED-GREEN-REFACTOR en `tests/test_cleaning.py`. |
| Unit | CSV vacío, header-only, encabezados duplicados, filas ragged | Espejar expectativas de `tests/test_diagnostics.py::test_rechaza_csv_intermedio_malformado_sin_generar_diagnostico`, permitiendo header-only. |
| Escritura | Atomicidad de las tres salidas, restauración y no salida parcial | Inyectar fallas con `monkeypatch` en writer/`Path.replace`; verificar contenido previo restaurado y sin `.tmp`, salvo backups preservados si falla restauración. |
| Regresión | Determinismo/idempotencia byte-for-byte | Ejecutar dos veces sobre el mismo fixture; comparar bytes de CSV, bitácora y reporte; asegurar que no hay filas duplicadas/stale. |
| CLI | Defaults, guards de `data/interim`, `data/processed`, `outputs/tablas`, exit codes | Cargar módulo con `importlib.util`, igual que CLIs actuales; error sin traceback. |
| Regresión | No mutar raw/interim/source outputs | Comparar contenido previo en tmp_path y verificar solo salidas permitidas. |

Comando obligatorio portable: `uv run pytest`. La ruta local absoluta `/home/jonialen/.local/bin/uv run pytest` queda aceptada solo como invocación específica de entorno si `uv` no está en `PATH`.

## Migración / despliegue

No requiere migración. Rollout: implementar primero tests fallidos, luego módulo/CLI y regenerar artefactos generados solo cuando apply lo indique. Rollback: borrar `src/proyecto1_ds/cleaning.py`, `scripts/limpiar_dataset.py`, tests nuevos y salidas generadas permitidas; `data/raw/`, `data/interim/`, `docs/diagnostico.md`, `docs/plan_limpieza.md` y tablas diagnósticas previas permanecen intactas.

## Preguntas abiertas

- [ ] Ninguna bloqueante para el primer slice determinístico.
