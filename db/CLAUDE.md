# db/ — Esquema PostgreSQL, migraciones dbmate y seeds

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `db/`.

PostgreSQL 15 + pgvector. SQL puro con dbmate; los modelos de `backend/app/models/` reflejan la migración, nunca al revés.

## Estado

Seis migraciones aplicadas; sus versiones quedan al final de `schema.sql`:

| Archivo | Qué dejó en la base |
|---------|---------------------|
| `20260811005732_enable_pgvector_extension.sql` | `CREATE EXTENSION vector`, y nada más |
| `20260811211250_create_app_user.sql` | `app_user` + siete usuarios con hash argon2id (1 admin, 2 por perfil) |
| `20260812065546_create_catalog.sql` | `catalog_source`, `catalog_field`, `catalog_tribal_note`, índice GIN sobre `search_document` e índice HNSW sobre `embedding VECTOR(768)` |
| `20260812121501_create_catalog_lineage.sql` | `catalog_lineage_step`, tramo aguas arriba por fuente |
| `20260813204211_create_export_job.sql` | `export_job` con `CHECK` de estados y de formatos, dos `CONSTRAINT` de coherencia y tres índices: uno compuesto `(requested_by, created_at DESC)` y dos parciales |
| `20260813205114_add_app_user_updated_at.sql` | `app_user.updated_at` |

Seis tablas reales, más `schema_migrations`. **`export_job` existe desde el 13-ago-2026** (US-009): nunca se borra una fila, un trabajo caducado sigue siendo historial y su enlace deja de funcionar por la firma, no por un `DELETE`. **No existe la migración `enable_pgvector`**: su contenido quedó repartido entre la extensión y `create_catalog`, porque `catalog_field` no existía al habilitarla. `catalog_field.embedding` está creada pero vacía — la búsqueda híbrida está diferida y hoy solo corre la de palabra clave.

**Los estados de `export_job` van con `CHECK` y no con un `ENUM` de PostgreSQL** a propósito: añadir
un valor a un `ENUM` es una migración con bloqueo, y ese vocabulario todavía se mueve. Sus tres
índices se justifican uno a uno, porque un índice de más es coste de escritura permanente:
`(requested_by, created_at DESC)` resuelve filtro **y** orden del historial sin `SORT`;
`(status) WHERE status IN ('pendiente','en_proceso')` es parcial porque un índice total sobre una
columna de cuatro valores sería inútil por baja cardinalidad; `(expires_at) WHERE status = 'completado'`
soporta la purga futura. **No hay índice sobre `dataset` ni GIN sobre `filters`**: ninguna consulta
los usa.

## Estructura

```
db/
├── migrations/                 # <timestamp>_<slug>.sql, una sección up y una down
├── seeds/
│   ├── catalog.sql             # GENERADO por ml/data/seed_catalog.py: 12 fuentes, 304 campos, 30 notas
│   └── catalog_lineage.sql     # CURADO a mano, sin emisor: 12 fuentes x 4 pasos = 48 filas
└── schema.sql                  # volcado versionado, lo regenera make db-up
```

## Comandos

Todos desde la raíz. dbmate corre como servicio de Compose (perfil `herramientas`), no como binario del host; la cadena sale de `backend/.env.local`.

```bash
make db-new SLUG=create_export_job   # crea db/migrations/<timestamp>_create_export_job.sql
make db-up                           # aplica lo pendiente y regenera schema.sql
make db-rollback                     # revierte la última aplicada
make db-seed                         # reemite catalog.sql y aplica db/seeds/*.sql en orden
bash scripts/dbmate.sh status        # no hay target Make; el script pasa cualquier subcomando
```

## Convenciones

- ❌ `SQLModel.metadata.create_all()`. Funciona en local y por eso se cuela; deja tu base distinta de `schema.sql` y de la de todos. El esquema solo cambia por dbmate.
- ❌ Editar una migración ya aplicada: el error se corrige con una migración nueva.
- ❌ Tocar la base a mano con `psql` para crear extensiones, columnas o índices.
- ❌ Contraseñas en claro en SQL: los hashes argon2id se generan fuera y se pegan una vez.
- ❌ `DELETE` de usuarios: baja lógica con `disabled = true`.
- ✅ `-- migrate:up` antes de `-- migrate:down`, ambas con sentencias reales.
- ✅ Encabezado en prosa que explique por qué la migración es así, no qué hace el SQL.
- ✅ `TIMESTAMPTZ NOT NULL DEFAULT now()`, FK con `ON DELETE` explícito, enum-like como `TEXT CHECK (...)` y no ENUM nativo, `UNIQUE` de negocio que respalde los 409 del API.
- ✅ Estructura en la migración, contenido en `db/seeds/`: una definición de negocio se corrige varias veces.
- ✅ Seed idempotente: transacción, `TRUNCATE ... RESTART IDENTITY`, reinserción; resembrar deja las mismas claves.
- ✅ ASCII sin diacríticos en todo lo que acabe volcado en `schema.sql`.

## No tocar

- `db/schema.sql` — artefacto generado por `make db-up`. Editarlo a mano miente sobre el estado real.
- `db/seeds/catalog.sql` — lo emite `ml/data/seed_catalog.py` con semilla fija: se corrige el emisor, no el SQL.
- Las cuatro migraciones listadas en Estado: aplicadas, congeladas. Cambios por rollforward.
- Resembrar borra los `embedding`: tras `make db-seed`, reejecutar el job de embeddings.

## Tests

`tests/backend/test_migraciones.py` valida el contrato del directorio leyendo archivos de git, sin abrir conexión: nombre, ambas secciones, versiones únicas y presencia en `schema.sql`. `test_migracion_app_user.py` fija los siete usuarios, el formato argon2id y que ningún hash llegue al volcado. `tests/ml/test_seed_catalog.py` comprueba emisión determinista, artefacto al día e invariantes del contenido. Las marcadas `integracion` piden `KARISMA_TEST_DATABASE_URL`; sin ella se omiten.

## Skills

| Acción | Skill |
|--------|-------|
| Migración, índice o extensión | `portal-db-migrations` |
| Modelo SQLModel espejo del esquema | `portal-db-models` |
| Seed del catálogo y notas tribales | `portal-synthetic-data` |
| Embeddings e índice pgvector | `portal-catalog-rag` |
