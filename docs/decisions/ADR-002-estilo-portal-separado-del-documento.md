# ADR-002 — El estilo del portal y el del documento son sistemas separados

**Fecha**: 11-ago-2026
**Estado**: vigente, con una discrepancia abierta (ver más abajo)

## Contexto

La interfaz se veía a documento impreso. La causa era que sus colores se derivaban de
`docs/entregables/estilo/uxdoc.sty`, la hoja de estilo del informe del curso. Esa paleta está
optimizada para tinta sobre papel, no para jerarquía en pantalla: contrastes pensados para
impresión, sin modo oscuro y sin la separación de planos que una interfaz necesita.

## Decisión

Son dos sistemas, y no se derivan uno del otro.

- `docs/entregables/estilo/uxdoc.sty` es la hoja de estilo **del informe** y está **congelada**:
  A1, A2 y A3 ya se entregaron y compilan contra ella.
- El portal tiene su propia fuente de tokens en `design/sistema.py`, con dos modos y su matriz
  de contraste calculada por modo.
- **Prohibido derivar el aspecto del portal de `uxdoc.sty`.**

Lo que sí viaja del portal al informe es **contenido, no formato**: el generador emite las
láminas con la paleta real del portal para que la guía de estilos de A4 documente el producto, y
esas láminas se maquetan con la tipografía y las reglas del informe. Una muestra de color del
portal impresa en el informe es contenido; no convierte al informe en el portal ni al revés.

## Discrepancia abierta — pendiente de resolver

Esta decisión dice que la fuente de los tokens del portal es `design/sistema.py`. El código dice
otra cosa: `make tokens` ejecuta `docs/entregables/generar_tokens_a4.py`, cuya constante
`RUTA_FUENTE` apunta a `docs/entregables/estilo/uxdoc.sty` y cuya salida es
`frontend/app/assets/css/main.css`. Es decir, hoy la cadena que corre en la máquina es
exactamente la que esta decisión prohíbe.

Las dos salidas posibles:

1. Reapuntar `make tokens` a `design/sistema.py` y dejar `generar_tokens_a4.py` solo para las
   láminas del informe.
2. Aceptar que `uxdoc.sty` sigue siendo la fuente y derogar esta decisión.

Hasta que el equipo elija, ninguna guía de carpeta debe afirmar de dónde salen los tokens. Lo
que sí es cierto en ambos escenarios, y lo que las guías deben decir, es que `main.css` es
**generado**, no se edita a mano, y `scripts/verificar_tokens_a4.sh` detecta la edición manual.

## Dónde vive la regla

[`docs/AGENTS.md`](../AGENTS.md) para el informe · [`frontend/AGENTS.md`](../../frontend/AGENTS.md)
para `main.css`.
