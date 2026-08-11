-- Habilita la extension pgvector en la base del proyecto.
--
-- Alcance deliberadamente minimo: SOLO la extension. La migracion canonica
-- "enable_pgvector" de db/AGENTS.md incluye ademas la columna embedding de
-- catalog_field y su indice HNSW, y esa tabla no existe hasta que corra
-- create_catalog. Por eso este slug lleva el sufijo _extension: deja libre el
-- nombre canonico para quien complete el trabajo, y ninguna migracion ya
-- aplicada tendra que editarse.
--
-- La imagen pgvector/pgvector:pg15 del compose trae la extension disponible;
-- disponible no es lo mismo que habilitada, y habilitarla a mano en la base
-- esta prohibido: solo por migracion.

-- migrate:up
CREATE EXTENSION IF NOT EXISTS vector;

-- migrate:down
DROP EXTENSION IF EXISTS vector;
