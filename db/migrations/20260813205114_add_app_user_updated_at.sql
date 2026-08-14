-- La marca de modificacion administrativa de app_user.
--
-- La escritura sobre app_user nace en US-018: hasta esta US nadie actualizaba
-- una fila, y por eso la columna no existia. La deuda quedo declarada con dueno
-- en la seccion 8.2 del plan de US-015.
--
-- El servicio fija updated_at de forma explicita en cada UPDATE. NO se instala
-- un disparador: un disparador hace invisible en el codigo lo que ocurre en la
-- base, y su reversa es mas superficie de la que esta columna justifica.
--
-- Las siete filas sembradas se igualan a created_at y no a now(): una cuenta
-- que nadie ha tocado no debe leerse como modificada el dia de la migracion.
--
-- Sin indice: ninguna consulta filtra ni ordena por esta columna. Un indice sin
-- consulta que lo use es peso muerto que ademas hay que revertir.

-- migrate:up
ALTER TABLE app_user
    ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

UPDATE app_user SET updated_at = created_at;

COMMENT ON COLUMN app_user.updated_at IS
    'Ultima modificacion administrativa: cambio de rol, desactivacion o reactivacion. La fija el servicio, nunca un disparador.';

-- migrate:down
ALTER TABLE app_user
    DROP COLUMN updated_at;
