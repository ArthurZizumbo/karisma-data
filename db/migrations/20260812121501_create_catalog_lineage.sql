-- Recorrido del dato entre el sistema de origen y la cifra visible.
--
-- El tramo aguas arriba -captura, extraccion, transformacion y control de
-- calidad- es el mismo para todos los campos de una fuente, porque es el mismo
-- trabajo de plataforma: por eso la fila cuelga de catalog_source y no de
-- catalog_field. Un recorrido por campo serian ~1200 filas generadas por regla,
-- es decir linaje inventado disfrazado de dato.
--
-- El paso terminal, el que dice cual es la cifra que se esta mirando, NO se
-- guarda: se compone en el servicio desde catalog_field, porque persistirlo
-- duplicaria columnas que esa tabla ya tiene y la primera correccion de una
-- definicion dejaria al linaje diciendo una cosa y al diccionario otra, sin
-- nada que lo detectara. Por eso 'presentacion' no aparece en el CHECK de
-- stage: una restriccion que admite un valor que jamas se inserta invita a
-- sembrarlo "para completar".
--
-- Esta migracion NO altera ninguna tabla de US-008. Cero ALTER TABLE.
--
-- El contenido no vive aqui sino en db/seeds/catalog_lineage.sql: una
-- migracion aplicada jamas se edita y un dato curado se corrige varias veces.

-- migrate:up
CREATE TABLE catalog_lineage_step (
    id                    BIGSERIAL PRIMARY KEY,
    source_id             BIGINT NOT NULL REFERENCES catalog_source(id) ON DELETE CASCADE,
    step_order            SMALLINT NOT NULL CHECK (step_order BETWEEN 1 AND 9),
    stage                 TEXT NOT NULL
        CHECK (stage IN ('origen', 'extraccion', 'transformacion', 'calidad')),
    system_code           TEXT NOT NULL CHECK (system_code <> ''),
    system_name           TEXT NOT NULL CHECK (system_name <> ''),
    transformation_code   TEXT NOT NULL
        CHECK (transformation_code IN ('origin_capture', 'batch_extract', 'stream_extract',
                                       'type_normalization', 'currency_conversion',
                                       'deduplication', 'business_rule',
                                       'reconciliation', 'quality_rule')),
    transformation_detail TEXT NOT NULL CHECK (transformation_detail <> ''),
    owner_area            TEXT NOT NULL,
    owner_name            TEXT NOT NULL,
    effective_from        DATE NOT NULL,
    effective_to          DATE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT catalog_lineage_step_validity_chk
        CHECK (effective_to IS NULL OR effective_to >= effective_from)
);

COMMENT ON TABLE catalog_lineage_step IS
    'Tramo aguas arriba del linaje, por fuente. El paso de presentacion se deriva de catalog_field y no se guarda aqui';
COMMENT ON COLUMN catalog_lineage_step.stage IS
    'presentacion no aparece en el CHECK a proposito: esa etapa se compone en el servicio';
COMMENT ON COLUMN catalog_lineage_step.transformation_code IS
    'Codigo cerrado; la prosa visible vive en las claves i18n lineage.transformation.*';
COMMENT ON COLUMN catalog_lineage_step.transformation_detail IS
    'Dato no traducible interpolado en la plantilla: nombre de trabajo, de regla o de control';

-- Unico indice, y es a la vez la restriccion de unicidad y el indice de
-- recuperacion: el servicio filtra por source_id y ordena por step_order, que
-- es exactamente el prefijo de esta clave. Un segundo indice sobre las mismas
-- columnas seria peso muerto.
CREATE UNIQUE INDEX catalog_lineage_step_source_order_key
    ON catalog_lineage_step (source_id, step_order);

-- migrate:down
DROP TABLE IF EXISTS catalog_lineage_step;
