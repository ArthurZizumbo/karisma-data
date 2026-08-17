# Prueba manual — US-ENTREGA-A4

**SHA base**: `aeafc6e` · **Rama**: `us-entrega-a4` · **Estado del handoff**: `testing`
**Ámbito**: solo lo que exige navegador real, PDF abierto o juicio humano. Todo lo demás está en
`make check`, `make test` y los recorridos automatizados ya ejecutados.
**Revisión de QA**: 15-ago-2026, 15:30. Cambios respecto de la versión de las 03:03 al final.

> ## Antes de tocar nada: el árbol no es el que produjo el PDF
>
> La rama sigue **sin commitear** y sobre ella arrancó una segunda US, **US-A4-EXCELENCIA**, que a
> las 13:55 del 15-ago reescribió `design/sistema.py` y regeneró `main.css` y
> `tokens.generated.ts`. El contrato de color pasó de **17 tokens a 21** (`accion`, `accion-apoyo`,
> `seleccion`, `reticula`) y el valor institucional de `info` en claro cambió de `123C7A` a
> `17395B`.
>
> **Consecuencia para esta prueba**: el portal que levantes hoy **no es** el que retrata
> `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` ni el que describen `a4_08` y `a4_04`. M1, M2
> y M3 miden el portal vivo contra un documento que ya no lo describe, y van a divergir por diseño,
> no por defecto. Consulta la tabla de bugs del handoff (QA-1 a QA-5) antes de reportar nada como
> hallazgo nuevo.
>
> Para probar US-ENTREGA-A4 tal como se entregó hace falta separar las dos US en commits distintos.
> Mientras no ocurra, esta prueba manual mide el estado combinado.

## Preparación

```bash
docker compose up -d --build          # db, api y web; espera a que las tres den "healthy"
docker compose ps                     # las tres filas en Up (healthy)
```

> **`web` no monta el código.** Su único volumen es el anónimo de `node_modules`, así que sirve lo
> horneado en la imagen: **cualquier cambio de frontend exige `docker compose up -d --build web`**
> antes de volver a probar. Una prueba contra la imagen vieja no dice nada.

Ventana a **1440x900**. `DEMO_LOGIN_ENABLED` encendida en `backend/.env.local`.

---

## Lo ya verificado con el MCP de Playwright — no repetir a mano

Los catorce recorridos de §6.3 del plan se ejecutaron y pasaron; el detalle con sus cifras está en el
handoff. Se listan aquí para que nadie gaste tiempo repitiéndolos: V1 a V8 (cuatro combinaciones,
persistencia sin destello, franja, cuatro estados del catálogo, familia y desbordes), V9 (once
capturas), V10 a V14 (rol desde el cromo, rol sin permiso, entrada en frío, retorno y un clic desde
el índice), más tres vectores de redirección abierta.

**Lo que sigue es lo que una máquina no puede juzgar.**

---

## M1 · El tema institucional se lee como el de la institución

**Pasos**
1. Abre `http://localhost:3000/inicio` y entra con el perfil **Analista**.
2. En la cabecera pulsa **Azul institucional**.
3. Recorre `/inicio`, `/exploracion` y `/gobierno` en modo claro, y luego en modo oscuro.

**Resultado esperado**
La paleta se lee como una identidad y no como un filtro de color sobre el tema anterior: el azul de
navegación manda, la letra es Inter y las cifras conservan el ancho fijo. En oscuro el suelo es un
azul profundo, **nunca negro puro**. Ningún bloque queda sin color ni hereda el color del otro tema.

**Juicio humano requerido**: si alguna pantalla se lee como «el tema de siempre con otro azul», el
tema no está haciendo su trabajo aunque las cifras de contraste pasen.

---

## M2 · El violeta del canal informativo no se lee como un error de marca

**Pasos**
1. Con el tema institucional puesto, busca en el portal un aviso informativo (modo claro y oscuro).
2. Compáralo con el color de confirmación que aparece al lado.

**Resultado esperado**
Se distinguen de un vistazo. En oscuro el informativo es un **violeta** deliberado, no un azul
apagado: es la única familia que bajo tritanopia no colapsa contra el verde de éxito.

**Juicio humano requerido**: el violeta es la decisión más discutible de esta entrega (riesgo R10 del
plan). Si al equipo le resulta ajeno a la identidad, la salida documentada es **aceptar el colapso y
declararlo en la guía con su dE**, nunca publicarlo sin decirlo.

---

## M3 · Las siete pantallas del tema, revisadas como imágenes del entregable

**Pasos**
1. Abre las once capturas de `docs/entregables/figuras/a4/tema/`.
2. Compáralas contra las de `figuras/a4/despues/`, que son del tema de omisión.

**Resultado esperado**
Las once están a 1440x900, ninguna tiene un cursor, un menú abierto ni un estado accidental, y todas
llevan la franja de alcance. **Las de `antes/` y `despues/` no cambiaron**: son evidencia cerrada de
la primera iteración y una recaptura destruiría el par.

---

## M4 · El PDF de la entrega, leído de principio a fin

**Pasos**
1. Abre `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` (92 páginas).
2. Comprueba la portada: **Mayoral Terán Alexandro, Sarmiento Cervantes Jacqueline, Zizumbo Velasco
   Arthur Jafed**.
3. Recorre el índice y confirma el orden: método, prototipos, guía de estilos, pre-validación,
   alcance, **el tema institucional**, **los cinco flujos**, cierre y anexo.
4. Lee la sección del tema institucional y la de los cinco flujos.

**Resultado esperado**
- Ninguna tabla se sale de la caja, ninguna figura queda huérfana de su pie, ningún `??`.
- **Cada pie de las láminas de flujo lleva la palabra «diseño»** y dice que no es una captura del
  portal en ejecución. Son diez pies: si a uno le falta, es el riesgo R8 y es crítico reputacional.
- El documento habla del **producto y de la entrega**: en ninguna página se atribuye una mitad a
  nadie ni se comparan las dos superficies como si compitieran.
- El tema institucional aparece **después** del alcance y **antes** del cierre. Si aparece detrás del
  anexo, el `\input` se movió.

**Juicio humano requerido**: que la sección nueva no repita lo que la guía de estilos ya dice. Sus 63
subsecciones cubren identidad, retícula, microinteracciones, voz y tono; `a4_08` solo aporta el tema,
su matriz y los flujos.

---

## M5 · El documento acumulado sigue contando una sola historia

**Pasos**
1. Abre `docs/entregables/main_completo.pdf` (240 páginas).
2. Lee «Sobre este documento» y la portadilla de la parte IV.
3. Salta a la parte IV y comprueba que el tema y los flujos están dentro.

**Resultado esperado**
Los dos textos describen lo consolidado —dos temas verificados en los dos modos y cinco flujos de
tarea— y no la versión anterior del producto. Las partes I a III no se movieron.

---

## M6 · El enlace al archivo de diseño abre de verdad

**Pasos**
1. En el PDF, sección «Acceso al archivo de trabajo», pulsa el enlace.
2. Comprueba las tres páginas: Guía de estilo (`0:1`), Componentes (`5:29`), Prototipos (`5:30`).

**Resultado esperado**
El enlace abre el archivo sin instalar nada y las tres páginas existen con esos nodos. **CA-14 depende
de esto y no se puede automatizar**: un enlace bien escrito hacia un archivo sin permisos de lectura
se ve idéntico a uno correcto.

**Juicio humano requerido**: comprobar que el archivo es **visible para quien califica**, no solo
para quien lo creó. Ábrelo en una ventana privada o con otra cuenta.

---

## M7 · La entrada en frío, con alguien que no conozca el portal

**Pasos**
1. Cierra sesión y borra las cookies `karisma_*`.
2. Pide a alguien que no haya visto el portal que abra `http://localhost:3000/` y que **entre a
   «Gobierno del dato»**. No le des ninguna instrucción más.

**Resultado esperado**
Llega a la pantalla de gobierno **en un clic**, sin pasar por el formulario y sin preguntar nada.

**Juicio humano requerido**: es el recorrido del evaluador y el motivo de la mitad de esta US. Si esa
persona duda, pregunta o retrocede, el defecto sigue vivo aunque V14 pase. Observa **dónde** duda.

---

## M8 · La preferencia sobrevive al cruce de layout

**Pasos**
1. Sin sesión, en `/acceso`, pon el modo **oscuro** y el tema **institucional**.
2. Entra con cualquier perfil de demostración.
3. **Sin recargar**, mira el fondo.

**Resultado esperado**
La pantalla sigue oscura. Si aparece clara mientras el selector marca «Oscuro», ha vuelto el defecto
del dueño de la entrada de `useHead`: `app.vue` debe instanciar `useSistemaDiseno()`.

---

## M9 · Subida a Canvas

**Pasos**
1. Sube `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` con **ese nombre exacto**.
2. Descarga lo subido y ábrelo.

**Resultado esperado**
El archivo descargado es el de 92 páginas y pesa unos 5.1 MB. Entregado antes del **dom 16, 20:00**
(gate 26.4, margen de 3h59 contra las 23:59).

---

---

## M10 · La tarjeta del índice, pulsada donde no hay texto

**Por qué existe**: el defecto corregido en implementación —la tarjeta que navegaba sin acuñar
sesión— se cerró con `@click.capture`, y su prueba de regresión dispara el clic **sobre un
descendiente del ancla** a propósito. El caso que nadie ejerció es el clic que cae en el ancla misma:
la tarjeta es `h-full` dentro de una retícula sin `gap-y`, así que las tarjetas más cortas de cada
fila tienen **zona vacía debajo del texto**, y ahí el destino del evento es el `<a>`. En esa
posición el navegador dispara captura y burbuja en orden de registro, no por fases, y el orden entre
el manejador propio y el de `vue-router` deja de estar garantizado por la corrección aplicada.

Una sonda en `happy-dom` con el `RouterLink` real **sí acuña sesión**, pero happy-dom no es prueba
de navegador para una regla de despacho de eventos. Esto se decide en Chromium.

**Pasos**
1. Cierra sesión y borra las cookies `karisma_*`. Abre `http://localhost:3000/`.
2. Localiza en cada fila de la retícula la tarjeta **más corta** (la que deja hueco bajo su texto).
3. Con la pestaña de red abierta, pulsa ese **hueco vacío**, no el título ni el subtítulo.
4. Repite en las tres anchuras: 1440, 1024 y 768 px.

**Resultado esperado**
Se dispara `POST /api/auth/demo` y se aterriza **dentro** de la pantalla con sesión del perfil que la
tarjeta declara. Si en cambio se aterriza en `/acceso` con el formulario, el defecto de
`preventDefault` sigue vivo en su mitad no cubierta: la corrección sería mover la decisión fuera del
ancla, no volver a jugar con la fase del evento.

**Automatizable** con el MCP de Playwright: `browser_click` sobre coordenadas del cuadro del ancla
por debajo del último hijo, comprobando `browser_network_requests`.

---

## M11 · La lámina de paleta de `/guia` cuenta 21 y pinta 18

**Por qué existe**: `laminas.spec.ts` está en rojo y el motivo es visible en pantalla. El emisor
produce un quinto grupo, `ACCION`, que `stores/sistemaDiseno.ts` no expone y `LaminaPaleta.vue` no
recorre: sus `GRUPOS` siguen siendo cuatro. La guía viva es un artefacto que la rúbrica de A4
califica, y hoy **se contradice a sí misma en su propio encabezado**.

**Pasos**
1. Abre `http://localhost:3000/guia` y ve a la lámina de paleta.
2. Lee el encabezado y cuenta las fichas pintadas.

**Resultado esperado**
El encabezado dice «21 tokens de color» y hay **18** fichas: faltan `accion`, `accion-apoyo` y
`seleccion`. Es un defecto abierto (QA-4), no un artefacto del entorno. Se cierra exponiendo el
grupo en el store y añadiéndolo a `GRUPOS`, no ajustando la cuenta del encabezado.

---

## Cambios de la revisión de QA del 15-ago, 15:30

| Paso | Cambio |
|---|---|
| Preámbulo | Aviso nuevo: el árbol combina dos US y el PDF ya no describe al portal |
| M10 | **Nuevo.** El clic en la zona muerta de la tarjeta, mitad no cubierta del defecto corregido |
| M11 | **Nuevo.** La lámina de paleta de `/guia`, con `laminas.spec.ts` en rojo |
| M1 · M2 · M3 | Sin cambios de texto, pero **léelos con el aviso del preámbulo**: van a divergir del PDF |

---

## Limpieza

```bash
docker compose down
```
