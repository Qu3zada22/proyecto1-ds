# Recibo de migración de la fuente canónica

## Alcance y recuperación

Este recibo fija el estado previo recuperable de la migración mecánica desde `data/interim/establecimientos_diversificado_raw_unificado.csv` hacia `data/source/establecimientos_diversificado_mineduc.csv`. La recuperación consiste en revertir conjuntamente el renombre y las referencias de PR1; no requiere modificar los 23 HTML, el manifest, `data/processed/` ni los outputs existentes.

## Fuente canónica

| Estado | Ruta | SHA-256 | Objeto Git |
|---|---|---|---|
| Antes de migrar | `data/interim/establecimientos_diversificado_raw_unificado.csv` | `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f` | `5a835ce777fa2d4a0455249999140b0ee6135e86` |
| Después de migrar | `data/source/establecimientos_diversificado_mineduc.csv` | `c83ac119326279b67acbbca5c9d1cada6877bb56526c76c1461fdc9b3bded82f` | `5a835ce777fa2d4a0455249999140b0ee6135e86` |

## Procedencia oficial preservada

Manifest: `data/raw/manifest.json`, SHA-256 `8b72e90ff85e0d646f15dcff88cf32f0cbb11bc8d605582cd7d2e46efa5f7e07`, objeto Git `6e7e100f4c2019edb3d51ed9407f6f67b30c5478`.

| HTML | SHA-256 |
|---|---|
| `mineduc_busca_establecimiento_diversificado_00.html` | `5b50e49c718671f04eae7ce9f44b67b042255524baa56a5a945ea85b57f4629a` |
| `mineduc_busca_establecimiento_diversificado_01.html` | `04503b4d5e4c0a79ed82520eb95c92889fa25f540fe1d896e25313bf2ff32d36` |
| `mineduc_busca_establecimiento_diversificado_02.html` | `0c7e5c62c597df7a2b013ac478f31673e90053dd119e19170987708b1765de4d` |
| `mineduc_busca_establecimiento_diversificado_03.html` | `e5d04ac4ee1ba0129b0a20cd2ce76a4cff689201f2b4d393dd211ec7f7ff46c1` |
| `mineduc_busca_establecimiento_diversificado_04.html` | `01d93375b662bd52c31e8e639ec25c6bbdc6e165d3f46aaf15dc87e03893e8c9` |
| `mineduc_busca_establecimiento_diversificado_05.html` | `e4a49a942eca551f5d97d4076184cc3481c91c1b37493da22666d10e1d75b056` |
| `mineduc_busca_establecimiento_diversificado_06.html` | `0b0d9224b50de5f1265764a688f7f6aff112a696b847cd62897ae40830c45e8e` |
| `mineduc_busca_establecimiento_diversificado_07.html` | `75f49cd161ab1adc4a05b3c236dd445a60af1a915dce8d750b69f620eb244ed5` |
| `mineduc_busca_establecimiento_diversificado_08.html` | `f3491966ead4326db6e2737355bf67f2ac2b76c06f5229bf03176a9cd55d85b3` |
| `mineduc_busca_establecimiento_diversificado_09.html` | `5c0324ae59decd95428a7f8a3407e912797b155f92b433c8d07a6e0d9ff0c4e0` |
| `mineduc_busca_establecimiento_diversificado_10.html` | `fda1a2a39e4b0b4ad20c42b68c9b13b300627c098d9fba7aaf5b4db1e6aee5d3` |
| `mineduc_busca_establecimiento_diversificado_11.html` | `9a8e62d173405419df5e3a1bee1e55d49c61f79efcb5315f9fddd5da532d2d85` |
| `mineduc_busca_establecimiento_diversificado_12.html` | `fe218d68d5165329ed3c918d015072ef8e74f790ba53721bd28bede6f861ec80` |
| `mineduc_busca_establecimiento_diversificado_13.html` | `b0d2d9b10412e43e6894608ede5c76e7af81045a32480529a2358c0d0152ff0a` |
| `mineduc_busca_establecimiento_diversificado_14.html` | `80e3d2c13c20e5a4a27ca6b21107d7cd0801f8c3cf4a9d7d3140fbca3f3f9785` |
| `mineduc_busca_establecimiento_diversificado_15.html` | `3a1d841a3712732c9483a084c766f81cd85e8bb189c0f1f9df8ec3f9aed96506` |
| `mineduc_busca_establecimiento_diversificado_16.html` | `084ee47c1e736c22ee46aef80a2f202cdb995f020e3d3990b1bd46ed28a07296` |
| `mineduc_busca_establecimiento_diversificado_17.html` | `f227a7bf924f51d5004ad0752d7fbe37bee816dcc55fda073cd7b94e0fe4fe0a` |
| `mineduc_busca_establecimiento_diversificado_18.html` | `2882cb696f1c71d6f5a6bda074254d34aae1b764172823bbfc383359222d89d0` |
| `mineduc_busca_establecimiento_diversificado_19.html` | `731a888ab621caaa422306a74cc69481da54049882737ea7ae2e7bfeb38d8336` |
| `mineduc_busca_establecimiento_diversificado_20.html` | `b7b40cfa7cd3a821bb0b2e29eaf23659fc930e4dfae1d18b9bb67f5cbc2e5513` |
| `mineduc_busca_establecimiento_diversificado_21.html` | `58309e0f765980d73e130af28144a2d6ae391a6f67224ecc063929728e79c63a` |
| `mineduc_busca_establecimiento_diversificado_22.html` | `32a102de3e8603175698d79b776d6c5b2ed1caf18b3c01172341d85add96a571` |

## Procesado y outputs protegidos

| Ruta | SHA-256 |
|---|---|
| `data/processed/establecimientos_diversificado_limpio.csv` | `5de3d05752f38f249180e08f46369e7d6225a5b8acc7c77535b40a4ffac78c03` |
| `outputs/tablas/bitacora_limpieza.csv` | `8a7faadf69fb15531d62d4bf1ae08e35c9382ce6c27c005d75960e078f06fe34` |
| `outputs/tablas/diagnostico_columnas.csv` | `e41123edcb09b3ae78cbf6f8555d317d0f55f222ce2132db70a5de1d1f06d69f` |
| `outputs/tablas/dominios_observados.csv` | `c95d4905a15854653a64b720bcc956c2151d2dda3569ee33de0de60fa1896f19` |
| `outputs/tablas/duplicados_exactos.csv` | `81cc2a2a3e2c9afa93030cd73e31966889297b9cd65730683ef40915e0f89bd3` |
| `outputs/tablas/problemas_potenciales.csv` | `9ccfa68b289547254ac47edb4fb646bbb1fa9f1e4c4b971959d30dd08df40170` |
| `outputs/tablas/reporte_calidad_antes_despues.csv` | `3e10db84354614849d23d43f34466aa0a990b69aa1a90ba528d4060bbf75c962` |
| `outputs/tablas/resumen_dataset.csv` | `2033301b36a70926a0a7dd45313e6298cbdfb5e59227964199131dbf1ad7bb2a` |

Los hashes anteriores se capturaron antes de ejecutar el harness de PR1 y permiten demostrar que el flujo no altera artefactos protegidos distintos de los documentos cuya ruta canónica debe actualizarse.
