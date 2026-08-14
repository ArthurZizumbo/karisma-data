# Planeación US-ENTREGA-A4 — Consolidación de la entrega de la Actividad 4

**Estado**: planning
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantalla de catálogo)
**Actividad**: A4 (dom 16-ago-2026) — apartado 3, prototipos, 50 % = 12.50 de 25; apartado 4, guía de estilos, 45 % = 11.25
**Sprint**: S4, cierre
**Rama**: `us-entrega-a4`, desde la punta de `us-ux-07`. Una rama por US, commits locales encadenados, **sin PR** (discrepancia RU-11 declarada, no corregida)
**SHA base**: se fija al abrir implementación con `git rev-parse --short HEAD` y se escribe en el handoff. Ancla del diff: `git diff --name-only <sha_base>`. **QA no usa `HEAD~N`**
**Estimación**: 13 SP en cuatro bloques independientes
**Fuente normativa**: §26 del plan para S4 · §25.5-2 para las capacidades prometidas · el handoff de US-UX-07 para lo ya construido

> **De qué habla este documento.** La Actividad 4 la produjo el equipo completo y se entrega como un
> solo trabajo. Una parte se construyó en el stack del producto y otra en Figma, y las dos describen
> el mismo portal: la misma arquitectura de la Actividad 3, las mismas personas de la Actividad 1 y
> el mismo sistema de diseño. Esta planeación consolida las dos mitades en **una entrega**, y el
> documento resultante habla del producto, nunca de quién hizo qué parte ni de una mitad frente a la
> otra.
>
> **Lo que salga de aquí es lo que se entrega.** No es un borrador ni un insumo para otra pasada: el
> PDF que produce la ola D, con el nombre que pide la actividad, es el archivo que sube a Canvas. Por
> eso el plan llega hasta la compilación, el renombrado y la subida, y no se detiene en el contenido.
> **Y el mismo avance entra al documento acumulado del proyecto**, `main_completo.tex`, que es el
> volumen que encadena las cinco actividades: una entrega que solo existiera en su envoltorio semanal
> dejaría al acumulado describiendo una versión anterior del producto.

---

## Lectura previa ejecutada

| Paso | Resultado |
|---|---|
| `docs/us-handoff/us-entrega-a4.md` | **No existe.** Se crea con estado `planning` al cerrar esta planeación |
| `docs/us-handoff/us-ux-07.md` | Leído completo, incluido el registro de implementación del 14-ago. De ahí salen los pendientes 1, 2 y 3, que esta US absorbe |
| `frontend/AGENTS.md` | Leído. Es la guía que manda sobre las olas B y C |
| `docs/AGENTS.md` | Leído. Manda sobre la ola D |
| `design/` y `scripts/` | **Sin guía propia** (routing de la raíz). Las reglas aplicables son las de la raíz más lo que `frontend/AGENTS.md` declara sobre archivos generados |
| `mem_search "entrega A4 tema institucional Figma tokens"` | **Sin resultados.** No hay decisión previa registrada sobre un segundo tema |
| `docs/us-resolved/` | **No existe.** No hay US previa de la que copiar |
| `docs/entregables/figma/*.pdf` | Tres exportes **con capa de texto**: guía de estilo, componentes y prototipos. Fuente de los tokens exactos |
| `docs/orchestration/auto-invoke.md` | Leído. Las skills por ola quedan escritas en §5 |

---

## Confirmación del 'Estado' contra el repositorio

Verificado con `grep` y `ls`, no supuesto.

| Comprobación | Resultado |
|---|---|
| `ls frontend/test/*.spec.ts \| wc -l` | **42** |
| `grep -rl EstadoPendiente frontend/app/` | **Solo `pages/exploracion/index.vue`**. Es el único andamiaje que queda |
| `grep -rn data-theme frontend/app/` | `main.css:117`, `main.css:148` y `composables/useModo.ts:62`. **El atributo transporta el modo, no un tema** |
| `ls frontend/app/components/` | 13 familias. **No existe `exploracion/`** |
| `grep -rl useBusquedaCatalogo frontend/app/` | Solo `components/gobierno/DiccionarioCampos.vue` |
| `ls db/migrations/ \| tail -5` | Cinco migraciones, la última `20260813205114_add_app_user_updated_at.sql` |

Ver §11 para las discrepancias que esto abre contra las guías.

---

## Ambigüedades del encargo, resueltas antes de planear

**1. Los dos temas conviven.** El tema construido queda **de omisión** y el tema de Figma entra como **opción seleccionable**. Ninguno sustituye al otro. Porqué: el tema de omisión sostiene las 15 capturas del entregable, la matriz de 44 pares y la iteración documentada; sustituirlo invalidaría evidencia ya producida a dos días del cierre. Y porque el encargo pide exactamente eso.

**2. Cómo se llaman, por dentro y en pantalla.** Por dentro, `corriente` e `institucional`. En pantalla, el selector los nombra con **claves i18n** en los dos catálogos: el primero por su mundo visual —el diagrama de línea hombre-máquina que declara `design/sistema.py`— y el segundo por el suyo. Porqué: nombrarlos por número obliga a recordar cuál es cuál, y nombrarlos por autor convierte una opción en una disputa. **Ninguna de las dos cadenas se escribe dentro del componente**, que es la regla de la capa.

**3. El tema institucional lleva modo oscuro.** Se diseña y se verifica con la misma maquinaria que el otro, no se hereda ni se aproxima. Porqué: es lo que el encargo pide, y un tema con un solo modo obligaría a bloquear el selector, que es peor experiencia que dos temas completos. El suelo del modo oscuro institucional es `#0B1B2B`, un azul profundo derivado de su color de navegación, nunca negro puro, que es la regla que el sistema ya se puso.

**4. Los ocho estados interactivos se derivan por regla escrita.** El archivo de Figma los declara como referencias a variables (`--karisma-action-primary-hover` y siete más) sin valor hexadecimal. Se derivan oscureciendo el 12 % para `hover` y el 20 % para `pressed` sobre el color base, que es la relación que las propias muestras exhiben, y **la derivación se marca como tal en la guía**. Porqué: bloquear un tema entero por ocho valores derivables sería desproporcionado, y presentarlos como si vinieran del archivo sería atribuirles una precisión que no tienen.

**5. El tema institucional trae su tipografía: Inter.** Fuente única del tema: los exportes de `docs/entregables/figma/`, que dicen «Inter mantiene claridad en tablas, filtros y metadatos». **El eje del tema deja de ser color y pasa a ser color y familia tipográfica.** El tema de omisión conserva Lexend Deca y Fira Sans. Porqué: es la decisión del equipo y el archivo exportado es la fuente declarada; y porque un tema que cambia la paleta pero conserva la letra de otro sistema no es el tema que se diseñó. **Lo que cuesta, declarado**: `design/sistema.py` gana un mapa de familias por tema, `nuxt.config.ts` carga Inter por `@nuxt/fonts`, y los nueve roles tipográficos se reverifican bajo la familia nueva —altura de x, alturas de fila y cortes— porque cambiar de familia mueve métricas de línea. **+1.5 SP sobre las olas A y B.** Las quince capturas ya entregadas no se rehacen: se tomaron bajo el tema de omisión, que no cambia.

**6. La paleta de series no cambia entre temas.** Los seis colores de serie son un canal de datos, no identidad de marca; están verificados bajo tres dicromacias y el archivo de Figma no define ninguna paleta categórica. Porqué: inventar seis colores nuevos y volver a verificar su separación es trabajo sin encargo y con riesgo alto; el canal de datos puede ser común a los dos temas sin que nada se pierda. Se comprueba, eso sí, que mantienen su razón sobre el suelo oscuro institucional, que no es el mismo suelo (§6).

**7. Los cinco flujos de Figma entran como diseño, no como pantallas del producto.** Son 30 pantallas y quedan dos días. Porqué: implementarlas no cabe, y presentarlas como producto contradiría lo que el proyecto lleva cuatro actividades sosteniendo. Entran con su persona, su objetivo y su recorrido, rotuladas como diseño de alta fidelidad.

**8. El rol se cambia desde el cromo, y el cambio es real.** Hoy pasar de un perfil a otro cuesta cinco pasos por la pantalla de acceso. En un prototipo cuyo propósito es que alguien recorra los cuatro espacios de trabajo, esa fricción no enseña nada. Decisión: **un selector de rol junto al de tema y al de idioma**, que llama a `POST /api/auth/demo` y **acuña una sesión de verdad**. Porqué: un conmutador que cambiara el rol en el cliente destruiría la única historia de seguridad que el portal cuenta —que la guarda decide en el servidor y un rol jamás recibe el HTML de otro—. Al re-acuñar el token, el recorrido se abrevia y la garantía se conserva intacta. **La pantalla de acceso se queda**: es uno de los siete prototipos y evidencia del apartado 3; lo que se retira es la obligación de repetirla. **El selector solo existe con `DEMO_LOGIN_ENABLED`**, igual que la puerta que usa, y desaparece sin la bandera. **Las credenciales no se prellenan**: un campo con la contraseña escrita enseña un hábito que ningún portal financiero debería enseñar, y la puerta de demostración ya resuelve el acceso sin pedirla.

**9. El rebote a la pantalla de acceso deja de ser mudo.** Hoy quien pulsa un prototipo sin sesión aterriza en `/acceso` **sin explicación** —la guarda solo manda `motivo` cuando la sesión expiró—, se encuentra un formulario de usuario y contraseña que no puede llenar, y si descubre los perfiles de demostración acaba en la casa de ese rol y no en la pantalla que pidió. Un evaluador concluye que el prototipo no abre. Decisión, en tres partes y ninguna toca la guarda:

- **La guarda lleva la ruta pedida y el motivo**: `?destino=/gobierno&motivo=sesion-requerida`.
- **La pantalla de acceso lo dice y reordena su jerarquía cuando `DEMO_LOGIN_ENABLED` está encendida**: los cuatro perfiles pasan a ser el camino principal, con el nombre del rol y lo que abre cada uno, y el formulario de credenciales queda como vía secundaria. Con la bandera apagada, el orden de hoy se conserva intacto.
- **Al elegir perfil se vuelve a la ruta pedida** si ese rol puede verla, y si no, a su espacio diciéndolo. El destino **se valida contra `RUTAS_CONTRATO`**: aceptar una ruta arbitraria del query sería una redirección abierta.

Porqué esto y no lo que parecía obvio. **Apagar el middleware** borraría los espacios por rol y el estado sin permiso, que son un patrón UX comprometido y cinco celdas de la matriz 7×4: costaría puntos de la rúbrica para ahorrar un clic. **Prellenar la contraseña** enseña un hábito que ningún portal financiero debería enseñar y, sobre todo, **no resuelve el problema**: quien no sabe qué es esa pantalla tampoco sabrá que debe pulsar «Entrar». El defecto no era el login: era que el portal no explicaba el rebote ni devolvía a donde ibas.

**10. La tarjeta del índice ya declara su rol: que lo honre.** El índice es la superficie del evaluador —es pública, no es rama del mapa de A3, y su propio docstring dice que existe para la evaluación y no para el producto— y hoy no hace su trabajo. Cada tarjeta rotula «Perfil analista», «Perfil directivo», y ese rótulo es decorativo: quien la pulsa rebota al acceso. Decisión: **la tarjeta acuña la sesión de su `rolSugerido` y deja a quien la pulsa dentro de la pantalla**, en un clic, con `POST /api/auth/demo` y token real. El índice añade además una línea de orientación —qué es esto, que cada tarjeta abre con un perfil, que el perfil se cambia desde la cabecera— y el enlace al sistema de diseño.

Porqué esto y no un embudo de tema, rol y prototipos. `PRODUCT.md` fija que **cuando la necesidad del usuario trabajando y la del evaluador chocan, gana el usuario trabajando**: un embudo obligatorio pondría al evaluador por delante en cada visita. Con la tarjeta acuñando sesión, el evaluador entra en un clic y **quien va a trabajar no ve nada nuevo**: entra por `/acceso` con sus credenciales como siempre. El tema no entra al camino de entrada porque es una preferencia, no una decisión de acceso, y vive en la cabecera junto al modo y al idioma. **`/acceso` sigue siendo el prototipo 0 con tarjeta propia**, así que el formulario sigue siendo demostrable, y el estado sin permiso se prueba desde el selector de rol de la cabecera, que es donde alguien iría a buscarlo a propósito. **Solo con `DEMO_LOGIN_ENABLED`**: sin la bandera la tarjeta navega como hoy.

**Anti-objetivo declarado**: que el portal se vuelva una demostración. Nada de esto cambia el recorrido de quien trabaja.

**11. La tabla de alcance gana un cuarto estado.**

---

## 1. Criterios de aceptación con métricas verificables

| CA | Criterio | Métrica | Cómo se verifica |
|---|---|---|---|
| **CA-1** | El sistema acepta dos temas | `Tema = Literal["corriente", "institucional"]`; los 17 tokens resuelven para las 4 combinaciones de tema y modo | `pytest tests/ml/test_contraste_temas.py` |
| **CA-2** | El tema de omisión no se mueve | **Los 17 valores de `corriente` idénticos byte a byte**, en los dos modos | Prueba de fijación escrita **antes** de tocar `sistema.py`; `git diff` del bloque de omisión de `main.css` vacío |
| **CA-3** | El tema institucional cumple el mismo listón de contraste | 0 incumplimientos en claro y en oscuro | `incumplimientos("institucional", modo)` devuelve tupla vacía en los dos modos |
| **CA-4** | La separación bajo dicromacia no baja del piso del tema de omisión | Peor par ≥ **13.6** en claro y ≥ **21.5** en oscuro | `separaciones("institucional", modo)` |
| **CA-4b** | **El cromo ofrece los dos temas y los cuatro roles** | Dos botones de tema y cuatro de rol en la cabecera, junto a modo e idioma; el activo marcado; **cero cadenas dentro de los componentes** | `test/tema.spec.ts` y `test/rol.spec.ts` + recorrido V10 |
| **CA-4c** | **El cambio de rol acuña sesión real** | El selector llama a `POST /api/auth/demo`; la cookie cambia y la guarda del servidor decide con el token nuevo. **Nunca se cambia el rol en el cliente** | Petición visible en la red y `GET /api/auth/me` devolviendo el rol nuevo (V10) |
| **CA-4d** | **El selector de rol desaparece sin la bandera** | Con `DEMO_LOGIN_ENABLED` apagado, el control no se pinta | Prueba de montaje con la bandera en falso |
| **CA-4d2** | **La tarjeta del índice entra con su rol** | Un clic desde `/` deja a quien lo pulsa **dentro de la pantalla y con sesión del `rolSugerido` de esa tarjeta**, sin pasar por el formulario. Con `DEMO_LOGIN_ENABLED` apagado, navega como hoy | Recorrido V14 + prueba de montaje con la bandera en los dos valores |
| **CA-4e** | **El rebote se explica y devuelve** | La guarda envía `destino` y `motivo`; `/acceso` muestra el aviso; al elegir perfil se vuelve a la ruta pedida. `destino` **validado contra `RUTAS_CONTRATO`** | `test/guarda.spec.ts` ampliada + recorrido V12 |
| **CA-4f** | **Los perfiles son el camino principal en demostración** | Con `DEMO_LOGIN_ENABLED` encendida, los cuatro perfiles preceden al formulario y cada uno declara qué abre. Con la bandera apagada, el orden actual | Prueba de montaje con la bandera en los dos valores |
| **CA-5** | El tema se elige y persiste | Cookie `karisma_tema`, aplicada antes del primer render, sobrevive a navegación y a recarga | `test/tema.spec.ts` + recorrido con Playwright MCP (§6.3) |
| **CA-6** | Los dos temas ofrecen los dos modos | Binario: las 4 combinaciones pintan y ninguna cae a un bloque vacío | Recorrido con Playwright MCP sobre las 4 combinaciones |
| **CA-7** | `/exploracion` deja de ser andamiaje | `grep -c EstadoPendiente frontend/app/pages/exploracion/index.vue` = **0**; la pantalla compone desde `useBusquedaCatalogo` | `test/exploracionCatalogo.spec.ts` + recorrido con Playwright MCP |
| **CA-8** | Los cuatro estados no felices de exploración, construidos | 4 de 4 en categoría (a); la matriz 7×4 pasa de 6/12/10 a **9/12/7** | Matriz en `a4_02` + capturas |
| **CA-9** | Las etiquetas de alcance dicen la verdad | 6 entradas de `PROTOTIPOS` corregidas; **`/asistente` conservada** en `navegable-sin-datos` | `alcancePrototipos.spec.ts` en verde contra el `.tex` actualizado |
| **CA-10** | La tabla de alcance distingue hoja de ruta diseñada de no diseñada | 4 estados; las 3 capacidades diseñadas con referencia a su figura; **0 US sin declarar** | Conteo cruzado en `a4_05` |
| **CA-11** | Los cinco flujos documentados como diseño | 5 flujos con persona, objetivo, número de pantallas y figura; **cada pie con la palabra diseño** | `a4_08` |
| **CA-12** | Segunda iteración documentada | hallazgo → cambio → versión, con la razón de contraste antes y después | `a4_04` |
| **CA-13** | El tema institucional trae Inter y no desajusta la maquetación | Binario: bajo el tema institucional la familia es Inter y bajo el de omisión son Lexend Deca y Fira Sans; los nueve roles conservan su jerarquía; altura de fila 48 px y 0 desbordes en las 4 combinaciones | Recorrido con Playwright MCP (V8), midiendo `font-family` y alturas |
| **CA-14** | **El documento publica el acceso al archivo de trabajo** | 1 sección con el enlace al archivo de Figma, la estructura de sus tres páginas y sus nodos, y qué se puede recorrer desde ahí | `a4_01`; el enlace se abre y lleva al archivo |
| **CA-15** | **La guia deja de declarar una sola paleta** | `a4_03` §«Modo oscuro, fuera de alcance» reescrita: la condicion de entrada que ella misma fijo —matriz calculada por el mismo generador y con el mismo umbral— queda cumplida por CA-3 y CA-4 | Subsección reescrita en esta US, con las cifras de la ola A |
| **CA-16** | **El PDF de la entrega queda listo** | `Entregable Actividad 4_equipo_8.pdf` compilado en dos pasadas, con portada de los tres integrantes, en `docs/semana_4/`, sin referencias sin resolver ni desbordes | `latexmk -xelatex main_a4.tex` + revision del PDF renombrado |
| **CA-17** | **El avance sube al documento acumulado** | `main_completo.tex` compila con la parte IV completa, incluido `a4_08`, y su portadilla y su seccion «Sobre este documento» describen lo consolidado | `latexmk -xelatex main_completo.tex` sin referencias sin resolver |
| **CA-18** | QA gate | `make check` limpio; frontend ≥ 50 %; gate combinado `backend/app` + `ml` ≥ 70 % | `make check && make test` |

---

## 2. Arquitectura de la solución y flujo de capas

### 2.1 De dónde sale cada color

```
  design/sistema.py            17 tokens x 2 temas x 2 modos
        |                      (unica fuente; nada se teclea aguas abajo)
        +--> design/contraste.py ---> matriz y separaciones POR TEMA
        |
        +--> design/emitir.py
                 |
                 +--> frontend/app/assets/css/main.css        [GENERADO]
                 +--> frontend/app/utils/tokens.generated.ts  [GENERADO]
                              |
                              v
                 stores/sistemaDiseno.ts  (tema + modo como estado compartido)
                              |
                 componentes  ->  capturas  ->  documento
```

### 2.2 El eje nuevo, y un nombre que hay que liberar

Hoy `Token` tiene dos ranuras y el CSS conmuta con un atributo mal nombrado:

```css
:root { /* claro */ }
@media (prefers-color-scheme: dark) { :root:not([data-theme="claro"]) { /* oscuro */ } }
:root[data-theme="oscuro"] { /* oscuro */ }
```

`data-theme` transporta el **modo** (`main.css:117`, `main.css:148`, `useModo.ts:62`). Introducir un tema dejando ese nombre ocupado garantiza la confusión. Se renombra a `data-modo` y el tema entra como `data-tema`.

```css
:root                                                  { /* corriente · claro */ }
@media (prefers-color-scheme: dark) {
  :root:not([data-modo="claro"])                       { /* corriente · oscuro */ }
  :root[data-tema="institucional"]:not([data-modo="claro"]) { /* institucional · oscuro */ }
}
:root[data-modo="oscuro"]                              { /* corriente · oscuro */ }
:root[data-tema="institucional"]                       { /* institucional · claro */ }
:root[data-tema="institucional"][data-modo="oscuro"]   { /* institucional · oscuro */ }
```

El orden importa: los bloques de tema van **después** de los de modo, y el par tema+modo va último, porque una regla con dos atributos gana por especificidad y debe poder ganar.

### 2.3 La paleta institucional, completa y ya verificada

Los valores marcados con asterisco vienen literalmente del archivo de Figma; los demás son derivación declarada. **Cada razón de la columna es el resultado de correr `design/contraste.py`, no una estimación.**

#### Modo claro, suelo `#FFFFFF`

| Token | Valor | Origen | Razón sobre suelo | Veredicto |
|---|---|---|---|---|
| `ground` | `#FFFFFF` | \*Superficie | — | suelo |
| `ground-alt` | `#F1F4F8` | derivado del azul de navegación | 1.10:1 | superficie |
| `grid` | `#DCE3EC` | derivado | decorativo | exento |
| `corriente-apagado` | `#A8B4C4` | derivado | decorativo | exento |
| `corriente-tenue` | `#4A5A6E` | derivado | **7.05:1** | AAA |
| `corriente-medio` | `#1D4C6E` | \*Secundario | **9.09:1** | AAA |
| `corriente-pleno` | `#102A43` | \*Navegación | **14.64:1** | AAA |
| `error` | `#B8443F` | \*Error | **5.33:1** | AA |
| `aviso` | `#A36A10` | \*Atención, oscurecida 12 % | **4.54:1** | AA |
| `ok` | `#287A58` | \*Éxito | **5.23:1** | AA |
| `info` | `#123C7A` | derivado, ver §2.4 | **10.75:1** | AAA |

#### Modo oscuro, suelo `#0B1B2B`

| Token | Valor | Origen | Razón sobre suelo | Veredicto |
|---|---|---|---|---|
| `ground` | `#0B1B2B` | derivado de \*Navegación | — | suelo |
| `ground-alt` | `#102A43` | \*Navegación como panel | 1.19:1 | superficie |
| `grid` | `#1D3348` | derivado | decorativo | exento |
| `corriente-apagado` | `#46586B` | derivado | decorativo | exento |
| `corriente-tenue` | `#93A6BC` | derivado | **6.98:1** | AA |
| `corriente-medio` | `#BFD0E2` | derivado | **11.06:1** | AAA |
| `corriente-pleno` | `#EAF2FA` | derivado | **15.41:1** | AAA |
| `error` | `#F08078` | \*Error aclarado | **6.69:1** | AA |
| `aviso` | `#E8A33D` | \*Atención aclarada | **8.07:1** | AAA |
| `ok` | `#5FCB94` | \*Éxito aclarado | **8.67:1** | AAA |
| `info` | `#B9A7F2` | derivado, ver §2.4 | **8.19:1** | AAA |

`serie-1` a `serie-6` **conservan los valores del tema de omisión** en los dos modos (ambigüedad 6), con la comprobación de §6 sobre el suelo oscuro institucional.

### 2.4 Los dos hallazgos que la verificación produjo

**Atención no alcanzaba el listón de texto.** `#B97812` da **3.65:1** sobre blanco, por debajo del 4.5:1 que exige un token que informa. Oscurecida un 12 % conservando matiz (36.6°) y saturación llega a `#A36A10` con **4.54:1**. Es el mínimo que cruza: a −10 % todavía da 4.40:1.

**El canal informativo necesita un matiz fuera del octeto.** El color de acción `#086B70` y el de éxito `#287A58` están a **dE 6.7 bajo tritanopia**, muy por debajo del piso de 13.6 que el tema de omisión sostiene: para quien no distingue azul de amarillo, un aviso informativo y una confirmación se ven igual. En claro se resuelve con un azul profundo derivado, `#123C7A`, que sube el peor par a **20.1**. En oscuro no hay azul que sirva —bajo tritanopia el azul y el verde colapsan— y la solución es un violeta, `#B9A7F2`, con peor par **25.9** sobre un piso de 21.5.

**Consecuencia declarada**: el color de acción `#086B70` **no entra en los 17 tokens**. Sigue siendo el color de acción del tema y se documenta en la guía como tal, aplicado por la capa de componentes. El contrato de 17 tokens no tiene ranura de acción hoy, y abrirla es trabajo que esta US no hace; queda como pendiente del handoff.

### 2.5 El criterio de la etiqueta de alcance, escrito antes de aplicarlo

El defecto no es que las etiquetas estén mal: es que **nadie escribió con qué regla se asignan**, así que se quedaron en su valor inicial. La regla:

> Una pantalla es *navegable con datos de ejemplo* si su contenido principal se compone desde una
> fuente real —un endpoint, un store que sondea, un silo sintético— y *navegable sin datos* si se
> compone desde literales escritos en el componente o en el proveedor.

| Pantalla | Hoy | Propuesto | Evidencia |
|---|---|---|---|
| `/acceso` | sin datos | **con datos de ejemplo** | El formulario opera contra el emisor de credenciales; la puerta de demostración acuña sesión real |
| `/inicio` | sin datos | **con datos de ejemplo** | El buscador consulta `/api/catalog/search`; los cinco bloques componen desde estado |
| `/exploracion` | sin datos | **con datos de ejemplo**, tras CA-7 | Consumirá `useBusquedaCatalogo`. **Antes de CA-7 la etiqueta es correcta y no se toca** |
| `/gobierno` | sin datos | **con datos de ejemplo** | `DiccionarioCampos.vue` ya consume `useBusquedaCatalogo`; el linaje consulta su endpoint |
| `/asistente` | sin datos | **sin datos, sin cambio** | `guionizado.py` devuelve `filas=[["Morosidad de la cartera hipotecaria", "3.42 %"]]`. Son literales |
| `/administracion` | sin datos | **con datos de ejemplo** | El panel compone desde el store contra su endpoint |
| `/exploracion/exportar` | sin datos | **con datos de ejemplo** | El store sondea `GET /api/export/{job_id}` cada 3 000 ms |

Seis cambian, una se queda. **Que una se quede es la prueba de que la regla se aplicó y no se barrió parejo.**

### 2.6 La pantalla de catálogo

No hay backend nuevo, ni composable nuevo, ni tipos nuevos. `useBusquedaCatalogo` expone `buscar`, `filtrarPorDominio`, `ConteoDominio` y `PaginaCatalogo` con paginación contra `/api/catalog/search`, y hoy solo lo consume un componente de gobierno. La pantalla compone eso con la disposición que el archivo de Figma ya resolvió: buscador arriba, conteos por dominio a la izquierda, resultados paginados al centro.

Sus cuatro estados no felices pasan de categoría (b) o (c) a (a): vacío sin resultados, cargando con esqueleto de la altura de las filas, error conservando el término, y sin permiso por el componente compartido.

---

## 3. Archivos exactos a crear o modificar

| Ruta | C/M | Qué cambia | Ola |
|---|---|---|---|
| `design/sistema.py` | M | `Tema`, `Paleta`, `Token` con dos paletas, los 17 tokens con su valor institucional en los dos modos | A |
| `design/contraste.py` | M | `matriz`, `separaciones`, `incumplimientos` y `_suelo` parametrizados por tema | A |
| `frontend/nuxt.config.ts` | M | Inter añadida a `fonts.families` por `@nuxt/fonts`, con el mismo proveedor que las otras dos | A |
| `design/emitir.py` | M | Bloques de tema; renombre `data-theme` → `data-modo`; tema y pares al módulo generado | A |
| `tests/ml/test_contraste_temas.py` | C | Fijación del tema de omisión, listones e invariantes (§6) | A |
| `frontend/app/assets/css/main.css` | **G** | **Generado por `make tokens`. No se edita a mano** | A |
| `frontend/app/utils/tokens.generated.ts` | **G** | **Generado. Idem** | A |
| `frontend/app/composables/useTema.ts` | C | Preferencia de tema, cookie `karisma_tema` | B |
| `frontend/app/composables/useModo.ts` | M | Atributo `data-modo` en vez de `data-theme` | B |
| `frontend/app/stores/sistemaDiseno.ts` | M | El tema entra como estado compartido junto al modo | B |
| `frontend/app/components/comun/SelectorTema.vue` | C | Dos botones, uno por tema, con el activo marcado | B |
| `frontend/app/components/comun/SelectorRol.vue` | C | Cuatro botones de perfil que acuñan sesión real por `POST /api/auth/demo`. Solo con `DEMO_LOGIN_ENABLED` | B |
| `frontend/app/components/comun/CabeceraProducto.vue` | M | Monta los dos selectores junto a `SelectorModo` y `SelectorIdioma` | B |
| `frontend/app/pages/index.vue` | M | Línea de orientación: qué es esto, que la tarjeta abre con un perfil y que el perfil se cambia arriba | B |
| `frontend/app/components/nav/BotonPrototipo.vue` | M | La tarjeta acuña la sesión de su `rolSugerido` antes de navegar, bajo la bandera | B |
| `frontend/app/utils/guarda.ts` | M | La decisión de redirigir lleva `destino` y un motivo nuevo, `sesion-requerida` | B |
| `frontend/app/pages/acceso.vue` | M | Aviso del rebote, jerarquía invertida bajo la bandera y retorno a la ruta pedida | B |
| `frontend/test/guarda.spec.ts` | M | Amplía la suite existente con el destino y el motivo nuevo | B |
| `frontend/app/composables/useRolDemo.ts` | C | Cambio de rol contra la puerta de demostración, con su estado de carga y su error | B |
| `frontend/test/rol.spec.ts` | C | §6 | B |
| `frontend/app/app.vue` | M | Aplica el tema antes del primer render, como ya hace con el idioma | B |
| `frontend/i18n/locales/es.json` · `en.json` | M | Subárboles `theme.*` y `roleSwitch.*`: etiquetas de los dos selectores, nombre de cada tema y de cada perfil | B |
| `frontend/test/tema.spec.ts` | C | §6 | B |
| `frontend/app/pages/exploracion/index.vue` | M | Deja de montar `EstadoPendiente`; compone el catálogo | C |
| `frontend/app/components/exploracion/**` | C | Buscador, conteos por dominio, resultados y los cuatro estados | C |
| `frontend/app/utils/navegacion.ts` | M | **Solo el campo `alcance`** de seis entradas | C |
| `frontend/test/exploracionCatalogo.spec.ts` | C | §6 | C |
| `docs/entregables/contenido/a4_01_metodo_prototipado.tex` | M | **Acceso al archivo de trabajo (CA-14)**: el enlace al archivo de Figma, sus tres páginas con sus nodos y qué se recorre desde ahí | D |
| `docs/entregables/contenido/a4_02_prototipos.tex` | M | Pantalla de catálogo; matriz 7×4 recontada | D |
| `docs/entregables/contenido/a4_04_prevalidacion.tex` | M | Segunda iteración, con su antes y su después numérico | D |
| `docs/entregables/contenido/a4_05_alcance.tex` | M | Cuarto estado; etiquetas corregidas; capacidades diseñadas | D |
| `docs/entregables/contenido/a4_07_anexo.tex` | M | Inventario ampliado; procedencia de los tokens | D |
| `docs/entregables/contenido/a4_08_tema_y_flujos.tex` | C | El tema institucional con su paleta, su tipografía y su matriz de contraste en los dos modos · los cinco flujos de tarea · **la tabla de verificación técnica del archivo de diseño**: 30 pantallas en 5 flujos, 84 nodos con 0 destinos inválidos, 12 conjuntos y 75 variantes, 0 textos bajo 12 px, 0 recortes, 0 controles bajo 44 px. **Nada que `a4_03` ya cubra** | D |
| `docs/entregables/contenido/a4_03_guia_estilos.tex` | M | **Solo la subsección «Modo oscuro, fuera de alcance y declarado»**, que se reescribe porque esta US cumple la condición de entrada que ella misma fijó. Ninguna otra línea del archivo se toca | D |
| `docs/entregables/main_a4.tex` | M | **Una línea**: el `\input` de `a4_08` | D |
| `docs/entregables/main_completo.tex` | M | El `\input` de `a4_08` en la parte IV y el ajuste de «Sobre este documento». **Archivo propio, sin coordinación** | D |
| `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` | M | Se **regenera** desde `main_a4.tex` al cerrar. Es el archivo que se sube | D |
| `docs/entregables/figuras/a4/tema/*.png` | C | El portal en las cuatro combinaciones de tema y modo | D |
| `docs/entregables/figuras/a4/figma/*.png` | C | Las cinco láminas de flujo | D |
| `docs/us-handoff/us-entrega-a4.md` | C | Handoff, estado `planning` | ahora |

**Prohibido tocar**: `estilo/uxdoc.sty` (congelada) · `contenido/a4_06_cierre.tex` · **el resto de `a4_03_guia_estilos.tex`** fuera de la subsección de modo oscuro · `estilo/a4_tokens.tex` y `generar_tokens_a4.py` (emitidos) · **`figuras/a4/antes/**` y `figuras/a4/despues/**`** (evidencia cerrada de la primera iteración: una recaptura destruiría el par) · `db/` y `backend/`.

---

## 4. Firmas públicas de cada módulo nuevo

```python
# design/sistema.py

Tema = Literal["corriente", "institucional"]

@dataclass(frozen=True)
class Paleta:
    """Values of one token inside one theme."""
    claro: str
    oscuro: str

@dataclass(frozen=True)
class Token:
    nombre: str
    corriente: Paleta
    institucional: Paleta
    uso: str
    informa: bool = True

    def valor(self, tema: Tema, modo: Modo) -> str: ...

def tokens_de_color() -> tuple[Token, ...]: ...
```

```python
# design/contraste.py

def matriz(tema: Tema, modo: Modo) -> tuple[Par, ...]: ...
def separaciones(tema: Tema, modo: Modo) -> tuple[Separacion, ...]: ...
def incumplimientos(tema: Tema, modo: Modo) -> tuple[str, ...]: ...
def _suelo(tema: Tema, modo: Modo) -> str: ...
```

```ts
// frontend/app/composables/useTema.ts

export type TemaPortal = 'corriente' | 'institucional'

export interface TemaActivo {
  readonly tema: Readonly<Ref<TemaPortal>>
  fijarTema: (nuevo: TemaPortal) => void
}

export function useTema(): TemaActivo
```

```ts
// frontend/app/components/exploracion/  (props de los componentes nuevos)

// ResultadosCatalogo.vue
defineProps<{ pagina: PaginaCatalogo | null, cargando: boolean, error: string | null }>()

// FiltroDominios.vue
defineProps<{ conteos: readonly ConteoDominio[], activo: string | null }>()
defineEmits<{ filtrar: [dominio: string | null] }>()
```

**Cero tipos nuevos en el contrato de navegación.** `EstadoAlcance` sigue viviendo en `app/types/navegacion.ts` y esta US cambia **valores**, nunca su definición. `PaginaCatalogo` y `ConteoDominio` ya existen en `useBusquedaCatalogo.ts` y se reutilizan sin tocarlas.

---

## 5. Dominios y sub-tareas, con el write-set disjunto de cada agente

**Checklist de dominios**: [ ] backend · [x] frontend · [ ] ml · [ ] db · [x] tests · [x] docs · [x] design (sin guía propia)

**Sí se reparte**, en cuatro olas. **Cada ola entrega sola y ninguna depende de que la siguiente ocurra**, que es la propiedad que se necesita a dos días del cierre.

| Ola | Qué entrega | SP | Write-set exclusivo | Depende de | Skills a cargar |
|---|---|---|---|---|---|
| **A** eje de tema | `design/**`, los generados y la carga de Inter. El portal se ve igual que hoy | **4** | `design/sistema.py`, `design/contraste.py`, `design/emitir.py`, `tests/ml/test_contraste_temas.py` | nada | ninguna del catálogo aplica; manda la raíz |
| **B** conmutadores y entrada en frío | Composables, store, selectores de tema y rol, cabecera, i18n, `app.vue`, guarda, pantalla de acceso, **índice y tarjeta de prototipo** | **5** | `composables/{useTema,useModo}.ts`, `stores/sistemaDiseno.ts`, `components/comun/SelectorTema.vue`, `app.vue`, `i18n/locales/*.json`, `test/tema.spec.ts` | A | `portal-frontend-composables` + `portal-frontend-components` |
| **C** catálogo y etiquetas | La pantalla de exploración y las seis etiquetas | 2 | `pages/exploracion/index.vue`, `components/exploracion/**`, `utils/navegacion.ts`, `test/exploracionCatalogo.spec.ts` | nada | `portal-frontend-components` + `portal-ux-patterns` |
| **D** documento y entrega | Los seis `.tex`, `a4_08`, figuras, los dos envoltorios y **el PDF que se sube** | **2** | `contenido/a4_0{1,2,4,5,7}.tex`, `a4_08_tema_y_flujos.tex`, `main_a4.tex` una linea, `a4_03` una subseccion, `main_completo.tex`, `figuras/a4/{tema,figma}/**`, `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` | A, B y C | `portal-ux-deliverables` + `portal-ux-patterns` |

**A y C son disjuntos y corren en paralelo.** B lee lo que A escribe, así que va después. D cierra: necesita las tres para poder citar cifras reales en vez de prometidas.

**Lo que uno lee y otro escribe**: B lee `tokens.generated.ts`, que emite A. Secuencial, y A va primero. D lee `navegacion.ts`, que escribe C. Secuencial, y C va primero.

**Regla del AGENTS.md de carpeta**: B y C escriben ambas en `frontend/`. **Ninguna de las dos actualiza `frontend/AGENTS.md`**; lo hace el orquestador al integrar, con las discrepancias de §11.

**Regla de frontera con US-UX-09**: esta US **asume las dos ediciones** en archivos que US-UX-09 escribió, y las acota por escrito. La primera es el `\input` de `a4_08` en `main_a4.tex`: se añade al final del bloque, sin reordenar ni tocar ninguna línea existente. La segunda es la subsección «Modo oscuro, fuera de alcance y declarado» de `a4_03`, que hoy afirma que el sistema entrega una sola paleta y deja de ser cierta: **se reescribe esa subsección y ninguna otra línea del archivo**. Las dos quedan anotadas en el handoff para que US-UX-09 las conozca sin tener que descubrirlas en un diff.

**Si el reloj aprieta, el orden es C, D, A, B.** C no depende de nada, quita el único andamiaje del entregable, corrige seis etiquetas y mejora la matriz de estados: es la de mejor relación con la rúbrica.

---

## 6. Plan de tests

Cada prueba declara qué defecto concreto la haría fallar. Las que no lo responden no se escriben.

### 6.1 Backend y design — `tests/ml/test_contraste_temas.py`

Umbral vigente: gate combinado `--cov=backend/app --cov=ml --cov-fail-under=70`. Esta US **sí añade código a `design/`**, así que el denominador se mueve por primera vez en la serie; la prueba nueva lo cubre.

| Prueba | Defecto que la haría fallar | Umbral |
|---|---|---|
| El tema de omisión no se mueve | Al abrir el eje, un token de `corriente` cambia de valor y las 15 capturas del entregable dejan de corresponder al producto | 17 tokens por 2 modos, con el valor de hoy, byte a byte |
| Ningún token que informa incumple su listón | Se adopta el tema institucional con Atención en 3.65:1 y el portal reprueba el listón que él mismo publica | `incumplimientos(tema, modo)` vacío en las 4 combinaciones |
| La separación bajo dicromacia no baja del piso | El canal informativo colapsa con el de éxito bajo tritanopia y dos estados distintos se ven igual | peor par ≥ 13.6 en claro y ≥ 21.5 en oscuro, en los dos temas |
| Las series conservan su razón sobre el suelo institucional | El suelo oscuro institucional es `#0B1B2B` y no `#0A0A0C`; una serie podría quedar por debajo de 3:1 sin que nadie lo note | 6 series ≥ 3:1 sobre el suelo de cada combinación |
| El emisor es idempotente | Dos corridas de `make tokens` producen archivos distintos y el verificador marca divergencia en cada commit | dos corridas byte a byte iguales |

### 6.2 Frontend — vitest, umbral 50 %

| Prueba | Archivo | Defecto que la haría fallar | Umbral |
|---|---|---|---|
| La preferencia de tema viaja en cookie | `test/tema.spec.ts` | El tema se aplica solo en el cliente: la primera pintura del servidor usa el otro y produce un destello visible | cookie presente y aplicada antes del primer render |
| El selector ofrece los dos temas y marca el activo | `test/tema.spec.ts` | El control se pinta sin estado activo y no se sabe cuál está puesto | 2 opciones, 1 marcada |
| Cero cadenas visibles en el selector | `test/contratos.spec.ts` **ya existe** | Se escribe «Institucional» dentro del componente y la interfaz en inglés muestra español | paridad de claves ya cubierta |
| La pantalla de catálogo compone desde el composable | `test/exploracionCatalogo.spec.ts` | La pantalla se reescribe sin conectar el composable y queda un andamiaje distinto | `EstadoPendiente` ausente; `useBusquedaCatalogo` invocado |
| Los cuatro estados de la pantalla montan | `test/exploracionCatalogo.spec.ts` | Se entrega el camino feliz y el vacío queda como una tabla sin filas, sin explicación | 4 estados con su marca en el DOM |
| El alcance publicado coincide con el código | `test/alcancePrototipos.spec.ts` **ya existe** | Se corrigen las etiquetas del código y no la tabla del PDF, o al revés | 7 filas contra 7 valores. **Debe fallar hasta que D actualice el `.tex`: es la prueba haciendo su trabajo** |

**No se escriben**: pruebas sobre el aspecto de un tema —el color es una decisión, no un comportamiento—, ni sobre la existencia de PNG —lo detecta la compilación de LaTeX—, ni sobre el contenido de los `.tex` más allá de las dos que ya existen.

### 6.3 Verificación en navegador con el MCP de Playwright

Lo que las pruebas unitarias **no** pueden ver: que las cuatro combinaciones pinten de verdad, que no haya destello al cargar y que la tipografía nueva no rompa alturas. Se ejecuta al cerrar cada ola y se anota en el handoff.

| # | Recorrido | Qué se comprueba | Criterio |
|---|---|---|---|
| V1 | Las 4 combinaciones de tema y modo sobre `/inicio` | Ninguna cae a un bloque vacío ni hereda color del otro tema | `getComputedStyle` de `--color-ground` distinto en las 4 y coincidente con la tabla de §2.3 |
| V2 | Cambiar de tema y recargar | La preferencia persiste y **no hay destello**: el primer render ya trae el tema | El atributo `data-tema` presente en el HTML del servidor, no añadido por script |
| V3 | Franja de alcance en las 4 combinaciones | R10: ninguna captura sin franja | `[data-franja-alcance]` visible y con ancho igual al de su columna |
| V4 | `/exploracion` con término que devuelve resultados | La pantalla compone desde el endpoint | Filas en el DOM y petición a `/api/catalog/search` en la red |
| V5 | `/exploracion` con término sin resultados | Estado vacío explícito, no una tabla sin filas | Marca de vacío presente |
| V6 | `/exploracion` con el api caído | Estado de error conservando el término escrito | Término intacto en el campo y aviso presente |
| V7 | `/exploracion` con rol sin permiso | Estado sin permiso, URL intacta, sin control de reintento | 403 y componente compartido montado |
| V8 | Familia y métricas en las 4 combinaciones | CA-13: la familia correcta por tema y sin desajuste de maquetación | `font-family` computada = Inter bajo `data-tema=institucional` y Fira Sans sin él; altura de fila 48 px; 0 elementos con `scrollWidth > clientWidth` |
| V9 | Las 7 pantallas bajo el tema institucional | Captura para `figuras/a4/tema/` | 7 PNG a 1440×900, modo declarado en el nombre |
| V10 | Cambiar de rol desde el cromo, en las cuatro opciones | CA-4b y CA-4c: el portal se reconfigura y la sesión es real | `POST /api/auth/demo` visible en la red, `GET /api/auth/me` con el rol nuevo, y la barra lateral mostrando el segundo nivel de ese perfil |
| V11 | Cambiar de rol a uno sin permiso sobre la pantalla actual | La guarda sigue mandando: no queda una pantalla prohibida pintada | Estado sin permiso o redirección, decidida en el servidor |
| V12 | **Entrar en frío**: desde el índice, sin sesión, pulsar «Gobierno del dato» | CA-4e: es el recorrido del evaluador que no conoce el portal | Aviso visible del motivo, los cuatro perfiles antes del formulario, y tras elegir analista se aterriza **en `/gobierno`**, no en `/inicio` |
| V14 | **Un clic desde el índice, sin sesión, sobre «Gobierno del dato»** | CA-4d2: es el recorrido completo del evaluador | Aterriza **en `/gobierno` con sesión de analista**, sin ver el formulario; `POST /api/auth/demo` en la red y `GET /api/auth/me` con el rol de la tarjeta |
| V13 | Entrar en frío a una pantalla que el rol elegido no puede ver | El retorno no puede llevar a una pantalla prohibida | Aterriza en su espacio con el motivo dicho, sin pantalla prohibida pintada |

**Las capturas de `antes/` y `despues/` no se rehacen.** Son evidencia cerrada de la primera iteración; las del tema nuevo van a `figuras/a4/tema/`, que es una carpeta distinta a propósito.

---

## 7. Nube

**No toca la nube.** Ningún recurso, ningún comando, ningún secreto. El despliegue existente no se altera y la evidencia del entregable sigue anclada a capturas locales reproducibles.

---

## 8. Schema

**No toca schema.** Ninguna migración y ningún rollback que escribir. La preferencia de tema vive en la cookie `karisma_tema`: es una preferencia de presentación por dispositivo, y persistirla por usuario exigiría una columna, una migración y un endpoint para algo que se pierde sin costo. Se declara así en el handoff para que nadie lo lea como un olvido.

---

## 9. Rúbrica: a qué rubro responde

| Apartado | Peso | Puntos de 25 | Cómo lo mueve |
|---|---|---|---|
| **3 · Prototipos de alta fidelidad** | 50 % | 12.50 | **Directo.** Quita el único andamiaje del set, corrige seis etiquetas, mejora la matriz de estados de 6/12/10 a **9/12/7** y añade cinco flujos de tarea con persona y objetivo |
| **4 · Guía de estilos** | 45 % | 11.25 | **Directo.** Un segundo tema completo con su matriz de contraste calculada en los dos modos, y la subsección de modo oscuro reescrita por CA-15, que hoy afirma lo contrario de lo que el sistema entrega. CA-14 publica además el acceso al archivo de trabajo, que es lo que permite al evaluador recorrer los cinco flujos por su cuenta |
| Introducción y método | 3 % | 0.75 | La segunda iteración documentada refuerza el criterio que la rúbrica premia: cambio por evidencia |

Las tres carencias que el encargo identifica quedan cerradas: **rigor de accesibilidad**, con la matriz numérica de los dos temas en los dos modos, incluidas las razones que fallaban y su corrección; **estados no felices**, con la matriz 7×4 extendida a la pantalla de catálogo; **iteración visible**, con la segunda iteración documentada, esta vez sobre el sistema de diseño.

La banda alta de la rúbrica premia **cobertura demostrada**, no profundidad: cada elemento con su propio subtítulo y ninguno en tiempo futuro.

---

## 10. Riesgos y mitigaciones

| # | Riesgo | Prob. | Impacto | Mitigación | Disparador |
|---|---|---|---|---|---|
| R1 | Regenerar los tokens mueve un valor del tema de omisión | Baja | **Crítico**: invalida las 15 capturas y la iteración ya entregada | La prueba de fijación se escribe **antes** de tocar `sistema.py` | Cualquier diferencia detiene la ola A |
| R2 | El renombre `data-theme` → `data-modo` rompe el composable de modo | Media | Medio | Va en commit propio, separado del tema, y está cubierto por las suites de modo existentes | Si la suite no queda verde en 30 min, se conserva `data-theme` para el modo y el tema entra como `data-tema` igual |
| R3 | Los ocho estados interactivos derivados no coinciden con los del archivo | Alta | Bajo | Se declaran como derivación, con la regla escrita, y se pide el valor oficial | Ninguno: es divergencia declarada, no defecto |
| R4 | Inter altera alturas de fila o produce cortes | **Alta** | Medio | V8 mide familia, alturas y desbordes en las cuatro combinaciones antes de capturar. Inter tiene altura de x mayor que Fira Sans, así que el riesgo real es que una celda densa crezca | Si V8 encuentra cortes, se ajusta la escala **dentro del tema institucional** y se declara; el tema de omisión no se toca |
| R5 | No alcanza el tiempo para las cuatro olas | **Alta** | Medio | Las olas son independientes; el orden recomendado pone primero la de mejor relación con la rúbrica | Sáb 15, 18:00: si A no está, se entregan C y D sin tema, y `a4_08` se reduce a la matriz de contraste de la paleta, que ya está calculada |
| R6 | Las dos ediciones sobre archivos de US-UX-09 colisionan con trabajo suyo | Media | Alto | Están acotadas: una línea al final de un bloque y una subsección completa que hoy es falsa. Se anotan en el handoff con su alcance | Si US-UX-09 tocó lo mismo, gana su versión y esta US reaplica encima |
| R7 | Corregir Atención altera el aspecto aprobado en el archivo | Media | Bajo | El cambio es de luminancia y conserva matiz y saturación; se documenta con su antes y su después | Si se prefiere el valor original, se conserva y **se declara el incumplimiento en la tabla**. Lo que no se hace es publicarlo sin decirlo |
| R8 | Presentar los flujos de Figma como pantallas del producto | Baja | **Crítico reputacional** | Cada pie de figura lleva la palabra diseño y la tabla de alcance los separa en su propio estado | Ninguna figura entra sin ese rótulo |
| R9 | Cambiar seis etiquetas rompe `alcancePrototipos.spec.ts` | **Alta y deseada** | Ninguno | Es el comportamiento esperado: la prueba debe fallar hasta que D actualice el `.tex` | No es incidente |
| R10 | El violeta del canal informativo se lee ajeno a la identidad | Media | Bajo | Se documenta el porqué con el número: bajo tritanopia no hay azul que separe del verde de éxito | Si se rechaza, se acepta el colapso y **se declara en la guía**, con su dE |

---

## 11. Discrepancias entre el 'Estado' de las guías y el repositorio

Manda el repositorio. Las de `frontend/AGENTS.md` ya se corrigieron el 14-ago-2026, con su espejo `CLAUDE.md` sincronizado.

| Guía | Decía | El repo dice | Estado |
|---|---|---|---|
| `frontend/AGENTS.md` | «38 `*.spec.ts` y tres auxiliares» | **42** `*.spec.ts` | **Corregido.** Con esta US serán 44 |
| `frontend/AGENTS.md` | «doce familias» de componentes | **13** directorios en `app/components/` | **Corregido.** Con esta US serán 14, al crear `exploracion/` |
| `frontend/AGENTS.md` | No mencionaba `@playwright/test` | Es dependencia de desarrollo desde US-UX-07 | **Corregido**: añadido a Estado y a Comandos |
| `frontend/AGENTS.md` | No mencionaba pruebas que lean `.tex` | `rutaRama.spec.ts` y `alcancePrototipos.spec.ts` leen `docs/entregables/` | **Corregido**: patrón documentado en Tests |
| `frontend/AGENTS.md` | No advertía de la medida de lectura | `main.css:207` aplica 68ch a todo `p` sin `max-w-*` | **Corregido**: convención nueva con la salida `max-w-none` |
| `frontend/AGENTS.md` | No advertía del parseo externo de `PROTOTIPOS` | `capturas_a4.mjs` lo parsea como texto | **Corregido**: entrada nueva en No tocar |
| `docs/AGENTS.md` | «de A4 solo existen `a4_03` y `a4_06`» | Existen los **ocho** | Corregir |
| `docs/AGENTS.md` | «`semana_4/` aún no tiene PDF de entrega» | Ya lo tiene | Corregir |
| `docs/AGENTS.md` | «`us-resolved/` y `us-research/` no existen» | **Confirmado**, no existen | Sin acción: la guía acierta |
| Raíz | El routing no lista `design/` con guía propia | `design/` tiene 1 026 líneas y es la fuente del sistema | Evaluar si merece `design/AGENTS.md`. **Fuera del alcance de esta US** |

---

## 12. Checklist de cierre verificable

- [ ] SHA base escrito en el handoff antes de la primera línea de código
- [ ] Prueba de fijación del tema de omisión escrita **antes** de tocar `design/sistema.py`
- [ ] Los 17 valores de `corriente` sin una sola diferencia, en los dos modos
- [ ] `Tema` declarado; los 17 tokens con su paleta institucional en claro y en oscuro
- [ ] Procedencia de cada valor citada: del archivo de Figma o derivación declarada
- [ ] `data-modo` para el modo y `data-tema` para el tema; ningún atributo con nombre prestado
- [ ] `incumplimientos` vacío en las cuatro combinaciones
- [ ] Peor separación bajo dicromacia ≥ 13.6 en claro y ≥ 21.5 en oscuro, en los dos temas
- [ ] Las seis series ≥ 3:1 sobre el suelo de cada combinación
- [ ] `make tokens` idempotente; `scripts/verificar_tokens_a4.sh` sin divergencia
- [ ] Selector de tema en la cabecera, con los dos temas nombrados por clave i18n, **cero cadenas dentro del componente**
- [ ] Selector de rol en la cabecera, con los cuatro perfiles, **acuñando sesión real** por la puerta de demostración (V10)
- [ ] El selector de rol **no se pinta** con `DEMO_LOGIN_ENABLED` apagado
- [ ] Cambiar a un rol sin permiso sobre la pantalla actual **lo decide el servidor** (V11)
- [ ] **Un clic desde el índice entra con el rol de la tarjeta**, sin pasar por el formulario (V14)
- [ ] El índice explica en una línea qué es esto, que la tarjeta abre con perfil y que el perfil se cambia arriba
- [ ] Con `DEMO_LOGIN_ENABLED` apagado, la tarjeta **navega como hoy** y nada de esto se pinta
- [ ] **El rebote sin sesión se explica** y devuelve a la ruta pedida, con `destino` validado contra `RUTAS_CONTRATO` (V12)
- [ ] Con `DEMO_LOGIN_ENABLED` encendida, **los cuatro perfiles preceden al formulario**; con la bandera apagada, el orden de hoy
- [ ] Entrar en frío a una pantalla prohibida para el rol elegido **no la pinta** (V13)
- [ ] **Las credenciales no se prellenan**, y el middleware **no se desactiva**
- [ ] La preferencia de tema viaja en cookie y se aplica antes del primer render, sin destello (V2)
- [ ] `/exploracion` compone desde `useBusquedaCatalogo`; `EstadoPendiente` ya no aparece ahí
- [ ] Los cuatro estados no felices de la pantalla de catálogo, construidos y capturados (V4 a V7)
- [ ] Matriz 7×4 recontada: **9 construidas, 12 de otras historias, 7 especificadas**
- [ ] Seis etiquetas corregidas y **`/asistente` conservada** en `navegable-sin-datos`, con su evidencia citada
- [ ] Tabla de alcance con cuatro estados y las tres capacidades diseñadas referidas a su figura
- [ ] Cinco flujos documentados, **cada pie con la palabra diseño**
- [ ] **Enlace al archivo de trabajo publicado** en `a4_01`, con las tres páginas y sus nodos, y el enlace abriendo de verdad
- [ ] **Sin duplicar la guía**: `a4_08` no reescribe identidad, retícula, microinteracciones, voz y tono ni bitacora de versiones. Las 63 subsecciones de `a4_03` ya las cubren; `a4_08` solo aporta el tema, su matriz y los flujos
- [ ] Subsección «Modo oscuro, fuera de alcance y declarado» de `a4_03` **reescrita**, con las cifras de la ola A, y **ninguna otra línea de ese archivo modificada** (`git diff` acotado a esa subsección)
- [ ] Las dos ediciones sobre archivos de US-UX-09 **anotadas en el handoff**, con su alcance exacto
- [ ] Segunda iteración documentada con su antes y su después numérico
- [ ] **Cada tema con su familia**: Inter bajo `data-tema="institucional"`, Lexend Deca y Fira Sans sin él, verificado con `font-family` computada en las cuatro combinaciones (V8)
- [ ] Los nueve roles tipográficos conservan su jerarquía bajo Inter; altura de fila 48 px y 0 desbordes (V8)
- [ ] Las siete pantallas capturadas bajo el tema institucional en `figuras/a4/tema/` (V9)
- [ ] `figuras/a4/antes/**` y `despues/**` **sin una sola modificación**
- [ ] Los nueve recorridos V1 a V9 ejecutados con el MCP de Playwright y anotados en el handoff
- [ ] `make check` limpio · `make test` en verde · frontend ≥ 50 % · gate `backend/app` + `ml` ≥ 70 %
- [ ] `latexmk -xelatex main_a4.tex` en dos pasadas, sin referencias sin resolver ni desbordes
- [ ] `latexmk -xelatex main_completo.tex` en dos pasadas: **el avance queda dentro del documento acumulado del proyecto**, con la parte IV completa
- [ ] PDF renombrado a `Entregable Actividad 4_equipo_8.pdf` en `docs/semana_4/`, **regenerado**, con portada de Alexandro Mayoral, Jacqueline Sarmiento y Arthur Zizumbo
- [ ] Subido a Canvas antes del **dom 16, 20:00** (gate 26.4, margen de 3h59 contra las 23:59)
- [ ] `grep -nE '#[0-9A-Fa-f]{6}'` sobre los `.tex` propios → 0, salvo la tabla de paleta de `a4_08`, que es su contenido
- [ ] El documento habla de **la entrega**: sin comparaciones entre partes ni atribución de mitades
- [ ] Guías corregidas con las discrepancias de §11
- [ ] Handoff actualizado con snapshot, decisiones y pendientes reales
- [ ] Commits sin trailer de asistente; rama encadenada, sin PR; el commit espera visto bueno
