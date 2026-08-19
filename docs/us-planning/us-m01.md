# Planeación US-M01 — Despliegue puente en GCP con base administrada

| Campo | Valor |
|---|---|
| **Epic** | E0 Plataforma (puente de despliegue; Terraform sigue congelado) |
| **Actividad** | A5 — Entrega final y prueba SUS (dom 23-ago-2026). Esta US **no se califica sola**: habilita el reclutamiento de participantes sobre una URL pública |
| **Sprint** | S5 |
| **Rama** | `us-m01`, **ya creada y activa**, encadenada sobre `f06acee` (merge del PR #7, punta de `main` tras `us-a4-excelencia`). Convención del usuario del 10-ago-2026: una rama por US, commits locales encadenados; el estándar de la raíz (`feature/E0-US-M01-despliegue-puente`) queda como discrepancia RU-11, igual que en todas las US previas |
| **SHA base** | `f06acee`, verificado con `git rev-parse --short HEAD` el 18-ago-2026 con el árbol **limpio**. Ancla del diff de todas las fases: `git diff --name-only f06acee`. **Nunca `HEAD~N`** |
| **Estimación** | 3 SP · **Días**: mar 18 y mié 19-ago-2026 · **Estado esperado al cierre**: cerrada, con la salida de IAM (§10 R2) declarada de antemano |
| **Fuente de alcance** | El enunciado de la US entregado por el usuario el 18-ago-2026. **No existe en `context/planeacion_proyecto.md`**: ver discrepancia D-1 |
| **Presupuesto** | Techo del proyecto < $45 USD/mes (§23 del plan, R09). Estimación de este despliegue en §10.C |

---

## Lectura previa ejecutada

| Paso | Resultado |
|---|---|
| `docs/us-handoff/us-m01.md` | **No existía.** Se crea en esta pasada con estado `planning` |
| `db/AGENTS.md` (Estado) | Leído. Seis migraciones aplicadas, seis tablas más `schema_migrations`. dbmate corre **como servicio de Compose**, no como binario del host, y la cadena sale de `backend/.env.local`. `catalog_field.embedding` existe pero está vacío. Confirmado contra el repo: `ls db/migrations/` devuelve exactamente los seis archivos que la guía lista |
| `frontend/AGENTS.md` (Estado) | Leído. Ocho rutas del contrato más `/` y `/guia`; el JWT sale de la cookie **solo dentro de `server/`**; prohibido `routeRules` con `swr`. El proxy `/api/**` es un handler de runtime que relee `runtimeConfig.apiBase` en cada solicitud **precisamente para que la misma imagen sirva en Cloud Run**, donde la URL del backend solo se conoce después de desplegarlo |
| `backend/.env.example` | Leído entero. Es la lista real de variables del despliegue: tres obligatorias, `APP_ENV`, `DATA_DIR`, `CHAT_PROVIDER`, cuatro `EXPORT_*`, `DEMO_LOGIN_ENABLED` y `KARISMA_DEMO_PASSWORD` (que **no se despliega**) |
| `docker-compose.yml` + `backend/Dockerfile` + `frontend/Dockerfile` | Leídos. Ambas imágenes ya honran `$PORT` y ya declaran el usuario no-root. El comentario del Dockerfile del backend **anticipa** `gcloud run deploy karisma-api --source backend`; esta US lo corrige a build local + push a Artifact Registry por el motivo de §2.4 |
| `frontend/server/api/[...].ts` | Leído entero. Escribe `authorization` **incondicionalmente** con el JWT de la cookie y vacía `cookie`. Es el archivo que decide toda la §2.3 |
| `backend/app/core/config.py` y `core/database.py` | Leídos. `reject_development_markers` **impide arrancar con `APP_ENV != local` y un secreto placeholder**. `build_async_dsn` preserva la cadena de consulta íntegra, `sslmode` incluido: es lo que permite el socket unix de Cloud SQL sin tocar código |
| `scripts/dbmate.sh` | Leído. **Ya soporta `DBMATE_URL` como sobreescritura** de `DATABASE_URL`, y pasa el valor por `-e DATABASE_URL` sin `=` para que no aparezca en `ps`. Esta US no lo modifica: le entrega la variable |
| `mem_search "despliegue GCP Cloud Run Cloud SQL secretos presupuesto"` y `"Cloud Run karisma despliegue puente gcloud"` | **Sin resultados.** No hay memoria previa de despliegue en este proyecto: nada que copiar y nada que contradecir |
| `docs/us-resolved/` | **No existe** el directorio. No hay US resuelta parecida |
| Skills cargadas ([`auto-invoke.md`](../orchestration/auto-invoke.md)) | `portal-terraform-gcp` (fila «Crear/modificar módulo Terraform (Cloud Run, GCS, Secret Manager)») y `portal-finops` (fila «Auditar costo cloud / budget alerts / scale-to-zero»). Sus desviaciones respecto de esta US están en D-2 y D-3 |
| Context7 | Consultado **una vez y con motivo**: `gcloud artifacts repositories set-cleanup-policies` es una superficie de CLI que no estaba en uso en este repositorio. Confirmado que la forma es `gcloud artifacts repositories set-cleanup-policies <repo> --location=<region> --policy=<archivo.json>`. La consulta de `gcloud billing budgets create` no devolvió el detalle de banderas: el comando de §7.7 queda escrito **con la obligación explícita de verificarlo con `--help` antes de ejecutarlo** |

### Verificación del «Estado» contra el repositorio

| Comprobación | Resultado |
|---|---|
| `ls infra/` | **No existe.** La raíz lo declaraba y es cierto: Terraform congelado, el puente es `gcloud run deploy` |
| `find . -name "Dockerfile*"` | Dos: `backend/Dockerfile` y `frontend/Dockerfile`. Ambos multi-stage y listos para Cloud Run |
| `git ls-files data \| wc -l` | **1**: solo `data/README.md`. `data/silos/` está en `.gitignore:116` |
| `grep -rn "data_dir" backend/app` | Tres consumidores reales: `api/metrics.py`, `services/series_service.py`, `services/export_service.py` |
| `ls db/migrations/ \| tail -5` | Coincide con la guía: última `20260813205114_add_app_user_updated_at.sql` |
| `git rev-parse --short HEAD` | `f06acee`, árbol limpio |

---

## 1. Criterios de aceptación con métricas verificables

Cada criterio trae el comando que lo declara cumplido. Un criterio sin comando no está cerrado.

| ID | Criterio | Verificación mecánica |
|---|---|---|
| **CA-1** | Todo ocurre en el proyecto `tareas-computo-nube` (número `${GCP_PROJECT_NUMBER}`), facturación `${GCP_BILLING_ACCOUNT}`, región `us-central1`. `karisma-data` no se toca | `gcloud config get-value project` → `tareas-computo-nube`; `gcloud beta billing projects describe tareas-computo-nube --format='value(billingAccountName)'` → `billingAccounts/${GCP_BILLING_ACCOUNT}`. El script aborta si no coinciden (§4.1, `exigir_proyecto`) |
| **CA-2** | Dos servicios Cloud Run: `karisma-api` y `karisma-web`, `min-instances 0`, `max-instances 3`, 512 MiB, concurrencia 80 | `gcloud run services describe <svc> --region us-central1 --format='value(spec.template.metadata.annotations["autoscaling.knative.dev/minScale"],spec.template.metadata.annotations["autoscaling.knative.dev/maxScale"],spec.template.spec.containerConcurrency,spec.template.spec.containers[0].resources.limits.memory)'` → `0 3 80 512Mi` en ambos |
| **CA-3** | Cloud SQL `karisma-pg`: PostgreSQL 15, Enterprise, `db-f1-micro`, zonal, 10 GB HDD **sin** crecimiento automático, **sin** respaldos | `gcloud sql instances describe karisma-pg --format='value(databaseVersion,settings.edition,settings.tier,settings.availabilityType,settings.dataDiskSizeGb,settings.dataDiskType,settings.storageAutoResize,settings.backupConfiguration.enabled)'` → `POSTGRES_15 ENTERPRISE db-f1-micro ZONAL 10 PD_HDD False False` |
| **CA-4** | Cloud Run conecta por `--add-cloudsql-instances`, **sin** conector de acceso VPC serverless | `gcloud run services describe karisma-api --format='value(spec.template.metadata.annotations["run.googleapis.com/cloudsql-instances"])'` → `tareas-computo-nube:us-central1:karisma-pg`; el mismo describe **no** debe contener `run.googleapis.com/vpc-access-connector` |
| **CA-5** | El navegador solo habla con el frontend: `/api/**` se proxyea desde Nitro, `karisma-api` está desplegado con `--no-allow-unauthenticated`, no hay CORS, la cookie sigue siendo del mismo sitio | `curl -s -o /dev/null -w '%{http_code}' $URL_API/health` → **403**; `curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $(gcloud auth print-identity-token)" $URL_API/health` → **200**; `curl -si $URL_WEB/api/auth/me` viaja y responde desde el mismo origen; `grep -rn "CORSMiddleware" backend/app` → **cero coincidencias**; la cookie de sesión conserva `SameSite=Strict` y `Secure` sobre HTTPS |
| **CA-5b** | **Salida declarada**: si el cierre por IAM excede **45 minutos** desde el primer `add-iam-policy-binding`, se despliega `karisma-api` con `--allow-unauthenticated` y JWT obligatorio en todo endpoint de datos, **escrito como decisión** | El reloj lo lleva el operador y el resultado queda en [`ADR-004`](../decisions/ADR-004-cierre-por-iam-y-su-salida.md), que se escribe **antes** de intentar el cierre, con las dos ramas ya redactadas y una marcada al terminar |
| **CA-6** | Artifact Registry `karisma` con política de limpieza a **tres** etiquetas | `gcloud artifacts repositories describe karisma --location=us-central1`; `gcloud artifacts repositories describe karisma --location=us-central1 --format=json \| jq '.cleanupPolicies'` muestra la regla `Keep` con `keepCount: 3` |
| **CA-7** | Secret Manager con `DATABASE_URL`, `JWT_SECRET_KEY` y `GEMINI_API_KEY` inyectados al servicio, **nunca** como variables en claro del comando | `gcloud secrets list --format='value(name)'` contiene los tres; `gcloud run services describe karisma-api --format=json \| jq '..\|.secretKeyRef?\|select(.)'` los muestra los tres; `grep -n "set-env-vars" scripts/desplegar.sh` **no** contiene ninguno de esos tres nombres |
| **CA-8** | `dbmate up` ejecutado contra Cloud SQL y `db/schema.sql` **sin diferencias** después del despliegue | `bash scripts/dbmate.sh status` con `DBMATE_URL` apuntando al proxy → seis migraciones aplicadas, cero pendientes; después, `git diff --exit-code db/schema.sql` → **código 0**. La comparación se hace sobre el archivo del repositorio, que `dbmate up` regenera |
| **CA-9** | Tres alertas de presupuesto: 22.50, 36 y 45 USD | `gcloud billing budgets list --billing-account=$CUENTA_FACTURACION --format=json \| jq '.[].thresholdRules'` → tres reglas con `0.5`, `0.8`, `1.0` sobre un `budgetAmount` de 45 USD |
| **CA-10** | Los **siete** usuarios sembrados entran por la URL pública y **cada rol ve su espacio** | `bash scripts/verificar_despliegue.sh` (§4.2) recorre los siete inicios de sesión y las cuatro matrices de visibilidad; el recorrido humano queda en `docs/manual-test/us-m01.md` **con fecha** y con la tabla de las cuatro sesiones |
| **CA-11** | El portal desplegado **muestra datos**, no vacíos: tablero, catálogo y linaje responden con contenido | `curl` autenticado a `/api/metrics/series?...` → 200 con puntos; `/api/catalog/search?q=credito` → resultados; `/api/lineage/...` → pasos. Es lo que obliga a §2.4 y §2.5 |

---

## 2. Arquitectura de la solución y flujo de capas

### 2.1 El camino completo de una solicitud

```
navegador
  │  HTTPS, un solo origen
  ▼
karisma-web  (Cloud Run publico, --allow-unauthenticated)
  │  Nitro server/api/[...].ts
  │    authorization:              Bearer <JWT del portal, sacado de la cookie httpOnly>
  │    x-serverless-authorization: Bearer <ID token de la SA de web, audiencia = URL del api>
  ▼
karisma-api  (Cloud Run PRIVADO, --no-allow-unauthenticated, IAM run.invoker)
  │  socket unix /cloudsql/tareas-computo-nube:us-central1:karisma-pg
  ▼
Cloud SQL karisma-pg  (PostgreSQL 15, sin IP privada, sin conector VPC)
```

Secretos: `DATABASE_URL`, `JWT_SECRET_KEY` y `GEMINI_API_KEY` entran a `karisma-api` por `--set-secrets`, es decir por referencia a Secret Manager. Ninguno viaja en el argv del despliegue.

Datos sintéticos: los Parquet de `data/silos/` y `data/aggregates/` viajan **dentro de la imagen** del api (§2.4). No hay volumen ni bucket.

### 2.2 Por qué el backend es privado y qué cuesta

El criterio «el navegador solo habla con el frontend» ya se cumple en el código: el proxy de Nitro es el único que conoce la API y la cookie nunca sale del mismo sitio. `--no-allow-unauthenticated` añade la mitad que el código no puede dar: que nadie **más** que `karisma-web` pueda llamar al api, ni siquiera saltándose el navegador. El coste es un token adicional por solicitud, y de ahí sale §2.3.

### 2.3 Dos portadores en la misma solicitud — la decisión de diseño de esta US

`karisma-api` privado exige un **ID token de Google** en `Authorization`. Pero `Authorization` ya lo ocupa el JWT del portal, que es lo que identifica al usuario y decide su rol; sustituirlo rompería toda la autorización por scopes, y anidarlos no es una forma que ninguna de las dos partes entienda.

Cloud Run resuelve exactamente esta colisión: cuando `Authorization` ya está en uso, el token de IAM se envía en **`X-Serverless-Authorization`**, que el frontend de Cloud Run consume y **retira** antes de entregar la solicitud al contenedor. El backend sigue leyendo `Authorization` y no se entera de nada. Consecuencias:

1. `frontend/server/api/[...].ts` añade una cabecera más, y solo cuando hay audiencia configurada. Sin `NUXT_API_AUDIENCE` el comportamiento es **idéntico al de hoy**, que es lo que mantiene verde Docker Compose y `pnpm dev`.
2. El ID token se pide al servidor de metadatos de Cloud Run y se **cachea en memoria** del proceso hasta un minuto antes de expirar. Sin caché, cada `/api/**` pagaría una llamada extra, y un tablero pinta muchas.
3. Si el metadatos falla, el proxy responde **502** y **no reenvía sin token**: reenviar produciría un 403 de Cloud Run que la interfaz leería como un error del backend, y el diagnóstico se perdería.
4. La cuenta de servicio de `karisma-web` necesita `roles/run.invoker` sobre `karisma-api`. Ese binding es el reloj de CA-5b.

### 2.4 Los datos sintéticos tienen que entrar a la imagen del api

**Hallazgo que ninguna guía declaraba** (D-4). `data/silos/` y `data/aggregates/` **no están versionados** (`.gitignore:116`), los produce `make data` con semilla fija, y `backend/Dockerfile` hace `COPY app ./app` y nada más: hoy el api solo los ve porque `docker-compose.yml` monta `./data:/app/data:ro`. En Cloud Run no hay bind mount. Desplegado tal cual, el portal arranca, entra, pinta el chasis entero **y el tablero, el detalle de serie y la exportación no tienen de dónde leer** — que es justo lo que CA-11 prohíbe.

Se descartan dos caminos y se elige uno:

- ❌ **Bucket GCS + descarga al arranque**: añade un recurso, una dependencia de red en el arranque en frío y un costo que la US no pidió.
- ❌ **`COPY dat[a] ./data` (glob opcional)**: un `COPY` cuyo único patrón no casa **falla** en BuildKit. El truco solo funciona cuando otro origen del mismo `COPY` sí casa.
- ✅ **Stage adicional `runtime-con-datos`** en `backend/Dockerfile`, construido sobre un **contexto efímero** que `scripts/desplegar.sh` arma en un directorio temporal con `backend/` más `data/silos` y `data/aggregates`. Compose fija `target: runtime` explícito para que el stage nuevo, que pasa a ser el último del archivo, no se convierta en su destino por omisión.

Son 25 MB de Parquet: la imagen crece de forma irrelevante y el api arranca sin red.

### 2.5 Migraciones y semillas: el Auth Proxy como servicio de Compose

`dbmate` ya corre como servicio de Compose y ya acepta `DBMATE_URL`. Lo único que le falta es alcanzar Cloud SQL. Se añade a `docker-compose.yml` un servicio `sqlproxy` bajo el perfil **`nube`** (`docker compose up` sigue sin arrancarlo) con la imagen oficial del Cloud SQL Auth Proxy v2, autenticado con las credenciales de aplicación por omisión del operador montadas en solo lectura. `dbmate` y `psql` lo alcanzan por nombre de servicio dentro de la red del proyecto:

```
DBMATE_URL=postgres://karisma:<clave>@sqlproxy:5432/karisma?sslmode=disable
```

Así `make db-up` y `make db-seed` funcionan **sin cambiar una línea de sus recetas** contra la base administrada, y `db/schema.sql` lo regenera el mismo cliente `pg_dump 18.4` que lo generó en local — que es la única forma de que CA-8 pueda dar cero diferencias.

### 2.6 Construcción y publicación de imágenes

Se construye en local con `docker build --platform linux/amd64`, se etiqueta con el SHA corto de HEAD y se empuja a `us-central1-docker.pkg.dev/tareas-computo-nube/karisma/{api,web}`. Se despliega con `--image`, no con `--source`. Tres razones: `--source` publica en el repositorio `cloud-run-source-deploy` que gcloud crea solo, no en `karisma` (CA-6 quedaría sin sujeto); `--source` no acepta `--target`, que §2.4 necesita; y el SHA en la etiqueta hace que la política de tres versiones tenga algo que contar.

### 2.7 Orden obligatorio del despliegue

El frontend necesita la URL del backend, que solo existe después de desplegarlo. El script respeta esta secuencia y aborta en el primer fallo:

```
APIs → Artifact Registry (+ política) → Cloud SQL (+ base + usuario) → Secret Manager
     → imágenes (build + push) → karisma-api → migraciones + semillas
     → karisma-web (con NUXT_API_BASE y NUXT_API_AUDIENCE ya conocidas)
     → IAM run.invoker → presupuesto → verificación
```

---

## 3. Archivos exactos a crear o modificar

### Crear

| Archivo | Contenido |
|---|---|
| `scripts/desplegar.sh` | Despliegue completo, idempotente, por fases. Firma en §4.1 |
| `scripts/verificar_despliegue.sh` | Verificación post-despliegue de CA-5, CA-10 y CA-11 contra la URL pública. Firma en §4.2 |
| `scripts/limpieza_artifact_registry.json` | Política de limpieza: conserva las tres versiones más recientes, borra el resto |
| `frontend/server/utils/identidadCloudRun.ts` | Obtención y caché del ID token del servidor de metadatos. Firma en §4.3 |
| `frontend/test/identidadCloudRun.spec.ts` | Pruebas del módulo anterior (§6.2) |
| `docs/decisions/ADR-004-cierre-por-iam-y-su-salida.md` | Las dos ramas de CA-5b escritas **antes** de intentar el cierre |
| `docs/despliegue.md` | Runbook: prerrequisitos, variables, ejecución, reversión, costo mensual observado |
| `docs/manual-test/us-m01.md` | Recorrido humano de los cuatro roles sobre la URL pública, con fecha |
| `docs/us-handoff/us-m01.md` | Handoff, estado `planning` (esta pasada) |

### Modificar

| Archivo | Cambio | Riesgo de regresión |
|---|---|---|
| `backend/Dockerfile` | Añade el stage `runtime-con-datos` al final, con su comentario | Ninguno mientras Compose fije `target` |
| `docker-compose.yml` | `api.build.target: runtime` (explícito) y servicio `sqlproxy` en el perfil `nube` | El `target` explícito es obligatorio: sin él, `make dev` intentaría construir el stage nuevo y fallaría por falta de `data/` en el contexto |
| `frontend/server/api/[...].ts` | Añade `x-serverless-authorization` **solo** cuando hay audiencia; 502 si el metadatos falla | Cubierto por `proxyApi.spec.ts`, que verifica que sin audiencia las cabeceras no cambian |
| `frontend/nuxt.config.ts` | `runtimeConfig.apiAudience` desde `NUXT_API_AUDIENCE` (vacío por omisión) | Ninguno: vacío = comportamiento actual |
| `frontend/.env.example` | Documenta `NUXT_API_AUDIENCE` y por qué en local va vacía | — |
| `backend/.env.example` | Documenta la forma de `DATABASE_URL` con socket unix de Cloud SQL y corrige la referencia «Secret Manager (US-003)» a esta US | — |
| `tests/backend/test_database_dsn.py` | Dos casos nuevos: DSN con `host=/cloudsql/...` en la cadena de consulta (§6.1) | — |
| `frontend/test/proxyApi.spec.ts` | Casos nuevos de la cabecera de identidad | — |
| `Makefile` | Objetivos `desplegar` y `verificar-despliegue`, ambos delegando en los scripts | — |

### No se tocan, y es decisión

`scripts/smoke_rutas.sh` (propiedad de US-001: consulta `/health` del api **directamente**, que con el api privado ya no es alcanzable sin token; duplicar su lógica dentro sería reescribir una US ajena), `scripts/dbmate.sh` (ya soporta `DBMATE_URL`), `db/migrations/**` (esta US no cambia esquema), `frontend/app/**` (ninguna pantalla cambia), `backend/app/**` (ninguna línea de aplicación cambia: el despliegue se sostiene sobre lo que ya está escrito).

---

## 4. Firmas públicas de cada módulo nuevo

### 4.1 `scripts/desplegar.sh`

```bash
# Uso:
#   bash scripts/desplegar.sh [FASE ...]
#
# Sin argumentos ejecuta todas las fases en el orden de §2.7. Con argumentos,
# solo las nombradas, en el orden dado.
#
# Fases: apis | registro | base | secretos | imagenes | api | migraciones
#        | semillas | web | iam | presupuesto | verificar
#
# Variables de entrada (todas con valor por omision salvo las dos ultimas):
#   PROYECTO=tareas-computo-nube
#   NUMERO_PROYECTO=${GCP_PROJECT_NUMBER}
#   CUENTA_FACTURACION=${GCP_BILLING_ACCOUNT}
#   REGION=us-central1
#   INSTANCIA=karisma-pg
#   REPOSITORIO=karisma
#   ETIQUETA=$(git rev-parse --short HEAD)
#   ENV_BACKEND=backend/.env.local     # de aqui salen los valores de los secretos
#   KARISMA_DB_PASSWORD               # OBLIGATORIA, nunca en el repositorio
#   CREDENCIALES_ADC                  # ruta al application_default_credentials.json
#
# Salida: distinta de cero al primer fallo. Imprime al final las dos URL.
```

Funciones internas con nombre estable, todas idempotentes (`describe || create`):

| Función | Qué garantiza |
|---|---|
| `exigir_proyecto` | Aborta si el proyecto activo, su número o su cuenta de facturación no son los de CA-1 |
| `habilitar_apis` | `run`, `sqladmin`, `artifactregistry`, `secretmanager`, `cloudbuild` **y `billingbudgets`** (§7.1, D-5) |
| `crear_registro` | Repositorio `karisma` y aplicación de la política de tres versiones |
| `crear_base` | Instancia, base `karisma`, usuario `karisma`, extensión pendiente de la migración |
| `cargar_secretos` | Crea el secreto si falta y **siempre añade una versión nueva** leyendo de `ENV_BACKEND` por `--data-file=-` |
| `construir_imagenes` | Contexto efímero con datos (§2.4), build y push de las dos imágenes |
| `desplegar_api` / `desplegar_web` | Los dos `gcloud run deploy` de §7.4 y §7.6 |
| `aplicar_migraciones` / `aplicar_semillas` | Levanta `sqlproxy`, exporta `DBMATE_URL`, delega en `scripts/dbmate.sh` y `scripts/seed_catalogo.sh` |
| `conceder_invocacion` | El binding de `run.invoker` y el cronómetro de CA-5b |
| `crear_presupuesto` | Las tres reglas de umbral de CA-9 |

### 4.2 `scripts/verificar_despliegue.sh`

```bash
# Uso:
#   bash scripts/verificar_despliegue.sh
#
# Variables:
#   URL_WEB     por omision, la que devuelve gcloud run services describe
#   URL_API     idem
#   KARISMA_DEMO_PASSWORD   obligatoria: es la de los siete usuarios sembrados
#
# Comprueba, y sale distinto de cero al primer fallo:
#   1. El api NO responde sin ID token (403) y SI responde con el (200).
#   2. Las diez rutas del web publico responden.
#   3. Los SIETE usuarios sembrados obtienen sesion por POST /api/auth/token.
#   4. Por cada uno de los CUATRO roles: una ruta permitida da 200 y una
#      prohibida da 403. La matriz sale de docs/security.md, no de este guion.
#   5. Tres endpoints de datos devuelven contenido no vacio (CA-11).
```

### 4.3 `frontend/server/utils/identidadCloudRun.ts`

```ts
/** Servidor de metadatos de Cloud Run. Solo responde dentro de la plataforma. */
export const URL_METADATOS: string

/** Margen con el que se renueva el token antes de que expire. */
export const MARGEN_DE_RENOVACION_MS: number

/**
 * ID token de la cuenta de servicio del servicio, para la audiencia dada.
 * Cachea en memoria del proceso hasta MARGEN_DE_RENOVACION_MS antes del `exp`.
 * Lanza si el servidor de metadatos no responde: el llamador decide el 502.
 */
export function tokenDeIdentidad(audiencia: string): Promise<string>

/** Vacia la cache. Existe para las pruebas, y no la llama nada de `server/`. */
export function limpiarCacheDeIdentidad(): void
```

---

## 5. Dominios y sub-tareas, con el write-set de cada agente

- [ ] backend — **ninguna línea de `backend/app/`**. Solo `backend/Dockerfile` y `backend/.env.example`, que son plataforma
- [x] frontend — `server/utils/identidadCloudRun.ts`, `server/api/[...].ts`, `nuxt.config.ts`, `.env.example`, dos archivos de prueba
- [ ] ml — no participa
- [x] db — **sin migración nueva**: se ejecutan las seis existentes contra Cloud SQL y se verifica `schema.sql`
- [x] tests — dos casos en `tests/backend/test_database_dsn.py`, un archivo nuevo y casos añadidos en el frontend
- [x] docs — ADR-004, `docs/despliegue.md`, `docs/manual-test/us-m01.md`, handoff
- [x] infra/scripts — los tres archivos nuevos de `scripts/`, `docker-compose.yml` y `Makefile`

### **No se reparte, y es una decisión, no una omisión**

Un solo ejecutor secuencial. Tres motivos:

1. **La mitad del trabajo no es escritura de archivos, es ejecución de `gcloud` con credenciales del usuario.** Cada comando de §7 crea un recurso facturable y varios piden aprobación; repartirlos entre agentes multiplica las solicitudes de permiso sin acortar nada, que es exactamente lo que la convención del usuario del proyecto pide evitar.
2. **Las fases están encadenadas por dato, no por archivo.** La URL del api es entrada del despliegue del web; el nombre de la instancia es entrada de `DATABASE_URL`; la etiqueta de la imagen es entrada del deploy. Un paralelismo real exigiría que un agente esperara al otro, que es lo mismo que ir en serie con más ceremonia.
3. **El write-set completo son 17 archivos**, de los cuales solo cuatro son código. No hay volumen que justifique dos contextos.

La única frontera que sí se declara, por si el trabajo se retoma en otra sesión: **el frontend (§4.3 y sus pruebas) es autocontenido y se puede escribir y probar en local antes de tocar la nube**, porque sin `NUXT_API_AUDIENCE` su comportamiento es el de hoy. Ese es el primer bloque, y el resto es despliegue.

---

## 6. Plan de tests

Se prueba comportamiento que existe, nunca el guion de bash: un `.sh` que llama a `gcloud` no tiene prueba unitaria honesta, y su verificación es `scripts/verificar_despliegue.sh` corriendo contra recursos reales.

### 6.1 Backend — umbral `--cov-fail-under=70` (ya configurado)

`tests/backend/test_database_dsn.py`, dos casos nuevos. **Defecto concreto que los haría fallar**: que `build_async_dsn` perdiera o reordenara la cadena de consulta, que es donde viaja `host=/cloudsql/...`; con ese parámetro perdido el api arrancaría y fallaría en la primera consulta, ya en producción.

| Caso | Entrada | Esperado |
|---|---|---|
| Socket unix de Cloud SQL | `postgresql://karisma:x@/karisma?host=/cloudsql/tareas-computo-nube:us-central1:karisma-pg&sslmode=disable` | Devuelve el mismo DSN con esquema `postgresql+psycopg` y **la cadena de consulta íntegra**, los dos parámetros incluidos |
| Idempotencia sobre el mismo DSN | El resultado anterior, reintroducido | Inalterado |

No se añade nada más al backend: esta US no cambia una sola línea de `backend/app/`.

### 6.2 Frontend — umbral `thresholds: 50` (ya configurado)

`frontend/test/identidadCloudRun.spec.ts` (nuevo), con doble de `fetch`; ninguna prueba abre un socket.

| Caso | Defecto que atrapa |
|---|---|
| Pide el token con `Metadata-Flavor: Google` y la audiencia en la consulta | Sin esa cabecera el servidor de metadatos responde 403 y el portal entero queda sin backend |
| Dos llamadas seguidas con la misma audiencia hacen **una** petición | Sin caché, cada `/api/**` paga una llamada extra; un tablero dispara decenas |
| Con el token a menos de `MARGEN_DE_RENOVACION_MS` del `exp`, renueva | Un token vencido produce 403 intermitentes, el peor síntoma posible |
| Audiencias distintas no comparten entrada de caché | Un token de audiencia equivocada es rechazado por Cloud Run |
| El metadatos falla → lanza | El proxy debe poder distinguirlo para responder 502 |

`frontend/test/proxyApi.spec.ts` (modificado):

| Caso | Defecto que atrapa |
|---|---|
| **Sin** `apiAudience`: las cabeceras reenviadas son **exactamente** las de hoy | Que el cambio rompa Compose y `pnpm dev`, donde no hay servidor de metadatos |
| **Con** `apiAudience`: viaja `x-serverless-authorization` **y** `authorization` conserva el JWT del portal | Pisar `authorization` con el ID token derriba toda la autorización por rol |
| El metadatos falla → **502** y `proxyRequest` **no se llama** | Reenviar sin token devuelve un 403 de Cloud Run que la interfaz atribuye al backend |

### 6.3 Verificación que no es unitaria

`make check` y `make test` en verde antes de cualquier `gcloud`. Después del despliegue: `bash scripts/verificar_despliegue.sh` y el recorrido humano de `docs/manual-test/us-m01.md`.

---

## 7. Nube: qué comando sobre qué recurso

> Todos con `--project=tareas-computo-nube --region=us-central1` (o su equivalente). El script los emite; aquí están para revisarlos **antes** de que se ejecuten.

**7.1 APIs**
```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com \
  cloudbuild.googleapis.com billingbudgets.googleapis.com
```

**7.2 Artifact Registry y su política**
```bash
gcloud artifacts repositories create karisma --repository-format=docker \
  --location=us-central1 --description="Imagenes del portal Karisma Data"
gcloud artifacts repositories set-cleanup-policies karisma --location=us-central1 \
  --policy=scripts/limpieza_artifact_registry.json
gcloud auth configure-docker us-central1-docker.pkg.dev
```
`scripts/limpieza_artifact_registry.json`: una regla `Keep` con `mostRecentVersions.keepCount = 3` y una regla `Delete` para el resto. Las reglas `Keep` ganan sobre las `Delete`, que es lo que hace que «tres etiquetas» signifique tres y no «tres o las que sobrevivan».

**7.3 Cloud SQL**
```bash
gcloud sql instances create karisma-pg --database-version=POSTGRES_15 \
  --edition=enterprise --tier=db-f1-micro --region=us-central1 \
  --availability-type=zonal --storage-type=HDD --storage-size=10 \
  --no-storage-auto-increase --no-backup
gcloud sql databases create karisma --instance=karisma-pg
gcloud sql users create karisma --instance=karisma-pg --password="$KARISMA_DB_PASSWORD"
```
Sin `--no-assign-ip`: la IP pública es la vía del Auth Proxy para las migraciones, y sin ella la alternativa sería un conector de acceso VPC serverless, que la propia US descarta por costar más que la base. Las redes autorizadas quedan **vacías**: el único camino es el proxy con IAM.

**7.4 Secret Manager**
```bash
gcloud secrets create DATABASE_URL   --replication-policy=automatic
printf '%s' "$VALOR" | gcloud secrets versions add DATABASE_URL --data-file=-
# idem JWT_SECRET_KEY y GEMINI_API_KEY
gcloud secrets add-iam-policy-binding DATABASE_URL \
  --member="serviceAccount:${NUMERO_PROYECTO}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor
```
Valor de `DATABASE_URL` en producción (nunca en el repositorio, nunca en el argv):
```
postgresql://karisma:<clave>@/karisma?host=/cloudsql/tareas-computo-nube:us-central1:karisma-pg&sslmode=disable
```

**7.5 Imágenes**
```bash
docker build --platform linux/amd64 --target runtime-con-datos \
  -t us-central1-docker.pkg.dev/tareas-computo-nube/karisma/api:$ETIQUETA "$CTX"
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/tareas-computo-nube/karisma/web:$ETIQUETA frontend
docker push ...  # las dos
```

**7.6 `karisma-api`**
```bash
gcloud run deploy karisma-api \
  --image=us-central1-docker.pkg.dev/tareas-computo-nube/karisma/api:$ETIQUETA \
  --region=us-central1 --no-allow-unauthenticated \
  --min-instances=0 --max-instances=3 --memory=512Mi --concurrency=80 \
  --add-cloudsql-instances=tareas-computo-nube:us-central1:karisma-pg \
  --set-secrets=DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars=APP_ENV=prod,LOG_LEVEL=INFO,DATA_DIR=/app/data,CHAT_PROVIDER=guionizado,EXPORT_STORAGE_BACKEND=local,DEMO_LOGIN_ENABLED=true
```
`APP_ENV=prod` activa `reject_development_markers`: un secreto placeholder impide el arranque, que es la comprobación gratis que el código ya trae. `DEMO_LOGIN_ENABLED=true` es **deliberado y queda escrito**: el evaluador de A5 entra sin credenciales. La propia plantilla de entorno lo advierte con estas palabras — «lo deliberado no es escribir true aquí, es escribirlo en el `--set-env-vars` de un despliegue».

**7.7 `karisma-web`**
```bash
gcloud run deploy karisma-web \
  --image=.../karisma/web:$ETIQUETA --region=us-central1 --allow-unauthenticated \
  --min-instances=0 --max-instances=3 --memory=512Mi --concurrency=80 \
  --set-env-vars=NUXT_API_BASE=$URL_API,NUXT_API_AUDIENCE=$URL_API,NUXT_PUBLIC_ENTORNO=demo,NUXT_PUBLIC_DEMO_ACCESO=true
```

**7.8 IAM — el reloj de CA-5b**
```bash
gcloud run services add-iam-policy-binding karisma-api --region=us-central1 \
  --member="serviceAccount:${NUMERO_PROYECTO}-compute@developer.gserviceaccount.com" \
  --role=roles/run.invoker
```

**7.9 Presupuesto**
```bash
gcloud billing budgets create --billing-account="${GCP_BILLING_ACCOUNT}" \
  --display-name="Karisma Data 45 USD" --budget-amount=900MXN \
  --filter-projects=projects/tareas-computo-nube \
  --threshold-rule=percent=0.5 --threshold-rule=percent=0.8 --threshold-rule=percent=1.0 \
  --calendar-period=month
```
22.50, 36 y 45 USD son el 50 %, el 80 % y el 100 % de 45. **Verificar la sintaxis con `gcloud billing budgets create --help` antes de ejecutar**: es el único comando de esta lista que Context7 no confirmó.

---

## 8. Schema: migración y rollback

**Esta US no crea ninguna migración.** Aplica las seis existentes contra una base nueva y verifica que el volcado no cambió.

```bash
docker compose --profile nube up -d sqlproxy
export DBMATE_URL="postgres://karisma:$KARISMA_DB_PASSWORD@sqlproxy:5432/karisma?sslmode=disable"
bash scripts/dbmate.sh --wait up        # aplica las seis y regenera db/schema.sql
git diff --exit-code db/schema.sql      # CA-8: cero diferencias
make db-seed                            # catalogo y linaje, con la misma DBMATE_URL
```

**Rollback**: `dbmate rollback` no es el mecanismo aquí — revertir una migración no revierte un despliegue. La reversión real de esta US es, en orden: `gcloud run services delete karisma-web`, `karisma-api`, `gcloud sql instances delete karisma-pg`, `gcloud artifacts repositories delete karisma`, `gcloud secrets delete` los tres, `gcloud billing budgets delete`. Queda escrita en `docs/despliegue.md` con esos comandos, porque una reversión que hay que reconstruir de memoria a las once de la noche no es una reversión.

**Si `git diff db/schema.sql` no da cero**: no se «arregla» editando el archivo. Se lee la diferencia, y solo hay dos desenlaces honestos — o la base administrada añadió algo que el volcado local no tenía (se documenta en `docs/despliegue.md` y se decide si entra al archivo), o falta aplicar algo (se aplica). Editar el volcado a mano para que el comando calle es exactamente el fallo que CA-8 existe para detectar.

---

## 9. Entregable: a qué rubro responde

US-M01 **no es un entregable calificado**. Es la condición material de A5 (dom 23-ago-2026): la prueba SUS exige ≥5 participantes reales sobre el prototipo, y sin una URL pública el reclutamiento no existe. Su contribución al documento de A5 es indirecta y concreta:

- La sección de método puede declarar que la prueba corrió sobre **el sistema desplegado**, no sobre una máquina de desarrollo — que es una diferencia que un evaluador nota.
- El recorrido de los cuatro roles con fecha (`docs/manual-test/us-m01.md`) es evidencia de que los espacios de trabajo por rol funcionan fuera del entorno de quien los programó.
- La cifra de costo mensual observado alimenta la sección de viabilidad, si A5 la pide.

Ningún rubro de rúbrica se marca con esta US. Si la rúbrica de A5 apareciera antes del cierre, se aplica el protocolo de absorción §25.2 del plan **antes** de tocar el documento, no después.

---

## 10. Riesgos y mitigaciones

### A. Riesgos de ejecución

| ID | Riesgo | Mitigación |
|---|---|---|
| **R1** | **Los Parquet no llegan a la imagen** y el portal público queda vacío por dentro | §2.4: stage `runtime-con-datos` y contexto efímero. Verificado por CA-11 en `verificar_despliegue.sh`, no a ojo |
| **R2** | **El cierre por IAM no cuaja en 45 min** (propagación, cuenta de servicio equivocada, política de organización) | CA-5b. `ADR-004` se escribe **antes** de empezar, con las dos ramas redactadas; al terminar se marca la que ocurrió, con la hora. La rama B despliega el api con `--allow-unauthenticated` y **no relaja ni un scope**: todo endpoint de datos sigue exigiendo JWT, y lo público sigue siendo lo que ya lo era (`/health`, `/api/auth/token`, `/api/auth/demo`, `/openapi.json`) |
| **R3** | **Exportaciones entre instancias**: `EXPORT_STORAGE_BACKEND=local` escribe en el disco efímero del contenedor; con `max-instances 3`, un trabajo creado en una instancia y descargado desde otra da un enlace muerto | Se acepta y se declara. Con concurrencia 80 y tráfico de demostración, una segunda instancia es improbable. La salida existe y no se construye aquí: `EXPORT_STORAGE_BACKEND=gcs` ya está implementado y solo le falta el bucket. Si aparece en la prueba SUS, se crea el bucket con ciclo de vida de 7 días y se cambia una palabra |
| **R4** | **`db/schema.sql` sale distinto** contra Cloud SQL | El volcado lo produce el mismo cliente (servicio `dbmate` de Compose, `pg_dump 18.4`). Si aun así difiere, §8 dice qué hacer y qué no |
| **R5** | **Arranque en frío** con `min-instances 0`: la primera visita de un participante de SUS espera varios segundos y lo puntúa | Se mide en el recorrido manual y se anota. Palanca conocida y ya prevista por `portal-finops`: subir a `min-instances 1` **solo el día de la prueba**, con la reversión escrita y fechada. No se sube en esta US |
| **R6** | **Un secreto acaba en el historial de la terminal o en el argv** | Los tres viajan por `--data-file=-` con `printf`, y a Cloud Run por referencia. `KARISMA_DB_PASSWORD` entra por variable de entorno del script. `make check` corre gitleaks antes del PR |
| **R7** | **pgvector no habilitado** en la instancia administrada | La extensión la crea la migración `20260811005732`, no el operador. Cloud SQL para PostgreSQL 15 admite `vector`. Si el `CREATE EXTENSION` fallara, se detiene aquí: es un supuesto que se verifica en la primera migración, no al final |
| **R8** | **La puerta de demostración abierta a internet**: con `DEMO_LOGIN_ENABLED=true`, cualquiera con la URL acuña una sesión de cualquier rol | Es deliberado y proporcionado: los datos son sintéticos con semilla fija y documentada, no hay dato real que exponer. Queda escrito en `docs/despliegue.md` junto al comando que lo apaga el día que deje de ser una demostración |
| **R9** | **La cuenta de servicio por omisión de Compute** es la identidad de ambos servicios y tiene más permisos de los necesarios | Se acepta para el puente y se anota. Crear dos cuentas de servicio dedicadas con permiso mínimo es trabajo de la US de Terraform, no de este puente, y meterlo aquí alarga la ventana de CA-5b |

### B. Supuestos que se verifican al ejecutar, no antes

1. Que la cuenta del operador tenga `roles/owner` o el conjunto `run.admin` + `cloudsql.admin` + `artifactregistry.admin` + `secretmanager.admin` + `billing.costsManager` sobre la cuenta de facturación.
2. Que `docker` esté disponible en la máquina (lo está: Compose es el entorno de desarrollo) y produzca `linux/amd64`.
3. Que la sintaxis exacta de `gcloud billing budgets create` sea la de §7.9.

### C. Costo mensual estimado

| Concepto | Estimación |
|---|---|
| Cloud SQL `db-f1-micro` zonal + 10 GB HDD | ≈ $8 USD |
| IP pública IPv4 de la instancia | ≈ $3 USD |
| Cloud Run, dos servicios con `min-instances 0` | $0–3 USD |
| Artifact Registry (dos imágenes, tres versiones) | < $1 USD |
| Secret Manager (tres secretos) | < $1 USD |
| **Total** | **≈ $13–16 USD/mes**, dentro del techo de $45 |

La primera alerta (22.50) es el aviso de que algo se salió de esta tabla, no un umbral que se espere alcanzar.

---

## 11. Discrepancias entre el «Estado» de las guías y el repositorio

> Todas se corrigen en la Fase 7. Aquí quedan enunciadas con su evidencia.

| ID | Discrepancia | Evidencia | Manda |
|---|---|---|---|
| **D-1** | **US-M01 no existe en `context/planeacion_proyecto.md`**, que la raíz declara «única fuente de verdad de las User Stories». `grep -rn "M01"` sobre el plan no devuelve nada | `grep` sin coincidencias, 18-ago-2026 | **El enunciado del usuario.** Fase 7: añadir la US al plan con su alcance real, o declarar por escrito que S5 se ejecuta fuera del documento |
| **D-2** | La skill `portal-terraform-gcp` nombra los servicios `portal-backend` y `portal-frontend`, y da por hecho un bucket de exports con IAM propia | Cuerpo de la skill | **La US**: los servicios son `karisma-api` y `karisma-web`, y **no hay bucket** en esta entrega. Fase 7: actualizar la skill con los nombres reales y marcar el bucket como diferido |
| **D-3** | `portal-finops` fija la alerta al 50 % y su ejemplo usa umbrales 0.5 / 0.9 / 1.0 | Cuerpo de la skill | **La US**: 22.50 / 36 / 45 = 0.5 / **0.8** / 1.0. Fase 7: corregir el ejemplo |
| **D-4** | **Ninguna guía declara que los datos sintéticos no entran a la imagen del backend.** `data/silos/` está en `.gitignore` y `backend/Dockerfile` solo copia `app`; en Compose el bind mount lo tapaba | `.gitignore:116`, `backend/Dockerfile`, `docker-compose.yml` | **El repositorio.** Fase 7: escribirlo en `backend/AGENTS.md` (Estado) y en `data/README.md` si procede — la imagen de producción lleva los Parquet dentro, y quien regenere los datos tiene que reconstruirla |
| **D-5** | La US enumera cinco APIs a habilitar; `billingbudgets.googleapis.com` falta y sin ella CA-9 no se puede ejecutar | §7.1 | **La necesidad técnica.** Se habilita y se anota; no altera ningún criterio |
| **D-6** | `backend/.env.example` dice que en producción los secretos «los inyecta Secret Manager (US-003)». US-003 es CI/CD y `.github/` no existe | `backend/.env.example`, `ls .github` falla | **El repositorio.** Fase 7: la referencia correcta es esta US |
| **D-7** | El comentario de `backend/Dockerfile` anticipa `gcloud run deploy karisma-api --source backend` | `backend/Dockerfile`, cabecera | **§2.6**: se despliega con `--image` sobre Artifact Registry `karisma`. Fase 7: corregir el comentario |

---

## 12. Checklist de cierre

**Antes de tocar la nube**
- [ ] `make check` limpio (lint + gitleaks + mapa de permisos)
- [ ] `make test` en verde, con los casos nuevos de §6.1 y §6.2
- [ ] `ADR-004` escrito con **las dos ramas** de CA-5b redactadas, ninguna marcada todavía
- [ ] `make dev` sigue levantando los tres servicios tras el cambio de `docker-compose.yml` y del Dockerfile (`target: runtime` explícito)
- [ ] `make data` ejecutado: `data/silos/` y `data/aggregates/` presentes antes de construir la imagen

**Recursos**
- [ ] CA-1: proyecto, número y facturación verificados por el propio script
- [ ] CA-6: repositorio `karisma` con la política de tres versiones aplicada
- [ ] CA-3 y CA-4: instancia con los ocho valores exactos; sin conector VPC
- [ ] CA-7: tres secretos, tres versiones, ningún valor en el argv
- [ ] CA-2: los cuatro valores de escalado en **ambos** servicios
- [ ] CA-8: seis migraciones aplicadas y `git diff --exit-code db/schema.sql` en cero
- [ ] Semillas del catálogo y del linaje aplicadas
- [ ] CA-5: 403 sin token, 200 con token, ningún `CORSMiddleware` en el árbol
- [ ] CA-5b: rama marcada en `ADR-004` **con la hora**
- [ ] CA-9: tres reglas de umbral listadas por `gcloud billing budgets list`

**Cierre**
- [ ] CA-10 y CA-11: `bash scripts/verificar_despliegue.sh` en verde
- [ ] `docs/manual-test/us-m01.md` con las **cuatro** sesiones recorridas a mano, **con fecha** y con lo que falló, si falló
- [ ] `docs/despliegue.md` con prerrequisitos, ejecución, reversión completa y costo observado
- [ ] Las dos URL escritas en el handoff
- [ ] Handoff a `cerrada`; discrepancias D-1 a D-7 corregidas en Fase 7
- [ ] `mem_save` de las tres decisiones que sobreviven a esta US: la cabecera `X-Serverless-Authorization`, los Parquet dentro de la imagen y el Auth Proxy como servicio de Compose
