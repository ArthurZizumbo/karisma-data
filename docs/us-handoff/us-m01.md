# Handoff US-M01 — Despliegue puente en GCP con base administrada

**Estado**: testing
**Epic**: E0 Plataforma (puente de despliegue; Terraform sigue congelado)
**Sprint**: S5 · **Actividad**: habilita A5 (dom 23-ago-2026, entrega final y prueba SUS). **No es entregable calificado**
**Rama**: `us-m01`, ya creada y activa. Commits locales encadenados, sin PR mientras el usuario no lo apruebe (discrepancia RU-11 declarada frente a `feature/E0-US-M01-despliegue-puente`)
**SHA base**: `f06acee` (merge del PR #7, punta de `main` tras `us-a4-excelencia`), verificado con el árbol limpio el 18-ago-2026. Ancla del diff de todas las fases: `git diff --name-only f06acee`. **QA no usa `HEAD~N`**
**Estimación**: 3 SP · **Días**: mar 18 y mié 19-ago-2026 · **Estado esperado al cierre**: cerrada
**Plan**: [`docs/us-planning/us-m01.md`](../us-planning/us-m01.md)

---

## Dominios y sub-tareas tocados

- [ ] backend — **ninguna línea de `backend/app/`**. Solo `backend/Dockerfile` (stage `runtime-con-datos`) y `backend/.env.example`
- [x] frontend — `server/utils/identidadCloudRun.ts` (nuevo), `server/api/[...].ts`, `nuxt.config.ts`, `.env.example`, dos archivos de prueba
- [ ] ml — no participa
- [x] db — **sin migración nueva**: se aplican las seis existentes contra Cloud SQL y se verifica `db/schema.sql`
- [x] tests — `tests/backend/test_database_dsn.py` (dos casos), `frontend/test/identidadCloudRun.spec.ts` (nuevo), `frontend/test/proxyApi.spec.ts`
- [x] docs — `ADR-004`, `docs/despliegue.md`, `docs/manual-test/us-m01.md`, este handoff
- [x] infra/scripts — `scripts/desplegar.sh`, `scripts/verificar_despliegue.sh`, `scripts/limpieza_artifact_registry.json`, `docker-compose.yml`, `Makefile`

**NO se reparte.** Un solo ejecutor secuencial: la mitad del trabajo es ejecución de `gcloud` con credenciales del usuario, las fases están encadenadas por dato (la URL del api es entrada del web, la etiqueta de imagen es entrada del deploy) y el write-set completo son 17 archivos, de los cuales cuatro son código. Motivos completos en §5 del plan.

---

## Zonas sensibles

| Archivo | Por qué |
|---|---|
| `frontend/server/api/[...].ts` | Es el único lugar donde el JWT sale de la cookie. La cabecera nueva **no puede tocar `authorization`**: pisarla derriba toda la autorización por rol. Sin `NUXT_API_AUDIENCE` el comportamiento debe ser byte a byte el de hoy |
| `docker-compose.yml` | El `target: runtime` explícito del servicio `api` es obligatorio: el stage nuevo pasa a ser el último del Dockerfile y sin `target` `make dev` intentaría construirlo y fallaría por falta de `data/` en el contexto |
| `db/schema.sql` | **No se edita a mano jamás**, ni para que `git diff` calle. Lo regenera `dbmate up` |
| `backend/.env.local` | De ahí salen los valores de los tres secretos. No se copia, no se sube, no entra a ninguna imagen |
| `scripts/dbmate.sh` y `scripts/smoke_rutas.sh` | Propiedad de US-001/US-002. **No se modifican**: el primero ya soporta `DBMATE_URL`; al segundo se le pasa por encima con `verificar_despliegue.sh`, que sí sabe de tokens de identidad |

---

## Gate del cierre por IAM (CA-5b)

`ADR-004` se escribe **antes** de ejecutar el primer `add-iam-policy-binding`, con las dos ramas ya redactadas:

- **Rama A (45 min o menos)**: `karisma-api` queda con `--no-allow-unauthenticated` y `karisma-web` lo invoca con `X-Serverless-Authorization`.
- **Rama B (más de 45 min)**: `karisma-api` se redespliega con `--allow-unauthenticated`. **No se relaja ni un scope**: todo endpoint de datos conserva su `Security(...)` y lo público sigue siendo lo que ya lo era. Se marca en el ADR con la hora, y la deuda queda nombrada.

Pasada la hora de corte no se espera más. La decisión se escribe, no se insinúa.

---

## QA del 19-ago-2026 — hallazgos

`make check` **verde** (exit 0). `make test` **rojo al abrir el QA** y verde tras normalizar un
artefacto; cobertura backend 98,23 % y frontend 93,75 %. Criterios verificados contra los recursos
reales con `gcloud` y contra la URL publica con `curl`: **CA-2, CA-3, CA-4, CA-5, CA-6, CA-7, CA-9,
CA-10 y CA-11 pasan**. Lo que sigue es lo que no.

### Bloqueantes

| ID | Hallazgo | Donde |
|---|---|---|
| **SEC-1** | **Tres secretos de produccion tienen valor por omision escrito en el repositorio.** Si la variable no esta en el entorno del operador, el guion **sube esa cadena a Secret Manager**: `JWT_SECRET_KEY` cae en `clave_secreta_super_segura_para_desarrollo_local_1234567890`, `GEMINI_API_KEY` en `placeholder_gemini_api_key` y la contrasena de Cloud SQL en `karisma`. Quien lea el repositorio puede **firmar tokens validos del portal desplegado**. `APP_ENV=prod` no lo atrapa: esos literales no estan en `DEVELOPMENT_MARKERS`, y gitleaks tampoco, porque no tienen forma de credencial conocida | `scripts/desplegar.sh:45,130,131` |
| **SEC-2** | **La contrasena de los siete usuarios sembrados esta en claro** como valor por omision. Es la puerta de la demostracion publica | `scripts/verificar_despliegue.sh:16` |
| **VER-1** | **La verificacion del criterio central no puede fallar.** Si `karisma-api` respondiera 200 sin identidad —el aislamiento roto— el guion imprime `ADVERTENCIA` y sigue hasta el mensaje final de exito. CA-5 quedaria en verde con el backend publico | `scripts/verificar_despliegue.sh:44-48` |

### Medios

| ID | Hallazgo | Donde |
|---|---|---|
| **QA-1** | `make test` estaba **rojo** en el arbol entregado: `test_el_artefacto_versionado_esta_al_dia` fallaba porque `db/seeds/catalog.sql` tenia finales de linea CRLF y el generador compara bytes. Se corrigio regenerando el artefacto; `git diff` sigue vacio, porque git normaliza. El cierre declaraba `make check` al 100 % y no mencionaba `make test` | `db/seeds/catalog.sql` |
| **SEC-3** | El fallo del servidor de metadatos se trata de **tres maneras distintas**: 502 en `token.post.ts` y `demo.post.ts`, y **silencio** en `leerPerfilDeSesion`, que sigue sin el token. Cloud Run devolvera 403 y la interfaz lo leera como sesion invalida del usuario, que es el diagnostico equivocado | `frontend/server/utils/sesion.ts:162-164` |
| **TEST-1** | **Cero cobertura de las tres ramas nuevas** de inyeccion del ID token en los manejadores de sesion. Son exactamente las lineas sin cubrir del informe | `token.post.ts:50-55`, `demo.post.ts:55-60`, `sesion.ts:162-164` |
| **CA-1b** | `exigir_proyecto` **advierte y continua** cuando la cuenta de facturacion no coincide. El plan lo especificaba como aborto | `scripts/desplegar.sh:60-64` |
| **GATE-1** | `verificar_gitleaks.sh` **redujo su cobertura**: el barrido de `.env.local` paso de `find` sobre el arbol a una lista fija de dos rutas, asi que un `.env.local` en cualquier otra carpeta ya no se comprueba. Es un gate de seguridad relajado dentro de una US de despliegue, y el archivo no estaba en el write-set del plan | `scripts/verificar_gitleaks.sh:103` |
| **DOC-1** | `docs/manual-test/us-m01.md` registraba el recorrido de los cuatro roles con **cuatro cuentas que no existen** (`patricia.operaciones@karisma.com` y tres mas). Los usuarios reales son `movalle`, `lmendez`, `eruiz`, `dhernandez`, `jmendieta`, `acastaneda` y `rvaldez`. **Reescrito** en el QA, con el recorrido de los siete rehecho contra la URL publica | `docs/manual-test/us-m01.md` |
| **CFG-1** | El servicio `sqlproxy` fija el nombre de instancia en claro y su volumen por omision usa `~`, que **Docker Compose no expande**: sin `CREDENCIALES_ADC` el montaje apunta a una ruta literal | `docker-compose.yml:175,177` |
| **REPRO-1** | El servicio desplegado lleva una variable `DEPLOY_TIMESTAMP` que `scripts/desplegar.sh` **no escribe**: hubo al menos un paso manual fuera del guion, y el criterio pedia el despliegue completo sin pasos manuales no escritos | `karisma-api` vs. `scripts/desplegar.sh` |
| **CTX-1** | `cp -r backend/* "$ctx/"` no copia `backend/.dockerignore`, asi que la imagen de produccion se construye **sin ninguna exclusion** | `scripts/desplegar.sh:159` |

### Notas, sin accion obligada

- **Presupuesto en MXN.** La alerta existe con los tres umbrales y el filtro correcto, pero el monto
  quedo en **900 MXN**: la cuenta factura en pesos y `gcloud` convirtio los 45 USD al crearla.
  Equivale al techo pedido hoy; si el tipo de cambio se mueve, el techo en dolares deriva.
- **URLs de Cloud Run en claro** como valor por omision en `verificar_despliegue.sh:18-19`.
- **El diff contra `f06acee` mezcla dos trabajos.** Trece archivos de `docs/entregables/`, las dos
  guias de `docs/` y `scripts/verificar_tokens_a4.sh` son la correccion del entregable A4 pedida por
  el profesor el 19-ago-2026, no US-M01. Auditados aparte: `make check` y el verificador de tokens
  quedan en verde y ninguno toca codigo de aplicacion.

### Correccion aplicada el 19-ago-2026

Los doce hallazgos quedan cerrados en el mismo arbol, antes del commit.

| ID | Que se hizo |
|---|---|
| **SEC-1** | Fuera los tres valores por omision. `exigir_secreto` aborta con el nombre de la variable que falta antes de tocar Secret Manager, y `cargar_secretos` exige las tres. Un secreto que falta detiene el despliegue en vez de publicar uno escrito en el repositorio |
| **SEC-2** | `KARISMA_DEMO_PASSWORD` sin valor por omision; el guion aborta si no viene del entorno. Fuera tambien las dos URL de Cloud Run escritas como respaldo: se preguntan a `gcloud` |
| **VER-1** | Las dos mitades del aislamiento **fallan** ahora: un codigo distinto de 403 sin identidad aborta, y no poder obtener un ID token tambien. Antes avisaba y seguia hasta el mensaje de exito |
| **QA-1** | `db/seeds/catalog.sql` regenerado; `make test` en verde. Sin cambio en git: era el final de linea |
| **SEC-3** | `leerPerfilDeSesion` ya no traga el fallo: lanza. `identidadCloudRun.ts` expone `ErrorDeIdentidad` y los dos manejadores de sesion lo traducen a **502**, no a 401 ni a `demo_deshabilitado` |
| **TEST-1** | `frontend/test/identidadEnSesion.spec.ts`, cinco casos: la cabecera viaja al API y al perfil sin tocar `authorization`; sin audiencia no se llama al metadatos; y las tres formas del fallo dan 502, incluida la caida **entre** la emision y la lectura del perfil, que es el defecto exacto de SEC-3 |
| **CA-1b** | `exigir_proyecto` aborta si la cuenta de facturacion no coincide, si no se puede leer o si no esta definida |
| **GATE-1** | Restaurado el barrido con `find` sobre el arbol, leido por `while read` para tolerar rutas con espacios. Verificado en verde |
| **DOC-1** | `docs/manual-test/us-m01.md` reescrito con los siete usuarios reales y el recorrido rehecho contra la URL publica |
| **CFG-1** | El servicio `sqlproxy` toma `INSTANCIA_CLOUD_SQL` y `CREDENCIALES_ADC` con `:?`, asi que Compose falla con un mensaje claro en vez de montar una carpeta llamada `~`. Las exporta `aplicar_migraciones` |
| **REPRO-1** | Escrito junto al `deploy` que `--set-env-vars` reemplaza el conjunto entero: la variable que alguien anadio a mano desaparece en el proximo despliegue, que es lo que hace del guion la unica fuente del estado |
| **CTX-1** | El contexto efimero copia tambien `backend/.dockerignore` |

`docs/despliegue.md` documenta las cuatro variables obligatorias, y dice que hay que **rotar**
`JWT_SECRET_KEY` y la contrasena de Cloud SQL si alguna vez se desplegó con un valor de ejemplo.


---

## Al cerrar

- **URL Frontend (pública)**: `https://karisma-web-${GCP_PROJECT_NUMBER}.us-central1.run.app`
- **URL Backend API (privada, IAM)**: `https://karisma-api-${GCP_PROJECT_NUMBER}.us-central1.run.app`

  Las dos se escriben por variable, como el resto de los identificadores de nube de esta US: el
  repositorio es público y el número de proyecto no tiene por qué viajar en él. La dirección real la
  imprime `scripts/desplegar.sh` al terminar y la devuelve
  `gcloud run services describe <servicio> --region=us-central1 --format='value(status.url)'`.
- **Base de Datos Administrada**: Cloud SQL PostgreSQL 15 (`karisma-pg`, `db-f1-micro`, 10 GB HDD) en `us-central1`
- **Autenticación e IAM**: Rama A ejecutada y verificada exitosamente (Invocación privada con `X-Serverless-Authorization` y token OIDC de cuenta de servicio)
- **Suite de verificación post-despliegue**: `scripts/verificar_despliegue.sh` y `make check` pasando al 100%.
- **Manual test**: `docs/manual-test/us-m01.md` con los 4 roles validados en producción.
- **Estado**: **testing**. Los doce hallazgos del QA quedaron corregidos el 19-ago-2026; cierra cuando el usuario apruebe el commit y, si aplica, la rotacion de secretos.
