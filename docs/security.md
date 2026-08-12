# Seguridad y matriz de permisos — Karisma Data

**US dueña**: US-016 (E2) · **Fecha**: 11-ago-2026 · **Estado**: vigente para el prototipo del MVP

Este documento describe **quién puede pedir qué** en el portal y qué responde la API cuando la
respuesta es «no». Cierra el gate del 6-ago-2026, que exigía una matriz de permisos escrita y
verificable.

## 1. Alcance y fuente de verdad

La política no vive aquí. Vive en `backend/app/core/permissions.py`, y este documento la publica.

| Pieza | Archivo | Qué decide |
|---|---|---|
| Vocabulario de roles y jerarquía | `backend/app/core/scopes.py` | Qué significa un rol y cuándo alcanza |
| Política por ruta | `backend/app/core/permissions.py` | Qué exige cada endpoint, quién lo posee y si ya existe |
| Resolución de la sesión | `backend/app/core/auth.py` | Quién es quien llama, y delega la decisión en las dos anteriores |

La sección 3 de este archivo es **generada**. Se regenera con:

```bash
poetry -P backend run python -c "from app.core.permissions import render_permission_matrix; print(render_permission_matrix())"
```

y la prueba `tests/backend/permisos/test_security_doc.py` compara el bloque línea a línea con la
salida de esa función. Editar la tabla a mano pone la suite en rojo, que es exactamente lo que se
pretende: un documento que puede mentir no es un control.

Tres capas impiden que un endpoint nuevo se olvide de declarar sus permisos, y las tres leen la
misma estructura:

1. **Registro** — `SCOPE_REGISTRY` obliga a escribir la regla, su US dueña y su estado.
2. **Guardia en pruebas** — `audit_scope_coverage(app)` cruza las rutas montadas con el esquema
   OpenAPI y devuelve violaciones de cuatro clases: `sin_scopes`, `fuera_del_registro`,
   `scope_divergente` y `ruta_oculta`.
3. **Arranque** — `create_app()` termina llamando a `assert_scope_coverage(...)`. Con violaciones la
   aplicación **no arranca**: en local muere `make dev`, y en Cloud Run la revisión no se promueve y
   el tráfico se queda en la anterior. Falla cerrado.

## 2. Roles y jerarquía

Cuatro roles, en minúsculas, sin acentos y sin sinónimos. Son literalmente los valores del scope del
JWT.

| Rango | Scope | Etiqueta en español | Label in English | Alcance |
|---|---|---|---|---|
| 0 | `operativo` | Operativo | Operations | Catálogo y consulta puntual sobre un silo |
| 1 | `analista` | Analista | Analyst | Agregaciones, exploración y exportaciones |
| 2 | `directivo` | Directivo | Executive | Resúmenes ejecutivos y tableros directivos |
| 3 | `admin` | Administrador | Administrator | Administración de usuarios y de la plataforma |

**La jerarquía es un orden total**: un rol alcanza todo lo que exige un rango menor o igual al suyo.
Es lo único que hace verdadero el «+» de «operativo+», «analista+» y «directivo+» del enunciado.

Dos consecuencias, escritas para que nadie las descubra tarde:

- **`admin` lee los resúmenes directivos.** Es separación de funciones imperfecta y es deuda
  aceptada (sección 11).
- **El modelo no puede expresar «solo directivo».** Si algún día hiciera falta, deja de ser un orden
  total y la comparación de `covers()` cambia de forma; no se parchea con una excepción.

La reclamación `scope` del token es una **cadena delimitada por espacios** que hoy lleva exactamente
un rol. Un nombre que el portal no conoce no concede nada: no es un error, es un permiso vacío. Esa
decisión evita que un token viejo o falsificado produzca un 500 en lugar de un 403.

Las etiquetas visibles son **capa de presentación** y pertenecen a US-017. El backend nunca las
emite.

## 3. Matriz de permisos

Bloque generado. **No editar a mano**: regenerar con el comando de la sección 1.

<!-- matriz-permisos:inicio -->
| Metodo y ruta | Scopes | Regla | US | Estado |
|---|---|---|---|---|
| `POST /api/auth/token` | *(publica)* | Emite el token; no puede exigirlo | US-015 | vigente |
| `POST /api/auth/demo` | *(publica)* | Emite token sin credenciales, como /token; existe solo cuando DEMO_LOGIN_ENABLED es verdadero | US-015 | vigente |
| `GET /api/auth/me` | *(ninguno)* | Cualquier sesion valida consulta su propio perfil | US-015 | vigente |
| `GET /api/catalog/search` | *(ninguno)* | Catalogo para todos los autenticados | US-008 | vigente |
| `GET /api/catalog/{entry_id}` | *(ninguno)* | Ficha de catalogo, mismo criterio | US-008 | vigente |
| `POST /api/query/records` | `operativo` | Consulta puntual sobre un silo | US-011 | planificado |
| `GET /api/metrics/series` | `analista` | Serie preagregada del tablero | US-025 | planificado |
| `POST /api/metrics/aggregate` | `analista` | Agregaciones y cruces de la capa semantica | US-011 | planificado |
| `POST /api/export` | `analista` | Exportacion en segundo plano | US-009 | planificado |
| `GET /api/export/{job_id}` | `analista` | Estado del trabajo y enlace firmado | US-009 | planificado |
| `GET /api/summaries/executive` | `directivo` | Resumenes directivos | US-026 | planificado |
| `GET /api/users` | `admin` | Gestion de usuarios | US-018 | planificado |
| `POST /api/users` | `admin` | Alta de usuario | US-018 | planificado |
| `PATCH /api/users/{user_id}` | `admin` | Cambio de rol; un admin no se degrada a si mismo | US-018 | planificado |
| `DELETE /api/users/{user_id}` | `admin` | Borrado logico; un admin no se desactiva a si mismo | US-018 | planificado |
| `POST /api/chat` | *(ninguno)* | El agente propaga el Bearer del usuario; cada tool cae en la fila del endpoint que envuelve | US-023 | planificado |
<!-- matriz-permisos:fin -->

Cómo se lee:

- ***(pública)*** — la ruta responde sin token. Son dos, y las dos emiten credenciales: exigir un
  token para conseguir un token es imposible.
- ***(ninguno)*** — hace falta una sesión válida, y cualquier rol sirve. **No es lo mismo que exigir
  `operativo`**, aunque hoy admitan al mismo conjunto de personas: no hay ningún rol por debajo de
  `operativo`. La diferencia está en la regla, no en el resultado de hoy.
- **`analista`** — hace falta ese rango **o superior**, por la jerarquía de la sección 2.
- **Estado `planificado`** — la fila es política publicada por adelantado y la ruta todavía no
  existe. Una fila sin ruta viva **no** es una violación; una ruta viva sin fila **sí**.

## 4. Contrato HTTP y códigos de error

El cuerpo de la respuesta lleva un **código estable**, nunca una frase. La interfaz es bilingüe desde
la decisión del 10-ago-2026: una frase en el cuerpo existiría en un solo idioma. El backend dice
`permisos_insuficientes` y US-017 elige el texto.

Retos conforme a RFC 6750 §3.1, con `realm="karisma"` en las cinco filas:

| Situación | Estado | `WWW-Authenticate` | `detail` |
|---|---|---|---|
| Sin cabecera `Authorization` | **401** | `Bearer realm="karisma"` (+ `, scope="..."` si el endpoint exige nivel) | `credenciales_ausentes` |
| Token malformado, firma ajena o `alg=none` | **401** | `Bearer realm="karisma", error="invalid_token"` | `credenciales_invalidas` |
| Token expirado | **401** | igual, con `error_description="sesion_expirada"` | `sesion_expirada` |
| Usuario desactivado | **401** | igual, con `error_description="sesion_revocada"` | `sesion_revocada` |
| Autenticado con rol insuficiente | **403** | `Bearer realm="karisma", error="insufficient_scope", scope="admin"` | `permisos_insuficientes` |

Copia para los dos locales. Las claves cuelgan de `errores.autorizacion.*` y **existen en español y
en inglés**; es el contrato que US-017 consume:

| Código | Clave i18n | Español | English |
|---|---|---|---|
| `credenciales_ausentes` | `errores.autorizacion.credenciales_ausentes` | Inicia sesión para continuar. | Sign in to continue. |
| `credenciales_invalidas` | `errores.autorizacion.credenciales_invalidas` | No pudimos validar tu sesión. Inicia sesión de nuevo. | We could not validate your session. Sign in again. |
| `sesion_expirada` | `errores.autorizacion.sesion_expirada` | Tu sesión expiró. Inicia sesión de nuevo. | Your session expired. Sign in again. |
| `sesion_revocada` | `errores.autorizacion.sesion_revocada` | Tu acceso fue desactivado. Solicítalo a la administración del portal. | Your access has been disabled. Contact the portal administrators. |
| `permisos_insuficientes` | `errores.autorizacion.permisos_insuficientes` | Tu perfil no tiene permiso para ver esta información. Solicita el acceso al administrador del portal. | Your profile does not have permission to view this information. Request access from the portal administrator. |

La última fila es el texto del estado «sin permiso» de US-017, y esa pantalla se muestra **sin botón
de reintento**: reintentar no cambia el rol de nadie.

Tres reglas más del contrato:

- **El 403 no revela nada.** Ni recurso, ni identificador, ni propietario. El único dato es el
  `scope=` del reto, que el propio token ya implica.
- **Un usuario desactivado recibe 401, no 403.** El 403 dejaría al navegador con una sesión que cree
  viva y sin salida; el 401 dispara el re-login limpio.
- **El 401 gana al 403, y ambos ganan al 422.** La dependencia de seguridad se resuelve antes de
  validar el cuerpo y lanza en lugar de acumular errores.

## 5. Canal de credenciales y CSRF

**El backend acepta exclusivamente `Authorization: Bearer`. FastAPI no lee cookies.**

```
navegador --cookie karisma_sesion (HttpOnly, SameSite=Strict)--> proxy Nitro
proxy Nitro --Authorization: Bearer <jwt>--> FastAPI
```

Si FastAPI leyera la cookie, cualquier formulario alojado en otro origen dispararía peticiones
autenticadas, porque el navegador adjunta la cookie solo. Eso obligaría a una capa anti-CSRF con
token sincronizado que nadie construye bien con prisa. Con el corte en el proxy, el control cabe en
tres piezas:

| # | Control | Dueño |
|---|---|---|
| 1 | Cookie `HttpOnly; Secure; SameSite=Strict`: el navegador no la envía en navegaciones cruzadas | US-015 |
| 2 | El proxy rechaza métodos no seguros cuando `Origin` o `Sec-Fetch-Site` no son del propio sitio | US-015 |
| 3 | El backend, sin cabecera `Authorization`, responde 401 pase lo que pase | US-016 |

El paso 5 de `docs/manual-test/us-016.md` comprueba la frontera: la cookie **no** autentica contra el
backend directo. Si ese paso devolviera 200, la superficie de CSRF sería otra.

## 6. Herencia del Bearer al agente

Regla escrita ahora, implementada por US-020, US-021 y US-023: **el agente jamás ve datos que el
usuario no puede ver.**

- `POST /api/chat` exige sesión válida y ningún rol concreto: el chat en sí no es el dato.
- Cada *tool* del agente envuelve un endpoint gobernado de esta misma matriz y **propaga el Bearer
  del usuario**. El permiso se evalúa en el endpoint envuelto, con la fila que le corresponde aquí.
- El agente no tiene credencial propia ni ruta privilegiada. Si una consulta necesita `analista` y
  quien pregunta es `operativo`, la *tool* recibe el 403 y el agente responde que no tiene acceso,
  sin cifras.
- Una *tool* que llamara a la capa semántica saltándose el endpoint quedaría fuera de la matriz: por
  eso las *tools* viven en `ml/agent/tools/` envolviendo endpoints, y no consultando Polars.

## 7. Cómo se añade un endpoint nuevo

Tres pasos, dos minutos. Sin ellos la suite se pone roja y la aplicación no arranca.

1. **Declarar la seguridad en el router**, siempre con `Security` y nunca con `Depends`:

   ```python
   @router.get("/api/metrics/series")
   async def read_series(
       user: Annotated[UserOut, Security(get_current_user, scopes=["analista"])],
   ) -> Series: ...
   ```

2. **Añadir la fila al registro** en `backend/app/core/permissions.py`, con su regla en prosa, su US
   dueña y su estado (`vigente` en cuanto la ruta se monta):

   ```python
   RouteKey("GET", "/api/metrics/series"): PermissionRule(
       scopes=(Scope.ANALISTA,),
       rule="Serie preagregada del tablero",
       us="US-025",
       status="vigente",
   ),
   ```

3. **Regenerar la sección 3** con el comando de la sección 1 y pegar el bloque entre los marcadores.

Casos especiales, los dos únicos que hay:

- **Ruta que emite credenciales** (`POST /api/auth/token`, `POST /api/auth/demo`): entra en
  `PUBLIC_ROUTES` con su justificación. No se exceptúan familias por prefijo; una excepción para todo
  `/api/auth/**` dejaría pasar mañana un `GET /api/auth/usuarios` sin permisos por vivir en el barrio
  correcto.
- **Ruta montada según una bandera**: se declara igual que una permanente. Una entrada declarada sin
  ruta viva no es violación; una ruta viva sin entrada, sí. La guardia se ejecuta con la bandera
  encendida y apagada.

## 8. Modelo de amenazas

| # | Amenaza | Control | Dónde se prueba |
|---|---|---|---|
| A-1 | Endpoint nuevo sin `Security(...)`, servido abierto | Registro + guardia + comprobación de arranque | `test_scope_coverage.py::test_detecta_endpoint_sin_security` y `::test_toda_ruta_viva_esta_declarada` |
| A-2 | Token falsificado con `alg=none` o con otra clave | `algorithms=["HS256"]` explícito y firma verificada | `test_permission_matrix.py::test_401_token_manipulado` |
| A-3 | Escalada de privilegios por un rol inventado en el token | Un scope desconocido no concede nada; el `CHECK` de `app_user` lo impide en origen | `test_scopes.py::test_scope_desconocido_en_el_token_no_concede_nada` |
| A-4 | Endpoint mal declarado (`scopes=["analysta"]`) que abre en lugar de cerrar | `covers()` falla cerrado ante un scope desconocido y deja `scope_desconocido` en la bitácora | `test_scopes.py::test_scope_desconocido_en_el_endpoint_niega_el_acceso` |
| A-5 | Usuario dado de baja que sigue leyendo con su token vivo | El estado se consulta en cada petición y responde 401 `sesion_revocada` | `test_permission_matrix.py::test_usuario_desactivado_es_401_aunque_su_rol_alcance` |
| A-6 | Sesión robada desde JavaScript | Cookie `HttpOnly`; el token nunca llega al cuerpo de la respuesta del login | US-015; `docs/manual-test/us-015.md` bloque 1 |
| A-7 | CSRF contra métodos no seguros | Sección 5, controles 1 a 3 | `docs/manual-test/us-015.md` bloque 6 |
| A-8 | Fuga de información en la negativa | El 403 lleva solo el código; el 401 de credenciales no distingue usuario inexistente de contraseña errónea | `test_permission_matrix.py::test_403_no_revela_nada` |
| A-9 | Documento que dice una política y código que aplica otra | El bloque de la matriz es generado y se compara línea a línea | `test_security_doc.py::test_el_bloque_del_documento_coincide_con_el_registro` |
| A-10 | Ruta interna con `include_in_schema=False` que esquiva la auditoría | La guardia cruza dos inventarios y la clasifica `ruta_oculta` | `test_scope_coverage.py::test_detecta_ruta_oculta` |
| A-11 | Ruta cuyo path es el prefijo exacto (`/api`, sin barra final) que la guardia no miraba | `_under_api` compara igualdad además de prefijo | `test_scope_coverage.py::test_la_ruta_que_es_el_prefijo_exacto_no_se_escapa` |
| A-12 | `Mount` o sub aplicación bajo `/api`, que no tiene operación en el esquema ni árbol de dependencias que exigir | La guardia la clasifica `ruta_ajena` y el arranque falla: si no puede autorizarla, no la deja pasar | `test_scope_coverage.py::test_un_mount_bajo_api_es_una_violacion_y_no_un_silencio` |

## 9. Privacidad de los registros

- **Contraseñas**: jamás, ni en claro ni con su digest, ni en registros ni en trazas.
- **Tokens**: jamás. La negativa de autorización registra los scopes exigidos y los del token, nunca
  el token. La identidad llega por `structlog.contextvars`, enlazada al resolver la sesión.
- **Prompts del agente**: solo `llm.prompt_hash` (SHA-256), nunca el texto.
- **Búsquedas del catálogo**: solo `consulta_hash` (SHA-256) y el número de términos, nunca el
  texto. La razón es concreta: `build_tsquery` no lematiza —baja a minúsculas y trocea—, así que un
  número de cuenta o un correo tecleados en la caja de búsqueda salían casi literales al registro, y
  con la identidad enlazada por `structlog.contextvars` esa línea correlacionaba persona con texto
  libre. Es la misma regla que mantiene los prompts crudos fuera de las trazas.
- **Eventos que sí se registran**: `autorizacion_denegada` (scopes exigidos y concedidos),
  `scope_desconocido` (nombre mal escrito en la declaración de un endpoint),
  `cobertura_de_scopes_incompleta` (violaciones al arrancar), `catalogo_busqueda`
  (`consulta_hash`, `terminos`, `total`, `devueltos`, `limit`, `offset`) y
  `catalogo_busqueda_sin_terminos` (solo `limit` y `offset`).
- Las respuestas de la API nunca serializan `hashed_password`: el contrato de salida es `UserOut`.

## 10. Fuera de alcance

Descartado con su razón, para que no se reabra sin decisión de equipo:

| Descartado | Razón | Qué haría falta para reabrirlo |
|---|---|---|
| Refresh tokens | La sesión dura 30 minutos y se vuelve a entrar; la rotación segura exige almacén de revocación y rompe el `scale-to-zero` sin estado | Una US propia con almacén de revocación y su matriz de pruebas |
| Recuperación de contraseña y OAuth/SSO externo (código de autorización, OpenID Connect) | Es un proveedor de identidad de terceros dentro de un prototipo de curso | Decisión de equipo y presupuesto de otra US |
| Seguridad por fila (RLS) | Los permisos del MVP son por endpoint y por rol; la RLS exige modelar propiedad del dato en cada tabla | Un requisito real de aislamiento por cliente |
| Limitación de intentos de acceso | Está en el backlog (`docs/us-backlog/05-limitacion-de-intentos-de-acceso.md`), no en S4 | Su propia US, con almacén de intentos |
| Permisos por objeto o por columna | La matriz es por ruta; un permiso por columna exige llevarlo a la capa semántica y al compilador | Una US que toque `ml/semantic/` |
| Auditoría persistente de accesos | Hoy los eventos van a la bitácora estructurada, sin tabla ni retención | Una US con su tabla, su retención y su consulta |

## 11. Deuda aceptada

| # | Deuda | Consecuencia | Dueño |
|---|---|---|---|
| 1 | `admin` alcanza los resúmenes directivos por ser el rango más alto | Separación de funciones imperfecta: quien administra usuarios también lee el tablero ejecutivo | Equipo, si el modelo deja de ser un orden total |
| 2 | `frontend/app/types/navegacion.ts` declara `'administrador'` donde el scope es `admin` | Hoy solo rotula el índice de prototipos; mañana es un `if` que nunca se cumple contra un token real | **US-017** |
| 3 | La matriz solo interroga hoy las rutas vivas: tres de dieciséis filas | La política de las trece restantes está escrita y sin ejercitar hasta que su US llegue | Cada US dueña, al montar su router |
| 4 | Verificación manual del 403 a través del proxy | **Reasignada el 12-ago-2026.** US-008 publicó sus dos rutas con `scopes=()` —cualquier sesión válida—, así que no cerró esta deuda: hoy **ninguna ruta viva puede responder 403** y la rama `else` de la matriz parametrizada es inalcanzable contra la aplicación real. El mecanismo sí está ejercitado contra la aplicación sintética, que usa la dependencia de producción. La cierra la primera US que publique una ruta con scope no vacío | **US-009** (`POST /api/export`, `analista`) |
| 5 | Sin auditoría persistente de quién consultó qué | Un incidente se reconstruye leyendo bitácoras efímeras | Fuera de alcance (sección 10) |

## 12. Bitácora

| Fecha | Cambio |
|---|---|
| 11-ago-2026 | Documento creado por US-016. Vocabulario de cuatro roles con jerarquía total, matriz generada desde `SCOPE_REGISTRY`, contrato HTTP con los cinco códigos bilingües, guardia de cobertura de tres capas y comprobación de arranque. Cierra el gate del 6-ago-2026 |
