-- Quinta migracion del proyecto: los trabajos de exportacion en segundo plano.
--
-- La tabla no borra nunca una fila: un trabajo caducado sigue siendo historial y
-- su enlace deja de funcionar por la firma, no por el DELETE. La politica de
-- ciclo de vida del bucket queda fuera de alcance (recorte #3 de S4).
--
-- Los estados van con CHECK y no con un ENUM de PostgreSQL a proposito: anadir un
-- valor a un ENUM es una migracion con bloqueo, y este vocabulario todavia se
-- mueve. El CHECK es la ultima linea de defensa contra una escritura directa que
-- no pase por EstadoTrabajo.
--
-- Los dos CONSTRAINT de coherencia impiden los dos estados imposibles que el
-- historial no sabria pintar: un trabajo completado sin archivo ni caducidad, y
-- un trabajo fallido sin motivo. La base los rechaza aunque el servicio falle.
--
-- Tres indices, cada uno con una consulta detras: el historial por dueno, el
-- barrido de trabajos vivos y la purga futura por caducidad. Ninguno sobre
-- dataset y ninguno GIN sobre filters: no hay consulta que los use y un indice
-- de mas es coste de escritura permanente.

-- migrate:up
CREATE TABLE export_job (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by  UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    dataset       TEXT NOT NULL,
    export_format TEXT NOT NULL
                  CHECK (export_format IN ('csv', 'xlsx')),
    filters       JSONB NOT NULL DEFAULT '{}'::jsonb,
    status        TEXT NOT NULL DEFAULT 'pendiente'
                  CHECK (status IN ('pendiente', 'en_proceso', 'completado', 'fallido')),
    row_count     BIGINT,
    byte_size     BIGINT,
    object_key    TEXT,
    error_code    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at    TIMESTAMPTZ,
    finished_at   TIMESTAMPTZ,
    expires_at    TIMESTAMPTZ,

    CONSTRAINT export_job_completado_coherente
        CHECK (status <> 'completado'
               OR (object_key IS NOT NULL AND expires_at IS NOT NULL AND finished_at IS NOT NULL)),
    CONSTRAINT export_job_fallido_coherente
        CHECK (status <> 'fallido' OR error_code IS NOT NULL)
);

COMMENT ON TABLE  export_job            IS 'Trabajos de exportacion en segundo plano. Nunca se borran: caducan.';
COMMENT ON COLUMN export_job.object_key IS 'Clave opaca en el almacen. Jamas se serializa en una respuesta.';
COMMENT ON COLUMN export_job.expires_at IS 'Instante en que el enlace firmado deja de servir. created_at + 24 h.';
COMMENT ON COLUMN export_job.filters    IS 'Consulta estructurada validada por Pydantic. Nunca SQL ni Polars libre.';

CREATE INDEX export_job_requested_by_created_at_idx
    ON export_job (requested_by, created_at DESC);

CREATE INDEX export_job_status_vivos_idx
    ON export_job (status)
    WHERE status IN ('pendiente', 'en_proceso');

CREATE INDEX export_job_expires_at_idx
    ON export_job (expires_at)
    WHERE status = 'completado';

-- migrate:down
DROP INDEX IF EXISTS export_job_expires_at_idx;
DROP INDEX IF EXISTS export_job_status_vivos_idx;
DROP INDEX IF EXISTS export_job_requested_by_created_at_idx;
DROP TABLE IF EXISTS export_job;
