# ml/ — Datos sintéticos, catálogo semántico y agente ADK

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `ml/`.

## Estado

La capa de datos existe y produce artefactos reales. La de agente todavía no.

**Existe hoy**, verificado en el árbol:

- `data/schemas.py` — contrato: 180 000 filas en `creditos`, 1 000 000 en `liquidez`, 80 000 en `derivados`; la serie preagregada, 500 000 puntos.
- `data/generators.py` escribe `data/silos/*.parquet` y su `manifest.json`; `data/anomalies.py` inyecta ~1 por mil; `data/aggregates.py` produce `serie_tablero.parquet` y su sidecar; `data/manifest.py` emite `data/README.md`.
- `data/catalog_content.py` y `data/seed_catalog.py` — doce fuentes (tres con extracto), de 200 a 400 campos y treinta notas tribales; emiten `db/seeds/catalog.sql`.
- `utils/seeding.py` (semilla y subflujos) y `utils/parquet.py`.

**No existe, no lo cites como existente**: `ml/agent/` (E3 sin arrancar: ni tools, ni runner, ni gate "hello tool"), `ml/semantic/` (el compilador SMQ no está escrito), `data/extractors.py`, `data/errors.py` y `data/embed_catalog.py`. La guía anterior los nombraba como existentes. La lectura del catálogo vive en `backend/app/services/catalog_service.py`, hoy solo keyword sobre `tsvector`: la fase híbrida con pgvector sigue pendiente.

## Estructura

```
ml/
├── data/     schemas.py · generators.py · anomalies.py · aggregates.py
│             manifest.py · catalog_content.py · seed_catalog.py
└── utils/    seeding.py · parquet.py
```

## Comandos

```bash
make data          # python -m ml.data.generators --out data
make db-seed       # reemite db/seeds/catalog.sql y lo aplica
make test          # pytest -c backend/pyproject.toml tests/backend tests/ml
make lint          # ruff y mypy; mypy pasa una segunda vez sobre ml y tests/ml
make verificar     # barrido completo; verificar_datos.sh es el de esta capa

poetry -P backend run python -m ml.data.generators --only derivados --scale smoke
```

## Convenciones

- ❌ Cambiar la semilla. Vale `SEED = 20260720` en `ml/utils/seeding.py`; `seed_catalog.py` declara la suya. Al cambiarla no falla nada de inmediato: la corrida siguiente se ve bien y deja de reproducir. Lo atrapa `scripts/verificar_datos.sh`, que compara byte a byte una segunda corrida; `make verificar` lo ejecuta junto a `scripts/verificar_reproducibilidad.sh`, que cubre los candados de dependencias y no los datos.
- ❌ Dar una cifra sin tool call. El modelo sabe la respuesta y la dirá si nadie se lo prohíbe: toda cifra del agente sale de un tool call y cita su fuente del catálogo.
- ❌ Abrir un flujo aleatorio con `default_rng(SEED)`. ✅ `seeded_rng("<nombre>")` declarado en `STREAM_IDS`: un flujo sin declarar cambia los bytes de un silo que nadie tocó.
- ❌ "Limpiar" los esquemas. `cli_ref`, `id_cliente` y `ctpty_cd` son crípticos e incompatibles a propósito: los traduce el catálogo.
- ❌ Duplicar en `catalog_content.py` las columnas de una fuente con extracto. ✅ `schemas.py` es la única fuente del vocabulario físico; el catálogo solo añade sinónimos y notas.
- ✅ Polars lazy (`pl.scan_parquet`) para lo que cruce silos: los conjuntos de clientes están anidados a propósito.
- ✅ Anomalías recontadas con predicados propios sobre el archivo escrito; preguntarle al inyector mide una intención.

### Agente ADK

`ml/agent/` no existe. Cuando se cree, estas reglas no se negocian:

- Tools en `ml/agent/tools/`: funciones tipadas que envuelven endpoints gobernados y propagan el Bearer del usuario. El agente nunca ve datos que el usuario no puede ver.
- Máximo cinco tool calls; `tool_call` se emite antes del texto y la cancelación no deja tareas colgadas.

## No tocar

- `data/silos/*.parquet`, `manifest.json` y `data/aggregates/*`: los produce `make data` y `.gitignore` los excluye (`data/silos/`, `data/aggregates/`, `*.parquet`). Se regeneran, no se editan.
- `data/README.md`: generado por `manifest.py` pero versionado (`!data/README.md`). La siguiente corrida lo reescribe: corrige el emisor.
- `db/seeds/catalog.sql`: lo emite `python -m ml.data.seed_catalog` y un test comprueba que esté al día. Se edita `catalog_content.py`, no el SQL.
- `tests/ml/data/consultas_referencia.json`: veinte consultas congeladas. Si una falla, el único arreglo permitido es añadir un sinónimo que una persona diría de verdad; ajustar la consulta está prohibido. También `tests/ml/fixtures/creditos_smoke.json`, la muestra dorada.

## Tests

Viven en `tests/ml/`, fuera del paquete a propósito, y corren con la configuración del backend (`-c backend/pyproject.toml`), que fija cobertura combinada de `backend/app` y `ml` con piso 70 %. Cubren determinismo y muestra dorada, bytes idénticos con `--only`, clientes anidados, anomalías contra lo publicado, idempotencia del README y el contrato del catálogo: rango de entradas, treinta notas con su condición y SQL determinista.

El Hit Rate@3 >= 0.8 no se mide aquí: vive en `tests/backend/test_catalog_integracion.py::test_hit_rate_at_3`, marcado `integracion`, y exige `KARISMA_TEST_DATABASE_URL` y `make db-seed`. El set congelado que consume sí es de `tests/ml/`.

## Skills

| Acción | Skill |
|--------|-------|
| Generadores, anomalías, manifiesto | `portal-synthetic-data` |
| Contenido del catálogo y seed | `portal-catalog-rag` |
| Compilador SMQ y joins entre silos | `portal-semantic-layer` |
| Extractores async y caché TTL | `portal-data-connectors` |
| Agente, tools y runner | `portal-adk-agent` |
| Bearer propagado en las tools | `portal-auth-jwt` |
