<!-- Generado por `make data`. No editar a mano: la siguiente corrida lo reescribe. -->

# Datos sinteticos de Karisma Data

**Advertencia: todo lo que hay en `data/` es sintetico.** Ninguna cifra proviene de una institucion real, ninguna persona ni empresa nombrada existe, y el tipo de cambio es un valor fijo inventado. Los datos imitan la forma y los defectos de tres sistemas internos que no se hablan entre si, que es el problema que el portal resuelve.

Semilla fija: **20260720**. Con ella, dos corridas de `make data` producen los mismos bytes.

## Volumenes y huellas

| Silo | Sistema origen | Filas | Columnas | Bytes | SHA-256 |
|---|---|---:|---:|---:|---|
| `creditos` | SIC-Core | 180 000 | 12 | 4 108 884 | `5a930c8e5269f29b...` |
| `liquidez` | TESO-Pos | 1 000 000 | 11 | 13 774 429 | `ae285c5fefd4efc8...` |
| `derivados` | DRV-Front | 80 000 | 11 | 1 395 794 | `da25455224eb6f16...` |
| `serie_tablero` | Karisma Data | 500 000 | 8 | 5 915 049 | `470652c7e6ef9232...` |

Los tres silos suman **1 260 000 filas**. El catalogo de julio describia unos 6 500 000: el alcance de este sprint es un **recorte del 81 %**, declarado como tal.

El volumen de `liquidez` no es una preferencia sino un piso aritmetico: la serie preagregada publica 500 000 puntos y cada uno necesita al menos una fila cruda detras.

## Diccionario de datos

### `creditos` — SIC-Core (Direccion de Credito)

| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |
|---|---|---|---|---|
| `cli_ref` | Referencia de cliente | Client reference | String | - |
| `nom_cli` | Nombre del cliente | Client name | String | - |
| `prod_cd` | Codigo de producto | Product code | String | - |
| `sdo_cap` | Saldo de capital | Outstanding principal | Float64 | MXN |
| `sdo_int` | Intereses devengados | Accrued interest | Float64 | MXN |
| `dias_mora` | Dias de mora | Days past due | Int16 | dias |
| `tasa_pct` | Tasa anual | Annual rate | Float64 | % |
| `f_apert` | Fecha de apertura | Origination date | Date | - |
| `f_venc` | Fecha de vencimiento | Maturity date | Date | - |
| `suc_cd` | Sucursal | Branch | String | - |
| `est_cta` | Estatus de la cuenta | Account status | String | - |
| `mon_cd` | Codigo de moneda | Currency code | String | - |

### `liquidez` — TESO-Pos (Tesoreria)

| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |
|---|---|---|---|---|
| `fec_pos` | Fecha de posicion | Position date | Date | - |
| `fec_val` | Fecha valor | Value date | Date | - |
| `id_cliente` | Identificador de cliente | Client identifier | Int64 | - |
| `cliente_desc` | Descripcion del cliente | Client description | String | - |
| `bucket_venc` | Bucket de vencimiento | Maturity bucket | String | - |
| `divisa` | Divisa | Currency | String | - |
| `unidad_negocio` | Unidad de negocio | Business unit | String | - |
| `mto_disp` | Monto disponible | Available amount | Int64 | miles de la divisa |
| `mto_comp` | Monto comprometido | Committed amount | Int64 | miles de la divisa |
| `ratio_lcr` | Razon de cobertura | Coverage ratio | Float64 | - |
| `tipo_pos` | Tipo de posicion | Position type | String | - |

### `derivados` — DRV-Front (Mesa de Derivados)

| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |
|---|---|---|---|---|
| `op_id` | Folio de operacion | Trade identifier | String | - |
| `ctpty_cd` | Codigo de contraparte | Counterparty code | String | - |
| `ctpty_name` | Contraparte | Counterparty | String | - |
| `subyacente` | Subyacente | Underlying | String | - |
| `tipo_instr` | Instrumento | Instrument | String | - |
| `nocional_usd` | Nocional | Notional | Float64 | USD |
| `mtm_val` | Valor a mercado | Mark to market | Float64 | USD |
| `f_trade` | Fecha de concertacion | Trade date | String | - |
| `f_settle` | Fecha de liquidacion | Settlement date | String | - |
| `book_cd` | Libro | Book | String | - |
| `cpty_rtg` | Calificacion | Rating | String | - |

## Heterogeneidad deliberada

Los tres sistemas nunca se pusieron de acuerdo, y esa es justamente la materia del portal. La misma entidad aparece con seis diferencias a la vez:

| Eje | `creditos` | `liquidez` | `derivados` |
|---|---|---|---|
| Columna del cliente | `cli_ref` | `id_cliente` | `ctpty_cd` |
| Codificacion | `CLI-100042` | `100042` | `C100042C` |
| Fecha | tipo fecha | tipo fecha, `fec_val` es T+1 | texto `AAAAMMDD` |
| Moneda | codigo interno `01` | ISO-4217 en `divisa` | implicita USD |
| Unidad del importe | pesos | **miles** de la divisa | dolares |
| Razon social | truncada a 30 | completa | mayusculas sin acentos |

**Regla de normalizacion**, ejecutable en `ml/data/schemas.py::normalize_client_key`: se quita el prefijo `CLI-` en creditos, se toma el entero tal cual en liquidez y se leen los seis digitos entre la `C` y la letra verificadora en derivados. Las tres codificaciones se reducen al mismo entero, y por eso los cruces devuelven filas.

Los conjuntos de clientes estan anidados: los de `derivados` son un subconjunto de los de `liquidez`, y estos de los de `creditos`.

## Anomalias inyectadas

Los conteos de esta tabla no son los que el inyector pretendia escribir: son los que una auditoria independiente encontro en el archivo ya escrito, con los predicados de la ultima columna.

| Silo | Tipo | Conteo | Predicado detector |
|---|---|---:|---|
| `creditos` | Monto negativo | 60 | `sdo_cap < 0` |
| `creditos` | Fecha imposible | 60 | `f_venc < f_apert` |
| `creditos` | Duplicado exacto | 40 | `filas menos filas unicas en todas las columnas` |
| `creditos` | Nulo obligatorio | 20 | `prod_cd nulo` |
| `creditos` | Cliente huerfano | 0 | `clave normalizada fuera de [100000, 160000)` |
| `liquidez` | Monto negativo | 300 | `mto_disp < 0 y tipo_pos = ACT` |
| `liquidez` | Fecha imposible | 200 | `fec_val < fec_pos` |
| `liquidez` | Duplicado exacto | 200 | `filas menos filas unicas en todas las columnas` |
| `liquidez` | Cliente huerfano | 0 | `clave normalizada fuera de [100000, 160000)` |
| `liquidez` | Outlier de magnitud | 300 | `ratio_lcr > 10` |
| `derivados` | Fecha imposible | 20 | `f_trade no parsea con el formato AAAAMMDD` |
| `derivados` | Duplicado exacto | 20 | `filas menos filas unicas en todas las columnas` |
| `derivados` | Cliente huerfano | 20 | `clave normalizada fuera de [100000, 160000)` |
| `derivados` | Outlier de magnitud | 20 | `nocional_usd > 1e10` |

Total: **1 260 anomalias** sobre 1 260 000 filas, es decir **0.100 %** (objetivo de diseno: 0.100 %).

Ninguna anomalia cae sobre la espina de `liquidez`, las primeras 500 000 filas: si una cayera ahi, esa celda de la rejilla se filtraria al agregar y la serie publicada tendria un punto menos.

## Serie preagregada del tablero

`data/aggregates/serie_tablero.parquet` y su sidecar `serie_tablero_meta.json`.

- **Grano**: una fila por (fecha, serie_id). 500 000 filas = 2 000 dias habiles x 250 claves.
- **Ventana**: del 2018-10-31 al 2026-06-30, lunes a viernes.
- **Orden en disco**: `(serie_id, fecha)`. Es parte del contrato: una serie es un tramo contiguo y el tablero la lee sin recorrer el archivo.
- **Rejilla**: 5 unidades de negocio x 5 divisas x 10 buckets de vencimiento, con `serie_id = unidad * 50 + divisa * 10 + bucket`.
- **Derivada, no fabricada**: sale de agrupar `liquidez.parquet`, asi que cada punto tiene filas crudas detras y `n_posiciones` nunca es cero.

| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |
|---|---|---|---|---|
| `serie_id` | Identificador de serie | Series identifier | UInt16 | - |
| `fecha` | Fecha | Date | Date | - |
| `unidad_negocio` | Unidad de negocio | Business unit | String | - |
| `divisa` | Divisa | Currency | String | - |
| `bucket_venc` | Bucket de vencimiento | Maturity bucket | String | - |
| `saldo_disponible_mxn` | Saldo disponible | Available balance | Float64 | MXN |
| `ratio_lcr` | Razon de cobertura | Coverage ratio | Float64 | - |
| `n_posiciones` | Posiciones | Positions | UInt32 | filas |

`saldo_disponible_mxn` ya resuelve las dos trampas del origen: multiplica por mil los miles de `mto_disp` y convierte la divisa a pesos con el tipo de cambio sintetico fijo.

## Limitaciones declaradas

1. **Sin calendario de dias festivos.** Los dias habiles son de lunes a viernes. Un calendario mexicano real cambiaria el conteo y no cambiaria nada de lo que las pantallas demuestran.
2. **Tipo de cambio sintetico fijo** (pesos por unidad): MXN 1.0, USD 17.85, EUR 19.4, GBP 22.6, JPY 0.118. No es una cotizacion de mercado ni pretende parecerlo.
3. **Volumenes recortados** respecto del catalogo de julio, con el porcentaje declarado arriba.
4. **`make data` no siembra la base de datos.** Solo escribe archivos, para que corra en una maquina sin Docker.
5. **Ningun campo tiene forma de RFC ni de identificador fiscal.** Ninguna pantalla lo necesita.

## Como regenerar y como verificar

```bash
make data                     # regenera los cuatro parquet y este archivo
bash scripts/verificar_datos.sh   # reproducibilidad, volumenes y anomalias
```

Los parquet, el manifiesto y el sidecar **no se versionan**: se regeneran con la semilla fija y dos corridas seguidas producen los mismos bytes. Quien clone el repositorio tiene que correr `make data` antes de que el explorador y el tablero muestren algo.

Este archivo es el unico de `data/` que si se versiona, y es **generado**: lo escribe `ml/data/manifest.py`. Editarlo a mano deja `git diff --exit-code data/README.md` en rojo en la siguiente corrida.
