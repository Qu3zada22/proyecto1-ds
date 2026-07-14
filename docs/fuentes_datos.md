# Fuentes de datos crudos

## MINEDUC - Busca Establecimiento

- Fuente indicada en las instrucciones: `http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO GE/`
- Fuente pública alcanzable: `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/`
- Fecha de extracción registrada: 2026-07-14
- Alcance consultado: `NIVEL ESCOLAR: DIVERSIFICADO`
- Código usado por el formulario para diversificado: `46`

## Investigación de descarga CSV

Se intentó localizar una descarga CSV, endpoint de exportación o API pública desde la página oficial. No se encontró un endpoint CSV directo reutilizable por HTTP simple. Sin embargo, los HTML capturados sí contienen un control WebForms `_ctl0:ContentPlaceHolder1:btnExportar` con texto `Exportar a Excel`; ese botón existe en la respuesta oficial y queda como investigación manual pendiente antes de asumir que no hay exportación tabular directa. Intentos relevantes:

| Intento | Resultado observado |
|---|---|
| `http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO GE/` | Redirige a HTTPS y responde `404`; la URL de instrucciones parece tener un espacio/typo. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/` | Responde `200` y muestra el formulario oficial de búsqueda. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/wbfBuscar.aspx` | Responde `200`, pero es otra vista HTML del formulario; no CSV. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/Busqueda.aspx` y `?rn=1` | Responden `404`. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/establecimientos.csv` | Responde `404`. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/Exportar.aspx` | Responde `404`. |
| `https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/Export.aspx` | Responde `404`. |
| Control `btnExportar` / `Exportar a Excel` en HTML capturado | Existe dentro de los resultados WebForms; todavía no se confirmó el POST/evento necesario para descargar Excel/CSV reproduciblemente. |

## Recaptura reproducible del HTML fuente

El CLI público permite recapturar el HTML oficial de `NIVEL ESCOLAR: DIVERSIFICADO` por departamento, preservándolo como artefacto crudo y actualizando `data/raw/manifest.json` sin generar CSV falso:

```bash
uv run python scripts/adquirir_datos.py \
  --capture-html \
  --department-code 01 \
  --department-name GUATEMALA \
  --fecha-extraccion 2026-07-14
```

Para reemplazar un HTML ya existente se debe pasar `--confirm-overwrite`; sin esa confirmación el CLI rechaza la sobrescritura para proteger los crudos.

## Campos WebForms preservados

Los HTML crudos contienen campos de estado de ASP.NET WebForms como `__VIEWSTATE` y `__EVENTVALIDATION`. Esos valores no son credenciales del proyecto ni secretos privados: son estado público devuelto por la página oficial y quedaron capturados dentro del artefacto HTML completo para reproducibilidad, trazabilidad y evidencia de procedencia.

El pipeline de consolidación no usa esos campos para construir registros; solo extrae la tabla oficial de resultados. Aun así, en futuras exploraciones del botón `Exportar a Excel` se debe preferir un flujo oficial más limpio que no requiera versionar estado WebForms innecesario si existe una exportación tabular reproducible.

## Artefactos preservados

Como no hubo CSV directo disponible, se preservó el contenido fuente legítimo en HTML, sin etiquetarlo como CSV. Los archivos están en `data/raw/`:

- `data/raw/mineduc_busca_establecimiento_diversificado_00.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_01.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_02.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_03.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_04.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_05.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_06.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_07.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_08.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_09.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_10.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_11.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_12.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_13.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_14.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_15.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_16.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_17.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_18.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_19.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_20.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_21.html`
- `data/raw/mineduc_busca_establecimiento_diversificado_22.html`

`data/raw/manifest.json` registra fuente URL, fecha de extracción, cobertura, versión, método (`html-form`), checksum SHA-256 y el bloqueo: `sin CSV directo visible en la página oficial`. La frase significa que no se encontró endpoint CSV directo; no niega la presencia del botón `Exportar a Excel` observado en el HTML.

## Siguiente paso manual

Si el curso exige estrictamente CSV descargado desde el sitio, el siguiente paso es validar manualmente en navegador el flujo del botón `Exportar a Excel` y capturar qué campos WebForms (`__VIEWSTATE`, `__EVENTVALIDATION`, evento y coordenadas del botón) requiere. El pipeline actual ya puede consolidar los HTML oficiales preservados hacia CSV intermedio mediante código reproducible, dejando claro que el origen crudo fue HTML y no un CSV descargado.
