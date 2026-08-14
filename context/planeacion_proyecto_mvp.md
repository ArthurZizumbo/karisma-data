# Plan de Construcción del MVP — Portal Centralizado de Datos Financieros (Karisma Data)

**Documento:** catálogo ejecutable de lo que falta para que el portal deje de ser un prototipo navegable y sea un **MVP operable**. Cada historia está redactada en formato completo (Como / quiero / para que + criterios + tareas + estimación) y numerada de forma contigua **en el orden en que hay que construirla**.

**Fecha:** viernes 14 de agosto de 2026.
**Mantenedor:** Arthur Zizumbo (Platform/Agent lead) — Equipo 8.

**Relación con el plan vigente.** Complementa [`context/planeacion_proyecto.md`](planeacion_proyecto.md) y **no altera ninguna decisión de alcance del curso**. Ese documento manda sobre rúbricas, entregables UX y calendario académico; su §26 mandó sobre la semana del 10 al 16 de agosto. Este documento manda sobre **la pista de construcción a partir del cierre de A4**: lo que §26.3 declaró *roadmap* y lo que §26.6 dejó fuera con nombre y razón es exactamente lo que aquí se numera, se estima y se ordena. Donde este plan contradiga a §11–§17 en un detalle de implementación, manda este; donde contradiga a §26 en alcance del curso, manda §26.

**Numeración.** `US-M01`…`US-M23`, contigua y en orden de ejecución. El prefijo `M` no es decorativo: `US-001`…`US-036` ya están tomadas y tienen handoff, plan y rama en el repositorio, así que reutilizar esos números rompería la trazabilidad de [`docs/us-handoff/`](../docs/us-handoff/). La columna **Deriva de** mantiene el vínculo con el catálogo original.

**Constante de estimación.** 2.4 h/SP del plan. El ritmo real observado en S4 fue **2.7 h/SP** (26 SP en ~70 h de una sola persona). Los totales se reportan en la banda de las dos cifras, no en la optimista.

---

## Línea base: qué existe hoy, para no volver a especificarlo

Las historias de abajo **no repiten** nada de esta lista. Verificado sobre el árbol al 14-ago-2026.

**Infraestructura y calidad.** `Makefile` con catorce objetivos reales, `docker-compose.yml`, Dockerfiles **multi-etapa** para backend y frontend, Poetry con `poetry.lock`, pnpm por Corepack con Node 22, `dbmate` operando, `db/schema.sql` versionado, `gitleaks`, `make check` y `make verificar` con nueve verificadores en `scripts/`. Los umbrales están configurados, no son honor system: `--cov-fail-under=70` en backend y `thresholds: 50` en frontend.

**Datos.** Tres silos con semilla fija `20260720`, 1 260 000 filas, esquemas crípticos heterogéneos, regla de normalización de clave de cliente ejecutable, 1 260 anomalías (0.100 %) documentadas en `data/README.md`, serie preagregada de 500 000 puntos con manifiesto y hashes.

**Base de datos.** `app_user`, `catalog_source`, `catalog_field`, `catalog_tribal_note`, `catalog_lineage_step`, `export_job`. Y dos cosas que ahorran trabajo futuro: `catalog_field` **ya tiene** la columna `embedding vector(768)` con índice HNSW y el `search_document` tsvector generado; `export_job` **ya tiene** `started_at`, `finished_at`, `row_count` y `byte_size`.

**Seguridad.** JWT HS256 con cookie `httpOnly` puesta por el proxy de Nitro, Argon2 vía pwdlib, `Scope` como orden total en `backend/app/core/scopes.py`, registro de permisos que **falla cerrado** si un endpoint olvida declarar su scope, matriz publicada en `docs/security.md`, mapa de permisos de la interfaz generado por `make permisos-ui`.

**Backend.** Ocho routers montados: health, auth, catalog, lineage, metrics, users, chat, export. Búsqueda de catálogo por palabra clave, linaje del dato, serie preagregada en marco binario con ETag, exportación en segundo plano con enlace firmado y caducidad, y **transporte SSE completo**: contrato v1 congelado con cuatro eventos tipados, cancelación real verificada, registro de streams vivos y techo declarado con 429.

**Las dos costuras que abaratan lo que sigue.** `chat_provider: Literal["guionizado", "gemini"]` ya está declarado en la configuración y `_FABRICAS` en `backend/app/services/proveedores/__init__.py` resuelve el proveedor por nombre sin que el transporte lo importe. `export_storage_backend: Literal["local", "gcs"]` ya existe y `backend/app/services/almacen/gcs.py` está **escrito y dormido**.

**Frontend.** Diez rutas, sistema de diseño con fuente única y ruta `/guia`, i18n real bilingüe, espacios por rol, tablero de 500 K con medidor de fluidez, tarjetas predictivas con etiqueta de método, tarjetas de tool call con sus cuatro estados, overlay de linaje con foco atrapado, panel de administración, guarda de sesión que decide en el servidor. El store `workspace` **ya calcula** `contextoAgente`.

**Lo que no existe.** `infra/`, `.github/`, `ml/agent/`, `ml/semantic/`, `ml/data/extractors.py`, `ml/eda/`, ninguna dependencia de OpenTelemetry, ninguna de Google ADK ni de Gemini, ningún servicio desplegado.

---

## Resumen: las 23 historias, su orden y su costo

| # | Historia | SP | Depende de | Deriva de |
|---|----------|----|------------|-----------|
| **Bloque 1 — Salir del laboratorio (5.5 SP)** | | | | |
| US-M01 | Despliegue puente en GCP con base administrada | 1.5 | — | US-003 |
| US-M02 | Almacén real de exportaciones en GCS | 1 | M01 | US-009 |
| US-M03 | Pipeline CI/CD con GitHub Actions | 2 | M01 | US-004 |
| US-M04 | Observabilidad base con OpenTelemetry | 1 | M01 | US-005 |
| **Bloque 2 — El motor de datos (7 SP)** | | | | |
| US-M05 | Conectores asíncronos con caché y degradación | 1 | — | US-007 |
| US-M06 | Silos al volumen declarado | 1 | M05 | US-006 |
| US-M07 | Capa semántica: consulta validada y compilador | 3 | M05 | US-011 |
| US-M08 | Routers de dominio y consultas de referencia | 2 | M07 | US-011 |
| **Bloque 3 — El agente real (9 SP)** | | | | |
| US-M09 | Suite de tools gobernadas | 2 | M08 | US-021 |
| US-M10 | Agente orquestador con Google ADK | 4 | M09 | US-020 |
| US-M11 | Proveedor Gemini detrás del contrato SSE v1 | 1.5 | M10 | US-023 |
| US-M12 | Privacidad de trazas: hash de prompts | 1 | M04, M11 | US-031 |
| US-M13 | Reintento contextual en el stream | 0.5 | M11 | US-024 |
| **Bloque 4 — Gobierno completo (4.75 SP)** | | | | |
| US-M14 | CRUD completo de usuarios (backend) | 0.75 | — | US-018 |
| US-M15 | Alta y edición en el panel de administración | 0.5 | M14 | US-019 |
| US-M16 | Búsqueda híbrida con pgvector | 3 | — | US-012 |
| US-M17 | Procedencia copiable en el catálogo | 0.5 | M07 | US-008 |
| **Bloque 5 — Cierre de patrones UX (1.5 SP)** | | | | |
| US-M18 | Estado compartido vivo tablero-chat | 1 | M10 | US-029 |
| US-M19 | Serie de un millón de puntos | 0.5 | M06 | US-025 |
| **Bloque 6 — Producción medible (7 SP)** | | | | |
| US-M20 | FinOps: spans del LLM y consumo de tokens | 2.5 | M04, M11 | US-030 |
| US-M21 | Tablero de consumo y costo | 1.5 | M20 | US-032 |
| US-M22 | Smoke post-deploy y cobertura de cierre | 1 | M03, M11 | US-033 |
| US-M23 | Pase a producción: TTFT p50, P90 y cold starts | 2 | M22 | US-034 |
| | **Total** | **34.75** | | |

**Camino crítico:** M05 → M07 → M08 → M09 → M10 → M11 → M20 → M21. Son 17.5 SP encadenados que no se pueden paralelizar. Todo lo demás —M01 a M04, M14 a M17, M19— corre en paralelo sin tocar el mismo write-set.

**Por qué este orden.** Primero la infraestructura, porque medir en local lo que va a correr en Cloud Run mide otra cosa, y porque la URL pública ya está bloqueando el reclutamiento de A5. Después el motor de datos, porque el agente no puede envolver endpoints que no existen: la capa semántica es el prerrequisito duro de las tools y las tools lo son del agente. Después el gobierno y los patrones que quedaron a medias, que son baratos y no bloquean a nadie. Al final la medición, porque no se puede instrumentar lo que todavía no responde.

---

## Bloque 1 — Salir del laboratorio

### US-M01 — Despliegue puente en GCP con base administrada

**Como** equipo de plataforma,
- **quiero** los dos servicios del portal corriendo en Cloud Run contra una base administrada, con los secretos fuera del repositorio,
- **para que** exista una dirección pública sobre la cual probar, medir y reclutar participantes, y para que todo lo que se construya después se verifique donde de verdad va a correr.

**Criterios de Aceptación:**

- **Ningún identificador de la cuenta se escribe en el repositorio.** El proyecto, su número y la cuenta de facturación viven en `.env.local` como `GCP_PROJECT_ID`, `GCP_PROJECT_NUMBER` y `GCP_BILLING_ACCOUNT`, y los scripts los leen de ahí. El repositorio es público: en documentación y en código se citan por su variable, nunca por su valor.
- Se despliega en el proyecto **con facturación activa** del equipo, región **`us-central1`**. El segundo proyecto, sin facturación, no se usa y no recibe recursos.
- **Dos servicios Cloud Run**, `karisma-api` y `karisma-web`, con `min-instances 0`, `max-instances 3`, 512 MiB y concurrencia 80.
- **Cloud SQL `karisma-pg`**: PostgreSQL 15, edición Enterprise, `db-f1-micro`, zonal, 10 GB HDD sin crecimiento automático, sin respaldos, conectada desde Cloud Run con `--add-cloudsql-instances` y **sin conector de acceso VPC serverless**, que costaría más que la propia base.
- **El navegador solo habla con el frontend**: las rutas `/api/**` se proxyean desde Nitro, `karisma-api` se despliega con `--no-allow-unauthenticated`, no hay CORS y la cookie `httpOnly` sigue siendo del mismo sitio. **Salida declarada** si el cierre por IAM excede 45 minutos: backend público con JWT obligatorio en todo endpoint de datos, escrito como decisión y no insinuado.
- Artifact Registry `karisma` con política de limpieza a tres etiquetas. Secret Manager con `DATABASE_URL`, `JWT_SECRET_KEY` y `GEMINI_API_KEY` inyectados al servicio, nunca como variables en claro del comando de despliegue.
- **`DEMO_LOGIN_ENABLED` va encendido, y por eso el despliegue no puede tocar datos reales.** `POST /api/auth/demo` emite un token sin credenciales para el usuario canónico de cada rol: es lo que US-015 comprometió como selector de perfil de demostración y lo que permite que un evaluador de A5 entre sin que le pasemos una contraseña. La decisión se mantiene. Su condición, que es lo que sí hay que sostener: **mientras esa puerta esté abierta, la base solo contiene silos sintéticos de semilla fija**, y la franja de alcance que declara el prototipo sigue visible en todas las rutas.
- **La condición se verifica, no se supone.** El día que el portal sirva un dato que no venga de `make data`, `DEMO_LOGIN_ENABLED` pasa a `false` **en el mismo cambio**, y se comprueba con `POST /api/auth/demo` devolviendo 404 y sin entrada en `/openapi.json`. No es una tarea posterior: es parte del cambio que introduce el dato real.
- `dbmate up` ejecutado contra Cloud SQL y `db/schema.sql` **sin diferencias** después del despliegue.
- **Tres alertas de presupuesto**: 22.50, 36 y 45 USD.
- Los siete usuarios sembrados entran por la URL pública y cada rol ve su espacio. Verificación manual de los cuatro roles registrada con fecha.

**Tareas técnicas:**

- [ ] Habilitar `run`, `sqladmin`, `artifactregistry`, `secretmanager`, `cloudbuild`
- [ ] Artifact Registry con política de limpieza
- [ ] Cloud SQL `karisma-pg` con los flags de arriba
- [ ] Secretos en Secret Manager y su enlace a los dos servicios
- [ ] `scripts/desplegar.sh` que reproduce el despliegue completo sin pasos manuales no escritos, leyendo los identificadores de `.env.local` y fallando si falta alguno
- [ ] Regla de `gitleaks` para el patrón de cuenta de facturación de GCP (`[0-9A-F]{6}-[0-9A-F]{6}-[0-9A-F]{6}`), para que el gate lo atrape en vez de la revisión humana
- [ ] Migraciones contra Cloud SQL y verificación de `schema.sql`
- [ ] Tres alertas de presupuesto
- [ ] Recorrido manual de los cuatro roles sobre la URL

**Estimación:** 1.5 puntos. **Depende de:** nada. **Deriva de:** US-003 (§26 lo dejó en estado *planning*; el gate del mar 11 quedó vencido).

---

### US-M02 — Almacén real de exportaciones en GCS

**Como** analista que pidió una extracción,
- **quiero** que el archivo exista fuera del contenedor y que su enlace caduque solo,
- **para que** una exportación sobreviva al reinicio del servicio y ningún archivo quede accesible para siempre.

**Criterios de Aceptación:**

- `EXPORT_STORAGE_BACKEND=gcs` en el servicio desplegado y `poetry install --extras gcs` en la imagen. El backend local sigue siendo el de desarrollo: **la fachada no se toca**, y si el diff modifica `backend/app/services/export_service.py` es que la fachada no era tal y hay que decir por qué.
- Bucket `karisma-exports` en `us-central1`, con acceso uniforme a nivel de bucket y acceso público bloqueado.
- **Política de ciclo de vida a 7 días** sobre el prefijo `exports/`, verificada leyendo la configuración del bucket y no de memoria.
- La URL firmada sigue caducando a las 24 h (`export_link_ttl_hours`, ya existente). Una URL vencida devuelve el rechazo del propio GCS y la interfaz muestra el estado de caducado que ya está construido.
- La cuenta de servicio de `karisma-api` firma URLs **sin llave privada en el repositorio** (IAM `signBlob`).
- **Auditoría de duración** sobre las columnas que el esquema ya tiene —`started_at`, `finished_at`, `row_count`, `byte_size`—: no se añade ninguna columna ni ninguna migración.
- **Prueba de no bloqueo con volumen real**: durante una exportación del silo completo, `GET /api/catalog/search` responde por debajo de 500 ms en el p95 de veinte llamadas.

**Tareas técnicas:**

- [ ] Bucket con acceso uniforme y política de ciclo de vida
- [ ] Permiso `signBlob` a la cuenta de servicio y verificación de firma sin llave local
- [ ] Extra `gcs` en la imagen y variable en el servicio
- [ ] Consulta de auditoría de duración sobre `export_job`
- [ ] Prueba de concurrencia exportación contra consulta

**Estimación:** 1 punto. **Depende de:** US-M01. **Deriva de:** US-009 — deroga el recorte #3.

---

### US-M03 — Pipeline CI/CD con GitHub Actions

**Como** equipo,
- **quiero** que cada push valide y que cada merge a `main` despliegue,
- **para que** el estado del repositorio y el de la URL pública no puedan divergir en silencio.

**Criterios de Aceptación:**

- `.github/workflows/ci.yml` con matriz backend y frontend, caché de lockfiles, y **exactamente lo que `make check` y `make test` corren hoy**: ruff, mypy, eslint, typecheck, gitleaks, mapa de permisos, pytest con `--cov-fail-under=70` y vitest con `thresholds: 50`. Un umbral relajado en la CI y no en el repositorio es fallo de la propia CI.
- `.github/workflows/deploy.yml` con el orden **build → push a Artifact Registry → `dbmate up` → deploy de los dos servicios**. Si la migración falla, no se despliega nada.
- Autenticación con **Workload Identity Federation**: ninguna llave de cuenta de servicio como secreto del repositorio.
- Los tres secretos de entorno viven en GitHub Environments, nunca en el árbol.
- El pipeline corre **en verde** sobre la rama vigente antes de considerar cerrada la historia. Un workflow escrito y nunca ejecutado no cierra.

**Tareas técnicas:**

- [ ] `ci.yml` con la matriz y los mismos umbrales del repositorio
- [ ] `deploy.yml` con migración antes del despliegue
- [ ] Workload Identity Federation y su vinculación al repositorio
- [ ] Environments y secretos
- [ ] Corrida verde registrada

**Estimación:** 2 puntos. **Depende de:** US-M01. **Deriva de:** US-004.

---

### US-M04 — Observabilidad base con OpenTelemetry

**Como** ingeniero de plataforma,
- **quiero** que cada petición HTTP sea una traza con sus spans de lectura de datos,
- **para que** cuando el agente exista solo haya que colgar los spans del modelo de una instrumentación ya probada.

**Criterios de Aceptación:**

- SDK inicializado dentro de `create_app`, instrumentación automática de FastAPI y exportador elegido por `app_env`: consola en local, Cloud Trace en el servicio desplegado.
- Span hijo **`db.retrieval`** en toda lectura de parquet —`series_service` hoy, el extractor de US-M05 mañana— con atributos de silo, filas leídas y milisegundos.
- **La traza no contiene el mensaje del usuario ni credencial alguna.** Prueba que recorre los atributos emitidos y falla si aparece cualquiera de los dos.
- El contexto se propaga a través del threadpool: un span abierto en el hilo de Polars cuelga de la petición que lo originó y no queda huérfano.
- **El arranque no depende del exportador**: si Cloud Trace no responde, la API sigue sirviendo y lo registra. La observabilidad no es una dependencia dura del servicio.

**Tareas técnicas:**

- [ ] Dependencias de OpenTelemetry y su inicialización en `create_app`
- [ ] Selección de exportador por entorno
- [ ] Decorador o gestor de contexto para `db.retrieval`
- [ ] Verificación de propagación a través del threadpool
- [ ] Prueba de ausencia de contenido sensible en atributos

**Estimación:** 1 punto. **Depende de:** US-M01 para el exportador de nube; la parte local no depende de nada. **Deriva de:** US-005.

---

## Bloque 2 — El motor de datos

### US-M05 — Conectores asíncronos con caché y degradación

**Como** analista,
- **quiero** que leer un silo no bloquee al resto del portal y que un silo caído no tumbe a los demás,
- **para que** una lectura pesada deje de ser una caída general.

**Criterios de Aceptación:**

- `ml/data/extractors.py` con funciones `async def` que delegan la lectura de Polars a un threadpool. **Ninguna corrutina bloquea el event loop**, verificado con una prueba que mide la latencia de una petición concurrente mientras corre una lectura larga.
- Caché en memoria con **TTL configurable** y clave por silo y consulta normalizada; los aciertos y fallos quedan en el log estructurado.
- **Excepciones propias por silo** (`SiloNoDisponible`, `SiloCorrupto`) y degradación elegante: si derivados falla, créditos y liquidez siguen respondiendo y la respuesta **declara el silo ausente** en lugar de fallar entera.
- Pruebas `pytest-asyncio` de los cinco caminos: éxito, silo caído, acierto de caché, caché expirado y degradación parcial.
- El endpoint de series existente migra a este extractor **sin cambiar su contrato de respuesta ni su ETag**. Las pruebas actuales de `series_service` corren sin modificarse.

**Tareas técnicas:**

- [ ] `ml/data/extractors.py` con lectura async y caché TTL
- [ ] Jerarquía de excepciones por silo
- [ ] Degradación parcial en la respuesta
- [ ] Pruebas asíncronas de los cinco caminos
- [ ] Migración de `series_service` al extractor

**Estimación:** 1 punto. **Depende de:** nada. **Deriva de:** US-007.

---

### US-M06 — Silos al volumen declarado

**Como** evaluador del sistema,
- **quiero** que las mediciones de rendimiento se hagan sobre el volumen que el proyecto declaró,
- **para que** las cifras del MVP no salgan de un recorte del 81 % presentado como si fuera el tamaño real.

**Criterios de Aceptación:**

- `creditos` entre 1 y 5 M de filas, `liquidez` cerca de 1 M, `derivados` cerca de 500 K, con la **misma semilla `20260720`** y la misma regla de normalización de clave de cliente. `data/README.md` actualizado con el manifiesto nuevo y sus hashes.
- La proporción de anomalías sigue siendo **0.100 %** y ninguna cae sobre la espina de la serie preagregada, por la razón que el propio README ya documenta.
- `make data` reproduce byte a byte en dos máquinas distintas y `make verificar` sigue en verde.
- **El repositorio no crece**: los parquet siguen fuera de git y lo versionado es el manifiesto con hashes.
- Tiempo de generación medido y documentado. Si supera diez minutos se declara y se deja un perfil reducido de desarrollo (`DATA_PROFILE=dev`) que produce el recorte actual, para que nadie tenga que regenerar millones de filas para correr una prueba.

**Tareas técnicas:**

- [ ] Parametrizar volúmenes en `ml/data/schemas.py` conservando la semilla
- [ ] Perfil `dev` y perfil completo
- [ ] Regenerar manifiesto y hashes
- [ ] Reescribir la sección de volúmenes de `data/README.md`
- [ ] Verificar reproducibilidad en dos máquinas

**Estimación:** 1 punto. **Depende de:** US-M05 (conviene tener el extractor antes de multiplicar por cinco el volumen). **Deriva de:** US-006 — cierra el recorte de §26.

---

### US-M07 — Capa semántica: consulta validada y compilador determinístico

**Como** analista y como agente conversacional,
- **quiero** componer consultas por métrica, dimensiones, filtros y rango temporal, validadas contra el catálogo y traducidas por un compilador determinístico,
- **para que** ninguna consulta, ni la mía ni la del modelo, se convierta en código libre sobre los datos.

**Criterios de Aceptación:**

- Modelo Pydantic `SemanticQuery` con `metric`, `dimensions`, `filters`, `time_range`, `order` y `limit`. **Ningún campo admite expresiones, SQL ni fragmentos de Polars.**
- Las métricas y dimensiones válidas se leen de `catalog_field`, que ya publica `metric_agg`, `unit`, `domain` y `certification`: **una métrica que no está certificada en el catálogo no compila**.
- `ml/semantic/compiler.py` traduce a expresiones **Polars lazy parametrizadas**. El compilador no interpola texto en ninguna expresión, y hay una prueba que le pasa nombres con comillas, punto y coma y guiones dobles y verifica que ni se ejecutan ni se filtran al resultado.
- Métrica inexistente devuelve **422 con código estable** en `detail.codigo` y sugerencia por coincidencia difusa contra el catálogo, sin prosa en el cuerpo: la interfaz es bilingüe y la copia es suya.
- El resultado incluye su **procedencia**: qué campos del catálogo y qué silos participaron.
- **Join cruzado créditos ⋈ derivados** por clave de cliente normalizada, resuelto en lazy sin materializar los dos silos completos.
- **Determinismo verificado**: la misma consulta sobre la misma semilla devuelve el mismo resultado byte a byte.

**Tareas técnicas:**

- [ ] `SemanticQuery` y sus validadores contra el catálogo
- [ ] `ml/semantic/compiler.py` con expresiones parametrizadas
- [ ] Sugerencia difusa y códigos de error estables
- [ ] Join cruzado por clave normalizada
- [ ] Pruebas de inyección, de determinismo y de métrica inexistente

**Estimación:** 3 puntos. **Depende de:** US-M05. **Deriva de:** US-011 (primera mitad).

---

### US-M08 — Routers de dominio y consultas de referencia

**Como** usuario del portal según mi rol,
- **quiero** endpoints por dominio que exijan mi permiso y respondan a la consulta que compuse,
- **para que** el portal deje de tener un solo endpoint de datos y el agente tenga una superficie gobernada que envolver.

**Criterios de Aceptación:**

- `/api/creditos`, `/api/liquidez` y `/api/derivados` montados con `Security(get_current_user, scopes=[...])` según la matriz de `docs/security.md`: consulta puntual `operativo`+, agregaciones y cruces `analista`+, resúmenes `directivo`+.
- El registro de permisos publica los tres routers y `make permisos-ui` regenera el mapa que la interfaz consume. **Un endpoint sin scope declarado sigue fallando cerrado**, que es el comportamiento que ya existe y no se debilita.
- **Diez consultas de referencia** del Anexo C con resultado esperado sobre la semilla fija, corriendo dentro de `make test`.
- La pantalla `/exploracion` consume estos endpoints en lugar de datos de ejemplo, conservando sus cuatro estados no felices del sistema de diseño.
- Matriz **401/403 parametrizada por rol** extendida a los tres routers, con la misma forma que la existente.

**Tareas técnicas:**

- [ ] Tres routers con dependencias de scope
- [ ] Alta en el registro de permisos y regeneración del mapa de la interfaz
- [ ] Suite de diez consultas de referencia
- [ ] Conexión de `/exploracion` a los endpoints reales
- [ ] Extensión de la matriz 401/403

**Estimación:** 2 puntos. **Depende de:** US-M07. **Deriva de:** US-011 (cierre) — deroga el recorte #2.

---

## Bloque 3 — El agente real

### US-M09 — Suite de tools gobernadas

**Como** ingeniero del agente,
- **quiero** cuatro funciones tipadas que envuelvan endpoints gobernados y propaguen el token del usuario,
- **para que** el agente jamás vea un dato que su usuario no podría pedir por sí mismo.

**Criterios de Aceptación:**

- Cuatro tools en `ml/agent/tools/`: `buscar_catalogo`, `consultar_metricas`, `solicitar_export` y `resumir_vista`. **Ninguna toca Polars ni la base directamente**: todas llaman al HTTP interno del portal.
- Cada tool **propaga el Bearer del usuario**. Una tool invocada con el token de un `operativo` contra una agregación devuelve 403 y el agente lo comunica en vez de inventar la cifra. Prueba por tool y por rol.
- Firmas con type hints y docstrings Google-style: **ADK deriva el esquema**, no se escribe a mano.
- El resultado de cada tool llega ya con la forma de `ResultadoTarjeta` del contrato SSE v1 —columnas como claves i18n, filas como datos crudos—, para que la tarjeta de tool call no necesite un traductor intermedio.
- Ninguna tool acepta texto libre que termine en una expresión: todas construyen un `SemanticQuery` validado.

**Tareas técnicas:**

- [ ] Cliente HTTP interno con propagación de credencial
- [ ] Las cuatro tools tipadas
- [ ] Conversión de resultado a `ResultadoTarjeta`
- [ ] Pruebas de contrato y de permiso por tool y por rol

**Estimación:** 2 puntos. **Depende de:** US-M08. **Deriva de:** US-021.

---

### US-M10 — Agente orquestador con Google ADK

**Como** perfil directivo,
- **quiero** preguntarle al portal en mi idioma y recibir una respuesta cuyas cifras vengan todas de una herramienta,
- **para que** el asistente sea auditable y no un generador de números plausibles.

**Criterios de Aceptación:**

- `LlmAgent` de Google ADK con `Runner` y `SessionService`, arquitectura **manager → workers**: el manager rutea entre catálogo, datos y fuera de dominio, y el rechazo fuera de dominio es cortés e inmediato.
- **Presupuesto duro de cinco tool calls** por consulta. Al sexto, el agente responde con lo que tiene y lo dice. Verificado por una prueba que cuenta invocaciones.
- `thinking_level: "medium"` por omisión; `"high"` solo a petición explícita de un analista.
- **Regla anti-alucinación verificable**: una prueba corre las nueve familias del Anexo C y **falla si el texto contiene una cifra que no aparece en ningún resultado de tool de ese mismo turno**. Sin esta prueba la regla es una intención.
- Cada respuesta **cita la fuente del catálogo** de la que salió el dato.
- La sesión del agente se ata a la sesión del portal: dos usuarios distintos nunca comparten historial, y el rol del usuario viaja con cada llamada.

**Tareas técnicas:**

- [ ] Manager y workers con sus instrucciones y su presupuesto de tools
- [ ] Integración de `SessionService` con la sesión del portal
- [ ] Citación de fuente del catálogo en la respuesta
- [ ] Prueba automática de la regla anti-alucinación
- [ ] Corrida de las nueve familias del Anexo C con revisión manual registrada

**Estimación:** 4 puntos. **Depende de:** US-M09. **Deriva de:** US-020.

---

### US-M11 — Proveedor Gemini detrás del contrato SSE v1

**Como** usuario del asistente,
- **quiero** que lo que se forma en pantalla venga de un modelo real,
- **para que** el transporte que ya funciona deje de transportar un guion.

**Criterios de Aceptación:**

- `backend/app/services/proveedores/gemini.py` implementa `ProveedorDeTokens` y se registra en `_FABRICAS`. `CHAT_PROVIDER=gemini` pasa a ser un valor servible. **Ninguna otra línea del transporte cambia**: si el diff toca `chat_stream.py`, la costura no era tal y hay que declarar por qué.
- El orden del **contrato SSE v1** se respeta sin excepción: `tool_call` antes de esperar datos, `token` incremental, `done` único y último. Las pruebas de contrato existentes corren **sin modificarse**.
- La cancelación real que ya está probada sigue verde **y ahora cancela también la llamada al modelo**: se verifica que la petición a Gemini se aborta, no solo que el generador termina.
- **Ninguna cadena visible se escribe en el proveedor.** Los mensajes de error siguen siendo claves i18n del patrón congelado, incluidas las que se emitan a partir de una falla del modelo.
- TTFT medido sobre el proveedor real y escrito en el registro de cierre, como ya hace el transporte.
- Con `GEMINI_API_KEY` ausente la aplicación no arranca, que es la regla vigente. Con la clave inválida, el turno falla como **error tipado de `generacion_de_texto`**, nunca como 500.

**Tareas técnicas:**

- [ ] Proveedor Gemini contra el protocolo existente y su alta en `_FABRICAS`
- [ ] Puente entre los eventos del agente ADK y los cuatro eventos del contrato
- [ ] Cancelación propagada hasta la llamada al modelo
- [ ] Claves i18n de las fallas nuevas
- [ ] Corrida de las pruebas de contrato sin tocarlas

**Estimación:** 1.5 puntos. **Depende de:** US-M10. **Deriva de:** US-023 — cierra el go/no-go que S4 resolvió como guionizado.

---

### US-M12 — Privacidad de trazas: hash de prompts

**Como** responsable de gobernanza del dato,
- **quiero** que ni el prompt ni la respuesta crudos existan fuera del proceso,
- **para que** la observabilidad no se convierta en la fuga que el resto del portal evita.

**Criterios de Aceptación:**

- `llm.prompt_hash` (SHA-256) calculado en el **único punto de salida** hacia Gemini. El contenido crudo no se escribe en spans, ni en logs, ni en la base.
- Prueba que captura los registros de una conversación completa —incluida una cancelada y una fallida— y **falla si aparece cualquier fragmento del mensaje del usuario**.
- El mismo prompt produce el mismo hash, de modo que dos trazas del mismo turno se correlacionan sin revelar el texto.
- La regla queda escrita en `docs/security.md`, junto a la matriz de permisos que ya vive ahí.

**Tareas técnicas:**

- [ ] Hash en el punto único de salida al modelo
- [ ] Atributo en el span y en el registro de cierre
- [ ] Prueba de ausencia de contenido crudo en los tres caminos
- [ ] Sección en `docs/security.md`

**Estimación:** 1 punto. **Depende de:** US-M04 y US-M11. **Deriva de:** US-031.

---

### US-M13 — Reintento contextual en el stream

**Como** usuario del asistente,
- **quiero** volver a intentar el turno que falló sin perder la conversación,
- **para que** un fallo transitorio no me cueste el hilo de lo que estaba analizando.

**Criterios de Aceptación:**

- El aviso de **error recuperable** ofrece Reintentar; el de **permiso** (403) no lo ofrece. Esa diferencia ya viaja tipada en el evento y no se vuelve a modelar.
- Reintentar reenvía el mismo turno, **conserva el historial** y no duplica la tarjeta de tool call del intento fallido.
- Un fallo inyectado en una tool produce el error tipado, y el reintento con la tool sana completa el turno. Prueba de los dos pasos.
- El **recorte #4 queda derogado aquí**, con fecha y razón escritas. No se deroga en silencio.

**Tareas técnicas:**

- [ ] Acción de reintento en el composable del stream
- [ ] Reconciliación de tarjetas del intento fallido
- [ ] Prueba de fallo inyectado y reintento exitoso
- [ ] Nota de derogación del recorte #4

**Estimación:** 0.5 puntos. **Depende de:** US-M11. **Deriva de:** US-024 (cierre).

---

## Bloque 4 — Gobierno completo

### US-M14 — CRUD completo de usuarios (backend)

**Como** administradora de la plataforma,
- **quiero** dar de alta y editar usuarios, además de cambiar su rol y desactivarlos,
- **para que** el gobierno del acceso no dependa de escribir en la base a mano.

**Criterios de Aceptación:**

- `POST /api/users` con contraseña temporal hasheada con Argon2 y rol; `GET /api/users/{id}`; `PATCH /api/users/{id}` para nombre, correo, rol y contraseña. **El listado y el borrado lógico ya existen y no se reescriben.**
- `username` y `email` únicos: **409 con código estable**, sin prosa en el cuerpo.
- Un administrador **no puede degradarse ni desactivarse a sí mismo**; la protección que ya está cerrada por los dos lados se extiende al `PATCH` de rol.
- `hashed_password` no aparece nunca en una respuesta ni en un registro. Prueba que lo verifica sobre el cuerpo ya serializado, no sobre el modelo.
- Un cambio de rol o una desactivación **surten efecto en la siguiente petición** del afectado.

**Tareas técnicas:**

- [ ] Esquemas `UserCreate` y `UserUpdate`
- [ ] Los tres endpoints nuevos con scope `admin`
- [ ] Conflictos 409 y reglas de negocio
- [ ] Pruebas de CRUD, de autoprotección y de fuga de hash

**Estimación:** 0.75 puntos. **Depende de:** nada. **Deriva de:** US-018 — cierra la degradación del recorte #5.

---

### US-M15 — Alta y edición en el panel de administración

**Como** administradora de la plataforma,
- **quiero** hacer las altas y las ediciones desde la pantalla,
- **para que** la degradación acordada en S4 deje de ser el producto.

**Criterios de Aceptación:**

- Formularios de alta y de edición en `/administracion`, con las mismas reglas del backend y **sin duplicar su validación** en el cliente: el servidor decide y la interfaz muestra.
- El 409 y las validaciones se muestran como copia bilingüe resuelta por i18n. **Ninguna cadena visible se escribe en el componente**, según ADR-001.
- Los estados de carga, vacío y error son los del sistema de diseño ya construido, no unos nuevos.
- La contraseña temporal se muestra **una sola vez**, no se guarda en el estado del cliente y no se registra en ninguna parte.

**Tareas técnicas:**

- [ ] Formulario de alta con contraseña temporal de un solo uso visual
- [ ] Formulario de edición
- [ ] Claves i18n de las dos locales
- [ ] Pruebas de componente de los dos formularios

**Estimación:** 0.5 puntos. **Depende de:** US-M14. **Deriva de:** US-019.

---

### US-M16 — Búsqueda híbrida con pgvector

**Como** perfil operativo,
- **quiero** encontrar el dato aunque yo lo llame distinto a como lo llama el sistema de origen,
- **para que** el catálogo responda a mi vocabulario y no al del silo.

**Criterios de Aceptación:**

- Job de embeddings que llena `catalog_field.embedding` con el modelo de embeddings de Gemini. **La columna `vector(768)` y su índice HNSW ya existen en el esquema: no se añade migración.**
- **Score híbrido** que combina la coincidencia tsvector ya existente con la similitud coseno, con los pesos escritos en un solo sitio, justificados y probados.
- `GET /api/catalog/search` **conserva su contrato**: mismos campos de respuesta, mismo comportamiento de facetas. Las pruebas existentes del endpoint corren sin modificarse.
- Set de **veinte consultas de negocio** con fuente esperada, y **Hit Rate@3 ≥ 0.8** medido y reportado. Si no llega, se publica la cifra obtenida y se declara.
- **Degradación explícita**: si falta el embedding de un campo o el servicio de embeddings no responde, la búsqueda cae a palabra clave y lo registra. Nunca deja de responder.

**Tareas técnicas:**

- [ ] Job de embeddings con reintentos y control de cuota
- [ ] Score híbrido y ranking en el servicio del catálogo
- [ ] Set de veinte consultas y medición de Hit Rate@3
- [ ] Camino de degradación a palabra clave y su prueba

**Estimación:** 3 puntos. **Depende de:** nada duro. **Deriva de:** US-012 — deroga el recorte #1.

---

### US-M17 — Procedencia copiable en el catálogo

**Como** analista que pega una cifra en un correo,
- **quiero** que el valor viaje con su fuente, su fecha y su definición,
- **para que** copiar deje de perder el contexto que hace defendible el número.

**Criterios de Aceptación:**

- La respuesta del catálogo y la de la capa semántica incluyen un **bloque de procedencia listo para pegar**: valor, fuente, propietario, fecha de vigencia y definición.
- La tarjeta de resultado ofrece **copiar con procedencia** como acción distinta de copiar el valor solo. Las dos existen; la de procedencia es la que está por omisión.
- Métrica del principio "Respaldado" medible sobre el propio endpoint: proporción de respuestas que llevan procedencia completa.
- Cubre la etapa 6 del journey de equipo de A2, que es **la única de las capacidades prometidas en A2 que quedó sin implementación**.

**Tareas técnicas:**

- [ ] Bloque de procedencia en la respuesta del catálogo
- [ ] Mismo bloque en el resultado de la capa semántica
- [ ] Acción de copiado con procedencia en la interfaz
- [ ] Prueba de composición del bloque

**Estimación:** 0.5 puntos. **Depende de:** US-M07 para el lado de la capa semántica. **Deriva de:** US-008 — cierra el compromiso de A2.

---

## Bloque 5 — Cierre de patrones UX

### US-M18 — Estado compartido vivo tablero-chat

**Como** usuario que ya filtró el tablero,
- **quiero** preguntarle al asistente sobre lo que estoy viendo sin volver a describírselo,
- **para que** el análisis no se reinicie cada vez que cambio de panel.

**Criterios de Aceptación:**

- El `contextoAgente` que el store `workspace` **ya calcula** viaja en la petición de chat como **contexto estructurado**, no como texto pegado en el prompt.
- Acción **"Resumir vista actual"** desde el tablero directivo: abre el asistente con el contexto ya cargado y la pregunta compuesta.
- El overlay de linaje ya construido se abre **desde una respuesta del agente**, y no solo desde un campo del catálogo: expandir la respuesta muestra qué tools se llamaron, con qué parámetros y de qué fuentes salieron los datos.
- **La mutación bidireccional plena sigue fuera** (el agente no reescribe los filtros del tablero): era STRETCH de +3 SP en el catálogo original y se mantiene declarada como tal. Lo que entra es el contexto vivo y el disparo desde el tablero.

**Tareas técnicas:**

- [ ] Contexto estructurado en la petición de chat
- [ ] Acción "Resumir vista actual" en el tablero directivo
- [ ] Apertura del overlay de linaje desde una respuesta
- [ ] Pruebas de serialización del contexto y de la acción

**Estimación:** 1 punto. **Depende de:** US-M10. **Deriva de:** US-029 — deroga el recorte #12 en su parte de payload estático.

---

### US-M19 — Serie de un millón de puntos

**Como** analista,
- **quiero** recorrer la serie completa sin muestreo previo,
- **para que** la degradación declarada en A4 deje de ser necesaria.

**Criterios de Aceptación:**

- Serie de **al menos 1 000 000 de puntos** servida por el endpoint existente, con el mismo marco binario y el mismo comportamiento de ETag.
- **Pan y zoom sin saltos perceptibles**, medidos con el medidor de fluidez ya construido, con la cifra registrada y fechada.
- Si la medición no pasa, se conserva 500 K **y se declara**: una degradación es legítima cuando está medida, no cuando está supuesta.
- La tabla alternativa y el resumen textual siguen cubriendo la serie completa, no una muestra.

**Tareas técnicas:**

- [ ] Preagregado de un millón de puntos sobre el volumen de US-M06
- [ ] Verificación del marco binario y del ETag con la nueva cardinalidad
- [ ] Medición de fluidez registrada
- [ ] Actualización de la declaración de alcance

**Estimación:** 0.5 puntos. **Depende de:** US-M06. **Deriva de:** US-025 (cierre).

---

## Bloque 6 — Producción medible

### US-M20 — FinOps: spans del LLM y consumo de tokens

**Como** líder de plataforma,
- **quiero** saber cuántos tokens costó cada respuesta y dónde se fue el tiempo,
- **para que** el presupuesto de 45 USD al mes sea una medición y no una esperanza.

**Criterios de Aceptación:**

- Sub-spans por petición de chat colgando de la traza de US-M04: **`rag.retrieval`**, **`llm.call`** y **`llm.postprocess`**, que es lo que permite aislar el cuello de botella real.
- `llm.call` lleva `llm.usage.prompt_tokens`, `llm.usage.completion_tokens`, `llm.usage.total_tokens`, `llm.model` y `llm.tool_calls.count`.
- **TTFT registrado como atributo** por petición de streaming, que es la fuente de la métrica de US-M23.
- Los atributos existen **también cuando el turno se cancela** a media respuesta: una cancelación ya consumió tokens de entrada y contarla como cero falsea el costo hacia abajo.

**Tareas técnicas:**

- [ ] Sub-spans del pipeline del agente
- [ ] Atributos de consumo en `llm.call`
- [ ] TTFT como atributo por petición
- [ ] Prueba de que la cancelación también reporta consumo

**Estimación:** 2.5 puntos. **Depende de:** US-M04 y US-M11. **Deriva de:** US-030.

---

### US-M21 — Tablero de consumo y costo

**Como** equipo,
- **quiero** ver tokens y costo por día,
- **para que** la cifra de FinOps sea citable y no reconstruida a mano la noche de la entrega.

**Criterios de Aceptación:**

- Tablero con **tokens por día, costo estimado por día y p50/p95 de `llm.call`**, alimentado por los atributos de US-M20.
- El costo se calcula con el precio vigente de Gemini 3.5 Flash-Lite **declarado en un solo sitio y fechado**, para que revisarlo sea cambiar una línea.
- Cifras exportables como evidencia para el informe y para §23 del plan.
- La alerta de presupuesto al 50 % de US-M01 se **contrasta al menos una vez** contra esta medición: dos fuentes que nunca se comparan no son dos fuentes, son dos suposiciones.

**Tareas técnicas:**

- [ ] Consulta de métricas hacia el tablero
- [ ] Precio declarado y fechado en un único módulo
- [ ] Exportación de cifras
- [ ] Contraste contra la alerta de presupuesto

**Estimación:** 1.5 puntos. **Depende de:** US-M20. **Deriva de:** US-032.

---

### US-M22 — Smoke post-deploy y cobertura de cierre

**Como** equipo,
- **quiero** que el pipeline pruebe el sistema desplegado y no solo el código,
- **para que** un despliegue en verde signifique que el portal responde.

**Criterios de Aceptación:**

- **Smoke post-deploy contra la URL pública**: acceso, búsqueda de catálogo, consulta semántica, chat con tool call y exportación. Corre en `deploy.yml` **después** del despliegue y pone el job en rojo si falla.
- Cobertura de backend **sostenida en ≥ 70 %** con los módulos nuevos dentro: compilador, extractores, tools y proveedor. Subir el umbral es opcional; bajarlo para que pase, no.
- Componentes críticos nuevos del frontend con prueba: los del asistente conectados al proveedor real y los formularios de administración.
- Un fallo de smoke **deja registrado qué paso falló**, con el mismo vocabulario cerrado del contrato SSE donde aplique.

**Tareas técnicas:**

- [ ] Script de smoke contra la URL pública
- [ ] Integración en `deploy.yml` como paso posterior
- [ ] Cobertura de los módulos nuevos
- [ ] Pruebas de componente de los formularios nuevos

**Estimación:** 1 punto. **Depende de:** US-M03 y US-M11. **Deriva de:** US-033.

---

### US-M23 — Pase a producción: TTFT p50, P90 y cold starts

**Como** equipo,
- **quiero** cifras de latencia medidas sobre el sistema desplegado,
- **para que** lo que se afirme del MVP se pueda sostener con datos.

**Criterios de Aceptación:**

- **TTFT p50 < 700 ms** sobre al menos cincuenta corridas contra la URL pública, con la metodología de percentiles escrita antes de medir.
- **P90 de consulta completa < 15 s.**
- **Cold starts medidos** y decisión documentada: aceptar el arranque en frío, o poner `min-instances 1` solo durante una ventana concreta, con su costo calculado y su fecha de reversión.
- Resultados en un documento fechado. **Si una cifra no se cumple, se publica igual y se declara**: una medición que solo se reporta cuando favorece no es una medición.

**Tareas técnicas:**

- [ ] Script de medición de TTFT y P90 con cincuenta corridas
- [ ] Registro de cold starts
- [ ] Decisión de `min-instances` con su costo
- [ ] Documento de resultados fechado

**Estimación:** 2 puntos. **Depende de:** US-M22. **Deriva de:** US-034.

---

## Lo que este plan deja fuera, con nombre y razón

El silencio es lo único que no funciona, así que queda escrito.

| Fuera del MVP | Razón |
|---------------|-------|
| **US-010** — perfilado EDA de los silos | STRETCH desde el 22-jul. Su valor era alimentar A2 y A3, que ya se entregaron |
| **US-013** — jerarquía Corpus2Skill para manuales | STRETCH. No hay corpus de manuales en el proyecto; construir el pipeline para un corpus inexistente es trabajo sin objeto |
| **US-014** — RAG relacional cross-silo | STRETCH. El join cruzado de US-M07 cubre la necesidad real; el grafo de relaciones es refinamiento |
| **US-022** — clasificador OOD previo al LLM | STRETCH. El manager de US-M10 ya rutea fuera de dominio; el ahorro de tokens es optimización, no capacidad |
| **US-035 / US-036** — harness LLM-as-judge y ciclo Tk-Boost | STRETCH. Presuponen un agente en uso con volumen de fallas que todavía no existe |
| **Terraform completo** | El puente `gcloud run deploy` de US-M01 satisface el MUST original, que admite el puente por escrito. El módulo parametrizado es +2 SP de STRETCH |
| **Mutación bidireccional plena tablero-chat** | +3 SP de STRETCH en el catálogo original. US-M18 entrega el contexto vivo, no la escritura del agente sobre el tablero |
| **Reordenamiento de módulos por arrastre** | +2 SP de STRETCH de US-027, congelado desde el 29-jul |
| **Modo oscuro** | Congelado en §26.6: un modo oscuro mal contrastado resta más de lo que suma. Sigue en el roadmap de la guía de estilos |
| **Refresh tokens, recuperación de contraseña, OAuth/SSO, RLS por fila, drift detection, switch A/B de LLM** | Descartes explícitos de §18 del plan. No son historias faltantes: son decisiones firmadas |

---

## Aritmética, calendario y los tres cortes posibles

**Costo total del MVP completo: 34.75 SP.** A la constante del plan (2.4 h/SP) son 83 h; al ritmo real observado en S4 (2.7 h/SP), 94 h. **Banda honesta: 85–95 horas**, es decir entre 8 y 10 días de trabajo a diez horas diarias de una sola persona.

> **Nota sobre la estimación previa.** El contraste del 14-ago estimó 33 SP y esta itemización da 34.75. La diferencia no es alcance nuevo: es alcance que la estimación por épica no veía porque trataba "el agente" y "la infraestructura" como bolsas. Se corrige aquí, por la misma razón y con la misma forma con que §26.1 corrigió el "8–11 SP" que al itemizarse resultaron 21.

**Esto no cabe antes del cierre del curso.** S5 (17 al 23 de agosto) tiene ≈29 SP de capacidad nominal al ritmo de una persona a setenta horas, y de ahí salen primero US-UX-08 y la ejecución de la prueba SUS con participantes, que por la regla de oro ganan cualquier conflicto. Lo que queda para código es del orden de 15 a 20 SP en el mejor caso.

**Tres cortes, para decidir con números en vez de con optimismo:**

| Corte | Contenido | SP | Qué se obtiene |
|-------|-----------|----|----------------|
| **A — MVP conversacional** | M01, M04, M05, M07, M08, M09, M10, M11, M12 | **17** | El asistente responde de verdad, sobre datos gobernados, con permisos heredados y sin filtrar prompts. Es la tesis del proyecto, funcionando |
| **B — MVP operable** | Corte A + M02, M03, M13, M14, M15, M17, M22 | **23.25** | Además: se despliega solo, el gobierno de usuarios está completo, la exportación es real y hay smoke contra el sistema desplegado |
| **C — MVP completo** | Las 23 historias | **34.75** | Además: búsqueda híbrida, volumen declarado, millón de puntos y FinOps medido con cifras de latencia publicables |

**Recomendación.** En S5, el **Corte A** y solo si A5 avanza sin sobresaltos; y dentro del Corte A, el orden ya está dado por el camino crítico, así que un corte por tiempo se hace por la cola —M12, luego M11— y no por el medio. Los cortes B y C quedan como trabajo posterior al curso, declarados en el apartado de trabajo futuro de A5 con esta numeración, para que quien lea el informe pueda ver que lo que falta está contado, ordenado y estimado, y no simplemente pendiente.

---

**FIN DEL DOCUMENTO**
