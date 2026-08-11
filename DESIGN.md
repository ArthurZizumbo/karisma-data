---
name: Karisma Data
description: Sistema de diseño del portal, escrito desde lo construido y no desde lo planeado
colors:
  ground: "#F4F6F9"
  ground-alt: "#EAEEF4"
  grid: "#DCE2EB"
  corriente-apagado: "#A8B2C1"
  corriente-tenue: "#5F6A7D"
  corriente-medio: "#414B5B"
  corriente-pleno: "#14171D"
  error: "#8C1D18"
  aviso: "#9A6200"
  ok: "#1F6F43"
  info: "#6D28D9"
  serie-1: "#1D4ED8"
  serie-2: "#B45309"
  serie-3: "#1F6F43"
  serie-4: "#6D28D9"
  serie-5: "#0E7490"
  serie-6: "#9D174D"
  ground-oscuro: "#0A0A0C"
  ground-alt-oscuro: "#131519"
  grid-oscuro: "#1C2028"
  corriente-apagado-oscuro: "#4A5361"
  corriente-tenue-oscuro: "#7A8698"
  corriente-medio-oscuro: "#B4C2D4"
  corriente-pleno-oscuro: "#E8F4FF"
  error-oscuro: "#FF5A36"
  aviso-oscuro: "#FFC233"
  ok-oscuro: "#4ADE80"
  info-oscuro: "#C4B5FD"
typography:
  display:
    fontFamily: "Lexend Deca, system-ui, sans-serif"
    fontSize: "40px"
    fontWeight: 600
    lineHeight: "44px"
    letterSpacing: "-0.02em"
  titulo-1:
    fontFamily: "Lexend Deca, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: "34px"
    letterSpacing: "-0.015em"
  titulo-2:
    fontFamily: "Lexend Deca, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: "26px"
    letterSpacing: "-0.01em"
  titulo-3:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: "20px"
  cuerpo:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "21px"
  cuerpo-amplio:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "26px"
  etiqueta:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: "16px"
    letterSpacing: "0.03em"
  dato:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "16px"
    fontWeight: 500
    lineHeight: "22px"
  micro:
    fontFamily: "Fira Sans, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 500
    lineHeight: "15px"
    letterSpacing: "0.02em"
rounded:
  sm: "2px"
  md: "4px"
  lg: "6px"
  full: "999px"
spacing:
  unidad: "4px"
  grid-gap: "16px"
  panel-padding: "24px"
  sidebar-width: "232px"
  sidebar-collapsed: "56px"
  header-height: "52px"
  table-row-height: "34px"
components:
  boton-primario:
    backgroundColor: "{colors.corriente-pleno}"
    textColor: "{colors.ground}"
    typography: "{typography.etiqueta}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  boton-contorno:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.corriente-pleno}"
    typography: "{typography.etiqueta}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  boton-destructivo:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.error}"
    typography: "{typography.etiqueta}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  campo:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.corriente-pleno}"
    typography: "{typography.cuerpo}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  chip:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.corriente-tenue}"
    typography: "{typography.etiqueta}"
    rounded: "{rounded.sm}"
    padding: "2px 8px"
  fila-tabla:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.corriente-pleno}"
    typography: "{typography.cuerpo}"
    height: "{spacing.table-row-height}"
  nodo-diagrama:
    backgroundColor: "{colors.corriente-pleno}"
    rounded: "{rounded.full}"
    size: "10px"
---

# Design

## Overview

**Mundo visual: diagrama hombre-máquina.** Una retícula visible como suelo, conectores ortogonales,
y corriente que se enciende al recorrer una cifra hacia su origen. Elegido por el usuario el
11-ago-2026 sobre la dirección que el tiro de concepto había asignado.

**Modo de la superficie: Operate.** El éxito es que la persona termine su tarea. Cuando la
necesidad del usuario trabajando y la del evaluador chocan, gana el usuario.

**Fuente única, en un solo sentido:**

```
design/sistema.py        <- los valores, declarados una vez
design/contraste.py      <- WCAG y las tres dicromacias, calculadas
design/emitir.py         <- publica lo que midio
        |
        +--> frontend/app/assets/css/main.css        (@theme + los dos modos)
        +--> frontend/app/utils/tokens.generated.ts  (paleta tipada)
        |
        v
   stores/sistemaDiseno.ts   <- resuelve cada token contra el modo en pantalla
        |
        v
   los componentes
```

`docs/entregables/estilo/uxdoc.sty` **no está en esta cadena**. Es la hoja de estilo del informe del
curso y está congelada: A1, A2 y A3 ya se entregaron y compilan contra ella. Una muestra de color del
portal impresa en el informe es **contenido, no formato**.

Este documento se escribe **al cerrar el rediseño y desde el código construido**. La versión anterior
describía el sistema que se iba a reemplazar y afirmaba, entre otras cosas, que la barra lateral
colapsaba a 768 px: el token existía y nadie lo había implementado.

## Colors

**Dos canales, y esa separación es la decisión central.**

**Canal 1, la corriente.** Cuatro peldaños de luminancia pura: `corriente-apagado`, `-tenue`,
`-medio`, `-pleno`. La luminancia es el único canal que ninguna dicromacia pierde, así que el estado
se lee por brillo. Salto mínimo medido: 0.061 en claro y 0.149 en oscuro.

**Canal 2, los semánticos.** `error`, `aviso`, `ok`, `info`, y siempre **color más forma más icono**.
Nunca color solo, y no por cortesía: la separación medida bajo las tres dicromacias simuladas es de
dE 21.5 en oscuro y **13.4 en claro**. El segundo es un techo estructural, no falta de esfuerzo:
sobre fondo claro los cuatro deben superar 4.5:1, lo que los encierra por debajo de 0.16 de
luminancia, y cuatro tonos no separan ahí dentro. Un lector con protanopia distingue un error de un
aviso **por el aspa y el triángulo**.

**No hay verde en la rampa de corriente.** La paleta original del mundo era de semáforo, y rojo
contra verde bajo protanopia separa dE=20.0: justo en el umbral, sostenido solo por luminancia.

`grid` y `corriente-apagado` quedan **por debajo de 3:1 a propósito** y el sistema declara que no
informan nunca. Son retícula y filete decorativo, no límite de componente. La verificación comprueba
las dos direcciones: que lo que informa alcance el umbral y que lo que dice no informar no lo alcance.

## Typography

Tres familias: **Lexend Deca** para titulares, **Fira Sans** para texto, **IBM Plex Mono** para
cifras. Nueve roles.

**El peso es un canal de jerarquía**, no decoración: 400 para texto corrido, 500 para etiquetas y
cifras, 600 para titulares. El sistema anterior fijaba 400 en los nueve roles, y la página medida
daba **750 de 750 nodos de texto en ese único peso**, encabezados incluidos, con una relación
título/cuerpo de 1.71. Con el tamaño como único canal y pasos de 1.2, ningún salto se leía como salto.

El cuerpo por omisión es 14 px: es una interfaz densa donde una tabla tiene que dejar ver muchas
filas. La prosa no pasa de **68 caracteres por línea**; lo medido antes llegaba a 179.

## Layout

Retícula de 12 columnas con canal de 16 px, ritmo en base 4.

| Punto de quiebre | Comportamiento, verificado en el navegador |
|---|---|
| 768 px | La barra lateral **colapsa de verdad** a una franja de 56 px de iconos |
| 1024 px | Vuelve con etiqueta |
| 1280 px | Segunda columna del tablero |
| 1440 px | Ancho de captura de las figuras del informe |

Medido a 375 px sobre `/guia`: desbordamiento horizontal **0**, barra lateral **56 px**, contenido
**319 px**, y **cero** elementos desbordando fuera de un contenedor con scroll propio. Las cifras
anteriores eran 112, 240, 135 y 148.

## Elevation & Depth

**Dos niveles, y solo donde comunican.** `menu` para lo que se abre encima, `dialogo` para lo que
interrumpe. El mundo separa regiones con la retícula y con `ground-alt`, no con sombra: el sistema
anterior declaraba tres niveles y la página medida usaba uno.

## Shapes

Radios de 2, 4 y 6 px, más el círculo completo para lo que es genuinamente redondo. El mundo está
**dibujado, no moldeado**: las esquinas son ajustadas.

El anillo de foco tiene **una sola definición**, en `app/utils/foco.ts`, con la cadena de clases
literal para que el escáner de Tailwind la vea. Una prueba recorre todos los `.vue` y falla si
alguno escribe su propio contorno; ya cazó una reincidencia durante este rediseño.

## Components

- **Barra lateral**: el mismo suelo que la página, separada por filete. El módulo activo se marca con
  corriente y peso, nunca con un bloque de color. La versión anterior era una losa de 240 × 900 del
  color de más contraste de la pantalla, y ganaba la primera lectura por delante del título.
- **Cabecera**: selector de modo de tres estados —claro, oscuro y seguir al sistema— y selector de
  idioma. Presente en las cuatro superficies de chasis.
- **Tarjeta de indicador**: la cifra manda, sin borde, con una regla derivando hacia ella. Lleva su
  etiqueta de método visible cuando es una proyección: honestidad de demostración.
- **Cadena de llamada a herramienta**: cuatro nodos colgando de una regla, con la corriente subiendo
  por la rampa. La consulta es visible en los cuatro momentos, y el que falla **no lleva ninguna
  cifra**. Es la regla antialucinación hecha inspeccionable.
- **Estado pendiente**: una pantalla cuyo contenido llega en una US posterior lo declara con sus
  capacidades como nodos apagados y el identificador de la historia que las entrega.
- **Los cuatro estados no felices** —vacío, cargando sin desplazamiento, error y sin permiso— son
  parte de cada pantalla.

## Do's and Don'ts

**Reglas del sistema, que la interfaz debe cumplir**

- El estado se lee por luminancia. El color lo refuerza y nunca lo sustituye.
- Todo semántico viaja con forma e icono.
- `corriente-apagado` y `grid` no informan nunca.
- El peso construye jerarquía: 400, 500, 600.
- La prosa no pasa de 68 caracteres por línea.
- La barra lateral colapsa por debajo de 768 px.

**Prohibido**

- Editar `main.css` o `tokens.generated.ts` a mano. Son generados y `make verificar` lo detecta.
- Leer un token desde el módulo generado en un componente: se lee del store, que lo resuelve contra
  el modo en pantalla.
- Derivar el aspecto del portal de `uxdoc.sty`.
- Scroll-hijack, marquesinas y animación decorativa. El modo es Operate: la animación se justifica
  con jerarquía, retroalimentación o cambio de estado, o no entra.
- Cualquier cifra en la interfaz sin procedencia visible.

**Deuda declarada, medida y no escondida**

- **50 objetivos táctiles por debajo de 44 px a 375 px** en `/guia`. La superficie está pensada para
  escritorio y las figuras del informe se capturan a 1440, pero es una deuda real de accesibilidad
  móvil y no está resuelta.
- La **capa de alias de US-001** sigue viva en el emisor. Ya no la usa ninguna pantalla ni ninguna
  lámina; se retira cuando nada la referencie.
- **Cobertura del frontend en 51.39 %** sobre un umbral de 50. Bajó al retirar 833 líneas de pruebas
  que fijaban el marcado de láminas reescritas y dejar 133 de contrato.
