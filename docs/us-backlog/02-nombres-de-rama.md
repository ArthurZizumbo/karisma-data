# 02 — Las ramas de S4 no siguen el estándar del orquestador

**Origen**: US-001, 10-ago-2026. Recogido como RU-11 en el handoff de US-001.
**Estado**: abierto, deliberadamente.

## Qué pasa

El `AGENTS.md` raíz fija `feature/E{epic}-US-XXX-{slug}` y §26 del plan usa `feature/UX-US-UX-07-alta-fidelidad`.
Las ramas reales de esta semana son `us-001`, `us-002`, `us-ux-09`, … : cortas, encadenadas una sobre otra, con
commits locales y sin PR.

Es una decisión del usuario del 10-ago, no un descuido: durante la semana de A4 el trabajo va en una cadena lineal
de ramas locales, cada US sobre la punta de la anterior, y nada sale a `develop` hasta que la cadena cierre.

## Por qué no se resolvió sobre la marcha

Renombrar ramas a mitad de una cadena encadenada obliga a rehacer el punto de partida de todas las posteriores.
El costo es real y el beneficio, cosmético, mientras no haya PR que leer.

## Qué lo absorbe

**El cierre de S4**: cuando la cadena se integre, o bien se abre un PR único con el nombre estándar, o bien se
actualiza la regla del `AGENTS.md` para admitir la cadena local corta como forma válida del trabajo de una semana de
entrega. Las dos salidas son legítimas; lo que no lo es es dejar la regla escrita y la práctica en otro sitio sin
que ningún documento lo diga.
