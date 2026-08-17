# Checklist de defectos de interfaz — Karisma Data

> Reglas de revisión, no un sistema de diseño. La fuente generativa sigue siendo la skill
> `ui-ux-pro-max`, de la que derivan la paleta y la tipografía de
> [`../entregables/estilo/uxdoc.sty`](../entregables/estilo/uxdoc.sty) desde la Actividad 1.
> Este archivo se aplica **después** de construir, como filtro.

## Por qué esto es un archivo y no una skill instalada

Las reglas de abajo vienen de `taste-skill` (Leonxlnx/taste-skill), evaluada el 10-ago-2026. Se
adoptan como checklist y **no se instala la skill**, por dos razones concretas:

1. **Su §2 manda usar un sistema oficial ajeno.** Para un brief de analítica empresarial B2B
   prescribe `@carbon/react` y prohíbe escribir CSS propio. Eso contradice una decisión
   irrevocable del stack: Tailwind v4 con tokens derivados de `uxdoc.sty`.
2. **Ella misma declara fuera de alcance** *"Dashboards, dense product UI, data tables,
   multi-step forms"*, que describe seis de las siete pantallas del portal.

Instalarla además crea colisión de invocación: su descripción y la de `ui-ux-pro-max` compiten
por el mismo tipo de prompt, y el modelo puede cargar ambas y recibir reglas contradictorias en
el mismo contexto (densidad 4 «airy» contra densidad máxima; `text-6xl` contra 14 px de cuerpo).

`impeccable.style` queda evaluada y **diferida a la semana del 24-ago**, después de A5. Es un
detector, no un sistema, así que sus falsos positivos se ignoran sin daño; pero necesita un
`DESIGN.md` que declare nuestros tokens antes de correr, o audita contra sus propios defaults y
marca nuestro sistema como desviación.

## Alcance por superficie

| Superficie | Rutas | Reglas que aplican |
|---|---|---|
| **Índice de prototipos** (es una página de aterrizaje) | `/` | Las 12 |
| **Producto denso** (tableros, tablas, paneles) | `/inicio`, `/exploracion`, `/gobierno`, `/asistente`, `/administracion` | 1 a 10; las 11 y 12 no aplican |

## Las diez reglas, con su verificación

| # | Regla | Cómo se verifica |
|---|---|---|
| 1 | **Un solo color de acento** en toda la superficie. Los semánticos (verde vigente, rojo error, ámbar aviso) no cuentan como acento: son estado, no decoración | Buscar usos de ámbar `#F97316` fuera de filete, marca, momento de la verdad y estado «requiere atención» |
| 2 | **Una sola escala de radios**. `--radius-sm/md/lg`, con `--radius-full` reservado a badges de rol y avatares como excepción documentada | `grep` de `rounded-` y de `border-radius` fuera de los tokens |
| 3 | **Una sola familia de iconos** (Lucide), sin SVG dibujados a mano, sin emoji como icono estructural | Revisar imports de iconos; buscar `<svg>` inline y caracteres emoji en plantillas |
| 4 | **Ni negro puro ni blanco puro**. Superficie más clara `#F8FAFC`, texto más oscuro `#0F172A`. **Una excepción declarada**: bajo el tema institucional el suelo claro es `#FFFFFF`, ver abajo | `grep` de `#000`, `#fff`, `black`, `white` en CSS y plantillas |
| 5 | **Prohibido el falso producto dibujado con `div`**. En el documento van capturas reales de la aplicación | Toda figura de pantalla sale del guion de Playwright, ninguna a mano |
| 6 | **Contraste verificado en botones**. Sin botón claro con texto claro, sin botón transparente sin borde. El ámbar nunca lleva texto blanco (2.6:1) | Matriz de contraste de `generar_tokens_a4.py` |
| 7 | **Ningún rótulo de botón se parte en dos líneas** en escritorio | Revisión visual de la ruta `/guia` a 1440 y 1280 px |
| 8 | **Sin dos llamadas a la acción con la misma intención** en una misma pantalla. Una acción primaria por pantalla | Recuento de botones variante «Contenido» por ruta: debe ser 1 |
| 9 | **Sin etiquetas de versión decorativas** ni tiras de texto ornamental (`001 · Índice`, `BETA`, `Scroll ↓`) | Lectura del índice y de los encabezados de sección |
| 10 | **El movimiento debe estar motivado**. Cada animación declara qué comunica; sin marquesinas; sin `addEventListener("scroll")` a mano | Inventario de animaciones del sistema de diseño: seis entradas, cada una con su columna «qué comunica» |

## Las dos que sí aplican solo al índice

| # | Regla | Nota |
|---|---|---|
| 11 | **El héroe cabe en el viewport inicial**: titular de máximo 2 líneas, subtexto de máximo 20 palabras | Solo `/`. En producto denso la primera pantalla es contenido, no héroe |
| 12 | **Restricción de eyebrow**: máximo 1 rótulo en versalitas con tracking amplio por cada 3 secciones | Solo `/`. Verificación mecánica: contar instancias de `uppercase tracking` |

## Las dos reglas que se rechazan, y por qué

Adoptar una guía entera sin criterio es el defecto que la propia guía denuncia. Estas dos no
pasan:

| Regla rechazada | Razón |
|---|---|
| **Cero guiones largos en todo el texto** | Es una heurística anti-slop pensada para copia publicitaria en inglés. En prosa española el guion largo es tipografía correcta y los cuatro documentos del curso lo usan. En cadenas de interfaz, que son cortas, no aparece de todos modos |
| **Imágenes reales obligatorias en toda página** | Karisma Data es un producto de datos. El sistema de diseño ya declara que no hay fotografía decorativa; añadirla restaría seriedad. Las únicas imágenes son la marca, los avatares por iniciales y los gráficos de datos |

## La excepción de la regla 4, declarada

El tema **institucional** pinta su suelo claro en `#FFFFFF`, blanco puro, y el token `reticula`
resuelve al mismo valor para no dibujar cuadrícula. La regla 4 lo prohíbe y aun así se queda.

**La razón**: *Superficie* del archivo de diseño **es** blanco puro, y ese tema existe para llevar el
archivo, no para mejorarlo. Es un choque entre dos fuentes normativas —este checklist y la lámina de
identidad— y se resuelve a favor del archivo, que es la fuente que el entregable cita. **El tema de
omisión no cambia**: conserva `#F4F6F9` y sigue siendo el suelo que la regla describe, así que el
producto nunca queda sin una superficie conforme.

**El alcance de la excepción es exactamente un token en un tema**: `ground` bajo `institucional` en
claro. Cualquier otro blanco puro que aparezca en una plantilla o en una hoja sigue siendo un
hallazgo. El precio de moverlo está medido: cambiar ese valor desplaza los 44 pares de la matriz de
contraste y deja sin correspondencia las once capturas tomadas contra él.

La declaración vive también en `design/sistema.py`, en el comentario del propio token, que es donde
la va a leer quien esté a punto de oscurecerlo.

## Reglas propias del proyecto que este checklist no cubre

Están en la guía de estilos de A4 y en las reglas NON-NEGOTIABLE de
[`../../AGENTS.md`](../../AGENTS.md): cifras tabulares en toda columna numérica, alternativa en
tabla para cada gráfica, `aria-sort` en tablas ordenables, `prefers-reduced-motion` respetado,
área táctil de 44 × 44 px, anillo de foco visible que nunca se elimina, y la prohibición de
emojis en código, comentarios, commits y logs.

## Bitácora

| Fecha | Cambio |
|---|---|
| 10-ago-2026 | Creado. Evaluación de `taste-skill` e `impeccable.style` registrada en `docs/semana_4/plan_excelencia.md`, sección 8 |
| 16-ago-2026 | Excepción de la regla 4 declarada: el suelo claro del tema institucional es `#FFFFFF`, por procedencia del archivo de diseño. La detectó el QA de US-A4-EXCELENCIA, que la encontró aplicada y sin declarar |
