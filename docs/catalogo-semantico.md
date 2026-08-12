# Catálogo semántico de Karisma Data

Qué hay en las tres tablas del catálogo, de dónde sale cada dato y cómo se
regenera. Documento escrito a mano y a propósito: es prosa explicativa, no un
recuento de cifras, así que no tiene el problema de desincronización que obligó
a `data/README.md` a ser generado.

> `data/README.md` es de US-006 y lo **escribe `make data`**. Esta US no lo
> toca: una sección añadida a mano la borraría la siguiente corrida.

## 1. Qué es y qué pregunta responde

El catálogo traduce los nombres crípticos de los sistemas de origen al lenguaje
del negocio. Contesta cuatro preguntas que hoy sólo se responden preguntándole a
una persona:

- **¿Qué significa `sdo_cap`?** Saldo de capital, en pesos, sin intereses.
- **¿De quién es este dato?** Un área propietaria y una persona responsable.
- **¿Está vigente esta definición?** Un intervalo `valid_from` – `valid_to`, con
  `valid_to` nulo cuando el campo sigue vivo.
- **¿Qué hay que saber antes de usarlo?** Las notas tribales, con su condición
  de aplicabilidad.

Tres tablas, creadas por `db/migrations/20260812065546_create_catalog.sql`:

| Tabla | Qué guarda |
|---|---|
| `catalog_source` | Las doce fuentes documentadas, con su sistema de registro y su propietario |
| `catalog_field` | Una fila por campo: nombre físico, nombre de negocio, definición, alias, facetas, vigencia y responsable |
| `catalog_tribal_note` | El conocimiento que ningún esquema publica, con su condición de aplicabilidad |

La búsqueda por palabra clave se apoya en `catalog_field.search_document`, una
columna `TSVECTOR` **generada** con configuración `spanish` y tres pesos:
`A` para el nombre de negocio, `B` para el nombre físico y los alias, `C` para
la definición. La columna `embedding VECTOR(768)` y su índice HNSW existen desde
la misma migración pero **están vacíos**: la búsqueda híbrida es de S5.

## 2. Volumetría: 12 fuentes, 304 campos, 30 notas

| Grupo | Fuentes | Campos | `has_extract` |
|---|---|---|---|
| Silos con extracto Parquet | `creditos` (12) · `liquidez` (11) · `derivados` (11) | **34** | `true` |
| Fuentes documentadas sin extracto | `clientes` · `garantias` · `pagos` · `provisiones` · `contabilidad` · `tesoreria` · `riesgo_mercado` · `canales` · `regulatorio` | **270** (30 cada una) | `false` |
| | **12** | **304** | |

Los 34 campos con extracto son, columna por columna, los que `make data`
escribe en `data/silos/`. Los 270 restantes documentan fuentes que la
institución tiene y que **este prototipo no extrae**: `has_extract = false` está
para poder decirlo en pantalla en vez de simular que hay datos detrás.

Las 30 notas tribales se reparten **18 en los tres silos con extracto** (seis por
silo, que es el recorrido que la demo hace y donde una cifra equivocada se puede
contrastar contra el Parquet) y **12 en las otras nueve fuentes**.

## 3. De dónde sale el vocabulario

```
ml/data/schemas.py          (US-006, sólo lectura)  ->  34 campos con extracto
ml/data/catalog_content.py  (US-008)                -> 270 campos + 30 notas
                                   |
                                   v
                      ml/data/seed_catalog.py  (emisor determinista)
                                   |
                                   v
                          db/seeds/catalog.sql  (artefacto versionado)
                                   |
                                   v
              PostgreSQL: catalog_source / catalog_field / catalog_tribal_note
```

**La cadena va en un solo sentido y nada fluye hacia atrás.** Una definición no
se corrige en la base de datos: se corrige en su fuente, se reemite el SQL y se
vuelve a sembrar.

- Si el campo pertenece a `creditos`, `liquidez` o `derivados`, su nombre de
  negocio y su definición salen de `FieldSpec.label_es` y `description_es` de
  **`ml/data/schemas.py`, que es de US-006**. Corregir esa redacción es un
  cambio en US-006, no aquí; `catalog_content.py` no vuelve a teclear ni una de
  esas columnas y una prueba lo impide.
- Si pertenece a cualquiera de las otras nueve fuentes, está curado a mano en
  `ml/data/catalog_content.py` y se revisa leyendo el diff.

Lo que `catalog_content.py` **sí** añade para los tres silos con extracto es lo
que un esquema físico no puede llevar: los sinónimos de búsqueda
(`SEARCH_SYNONYMS`) y las notas tribales. Las claves de ambas tablas se validan
contra `schemas.py` al emitir, así que una columna mal escrita revienta la
emisión en vez de indexar el vacío.

### Los alias hacen tres trabajos

1. **Traen el término en inglés.** La interfaz es bilingüe y las definiciones
   **no se traducen**: son vocabulario de la institución, igual que `sdo_cap`.
   Quien navega en inglés busca en inglés y encuentra la entrada; lo que lee es
   la definición institucional. Para los 34 campos con extracto ese término sale
   de `label_en`, nunca se teclea.
2. **Traen las etiquetas de los valores.** Nadie busca `HIP`: busca
   «hipotecario». Esas etiquetas viven en `schemas.DOMAIN_LABELS`, en los dos
   idiomas, y se importan.
3. **Traen la grafía acentuada.** Ver el apartado 5.

## 4. Qué está sorteado y qué está curado

La semilla es **20260720**, la misma de US-006 por mandato de `ml/AGENTS.md`.
Pero no todo se sortea: sortear una definición produce texto sin sentido.

| Atributo | Origen |
|---|---|
| `physical_name`, `business_name`, `definition`, `aliases`, `unit`, `metric_agg` de los tres silos | Importado de `ml/data/schemas.py` |
| `data_type` de los tres silos | Derivado del `dtype` de Polars con una tabla fija de siete entradas; `categoria` cuando la columna tiene lista cerrada de valores |
| `domain` de los tres silos | Derivado: el dominio de la fuente, salvo las claves de cliente, que son `cliente` |
| Todo lo anterior en las nueve fuentes sin extracto | Curado, literal en `catalog_content.py` |
| `sensitivity` de nombres de personas y empresas | Curado: la sensibilidad de un dato personal no es una tirada de dados |
| `sensitivity` del resto, `refresh_frequency`, `certification`, `valid_from`, `valid_to`, `steward` | Sorteado con `random.Random(20260720)` sobre listas controladas |

**Regla de determinismo**: una sola instancia `Random(SEED)`, consumida
recorriendo las entradas en un orden fijo —primero las 34 importadas, en el
orden `creditos`, `liquidez`, `derivados`, y dentro de cada silo el orden de sus
columnas; después las 270 curadas en su orden de declaración—. Los cinco sorteos
de cada entrada ocurren **siempre**, incluso cuando el valor se descarta por
haber uno curado: una rama que se saltara un sorteo movería todos los atributos
de todas las entradas siguientes.

**Invariante de coherencia**: `certification = 'obsoleto'` si y sólo si
`valid_to` no es nulo. Está declarado como `CHECK` en la tabla, así que la base
rechaza un seed incoherente en vez de servirlo, y hay una prueba que lo
comprueba antes de llegar ahí.

## 5. Los acentos: un hallazgo que cambió el contenido

La planeación daba por bueno que la configuración `spanish` normaliza los
acentos y que por eso no hacía falta `unaccent`. **Sólo es verdad a medias**, y
se comprobó contra PostgreSQL 15.18 el 12-ago-2026:

| Palabra | Lexema sin acento | Lexema con acento | ¿Casan? |
|---|---|---|---|
| crédito | `credit` | `credit` | Sí |
| días | `dias` | `dias` | Sí |
| posición | `posicion` | `posicion` | Sí |
| **tesorería** | `tesoreri` | `tesor` | **No** |
| **garantía** | `garanti` | `garant` | **No** |
| **estimación** | `estimacion` | `estim` | **No** |
| **capitalización** | `capitalizacion` | `capitaliz` | **No** |

El corpus está escrito sin diacríticos, siguiendo a `ml/data/schemas.py`, así
que una persona que escribe español correcto no encontraría nada en las palabras
largas. La solución es la columna de alias haciendo su trabajo: `ACCENTED_FORMS`
lista las palabras cuyo lexema cambia y el emisor indexa también la grafía
acentuada. No se listan las que ya colapsan solas: serían ruido.

## 6. Cómo se reeembra

```bash
make db-up      # crea las tres tablas (sólo la primera vez)
make db-seed    # reemite db/seeds/catalog.sql y lo aplica
```

`make db-seed` hace dos cosas en orden: ejecuta
`python -m ml.data.seed_catalog`, que reescribe el artefacto, y después lo
aplica con el `psql` que trae la imagen del servicio `dbmate`. Al terminar
imprime los conteos **medidos** en la base, no los prometidos por el generador.

Comprobaciones que valen la pena:

```bash
git diff --exit-code db/seeds/catalog.sql   # el contenido no cambió sin querer
poetry -P backend run python -m ml.data.seed_catalog --check   # idem, sin escribir
make db-seed && make db-seed                # idempotente: los conteos no cambian
```

El seed abre transacción y hace
`TRUNCATE catalog_tribal_note, catalog_field, catalog_source RESTART IDENTITY CASCADE`
antes de insertar. Sembrar dos veces deja la base idéntica **hasta en las claves
primarias**, que es lo que permite que una prueba de integración fije
identificadores.

> **Aviso para S5**: como el seed trunca, **reseembrar borra los `embedding`**.
> Después de cada `make db-seed` hay que volver a ejecutar el job de embeddings
> (`ml/data/embed_catalog.py`) cuando exista.

## 7. Códigos de faceta y claves i18n

La API devuelve **códigos estables en `snake_case`, nunca etiquetas**: traducir
comparando cadenas de prosa es frágil y duplicar el catálogo en dos idiomas crea
dos verdades para una definición. Las etiquetas las pone el frontend.

| Faceta | Códigos | Clave i18n que crea US-UX-07 |
|---|---|---|
| `domain` | `cartera` `riesgo` `liquidez` `mercado` `cliente` `contable` `operacion` `regulatorio` | `catalogo.facetas.dominio.*` |
| `data_type` | `entero` `decimal` `texto` `fecha` `booleano` `categoria` | `catalogo.facetas.tipo.*` |
| `sensitivity` | `publica` `interna` `restringida` | `catalogo.facetas.sensibilidad.*` |
| `refresh_frequency` | `intradia` `diaria` `semanal` `mensual` | `catalogo.facetas.frecuencia.*` |
| `certification` | `certificado` `en_revision` `obsoleto` | `catalogo.facetas.certificacion.*` |
| `unit` | `MXN` `USD` `porcentaje` `dias` `conteo` o nulo | `catalogo.facetas.unidad.*` |
| `metric_agg` | `sum` `mean` `count` `max` `min` o nulo | `catalogo.facetas.agregacion.*` |

Son 30 códigos, 60 claves entre los dos idiomas. Los valores que **no** se
traducen son `business_name`, `definition`, `aliases` y el texto de las notas:
son datos del negocio, no cadenas de interfaz.

### Una unidad que no tiene código, y por qué

`liquidez.mto_disp` y `liquidez.mto_comp` están en **miles de la divisa de la
fila**. Eso no es una unidad sino una escala sobre una divisa que cambia fila a
fila, así que no le corresponde ninguno de los cinco códigos y su `unit` queda
nula. La definición de la columna lo dice y su nota tribal lo repite: es el
error que este conjunto de datos existe para dramatizar.
