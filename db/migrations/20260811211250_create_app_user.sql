-- Segunda migracion del proyecto: la tabla de usuarios del portal y sus siete
-- perfiles sembrados.
--
-- Las contrasenas van PREHASHEADAS con argon2id (pwdlib). El SQL no contiene, ni
-- puede contener, la contrasena en claro: los hashes se generan fuera con
--     KARISMA_DEMO_PASSWORD=... poetry -P backend run python scripts/generar_hashes_demo.py --sql
-- y se pegan aqui una sola vez. La correspondencia entre los siete hashes y la
-- contrasena documentada se comprueba con el modo --verificar del mismo script.
-- Argon2 sala al azar: dos corridas dan hashes distintos y ninguno se puede
-- fijar en una prueba, por eso las pruebas fijan formato y correspondencia.
--
-- gen_random_uuid() es funcion del nucleo desde PostgreSQL 13: no hace falta
-- pgcrypto y por eso esta migracion no habilita ninguna extension.
--
-- Los siete usuarios son las personas de A1 agrupadas en los cuatro roles de
-- control de acceso: un administrador y dos por cada perfil de dato. Los
-- nombres van sin diacriticos a proposito: db/schema.sql se compara byte a byte
-- en CI y nada se gana metiendo UTF-8 no ASCII en un volcado.

-- migrate:up
CREATE TABLE app_user (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        TEXT NOT NULL UNIQUE,
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    role            TEXT NOT NULL
                    CHECK (role IN ('operativo', 'analista', 'directivo', 'admin')),
    disabled        BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  app_user                 IS 'Usuarios del portal. Baja logica con disabled, nunca DELETE.';
COMMENT ON COLUMN app_user.hashed_password IS 'argon2id via pwdlib. Jamas texto plano, jamas serializado en una respuesta.';
COMMENT ON COLUMN app_user.role            IS 'Scope del JWT: operativo | analista | directivo | admin.';

INSERT INTO app_user (username, email, full_name, hashed_password, role) VALUES
    ('movalle',    'movalle@karisma.demo',    'Mariana Ovalle',   '$argon2id$v=19$m=65536,t=3,p=4$DNuxntWBsc2Nco+4Uhf9Vg$avSDe2+dTBIAR4+HVQ85KU+emSrpemNs0CmKVfQyzuA', 'admin'),
    ('lmendez',    'lmendez@karisma.demo',    'Laura Mendez',     '$argon2id$v=19$m=65536,t=3,p=4$1hCUIOfp+mZWkahix+cIYg$UyXxuvug8mKzxurJkdjpZEm9c3L5b2UompSa27EVueA', 'operativo'),
    ('eruiz',      'eruiz@karisma.demo',      'Elena Ruiz',       '$argon2id$v=19$m=65536,t=3,p=4$ygDXCiweQo7tgUHEJvQcqA$R9c5x2i8DuwOiEneRSsw19KpyaNRvg83TT41DhtURhQ', 'operativo'),
    ('dhernandez', 'dhernandez@karisma.demo', 'Diego Hernandez',  '$argon2id$v=19$m=65536,t=3,p=4$wn2MDekoS/jwZTe213uWvA$Kiil80WgymnS9lnsoTL5EqT0u1st/8Ql3D2nX/dvgqI', 'analista'),
    ('jmendieta',  'jmendieta@karisma.demo',  'Jorge Mendieta',   '$argon2id$v=19$m=65536,t=3,p=4$frsUWQJSGoUF+p8JMaJZOA$sI67KjsI7QyMJU+5irbpL4mxIvOk7ir4E821OYWj2zg', 'analista'),
    ('acastaneda', 'acastaneda@karisma.demo', 'Arturo Castaneda', '$argon2id$v=19$m=65536,t=3,p=4$NsypCLBjvjEtplyrSqNiMw$/Lu6s5XDTW/xXvgXIGEassHkdH9K1BgPRs44Z4SBy+M', 'directivo'),
    ('rvaldez',    'rvaldez@karisma.demo',    'Roberto Valdez',   '$argon2id$v=19$m=65536,t=3,p=4$hTWsAZFwaB1z8Rkl332NQQ$zI0JcBwrG/eYkvYCeTJt/6dXrv/kdpHoi9fQosyH0Cc', 'directivo');

-- migrate:down
DROP TABLE IF EXISTS app_user;
