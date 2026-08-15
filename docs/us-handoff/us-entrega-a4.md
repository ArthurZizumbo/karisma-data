# Handoff US-ENTREGA-A4 — Consolidación de la entrega de la Actividad 4

**Estado**: testing
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantalla de catálogo)
**Sprint**: S4, cierre · **Actividad**: A4 (dom 16-ago-2026)
**Rama**: `us-entrega-a4`, desde la punta de `us-ux-07`. Sin PR (discrepancia RU-11 declarada)
**SHA base**: `aeafc6e` (fijado 14-ago-2026 al abrir implementación). Ancla del diff: `git diff --name-only aeafc6e`. **QA no usa `HEAD~N`**
**Estimación**: 13 SP en cuatro olas independientes
**Plan**: [`docs/us-planning/us-entrega-a4.md`](../us-planning/us-entrega-a4.md)

> La Actividad 4 la produjo el equipo completo y se entrega como un solo trabajo. Una parte se
> construyó en el stack del producto y otra en Figma, y las dos describen el mismo portal. Esta US
> consolida las dos mitades en **una entrega**: el documento resultante habla del producto, nunca de
> quién hizo qué parte.
>
> **Lo que salga de aquí es lo que se entrega**: el PDF de la ola D es el archivo que sube a Canvas,
> y el mismo avance entra al documento acumulado del proyecto, `main_completo.tex`.

---

## Dominios y sub-tareas tocados

- [ ] backend
- [x] frontend — composables y store de tema, **selector de tema y selector de rol en la cabecera**, pantalla de catálogo, campo `alcance`
- [ ] ml
- [ ] agent
- [ ] infra
- [ ] db
- [x] design — el eje de tema en `design/sistema.py`, `contraste.py` y `emitir.py`
- [x] tests — una suite de diseño y dos de frontend
- [x] docs — seis `.tex`, `a4_08` nuevo, las figuras, los dos envoltorios y el PDF de la entrega

**Sí se reparte**, en cuatro olas con write-sets disjuntos. Cada una entrega sola.

| Ola | Qué entrega | SP | Depende de |
|---|---|---|---|
| **A** eje de tema | `design/**`, los generados y la carga de Inter. El portal se ve igual que hoy | 4 | nada |
| **B** conmutadores y entrada en frío | Composables, store, selectores de tema y rol, cabecera, i18n, `app.vue`, guarda, acceso, **índice y tarjeta de prototipo** | 5 | A |
| **C** catálogo y etiquetas | La pantalla de exploración y las seis etiquetas de alcance | 2 | nada |
| **D** documento y entrega | Los seis `.tex`, `a4_08`, figuras, los dos envoltorios y **el PDF que se sube** | 2 | A, B y C |

**A y C corren en paralelo.** B lee lo que A emite. D cierra.
**Si el reloj aprieta, el orden es C, D, A, B.**

---

## Zonas sensibles

| Archivo | Por qué |
|---|---|
| `frontend/app/assets/css/main.css` · `app/utils/tokens.generated.ts` | **Generados** por `design/emitir.py`. Se regeneran con `make tokens`, jamás se editan a mano. `scripts/verificar_tokens_a4.sh` compara disco contra emisor y una edición manual aparece como divergencia |
| `docs/entregables/figuras/a4/antes/**` y `despues/**` | **Evidencia cerrada** de la primera iteración. Una recaptura bajo el tema nuevo destruye el par y tumba el criterio 6. Las capturas del tema van a `figuras/a4/tema/` |
| `design/sistema.py` | Fuente única de los 17 tokens. La prueba de fijación del tema de omisión se escribe **antes** de tocarlo |
| `docs/entregables/main_a4.tex` | De US-UX-09. Esta US añade **una línea**: el `\input` de `a4_08`, al final del bloque, sin reordenar |
| `contenido/a4_03_guia_estilos.tex` | De US-UX-09. Esta US reescribe **solo** la subsección «Modo oscuro, fuera de alcance y declarado», que hoy afirma que el sistema entrega una sola paleta y deja de ser cierta. **Ninguna otra línea.** Sus 63 subsecciones ya cubren retícula, microinteracciones, voz y tono, imágenes y bitácora: `a4_08` no las repite |
| `contenido/a4_06_cierre.tex` | De US-UX-09. Se lee para no repetir; no se escribe |
| `estilo/uxdoc.sty` · `estilo/a4_tokens.tex` · `generar_tokens_a4.py` | Congelada la primera, emitidos los otros dos |
| `frontend/app/utils/navegacion.ts` | Esta US **sí lo escribe**, y solo el campo `alcance` de seis entradas. La séptima, `/asistente`, se conserva |
| `frontend/i18n/locales/{es,en}.json` | Subárbol `theme.*` únicamente. Clave nueva a los dos catálogos en el mismo commit |
| `frontend/AGENTS.md` | Lo escribe **el orquestador al integrar**, no las olas B y C, que escriben ambas en `frontend/` |

---

## Decisiones tomadas en planeación

1. **Los dos temas conviven**: `corriente` de omisión e `institucional` opcional. Ninguno sustituye al otro; el de omisión sostiene la evidencia ya entregada.
2. **El tema institucional lleva modo oscuro**, diseñado y verificado con la misma maquinaria, no heredado. Suelo `#0B1B2B`, azul profundo derivado de su color de navegación, nunca negro puro.
3. **La paleta institucional está calculada y verificada**, los 17 tokens en los dos modos, con la procedencia de cada valor citada. Tabla completa en §2.3 del plan.
4. **Dos hallazgos de la verificación**: el color de atención daba **3.65:1** y sube a `#A36A10` con **4.54:1**; y el canal informativo necesita un matiz fuera del octeto, porque el color de acción y el de éxito están a **dE 6.7 bajo tritanopia** contra un piso de 13.6.
5. **El tema institucional trae Inter**, que es lo que declaran los exportes de `docs/entregables/figma/`, fuente única del tema por decisión del equipo. El eje del tema es **color y familia tipográfica**; el de omisión conserva Lexend Deca y Fira Sans. Cuesta +1.5 SP: mapa de familias por tema, Inter en `nuxt.config.ts` y reverificación de los nueve roles.
6. **La paleta de series no cambia entre temas**: es canal de datos, no identidad, y ya está verificada.
7. **Los cinco flujos entran como diseño**, con la palabra escrita en cada pie.
8. **La tabla de alcance gana un cuarto estado** para distinguir hoja de ruta diseñada de hoja de ruta sin diseño.
9. **`data-theme` se renombra a `data-modo`** y el tema entra como `data-tema`. Hoy el atributo transporta el modo y dejarlo así garantiza la confusión.
10. **El color de acción no entra en los 17 tokens**: el contrato no tiene ranura de acción y abrirla no cabe en esta US. Queda como pendiente.
11. **La tarjeta del índice acuña la sesión de su `rolSugerido`** y deja a quien la pulsa dentro de la pantalla, en un clic y con token real. El índice es la superficie del evaluador y hoy no hace su trabajo. **No se hace un embudo de tema, rol y prototipos**: `PRODUCT.md` fija que gana el usuario trabajando, y un embudo obligatorio pondría al evaluador por delante en cada visita. El tema es preferencia y vive en la cabecera. Solo con `DEMO_LOGIN_ENABLED`.
12. **El rebote sin sesión deja de ser mudo**: la guarda lleva `destino` y `motivo`, la pantalla de acceso lo dice, bajo `DEMO_LOGIN_ENABLED` los cuatro perfiles preceden al formulario, y al elegir perfil se vuelve a la ruta pedida con el destino validado contra `RUTAS_CONTRATO`. **Ni se apaga el middleware ni se prellenan credenciales**: lo primero borraría los espacios por rol y cinco celdas de la matriz; lo segundo no resuelve el caso de quien no sabe qué es esa pantalla.
12. **El rol se cambia desde el cromo y el cambio es real**: el selector llama a `POST /api/auth/demo` y acuña sesión, nunca cambia el rol en el cliente. Solo existe con `DEMO_LOGIN_ENABLED`. La pantalla de acceso se queda —es uno de los siete prototipos— y **las credenciales no se prellenan**.
12. **Esta US asume las dos ediciones en archivos de US-UX-09** y no espera coordinación: el `\input` de `a4_08` en `main_a4.tex` y la subsección de modo oscuro de `a4_03`. Las dos van acotadas y anotadas aquí.

---

## Pendientes al abrir implementación

1. Fijar el SHA base y escribirlo arriba.
2. Escribir la prueba de fijación del tema de omisión **antes** de la primera línea de `design/sistema.py`.
3. Pedir los ocho valores oficiales de los estados interactivos; mientras tanto se derivan por regla declarada.
4. Decidir si el contrato de tokens gana una ranura de acción. **Fuera del alcance de esta US.**
5. Evaluar si `design/` merece guía propia. **Fuera del alcance de esta US.**
6. Corregir las guías con las discrepancias de §11 del plan: `frontend/AGENTS.md` dice 38 spec y hay 42; dice doce familias y hay 13; `docs/AGENTS.md` dice que de A4 solo existen dos `.tex` y existen los ocho.

---

## Verificación comprometida

Los catorce recorridos de §6.3 del plan **se ejecutaron** con el MCP de Playwright contra el portal levantado con Docker Compose. Resultado y hallazgos en «Registro de verificación en navegador».

---

# Registro de implementación — 14-ago-2026

**Estado**: `testing` · **SHA base**: `aeafc6e` · **Diff**: `git diff --name-only aeafc6e`

Las cuatro olas se repartieron con write-sets disjuntos y corrieron con dos agentes concurrentes como máximo: **A ‖ C**, luego **B**, luego **D1 ‖ D2**. La ola D se subdividió en dos write-sets disjuntos dentro de `contenido/`. La integración —los dos envoltorios, `a4_00`, las guías de carpeta y el PDF— la hizo el orquestador.

## Snapshot de archivos

**Creados (14)**

| Archivo | Ola |
|---|---|
| `tests/ml/test_contraste_temas.py` | A |
| `tests/ml/test_emision_temas.py` | TESTS |
| `frontend/app/composables/useTema.ts` · `useRolDemo.ts` | B |
| `frontend/app/components/comun/SelectorTema.vue` · `SelectorRol.vue` | B |
| `frontend/app/components/exploracion/{BuscadorCatalogo,FiltroDominios,ResultadosCatalogo,AccionesCatalogo}.vue` | C |
| `frontend/test/tema.spec.ts` · `rol.spec.ts` | B |
| `frontend/test/exploracionCatalogo.spec.ts` | C |
| `frontend/test/superficie.spec.ts` · `cabeceraProducto.spec.ts` · `accionesCatalogo.spec.ts` | TESTS |
| `docs/entregables/contenido/a4_08_tema_y_flujos.tex` | D1 |

**Modificados (38)**

- **design** — `sistema.py`, `contraste.py`, `emitir.py` (A)
- **frontend, generados** — `app/assets/css/main.css`, `app/utils/tokens.generated.ts` (emitidos por `make tokens`, nunca a mano)
- **frontend, código** — `nuxt.config.ts` (A) · `app.vue`, `composables/useModo.ts`, `stores/sistemaDiseno.ts`, `components/comun/CabeceraProducto.vue`, `components/nav/BotonPrototipo.vue`, `components/acceso/SelectorDemostracion.vue`, `pages/index.vue`, `pages/acceso.vue`, `utils/guarda.ts`, `types/guarda.ts`, `middleware/auth.global.ts`, `i18n/locales/{es,en}.json` (B) · `pages/exploracion/index.vue`, `utils/navegacion.ts` (C)
- **frontend, pruebas** — `test/guarda.spec.ts` (B), `test/rol.spec.ts` (TESTS, +4), `test/indice.spec.ts` (orquestador)
- **docs** — `contenido/a4_03_guia_estilos.tex` (D1, una subsección) · `a4_01`, `a4_02`, `a4_04`, `a4_05`, `a4_07` (D2) · `a4_00_preliminares.tex`, `main_a4.tex`, `main_completo.tex`, `semana_4/Entregable Actividad 4_equipo_8.pdf` (orquestador)
- **guías** — `frontend/AGENTS.md` + `CLAUDE.md`, `docs/AGENTS.md` + `CLAUDE.md` (orquestador; espejos verificados idénticos)

## Decisiones tomadas durante la implementación

1. **La tabla §2.3 del plan tenía un defecto y los valores emitidos no son los suyos.** El plan analizó solo los pares del canal informativo; el par error/confirmación del tema institucional caía a **dE 10.1** bajo protanopia en claro (piso 13.6) y a **dE 13.1** en oscuro (piso 21.5). Corregido con la regla declarada del propio plan —oscurecer conservando matiz y saturación— y **solo sobre `error`**: `933632` en claro (7.46:1, peor par 14.5) y `EC5B51` en oscuro (5.13:1, peor par 22.6). Las otras 20 razones de §2.3 reproducen exactas. `a4_08` y `a4_04` publican los valores emitidos, no los del plan.
2. **El eje nuevo se expuso en paralelo, no sustituyendo.** `tokens.generated.ts` añade `CONTRASTES_POR_TEMA`, `SEPARACIONES_POR_TEMA` y `PEOR_SEPARACION_POR_TEMA`, y conserva `CONTRASTES`, `SEPARACIONES` y `PEOR_SEPARACION` filtrados al tema de omisión. Motivo: `stores/sistemaDiseno.ts` y `sistemaDeDiseno.spec.ts` los consumen y **no estaban en ningún write-set**.
3. **Tres archivos de la ola B fuera de su write-set literal, todos sin dueño.** `types/guarda.ts` (la unión `MotivoDeSalida` vive ahí), `middleware/auth.global.ts` (8 líneas: sin ellas la guarda decide bien y el rebote sigue mudo) y `components/acceso/SelectorDemostracion.vue` (único componente que pinta los cuatro perfiles, y CA-4f exige que cada uno declare qué abre). Sin los tres, CA-4e y CA-4f no existen.
4. **`a4_08` va entre `a4_05` y `a4_06`, no al final del bloque.** El plan decía «al final», pero `a4_06` es el cierre y `a4_07` el anexo: poner cuerpo detrás del anexo se lee como error de ensamblado en un documento calificado. Es una línea añadida en cada envoltorio y **ninguna línea existente cambia de contenido**, que es lo que la regla de frontera con US-UX-09 protege. **Desviación declarada del plan.**
5. **`a4_00_preliminares.tex` lo corrigió el orquestador, no una ola.** No estaba en ningún write-set y quedó falso en cinco puntos por el trabajo de esta US: decía «tres estados» de alcance (son cuatro), «el hallazgo que produjo un cambio» (fueron tres), su hoja de ruta omitía las dos secciones nuevas y numeraba el cierre como 6 (es 8), y su «Nota de herramienta» defendía haber construido **en lugar de** dibujar en un archivo de diseño, que contradice de frente la subsección «Las dos superficies del prototipo» que `a4_01` añade. Reescrito para decir lo que la entrega hace: las dos superficies, y ninguna sustituye a la otra.
6. **El cuarto estado de alcance no toca `EstadoAlcance`**, que sigue con tres valores porque etiqueta pantallas. El desdoblamiento «diseñada / sin diseñar» se aplica solo a capacidades e historias, fuera de las siete filas delimitadas por `% tabla-alcance:inicio/fin`. Así `alcancePrototipos.spec.ts` sigue siendo posible.
7. **La matriz 7×4 quedó en 10 / 9 / 9 sobre 28, no en el 9 / 12 / 7 que preveía CA-8.** La fila de exploración era `(b)(b)(c)(b)` y solo había una `(c)`; para llegar a 12 de otras historias harían falta tres. Se publica la medida con el párrafo que explica por qué la previsión no se cumplió. **La cifra no se forzó.**
8. **`indice.spec.ts:43` era un pin, no una barrera.** Fijaba `'navegable-sin-datos'` siete veces como valor de US-001 y enrojeció al corregir seis alcances, sin que nada estuviera roto. Pasa a comparar contra `PROTOTIPOS`, que es el contrato. La barrera real contra el entregable sigue siendo `alcancePrototipos.spec.ts`.
9. **Los colores se publican sin almohadilla** (`\texttt{0B1B2B}`). No es cosmético: el paso 4 de `scripts/verificar_tokens_a4.sh` corre `grep -lE '#[0-9A-Fa-f]{6}'` sobre **todos** los `contenido/a4_*.tex` y un solo hexadecimal con almohadilla lo pone en rojo. La regla alcanzó también a los comentarios de `design/emitir.py`.
10. **El cambio de rol acuña sesión real** contra `POST /api/auth/demo`, reutilizando `useSesion.iniciarSesionDemo`. Nunca se cambia el rol en el cliente. `useRolDemo` devuelve `ResultadoEntrada` y **no navega**, siguiendo el precedente de `usePermisos.expirarSesion`, para que las tres superficies decidan distinto sobre el mismo resultado. El `destino` se valida contra `RUTAS_CONTRATO` **dentro de `utils/guarda.ts`**, no en la pantalla.

## Ediciones sobre archivos de US-UX-09, con su alcance exacto

| Archivo | Alcance | Motivo |
|---|---|---|
| `contenido/a4_03_guia_estilos.tex` | **Solo la subsección 3.8**, «Modo oscuro…», líneas 159 y 161 en `aeafc6e`. El título pasa a «Modo oscuro, verificado y declarado» y su párrafo único se sustituye por tres. `git diff --stat`: **6 insertadas / 2 borradas**. `v1.0` intacto en la cabecera | CA-15: afirmaba que el sistema entrega una sola paleta y fijaba una condición de entrada que esta US cumple |
| `main_a4.tex` | **Una línea**: el `\IfFileExists` de `a4_08`, entre `a4_05` y `a4_06` | Sin ella `a4_08` no entra al PDF y `a4_05` deja dos referencias sin resolver |

## Verificación ejecutada

| Puerta | Resultado |
|---|---|
| `make check` | **exit 0** — ruff, mypy, eslint, typecheck, gitleaks (sin fugas, con su fixture de control) y mapa de permisos al día e idempotente |
| `bash scripts/verificar_tokens_a4.sh` | **las cinco en verde** — 11 anclas intactas, 37 nombres, un emisor por archivo, portal e informe al día, dos corridas byte a byte iguales, **22 archivos sin ningún hexadecimal**, v2.0/2026-08-16 y v1.0/2026-08-16 |
| `pytest tests/ml` | **91 pasan, 1 falla** (preexistente, abajo). Gate combinado `backend/app` + `ml`: **98.23 %** contra un piso de 70 % |
| `pytest tests/backend` | **794 pasan**, 17 saltadas por falta de `KARISMA_TEST_DATABASE_URL` |
| `pnpm test` (frontend) | **48 archivos, 875 pasan, 2 fallan** (preexistentes, abajo). Cobertura **94 % líneas** contra un piso de 50 % |
| `latexmk -xelatex main_a4.tex` | **90 páginas**, 0 referencias sin resolver, 0 `Overfull`, 0 reruns pendientes |
| `latexmk -xelatex main_completo.tex` | **238 páginas**, 0 referencias sin resolver, 0 `Overfull` |
| PDF de la entrega | `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` **regenerado**, 4.89 MB, con la portada de los tres integrantes |

**Las pruebas nuevas se verificaron por mutación**: para cada una se inyectó el defecto que declara atajar y se comprobó que enrojece. Las que no cambiaban de color se descartaron.

### Los tres fallos en rojo, corregidos

Los tres eran el mismo defecto de fondo, y ninguno venía de esta US: una expresión que exige `\n`
contra un archivo que en esta máquina está en disco con **CRLF**, por `core.autocrlf`.

| Fallo | Causa | Corrección |
|---|---|---|
| `tests/ml/test_seed_catalog.py::test_el_artefacto_versionado_esta_al_dia` | El generador escribe LF y comparaba contra un `db/seeds/catalog.sql` en CRLF | Regenerado con `python -m ml.data.seed_catalog`. **Cero cambio de contenido** (`git diff` vacío): solo el final de línea |
| `frontend/test/smokeRutas.spec.ts` ×2 | `/^RUTAS=\(\n…^\)$/m` no casaba contra `scripts/smoke_rutas.sh` en CRLF, y `?.[1] ?? ''` convertía el fallo en cero rutas en silencio | La expresión pasa a `/^RUTAS=\(\r?\n…^\)\s*$/m`. El guion no se tocó |

---

# Registro de verificación en navegador — 15-ago-2026

Entorno levantado con `docker compose up -d --build`: `db`, `api` y `web` sanos, `DEMO_LOGIN_ENABLED`
encendida. Ventana a **1440x900**, que es la resolución del protocolo de capturas.

> **`web` no monta el código**: su único volumen es el anónimo de `node_modules`, así que sirve lo
> horneado en la imagen. Cada corrección de frontend exige `docker compose up -d --build web` antes de
> volver a medir. Es lo que hizo que el primer fallo fuera real y no un artefacto del arnés.

## Los catorce recorridos

| # | Recorrido | Resultado |
|---|---|---|
| V1 | Las 4 combinaciones de tema y modo | **Pasa.** Cuatro suelos distintos y ninguno hereda del vecino: `F4F6F9`, `0A0A0C`, `FFFFFF`, `0B1B2B`. Los 17 tokens institucionales coinciden con §2.3, con `error` en los valores corregidos por la ola A |
| V2 | Persistencia sin destello | **Pasa.** El servidor devuelve `<html lang="es" data-tema="institucional" data-modo="oscuro">`. El atributo llega con el primer byte, no lo añade un script |
| V3 | Franja de alcance en las 4 combinaciones | **Pasa.** Presente en las cuatro |
| V4 | `/exploracion` con resultados | **Pasa.** Estado `listo`, «Se muestran 14 de 14 campos», `GET /api/catalog/search?q=saldo&limit=20` → 200 |
| V5 | `/exploracion` sin resultados | **Pasa.** Estado `vacio` con explicación, no una tabla sin filas |
| V6 | `/exploracion` con el api caído | **Pasa.** Con `docker compose stop api`: estado `error`, término `morosidad` intacto en el campo y control de reintento |
| V7 | `/exploracion` con rol sin permiso | **Pasa.** Con `analista` las dos continuaciones son enlaces; con `operativo` el estado `sin-permiso` se pinta, los enlaces desaparecen y dice qué perfil piden. URL intacta |
| V8 | Familia y métricas en las 4 combinaciones | **Pasa.** Lexend Deca bajo el tema de omisión, Inter bajo el institucional, y **0 desbordes** en las cuatro |
| V9 | Capturas del tema | **Pasa.** 11 PNG a 1440x900 en `figuras/a4/tema/`: las 7 pantallas bajo el tema institucional y las 4 combinaciones |
| V10 | Cambiar de rol desde el cromo | **Pasa.** Los cuatro acuñan sesión real; `GET /api/auth/me` devuelve el rol nuevo cada vez; `admin` gana `/administracion` en la barra lateral y los otros tres no |
| V11 | Cambiar a un rol sin permiso sobre la pantalla actual | **Pasa.** De `admin` a `operativo` sobre `/administracion` desvía a `/inicio` y **la tabla de usuarios no queda pintada** |
| V12 | Entrar en frío por URL directa | **Pasa.** Aviso «Gobierno del dato pide una sesión abierta», los cuatro perfiles antes del formulario, cada uno declarando qué abre, credenciales **sin prellenar**, y al elegir analista se aterriza en `/gobierno` |
| V13 | Entrar en frío a una pantalla prohibida | **Pasa.** «Entraste como Analista y Administración pide el perfil Administrador», con el enlace a `/inicio`. **No se pinta la pantalla prohibida y no se mueve a nadie en silencio** |
| V14 | Un clic desde el índice | **Pasa tras corregir un defecto** (abajo). Aterriza en `/gobierno` con sesión de `analista`, sin ver el formulario |

## Redirección abierta, probada con vectores hostiles

`destino` se validó con `https://evil.example/robo`, `//evil.example` y `/ruta-inventada`. **Los tres
aterrizan en `/inicio`**: ninguno sale del contrato y ninguno abandona el origen.

## Dos defectos que solo el navegador podía encontrar

**1. La tarjeta del índice nunca acuñaba sesión** (CA-4d2, V14). `BotonPrototipo` guardaba contra
`evento.defaultPrevented` para no robar un clic ya atendido por otro. Pero el clic lo atiende antes
**su propio `NuxtLink`**: `guardEvent` de vue-router llama a `preventDefault()` en fase de burbuja, y
el handler propio corría después, veía la bandera puesta y se retiraba. La tarjeta degradaba al
enlace de siempre —sin sesión, con el lector en el formulario— **con toda la suite en verde**, porque
el doble de `NuxtLink` de las pruebas es un `<a>` inerte que nunca previene nada.

- **Corrección**: `@click` pasa a `@click.capture`. La fase de captura corre antes que la de burbuja,
  y `guardEvent` se retira ante un evento ya prevenido, así que solo uno de los dos mueve al lector.
  Un clic con modificador sigue saliendo intacto al navegador, porque vue-router lo salta por la misma regla.
- **Prueba de regresión**: `rol.spec.ts` gana dos casos montados con el **`RouterLink` real**, no con
  el doble, y el clic se dispara sobre un descendiente del ancla para que la captura sea inequívoca.
  Comprobado: con `@click` enrojecen; con `@click.capture` pasan. El primer intento de esta prueba
  **pasaba sin el arreglo** —sin registrar el componente, `NuxtLink` no se resuelve y no ejerce nada—
  y se rehízo hasta que enrojeció por el motivo correcto.

**2. El modo se perdía al cruzar de layout.** `useModo` declara `data-modo` con `useHead` desde el
setup del store, y una entrada de `useHead` pertenece a la instancia que estaba activa al
registrarla. Dejado al primer lector, ese dueño era un control dentro de un layout: entrar por la
puerta de demostración cambia el layout `acceso` por `portal`, el dueño se desmonta, la entrada se
descarta y **el lector que eligió oscuro aterriza en una página clara mientras el selector sigue
diciendo oscuro**, hasta recargar. `useTema` no lo sufría porque `app.vue` siempre lo llamó.

- **Corrección**: `app.vue` instancia `useSistemaDiseno()` junto a `useTema()`. El chasis no se
  desmonta nunca, así que el modo tiene la misma vida que el tema.
- **Prueba de regresión** en `superficie.spec.ts`: el chasis registra los dos ejes, y antes del
  `await` del idioma, porque después el contexto de Nuxt ya no está.
- **Es preexistente**, no lo introdujo esta US: el defecto estaba en `data-theme` igual que en
  `data-modo`. Lo que esta US añadió fue el recorrido que lo hace visible.

## Pendientes cerrados en esta sesión

| Pendiente | Cierre |
|---|---|
| `make lint` no cubría `design/` | `design` entra a `ruff check`, `ruff format --check` y a la invocación de `mypy` que lleva `ml` y `tests/ml`, con el porqué escrito en el Makefile |
| `nuxt.config.ts` no listaba IBM Plex Mono | Declarada, con el mismo proveedor que las otras tres |
| `a4_06_cierre.tex` decía que el modo oscuro quedó fuera | Su fila lo dice completo: quedó fuera de la v1.0 de la guía, **y la condición se cumplió después**. Ninguna otra fila se movió |
| El docstring de `perfilFaltante` describía mal su rama | Reescrito: la rama no ocurre con el contrato de hoy y se dice por qué se conserva |
| `a4_08` no publicaba las capturas del tema | Subsección nueva con la tabla de medición en navegador de las 4 combinaciones y tres figuras del tema |

## Verificación final

| Puerta | Resultado |
|---|---|
| `make check` | **exit 0** |
| `make test` | **814 pytest pasan, 0 fallan** (17 saltadas por falta de base de integración) · **48 archivos y 880 pruebas de vitest, 0 fallan** |
| Cobertura | backend + ml **98.23 %** (piso 70) · frontend **94.03 % líneas, 85.64 % ramas** (piso 50) |
| `bash scripts/verificar_tokens_a4.sh` | **las cinco en verde**, 22 archivos sin un solo hexadecimal |
| `latexmk -xelatex main_a4.tex` | **92 páginas**, 0 referencias sin resolver, 0 `Overfull` |
| `latexmk -xelatex main_completo.tex` | **240 páginas**, 0 referencias sin resolver, 0 `Overfull` |
| PDF de la entrega | `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` regenerado, 5.13 MB, 92 páginas |
| `figuras/a4/{antes,despues}` | **Sin una sola modificación** (`git status` vacío sobre las dos carpetas) |

## Nube y schema

**No se tocó ninguno de los dos.** Ningún recurso de nube, ningún comando, ningún secreto, ninguna
revisión desplegada. Ninguna migración: la preferencia de tema vive en la cookie `karisma_tema`, que
es preferencia de presentación por dispositivo. `db/seeds/catalog.sql` se regeneró sin cambio de
contenido, y el esquema no se movió.

## Lo que queda abierto

1. **`comun/EstadoPendiente.vue` sigue en disco** y ya no lo monta ninguna pantalla. Solo lo nombran
   dos pruebas, una de ellas para comprobar su ausencia. Borrarlo es de quien lo necesite.
2. Los pendientes 3, 4 y 5 de la apertura siguen abiertos y **fuera del alcance declarado de esta
   US**: los ocho valores oficiales de los estados interactivos (hoy derivados por regla escrita), la
   ranura de acción en el contrato de 17 tokens, y si `design/` merece guía propia.

## Lo que falta para entregar

- **Commit**: la rama queda lista y **sin commitear, a la espera de visto bueno**. Sin PR
  (discrepancia RU-11 declarada).
- Subir `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` a Canvas antes del **dom 16, 20:00**.

---

# Fase de QA y Testing — 15-ago-2026

Ámbito: **solo los archivos del diff** contra `aeafc6e`. 41 modificados y 15 nuevos, en `design/`,
`frontend/`, `docs/`, `tests/` y el `Makefile`.

## 1-2. Gates

| Gate | Resultado |
|---|---|
| `make check` | **exit 0**. ruff, ruff format, mypy, eslint, `nuxt typecheck`, gitleaks (sin fugas, con su fixture de control probando que el escaneo detecta) y mapa de permisos al día e idempotente |
| `make test` | **814 pytest pasan, 0 fallan** (17 saltadas por falta de base de integración) · **48 archivos y 880 pruebas de vitest, 0 fallan** |
| Cobertura backend + ml | **98.23 %** contra un piso de 70 % |
| Cobertura frontend | **94.03 % sentencias · 85.64 % ramas · 94.1 % líneas** contra un piso de 50 % |

Cobertura por archivo del diff, la más baja primero: `sistemaDiseno.ts` 76.66 · `useRolDemo.ts` 90.9 ·
`auth.global.ts` 90.9 · `useTema.ts` 93.33 · `SelectorRol.vue` 93.33 · `components/exploracion` 97.75 ·
`components/comun` 96.82 · `components/nav` 100 · `acceso.vue`, `guarda.ts`, `navegacion.ts`,
`index.vue` al 100 % de líneas. **Ninguno por debajo del piso.**

## 3. Auditoría de seguridad del diff

El subagente `security-reviewer` **murió por un error de API**; la auditoría la ejecutó el orquestador
sobre el mismo alcance. Vector por vector:

| Vector | Veredicto | Evidencia |
|---|---|---|
| **Redirección abierta** por `?destino=` | **Limpio** | `destinoDeRetorno` (`utils/guarda.ts:97`) es una **lista blanca**: normaliza quitando query, hash y barra final, y luego exige `RUTAS_CONTRATO.includes(ruta)` con igualdad exacta. Rechaza además `/acceso` para cerrar el bucle. Rutas externas, `//host`, `javascript:`, rutas fuera del contrato y variantes de caja **fallan cerrado**. Probado en navegador con tres vectores: los tres aterrizan en `/inicio` |
| **Doble validación** | **Limpio** | Se valida en la guarda (`guarda.ts:152`) **y** en la pantalla (`acceso.vue:92`). La pantalla no confía en su propio query string |
| **Rol cambiado en el cliente** | **Limpio** | No existe ninguna asignación local de rol. `useRolDemo.entrarComoRol` llama a `useSesion.iniciarSesionDemo`, que es `POST /api/auth/demo`. Confirmado en navegador: `GET /api/auth/me` devuelve el rol nuevo en las cuatro opciones |
| **Escalada de privilegios** | **Limpio** | `backend/`, `db/` y `ml/` **intactos** desde el SHA base: ninguna ruta, ningún scope, ninguna migración. `permisos.generated.ts` y `docs/security.md` **sin cambio de contenido**. V11 comprueba que al bajar de `admin` a `operativo` sobre `/administracion` la tabla de usuarios **no queda pintada** |
| **Middleware desactivado** | **Limpio** | `auth.global.ts` sigue siendo global y su diff son 8 líneas que solo serializan `destino` y `motivo`. Ninguna salida nueva. `motivo` es obligatorio en el tipo, así que no puede colarse un `motivo=undefined` |
| **Credenciales prellenadas** | **Limpio** | Ningún `value` con usuario o contraseña en `acceso.vue` ni en `SelectorDemostracion.vue` |
| **Gating de la puerta** | **Limpio** | `demoAcceso` sale de `useRuntimeConfig().public`, derivado de la variable de entorno. Los tres consumidores lo respetan y hay prueba de montaje con la bandera en falso |
| **Fugas de secretos** | **Limpio** | gitleaks sin hallazgos sobre 48.9 MB. Ninguna contraseña, token ni prompt crudo en el diff ni en `docs/entregables/` |
| **Fuga de datos por rol** | **Limpio** | `AccionesCatalogo.vue` muestra a un `operativo` los **nombres de ruta del mapa A3**, que son públicos y ya están en el entregable. No renderiza ni un dato |

**Sin hallazgos de seguridad.**

## 4-5. Revisión de código y archivos generados

Las líneas ❌ de `frontend/AGENTS.md` y `docs/AGENTS.md`, una por una sobre el diff:

| Regla | Resultado |
|---|---|
| ❌ Texto visible dentro del componente | **Limpio**. Ninguna cadena suelta en los componentes nuevos; todo por i18n, en los dos catálogos, con paridad probada |
| ❌ Editar `main.css` a mano | **Limpio y comprobado por regeneración**: `python -m design.emitir --verificar` sale 0, es decir el disco coincide byte a byte con lo que produce la fuente. No fue edición manual |
| ❌ `routeRules` con `swr` | **Limpio**. Ninguna |
| ❌ Tiempo futuro en los `.tex` | **Limpio** |
| ❌ Emojis | **Limpio** |
| ❌ `print()` en producción | **Limpio**. El único `print` añadido está en el `main()` de `design/emitir.py`, que es una herramienta de línea de comandos, y solo reformatea uno que ya existía |
| ❌ Trailer `Co-Authored-By` | **Limpio**. No hay commits nuevos |
| ❌ Colores a mano en los `.tex` | **Limpio**. 22 archivos revisados, cero hexadecimales |
| DRY y separación de capas | **Limpio**. `useBusquedaCatalogo` se reutilizó sin tocarla; `useSesion.iniciarSesionDemo` se reutilizó en vez de abrir una segunda puerta; la validación del destino vive en una función y la llaman los dos consumidores |

**Archivos de 'No tocar' que el diff toca**: `main.css` y `tokens.generated.ts`, los dos **regenerados
por su emisor y verificados**, no editados. `permisos.generated.ts`, `a4_tokens.tex`, `a4_tokens.json`
y `uxdoc.sty` aparecen en `git status` pero **su diff de contenido está vacío**: solo cambió el final
de línea al regenerar. `figuras/a4/{antes,despues}` **sin una sola modificación**.

## 6-7. Checklist de interfaz

Las diez reglas de `docs/orchestration/checklist-ui.md` sobre los componentes nuevos: escala de
radios, familia única de iconos, sin SVG a mano, una sola acción primaria, sin `scroll` a mano —
**todas limpias**.

**Los cuatro estados no felices de `/exploracion`, construidos y verificados en navegador**: vacío con
explicación (no una tabla sin filas), cargando con esqueleto de la altura de las filas, error
**conservando el término escrito** con control de reintento, y sin permiso de zona que retira los
enlaces y dice qué perfil piden.

## 8. Criterios de aceptación contra el código real

| CA | Criterio | Estado | Evidencia |
|---|---|---|---|
| CA-1 | Dos temas, 17 tokens, 4 combinaciones | **Pasa** | 17 tokens resueltos en las cuatro |
| CA-2 | El tema de omisión no se mueve | **Pasa** | Prueba de fijación escrita **antes** de tocar `sistema.py`, en verde |
| CA-3 | Cero incumplimientos | **Pasa** | `incumplimientos()` vacío en las cuatro |
| CA-4 | Separación bajo dicromacia | **Pasa** | 13.6 / 21.5 (omisión) y **14.5 / 22.6** (institucional), sobre pisos de 13.6 y 21.5 |
| CA-4b | Cromo con dos temas y cuatro roles | **Pasa** | V10, con el activo marcado y cero cadenas en los componentes |
| CA-4c | El cambio de rol acuña sesión real | **Pasa** | V10: `POST /api/auth/demo` y `GET /api/auth/me` con el rol nuevo, cuatro de cuatro |
| CA-4d | El selector desaparece sin la bandera | **Pasa** | Prueba de montaje con la bandera en falso |
| CA-4d2 | La tarjeta del índice entra con su rol | **Pasa tras corregir** | V14: un clic a `/gobierno` con sesión de analista. **Defecto encontrado y corregido** |
| CA-4e | El rebote se explica y devuelve | **Pasa** | V12 más tres vectores hostiles rechazados |
| CA-4f | Los perfiles, camino principal | **Pasa** | V12: preceden al formulario y cada uno declara qué abre |
| CA-5 | El tema persiste sin destello | **Pasa** | V2: el servidor emite `data-tema` con el primer byte |
| CA-6 | Los dos temas con sus dos modos | **Pasa** | V1: cuatro suelos distintos, ninguno hereda del vecino |
| CA-7 | `/exploracion` deja de ser andamiaje | **Pasa** | `grep -c EstadoPendiente` = **0**; compone desde `useBusquedaCatalogo` |
| CA-8 | Los cuatro estados no felices | **Pasa con desviación** | Los cuatro construidos (V4 a V7). La matriz quedó en **10/9/9**, no en el 9/12/7 previsto, y el documento explica por qué |
| CA-9 | Las etiquetas dicen la verdad | **Pasa** | `alcancePrototipos.spec.ts` en verde contra el `.tex`; `/asistente` conservada |
| CA-10 | Cuarto estado de alcance | **Pasa** | Publicado en `a4_05`, **sin tocar** `EstadoAlcance` ni las siete filas delimitadas |
| CA-11 | Cinco flujos como diseño | **Pasa** | 13 pies con la palabra diseño en `a4_08` |
| CA-12 | Segunda iteración documentada | **Pasa** | `a4_04` con tres hallazgos, cada uno con su antes y su después numérico |
| CA-13 | Inter sin desajustar la maquetación | **Pasa** | V8: Inter bajo el tema institucional, Lexend Deca bajo el de omisión, **0 desbordes** en las cuatro |
| CA-14 | El acceso al archivo de trabajo | **Pasa en código, falta juicio humano** | Enlace y los tres nodos publicados en `a4_01`. **Que abra para quien califica es M6** |
| CA-15 | La guía deja de declarar una sola paleta | **Pasa** | Subsección reescrita, 6 insertadas y 2 borradas, ninguna otra línea |
| CA-16 | El PDF listo | **Pasa** | 92 páginas, 0 referencias sin resolver, 0 `Overfull`, portada de los tres |
| CA-17 | El avance al documento acumulado | **Pasa** | 240 páginas, parte IV completa, portadilla y «Sobre este documento» actualizados |
| CA-18 | QA gate | **Pasa** | `make check` exit 0, `make test` sin un solo fallo |

**24 de 24.** Una con desviación declarada (CA-8) y una que necesita juicio humano (CA-14).

## 9. Búsqueda de bugs similares previos

`mem_search` sobre el defecto de `preventDefault`/`NuxtLink` y sobre el de la vida de la entrada de
`useHead`: **sin resultados**. No hay precedente registrado. Los dos quedaron guardados con su regla
general, porque son de la clase que se repite.

## Bugs encontrados en esta fase

**Ninguno nuevo.** Los dos defectos de esta US los encontró la sesión de navegador y están corregidos,
con prueba de regresión verificada por mutación en los dos casos. Los tres rojos preexistentes de CRLF
también quedaron cerrados.

## Una desviación del checklist de interfaz, para que la decida el equipo

La regla 4 de `checklist-ui.md` dice **«ni negro puro ni blanco puro»**. El tema institucional usa
`FFFFFF` como suelo en modo claro, porque es el valor que declara el archivo de diseño como
superficie. En oscuro **sí** cumple: `0B1B2B`, azul profundo y no negro. No es un color escrito a
mano en un componente —vive en `design/sistema.py` con su procedencia citada— pero la regla se
incumple en la letra. **No se cambió por cuenta propia**: es la superficie declarada de la identidad
institucional y moverla es decisión del equipo.

## Documento de prueba manual

`docs/manual-test/us-entrega-a4.md`, nueve pasos: solo lo que exige navegador real, PDF abierto o
juicio humano. Los catorce recorridos automatizados se listan ahí para que nadie los repita a mano.
---

# Segunda fase de QA — 15-ago-2026, 15:30

Ámbito: los archivos de `git diff --name-only aeafc6e`, el ancla que fija la cabecera de este
handoff. Ejecutada de cero, sin dar por buena la fase anterior.

> **El hallazgo que ordena todos los demás.** El ancla `aeafc6e` ya **no aísla esta US**. La rama
> sigue sin commitear y sobre el mismo árbol arrancó **US-A4-EXCELENCIA**, cuyo propio handoff
> declara el mismo SHA base y lo llama «diff acumulado». Las marcas de tiempo lo separan sin
> ambigüedad: todo lo de esta US va de 08-14 19:18 a 08-15 03:07, y a las **13:55-13:56** del 15-ago
> se reescribieron `design/sistema.py` y `design/emitir.py` y se regeneraron `main.css` y
> `tokens.generated.ts`.
>
> Sin commits intermedios **el estado verificado de esta US es irrecuperable**: no hay árbol contra
> el que reproducir las cifras de la primera fase. Las cinco entradas de abajo son las que existen
> hoy, y las cinco las introdujo la US posterior sobre la capa que ésta entregó.

## Gates, vueltos a correr

| Gate | Primera fase | Ahora | Nota |
|---|---|---|---|
| `make check` | exit 0 | **FALLA** | Aborta en el primer comando: `ruff` E501 en `design/sistema.py:176` (89 > 88). gitleaks y el mapa de permisos **ni se ejecutan** |
| `make test` | 814 pytest, 0 fallan | **FALLA** | 2 fallan en `tests/ml/test_contraste_temas.py`; vitest **ni se ejecuta**, porque make aborta |
| vitest, corrido aparte | 880 pasan | **1 falla** de 881 | `laminas.spec.ts` |
| gitleaks, corrido aparte | limpio | **limpio** | 51.03 MB, sin hallazgos |
| mapa de permisos, aparte | al día | **al día** | Idempotente, con su cabecera de generado |
| `ruff format` · mypy ×2 · eslint · `nuxt typecheck` | verdes | **verdes** | 118 formateados; 87 y 25 archivos sin incidencias |
| `verificar_tokens_a4.sh` | 5 en verde | **5 en verde** | 22 archivos sin un hexadecimal |
| `design.emitir --verificar` | — | **exit 0** | 21 colores: el disco coincide con la fuente |

**Nota de método**: la primera fase midió con `make check 2>&1 | tail -N`. En una tubería el estado
de salida es el de `tail`, no el de `make`: el gate puede estar en rojo y la corrida leerse como
verde. Las cifras de la primera fase se emitieron con esa lectura y no se pueden dar por buenas.

## Bugs encontrados

| ID | Bug | Severidad | Origen | Evidencia |
|---|---|---|---|---|
| **QA-1** | `make check` en rojo. `design/sistema.py:176` mide 89 caracteres contra el límite de 88. `ruff format` no lo arregla: es un literal de cadena y no se puede partir solo | **Bloqueante** — es el gate del PR y no hay CI que lo repita | US-A4-EXCELENCIA, 13:55 | `ruff check` exit 1, un solo error |
| **QA-2** | La prueba de fijación del tema de omisión y la de los 17 tokens, en rojo. El contrato pasó a **21 tokens**: `reticula`, `accion`, `accion-apoyo` y `seleccion`. `tests/ml/test_contraste_temas.py` quedó sin actualizar | **Bloqueante** — es la barrera declarada de CA-2 y aborta `make test` | US-A4-EXCELENCIA, 13:55 | `assert 21 == 17`. El diff dice «Omitting 17 identical items»: **los 17 valores del tema de omisión no se movieron**, falla la cuenta y no la fijación |
| **QA-3** | La decisión 10 de esta US —«el color de acción no entra en los 17 tokens»— está **revertida en el código y vigente en el documento**. `a4_08` le dedica una subsección entera a defenderla, y `a4_04` y `a4_07` dicen «diecisiete» | **Alta** — el PDF que se sube afirma algo que la fuente contradice | US-A4-EXCELENCIA, 13:55 | `a4_08:195`, `a4_04:213`, `a4_07:99-100` contra `design/sistema.py` |
| **QA-4** | La lámina de paleta de `/guia` anuncia «21 tokens de color» y pinta **18**. El emisor añadió un quinto grupo, `ACCION`; `stores/sistemaDiseno.ts` no lo expone y los `GRUPOS` de `LaminaPaleta.vue` siguen siendo cuatro | **Alta** — la guía viva es artefacto calificado de A4 y se contradice en su propio encabezado | US-A4-EXCELENCIA, 13:56 | `laminas.spec.ts` en rojo: `expected '...' to contain 'seleccion'` |
| **QA-5** | `a4_08` publica el `info` institucional en claro como `123C7A`; el emisor produce hoy `17395B`. Los otros 16 valores de la tabla reproducen exactos | **Media** — una cifra del entregable que la fuente ya no sostiene | US-A4-EXCELENCIA, 13:55 | Volcado del emisor contra `a4_08:75` |

**Ninguno de los cinco lo introdujo el trabajo de US-ENTREGA-A4.** Los cinco son daño colateral de
haber construido una US sobre el árbol sin commitear de otra, sin correr la barrera que la zona
sensible de las dos US manda correr «antes de cada ola».

## Lo que sí se sostiene

Auditado sobre el diff, con el ruido de la US posterior descontado:

| Frente | Veredicto |
|---|---|
| **Seguridad** | **Sin hallazgos.** `backend/`, `db/` y `ml/` intactos desde el SHA base: ninguna ruta, ningún scope, ninguna migración. `destinoDeRetorno` (`utils/guarda.ts:97`) es lista blanca por igualdad exacta contra `RUTAS_CONTRATO`, con `/acceso` excluido, y se valida **dos veces**, en la guarda y en la pantalla. Ninguna asignación local de rol: `useRolDemo` acuña contra `POST /api/auth/demo`. `auth.global.ts` sigue siendo global y su diff solo serializa `destino` y `motivo`. Sin credenciales prellenadas. `ruff --select=S` sobre `design/` limpio. gitleaks limpio |
| **Líneas ❌ de las guías** | Todas limpias. Sin `data-theme` escrito —solo citado en prosa al explicar el renombrado—, sin `routeRules` con `swr`, sin emojis, sin cadenas visibles fuera de i18n en los componentes nuevos, sin colores a mano en los `.tex` sobre 22 archivos, y `print()` solo en el `main()` de `design/emitir.py`, que es herramienta de línea de comandos |
| **Archivos de 'No tocar'** | `main.css` y `tokens.generated.ts` **regenerados por su emisor**, no editados: `design.emitir --verificar` sale 0. `permisos.generated.ts` al día e idempotente. `figuras/a4/{antes,despues}` **sin una sola modificación**. Espejos `AGENTS.md`/`CLAUDE.md` byte a byte idénticos en `frontend/` y en `docs/` |
| **Cobertura** | Frontend **93.97 % sentencias · 85.34 % ramas · 94.03 % líneas**, piso 50. El más bajo del diff es `sistemaDiseno.ts` con 76.66; le siguen `useRolDemo.ts` 90.9, `auth.global.ts` 90.9, `useTema.ts` 93.33 y `SelectorRol.vue` 93.33. `guarda.ts`, `navegacion.ts` y `acceso.vue` al 100 de líneas. Backend y ml **98 %**, piso 70 |
| **Cuatro estados no felices** | Los cuatro construidos y marcados con `data-estado` en `ResultadosCatalogo.vue`: `error` con `role="alert"`, código y control de reintento; `cargando` con esqueleto `h-20` contra filas `min-h-20`, **sin salto de maquetación**; `vacio` con explicación en vez de una tabla sin filas; y `sin-permiso` desde la guarda vía `marcarBloqueo` |
| **Paridad i18n** | `contratos.spec.ts` en verde: los dos catálogos aplanados coinciden |
| **DRY y capas** | La decisión del destino vive en una función y la llaman los dos consumidores; `useRolDemo` reutiliza `useSesion.iniciarSesionDemo` en vez de abrir una segunda puerta; `useBusquedaCatalogo` se reutilizó sin tocarla. La guarda es función pura y el middleware solo pega |

## Criterios de aceptación, revisados contra el árbol de hoy

CA-3, CA-4, CA-4b a CA-4f, CA-5 a CA-13 y CA-15 a CA-17 se sostienen: las pruebas de contraste y de
separación bajo dicromacia pasan en las cuatro combinaciones también con 21 tokens. Los que cambian
de estado son cuatro.

| CA | Estado en la 1.ª fase | Ahora | Motivo |
|---|---|---|---|
| CA-1 | Pasa | **Falla** | El contrato ya no es de 17 tokens (QA-2, QA-3) |
| CA-2 | Pasa | **Falla en la barrera** | La fijación está en rojo, aunque los 17 valores no se movieron (QA-2) |
| CA-14 | Pasa en código, falta juicio humano | **Igual** | Sigue siendo M6 |
| CA-18 | Pasa | **Falla** | `make check` y `make test` en rojo (QA-1, QA-2) |

**21 de 24**: tres caídos por la US posterior y uno pendiente de juicio humano.

## Desviaciones que siguen abiertas, sin cambio

1. **Regla 4 de `checklist-ui.md`**, «ni negro puro ni blanco puro»: el suelo institucional en claro
   es `FFFFFF`. Vive en `design/sistema.py` con su procedencia citada, no escrito a mano en un
   componente. Es decisión del equipo, no de QA.
2. **CA-8** publicó la matriz medida 10/9/9 en vez del 9/12/7 previsto, con su párrafo explicando
   por qué. La cifra no se forzó.
3. `frontend/AGENTS.md` declara **45** `*.spec.ts` y hay **48**. Deriva menor de la guía respecto de
   su carpeta, del mismo tipo que el pendiente 6 de la apertura.

## Documento de prueba manual

`docs/manual-test/us-entrega-a4.md` actualizado: aviso de cabecera sobre el árbol combinado, y dos
pasos nuevos. **M10**, el clic en la zona muerta de la tarjeta del índice, que es la mitad que la
prueba de regresión no ejerce —dispara sobre un descendiente a propósito, y en el ancla misma el
navegador ordena por registro y no por fases; una sonda en happy-dom con el `RouterLink` real sí
acuña sesión, pero eso no decide una regla de despacho de eventos—. Y **M11**, la lámina de paleta
de `/guia`.

## Qué hace falta para cerrar

1. **Separar las dos US en commits.** Es lo primero: sin eso ninguna cifra de esta US es
   reproducible y la siguiente sesión hereda el mismo nudo.
2. Cerrar QA-1 partiendo la cadena de `design/sistema.py:176`.
3. Cerrar QA-2 actualizando `tests/ml/test_contraste_temas.py` al contrato de 21, **conservando la
   fijación byte a byte de los 17 valores del tema de omisión**, que es lo que sostiene las capturas
   ya entregadas.
4. Decidir QA-3 y QA-5: o el documento se realinea con el emisor, o la US posterior revierte. Es
   decisión de alcance, no de QA, y toca el PDF que se sube el domingo.
5. Cerrar QA-4 exponiendo `ACCION` en el store y en `GRUPOS`.

---

# Corrección de los bloqueantes — 15-ago-2026, 16:05

Encargo: **separar las dos US** —US-A4-EXCELENCIA queda como planeación, así que el trabajo de
color del 15-ago se absorbe aquí— y **corregir todo lo bloqueante**. Se corrigieron los tres que
tumbaban un gate. QA-3 y QA-5 no lo son y siguen abiertos, ahora bajo esta US.

## Los tres cerrados

| ID | Corrección | Archivo |
|---|---|---|
| **QA-1** | La cadena de 89 caracteres se parte en dos literales con concatenación implícita, que es el patrón que ya usan los otros tokens del archivo. **El emitido no cambia**: Python concatena en tiempo de compilación, así que `design.emitir --verificar` sigue saliendo 0 y ningún byte de `main.css` ni de `tokens.generated.ts` se mueve | `design/sistema.py:176` |
| **QA-2** | La fijación pasa al contrato de 21, **en dos mitades y el corte es lo importante**. `FIJACION_ENTREGADA` son los 17 de `aeafc6e`, que es sobre lo que descansan las capturas y el PDF ya publicados, y no se toca. `FIJACION_AMPLIACION` son las cuatro ranuras nuevas. `FIJACION_CORRIENTE` es la unión, así que una deriva en cualquiera de las dos mitades enrojece. La cuenta pasa a 21 y el nombre de la prueba con ella | `tests/ml/test_contraste_temas.py` |
| **QA-4** | El store expone `accion` junto a los otros cuatro grupos y `LaminaPaleta.vue` lo recorre, en el orden en que el emisor dispone `TOKENS`. Clave `guide.palette.group.action` a los dos catálogos en el mismo cambio | `stores/sistemaDiseno.ts` · `components/guia/LaminaPaleta.vue` · `i18n/locales/{es,en}.json` |

**Bajo el tema de omisión ninguna de las cuatro ranuras nuevas es un color nuevo**: `reticula` es
`grid`, `accion` es `corriente-pleno` y `accion-apoyo` es `corriente-medio`. Solo `seleccion` es un
par genuinamente nuevo, y es un tinte que nada de lo entregado pintaba. Es la razón de que el tema
que sostiene los artefactos publicados **no se mueva un píxel** aunque el contrato crezca.

## Verificación por mutación

Los tres se validan por la vía más fuerte que hay: **las tres pruebas estaban en rojo antes del
cambio y en verde después**, y ninguna se tocó para que dejara de mirar. `test_contraste_temas.py`
fallaba con `assert 21 == 17`; `laminas.spec.ts` fallaba con `expected '...' to contain 'seleccion'`.
La prueba de la lámina siguió siendo la misma línea: lo que cambió fue la página que mide.

## Gates, con el estado de salida leído de verdad

Medidos con redirección a archivo y `$?`, no con tubería.

| Gate | Resultado |
|---|---|
| `make check` | **exit 0**, completo — ruff, ruff format, mypy ×2, eslint, `nuxt typecheck`, gitleaks con su fixture de control, y mapa de permisos al día e idempotente. Esta vez sí llegó al final |
| `make test` | **exit 0** — **814 pytest pasan, 0 fallan**, 17 saltadas por falta de base de integración · **48 archivos y 880 pruebas de vitest, 0 fallan** |
| Cobertura backend + ml | **98.23 %**, piso 70 |
| Cobertura frontend | **94.03 % sentencias · 85.64 % ramas · 94.1 % líneas**, piso 50. `LaminaPaleta.vue` 95.45 |
| `design.emitir --verificar` | **exit 0**, 21 colores: el disco coincide con la fuente |
| `verificar_tokens_a4.sh` | **las cinco en verde** |

## Criterios de aceptación, otra vez

| CA | Antes de la corrección | Ahora |
|---|---|---|
| CA-1 | Falla | **Pasa con alcance corregido** — el contrato es de 21 tokens, no de 17. El criterio se cumple en su sustancia (dos temas, todos los tokens resueltos en las cuatro combinaciones); lo que cambió es la cifra, y el documento todavía no lo dice |
| CA-2 | Falla la barrera | **Pasa** — los 17 valores entregados fijados byte a byte en `FIJACION_ENTREGADA`, en verde |
| CA-18 | Falla | **Pasa** — los dos gates en exit 0 |
| CA-14 | Juicio humano | Igual: M6 |

**23 de 24**, con CA-1 cumplido sobre un contrato de 21 y CA-14 esperando juicio humano.

## Lo que sigue abierto y ya no se puede diferir

Con US-A4-EXCELENCIA reducida a planeación, **QA-3 y QA-5 son de esta US** y tocan el PDF que sube
el domingo:

| ID | Qué dice el documento | Qué dice la fuente |
|---|---|---|
| **QA-3** | `a4_08:195` dedica una subsección a «El color de acción no entra en los diecisiete tokens»; `a4_08:57-64`, `a4_04:213` y `a4_07:99-100` dicen «diecisiete» | `design/sistema.py` tiene 21 tokens y `accion` es uno de ellos |
| **QA-5** | `a4_08:75` publica el `info` institucional en claro como `123C7A` | El emisor produce `17395B`. Los otros 16 valores de la tabla reproducen exactos |

Son edición de `.tex` y recompilación del PDF, no código. **No se tocaron**: cambiar el alcance de
un entregable calificado no es decisión de QA, y la subsección de QA-3 no se corrige borrándola —hay
que decir qué hace el color de acción en el sistema, que es justamente lo que la US de excelencia
planea.
