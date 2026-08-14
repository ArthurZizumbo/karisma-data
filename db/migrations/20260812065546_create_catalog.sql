-- Crea las tres tablas del catalogo semantico y su indice de busqueda por
-- palabra clave.
--
-- Sobre pgvector: la extension la habilito 20260811005732_enable_pgvector_extension
-- (US-002). La canonica "enable_pgvector" de db/AGENTS.md incluia ademas la
-- columna embedding y el indice HNSW; esas dos piezas viven aqui, porque
-- catalog_field no existia cuando se aplico aquella. El nombre canonico
-- enable_pgvector queda sin uso: su contenido esta repartido entre esa
-- migracion y esta.
--
-- La columna search_document es GENERATED ALWAYS ... STORED. Se verifico contra
-- PostgreSQL 15.18 que la expresion es inmutable con setweight y to_tsvector de
-- configuracion fija; con array_to_string sobre un TEXT[] no lo es, y por eso
-- los alias se guardan como texto plano separado por espacios.
--
-- El contenido no vive aqui sino en db/seeds/catalog.sql, que emite
-- ml/data/seed_catalog.py: una migracion aplicada jamas se edita y una
-- definicion de negocio se corrige varias veces. La migracion crea estructura;
-- el seed pone contenido.

-- migrate:up
CREATE TABLE catalog_source (
    id               BIGSERIAL PRIMARY KEY,
    code             TEXT NOT NULL UNIQUE,
    display_name     TEXT NOT NULL,
    description      TEXT NOT NULL,
    owner_area       TEXT NOT NULL,
    owner_name       TEXT NOT NULL,
    system_of_record TEXT NOT NULL,
    has_extract      BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  catalog_source             IS 'Fuentes de datos que el portal documenta, con extracto o sin el.';
COMMENT ON COLUMN catalog_source.has_extract IS
    'true solo en los silos con Parquet generado por US-006; el resto se documenta sin extracto';

CREATE TABLE catalog_field (
    id                BIGSERIAL PRIMARY KEY,
    source_id         BIGINT NOT NULL REFERENCES catalog_source(id) ON DELETE CASCADE,
    physical_name     TEXT NOT NULL,
    business_name     TEXT NOT NULL,
    definition        TEXT NOT NULL,
    aliases           TEXT NOT NULL DEFAULT '',
    domain            TEXT NOT NULL
        CHECK (domain IN ('cartera', 'riesgo', 'liquidez', 'mercado',
                          'cliente', 'contable', 'operacion', 'regulatorio')),
    data_type         TEXT NOT NULL
        CHECK (data_type IN ('entero', 'decimal', 'texto', 'fecha',
                             'booleano', 'categoria')),
    sensitivity       TEXT NOT NULL
        CHECK (sensitivity IN ('publica', 'interna', 'restringida')),
    refresh_frequency TEXT NOT NULL
        CHECK (refresh_frequency IN ('intradia', 'diaria', 'semanal', 'mensual')),
    certification     TEXT NOT NULL
        CHECK (certification IN ('certificado', 'en_revision', 'obsoleto')),
    unit              TEXT
        CHECK (unit IN ('MXN', 'USD', 'porcentaje', 'dias', 'conteo')),
    metric_agg        TEXT
        CHECK (metric_agg IN ('sum', 'mean', 'count', 'max', 'min')),
    steward           TEXT,
    valid_from        DATE NOT NULL,
    valid_to          DATE,
    embedding         VECTOR(768),
    search_document   TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('spanish', business_name), 'A')
        || setweight(to_tsvector('spanish', physical_name || ' ' || aliases), 'B')
        || setweight(to_tsvector('spanish', definition), 'C')
    ) STORED,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT catalog_field_source_physical_key UNIQUE (source_id, physical_name),
    CONSTRAINT catalog_field_validity_chk
        CHECK (valid_to IS NULL OR valid_to >= valid_from),
    CONSTRAINT catalog_field_obsolete_chk
        CHECK ((certification = 'obsoleto') = (valid_to IS NOT NULL))
);

COMMENT ON TABLE  catalog_field                 IS 'Una entrada del catalogo: la traduccion de una columna fisica al lenguaje del negocio.';
COMMENT ON COLUMN catalog_field.aliases         IS
    'Sinonimos separados por espacio, incluidos los equivalentes en ingles; alimentan el peso B';
COMMENT ON COLUMN catalog_field.search_document IS
    'Documento indexado: business_name en A, physical_name y aliases en B, definition en C';
COMMENT ON COLUMN catalog_field.embedding       IS
    'Gemini 768d. Sin escribir en S4: la busqueda hibrida esta diferida por el recorte 1';

CREATE INDEX catalog_field_search_document_idx
    ON catalog_field USING gin (search_document);
CREATE INDEX catalog_field_source_id_idx
    ON catalog_field (source_id);
CREATE INDEX catalog_field_embedding_idx
    ON catalog_field USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE catalog_tribal_note (
    id                  BIGSERIAL PRIMARY KEY,
    field_id            BIGINT NOT NULL REFERENCES catalog_field(id) ON DELETE CASCADE,
    note                TEXT NOT NULL,
    applicability       TEXT NOT NULL,
    applicability_terms TEXT NOT NULL DEFAULT '',
    author              TEXT NOT NULL,
    recorded_at         DATE NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT catalog_tribal_note_field_note_key UNIQUE (field_id, note)
);

COMMENT ON TABLE  catalog_tribal_note                     IS 'Conocimiento tribal con condicion de aplicabilidad (patron Tk-Boost).';
COMMENT ON COLUMN catalog_tribal_note.applicability_terms IS
    'Terminos disparadores (patron Tk-Boost); cadena vacia significa que la nota aplica siempre';

CREATE INDEX catalog_tribal_note_field_id_idx
    ON catalog_tribal_note (field_id);

-- migrate:down
DROP TABLE IF EXISTS catalog_tribal_note;
DROP TABLE IF EXISTS catalog_field;
DROP TABLE IF EXISTS catalog_source;
