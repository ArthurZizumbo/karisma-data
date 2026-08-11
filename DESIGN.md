---
name: Karisma Data
description: Sistema de diseño vigente del portal centralizado de datos financieros, extraído del generador de tokens
colors:
  primary-100: "#DBEAFE"
  primary-300: "#93C5FD"
  primary-500: "#2563EB"
  primary-700: "#1F4D78"
  primary-900: "#0F2C46"
  secondary-100: "#E3EDF7"
  secondary-300: "#B8CCE4"
  secondary-500: "#3B82F6"
  secondary-700: "#1E5FA8"
  secondary-900: "#14385F"
  accent-100: "#FEEBD9"
  accent-300: "#FDBA8C"
  accent-500: "#F97316"
  accent-700: "#C2540A"
  accent-900: "#7C3606"
  success-100: "#DCFCE7"
  success-300: "#86EFAC"
  success-500: "#16A34A"
  success-700: "#166534"
  success-900: "#0B3D1F"
  surface: "#F8FAFC"
  surface-alt: "#EEF3FA"
  line: "#CBD5E1"
  line-strong: "#64748B"
  muted: "#64748B"
  ink: "#1E293B"
  ink-strong: "#0F172A"
  danger: "#B91C1C"
  danger-strong: "#7F1D1D"
  warning: "#C2540A"
  info: "#2563EB"
  serie-1: "#2563EB"
  serie-2: "#C2540A"
  serie-3: "#166534"
  serie-4: "#7C3AED"
  serie-5: "#0E7490"
  serie-6: "#9D174D"
typography:
  display:
    fontFamily: "Lexend Deca, sans-serif"
    fontSize: "32px"
    fontWeight: 400
    lineHeight: "40px"
    letterSpacing: "-0.01em"
  titulo-1:
    fontFamily: "Lexend Deca, sans-serif"
    fontSize: "24px"
    fontWeight: 400
    lineHeight: "32px"
    letterSpacing: "-0.01em"
  titulo-2:
    fontFamily: "Lexend Deca, sans-serif"
    fontSize: "20px"
    fontWeight: 400
    lineHeight: "28px"
  titulo-3:
    fontFamily: "Lexend Deca, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "22px"
  cuerpo:
    fontFamily: "Fira Sans, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "20px"
  cuerpo-amplio:
    fontFamily: "Fira Sans, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "26px"
  etiqueta:
    fontFamily: "Fira Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "16px"
    letterSpacing: "0.04em"
  dato:
    fontFamily: "Fira Sans, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: "24px"
  micro:
    fontFamily: "Fira Sans, sans-serif"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: "16px"
rounded:
  sm: "4px"
  md: "6px"
  lg: "10px"
  full: "999px"
spacing:
  unidad: "4px"
  grid-gap: "8px"
  card-padding: "12px"
  sidebar-width: "240px"
  header-height: "56px"
  table-row-height: "36px"
components:
  boton-primario:
    backgroundColor: "{colors.primary-500}"
    textColor: "#FFFFFF"
    typography: "{typography.cuerpo}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  boton-secundario:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary-700}"
    typography: "{typography.cuerpo}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  boton-destructivo:
    backgroundColor: "{colors.danger}"
    textColor: "#FFFFFF"
    typography: "{typography.cuerpo}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  campo:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.cuerpo}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  tarjeta:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "{spacing.card-padding}"
  chip:
    backgroundColor: "{colors.primary-100}"
    textColor: "{colors.primary-700}"
    typography: "{typography.etiqueta}"
    rounded: "{rounded.sm}"
    padding: "2px 8px"
  fila-tabla:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.cuerpo}"
    height: "{spacing.table-row-height}"
---

# Design

## Overview

Sistema de una sola fuente: `docs/entregables/generar_tokens_a4.py` emite el bloque `@theme` de
Tailwind v4, la paleta tipada que consume la interfaz, las láminas LaTeX y un manifiesto JSON.
**Ningún color se escribe a mano en un componente**, y hay un `grep` que lo verifica.

Modo de la superficie: **Operate**. El éxito es que la persona termine su tarea, así que la
escaneabilidad, la consistencia y la densidad de datos pesan más que la expresión. Confirmado el
11-ago-2026: cuando la necesidad del usuario trabajando y la del evaluador chocan, gana el usuario.

**Este documento captura el estado vigente antes del rediseño, y es a la vez referencia y
anti-referencia.** Lo que sirve —la disciplina de fuente única, la matriz de contraste calculada,
la escala de nueve roles, el vocabulario en español— se conserva. Lo que no —el diagnóstico está en
«Do's and Don'ts»— se reemplaza en `new-work`.

## Colors

Cuatro familias de cinco tonos, siete neutros, cuatro semánticos y seis colores de serie
categórica distintos de la paleta de marca. **Los once colores marcados como ancla conservan su
valor byte a byte** porque las entregas A1, A2 y A3 ya están calificadas y compilan contra ellos:
`primary-500`, `primary-700`, `secondary-300`, `secondary-500`, `accent-500`, `success-700`,
`surface`, `surface-alt`, `line`, `muted`, `ink`.

**Reglas derivadas de la matriz de contraste, calculada con la fórmula WCAG 2.x sobre 37 pares.**
No son opiniones: el cálculo refutó cuatro reglas que se habían dado por buenas.

| Regla | Razón |
|---|---|
| `accent-500` es **solo decorativo**. Nunca informa | 2.68:1 sobre `surface`, falla el 3:1 de elemento gráfico |
| El ámbar que informa usa `accent-700` | 4.40:1, cumple |
| El texto de aviso usa `accent-900` sobre `accent-100` | 7.58:1 AAA. Con `accent-700` daba 3.96:1 y fallaba AA |
| El borde de campo usa `line-strong`, no `line` | `line` da 1.42:1 y falla el 3:1 de límite de componente |
| `muted` solo a partir de 14 px, y **nunca sobre `surface-alt`** | 4.27:1 sobre `surface-alt`: AA-grande únicamente |
| Blanco sobre `accent-500`: **prohibido** | 2.80:1. El número que circulaba, 2.6:1, estaba mal |

Ninguna gráfica depende solo del color: cada serie lleva forma de marcador y patrón de línea
propios, más alternativa en tabla y resumen textual.

## Typography

Dos familias servidas desde el propio origen: **Lexend Deca** para titulares y **Fira Sans** para
texto. Nueve roles, cada uno con su interlineado fijado en píxeles.

El cuerpo por omisión es **14 px**, no 16: es una interfaz densa donde una tabla tiene que dejar
ver muchas filas. Los 16 px viven en `cuerpo-amplio`, para párrafos largos como la ayuda, la
respuesta del asistente y el aviso de alcance. Las cifras usan `dato` con numeración tabular, para
que las columnas numéricas alineen.

## Layout

Retícula de 12 columnas con canal de 8 px. Ritmo en base 4: Tailwind deriva 4/8/12/16/24/32/48/64
de la unidad única.

| Punto de quiebre | Comportamiento |
|---|---|
| 768 px | **Declarado, no implementado.** El token existe y `BarraLateral.vue:37` usa `w-[var(--sidebar-width)]` sin ningún modificador responsivo. Medido a 375 px: la barra ocupa el 64 % y deja el contenido en 135 px, con 112 px de desbordamiento horizontal |
| 1024 px | Vuelve la barra lateral con etiqueta |
| 1280 px | Aparece la segunda columna del tablero |
| 1440 px | Ancho de captura de las figuras de A4 |

Medidas fijas del chasis: barra lateral 240 px, cabecera 56 px, fila de tabla densa 36 px.

**Los cuatro puntos de quiebre son aspiración, no comportamiento.** En toda la aplicación existen
7 modificadores `sm:`, 7 `lg:` y 2 `xl:`, y `guia.vue` y `portal.vue` no tienen ninguno. Corregido
el 11-ago-2026 tras medirlo: la versión anterior de este documento describía el colapso como si
ocurriera.

## Elevation & Depth

Tres niveles, y ninguno es negro puro: la sombra se tiñe con `ink-strong` a baja opacidad.

- **reposo** `0 1px 2px 0 rgb(15 23 42 / 0.06)` para tarjeta y tabla en reposo.
- **elevado** `0 2px 6px -1px rgb(15 23 42 / 0.1)` para tarjeta con puntero encima y menú abierto.
- **flotante** `0 8px 24px -6px rgb(15 23 42 / 0.18)` para diálogo, panel lateral y sugerencia.

## Shapes

Cuatro radios, asignados por función y no por gusto: 4 px chip e insignia · 6 px botón, campo y
celda activa · 10 px tarjeta, panel y diálogo · 999 px avatar, punto de estado y botón circular.

El anillo de foco tiene **una sola definición**, en `frontend/app/utils/foco.ts`, con la cadena de
clases literal para que el escáner de Tailwind la vea. Ningún `.vue` escribe una clase de contorno.

## Components

- **Barra lateral** sobre `primary-700`, con las cuatro categorías del mapa de A3 y las nueve
  facetas transversales como accesos cruzados.
- **Franja de alcance** permanente: declara que el prototipo usa datos sintéticos y no está
  conectado a sistemas reales. No se oculta ni se cierra.
- **Selector de idioma** en las cuatro superficies de chasis. La interfaz es bilingüe con
  estrategia sin prefijo: las URL no cambian.
- **Tarjeta de llamada a herramienta**, cuatro estados en secuencia: anuncio, ejecución, resultado
  con la fuente citada, error. El resultado aparece **antes** del texto generado.
- **Tabla densa** con cabecera fija, fila alterna sobre `surface-alt`, cifras tabulares y
  `aria-sort`.
- **Los cuatro estados no felices** —vacío, cargando sin desplazamiento de maquetación, error y sin
  permiso— son parte de cada pantalla. El estado «sin permiso» indica a quién pedir acceso y **no
  ofrece reintento**.

## Do's and Don'ts

**Conservar**

- La fuente única y el `grep` que prueba que ningún color está escrito a mano.
- La matriz de contraste calculada, no estimada. Ya evitó cuatro defectos impresos.
- El vocabulario de tokens en español y los nombres congelados: renombrar rompe componentes.
- Los once colores ancla, byte a byte.

**Reemplazar. Diagnóstico del 11-ago-2026 sobre la interfaz renderizada**

- **El sistema es monocromo azul sin quererlo.** Marca, texto secundario, bordes de chip, bordes de
  botón y barra lateral caen todos en la misma familia. Cuando todo es el color de marca, nada
  destaca: eso es lo que se lee como apagado. Falta terreno neutro de verdad.
- **La escala de nueve roles existe y la interfaz usa dos.** El título de pantalla es apenas mayor
  que el cuerpo. La jerarquía está emitida en los tokens y no aplicada en las plantillas.
- **Sopa de cajas.** Chip, tarjeta, botón y lámina comparten borde de 1 px y peso visual. Los tres
  niveles de elevación están definidos y prácticamente sin usar.
- **La navegación no usa ni un icono** habiendo 34 de Lucide empaquetados, y la marca es texto
  plano sin ninguna forma gráfica.
- **La causa raíz, y es de arquitectura, no de gusto:** la paleta se derivó de `uxdoc.sty`, una
  hoja de estilo LaTeX pensada para tinta sobre papel. Optimizaba legibilidad impresa, no jerarquía
  en pantalla. **La dirección de la cadena se invirtió el 11-ago-2026**: el sistema de diseño del
  producto pasa a ser el origen y el generador exporta hacia LaTeX. La tesis de fuente única
  sobrevive intacta; lo que cambia es quién manda.

**Prohibido, y no por conservadurismo**

- Nada de scroll-hijack, marquesinas ni animación decorativa. El modo es Operate y en un portal
  bancario el movimiento gratuito resta credibilidad. La animación se justifica con jerarquía,
  retroalimentación o cambio de estado, o no entra.
- Nunca editar `main.css` ni `tokens.generated.ts` a mano: son generados, y `make verificar` lo
  detecta.
- Ninguna cifra en la interfaz sin procedencia visible. Sin tarjeta de herramienta, no hay número.
