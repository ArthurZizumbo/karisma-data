# Handoff US-ENTREGA-A4 — Consolidación de la entrega de la Actividad 4

**Estado**: planning
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantalla de catálogo)
**Sprint**: S4, cierre · **Actividad**: A4 (dom 16-ago-2026)
**Rama**: `us-entrega-a4`, desde la punta de `us-ux-07`. Sin PR (discrepancia RU-11 declarada)
**SHA base**: pendiente. Se fija al abrir implementación con `git rev-parse --short HEAD` y se escribe aquí. Ancla del diff: `git diff --name-only <sha_base>`. **QA no usa `HEAD~N`**
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

Nueve recorridos con el MCP de Playwright, detallados en §6.3 del plan: las cuatro combinaciones de tema y modo, la persistencia sin destello, la franja de alcance, los cuatro estados de la pantalla de catálogo, las alturas con la tipografía nueva y las siete capturas del tema. **Se anotan aquí al ejecutarse.**
