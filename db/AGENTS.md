# db/ — Migraciones dbmate, pgvector y Seeds

Guía de carpeta: sobreescribe la raíz dentro de `db/`. Normas transversales en [`../AGENTS.md`](../AGENTS.md).

## Estructura

```
db/
├── migrations/    # <timestamp>_<slug>.sql con -- migrate:up / -- migrate:down
├── seeds/         # seeds auxiliares invocados por make data (si no van en migración)
└── schema.sql     # dump versionado — se regenera con cada make db-up, va en git
```

## Reglas — NON-NEGOTIABLE

- dbmate es la ÚNICA vía de cambio de esquema. Jamás `SQLModel.metadata.create_all()` en prod; los modelos SQLModel (`backend/app/models/`) solo reflejan lo que dbmate creó.
- Toda migración es reversible: secciones `-- migrate:up` y `-- migrate:down` obligatorias.
- Jamás editar una migración ya aplicada: los errores se corrigen con una migración nueva.
- `schema.sql` actualizado y commiteado en el mismo PR que la migración (QA gate raíz).
- pgvector se habilita vía migración (`CREATE EXTENSION IF NOT EXISTS vector;`), nunca a mano en la BD.
- Timestamps `TIMESTAMPTZ DEFAULT now()`; FKs con `ON DELETE` explícito; `UNIQUE` de negocio respalda los 409 del API.
- Contraseñas seed SIEMPRE pre-hasheadas con Argon2 (pwdlib); jamás texto plano en SQL.
- Usuarios: soft delete (`disabled = true`), nunca `DELETE` físico (auditoría).

## Migraciones canónicas

| Orden | Slug | Contenido |
|-------|------|-----------|
| 1 | `create_catalog` | `catalog_source`, `catalog_field`, `catalog_tribal_note` + índice tsvector |
| 2 | `create_app_user` | `app_user` + seed 7 usuarios (1 admin + 2 por perfil) |
| 3 | `create_export_job` | `export_job` con auditoría (usuario, filtros, tamaño, duración) |
| 4 | `enable_pgvector` | extensión `vector` + `embedding VECTOR(768)` en `catalog_field` + índice HNSW |

## Comandos

```bash
make db-new SLUG=create_catalog   # dbmate new — genera db/migrations/<ts>_create_catalog.sql
make db-up                        # dbmate up — aplica y regenera schema.sql
make db-rollback                  # dbmate rollback — revierte la última
dbmate status                     # estado de migraciones
```

## Flujo de trabajo

1. `make db-new SLUG=<slug>` → editar el SQL con up y down.
2. `make db-up` local → verificar `schema.sql` cambiado y modelos SQLModel alineados.
3. `make db-rollback && make db-up` → probar reversibilidad antes del PR.
4. CI aplica `dbmate up` en el deploy a `main`.

## Skills relevantes

| Acción | Skill |
|--------|-------|
| Escribir migraciones y seeds | `portal-db-migrations` |
| Modelos SQLModel espejo | `portal-db-models` |
| Embeddings/índices pgvector | `portal-catalog-rag` |
| Datos sintéticos y seed de catálogo | `portal-synthetic-data` |
