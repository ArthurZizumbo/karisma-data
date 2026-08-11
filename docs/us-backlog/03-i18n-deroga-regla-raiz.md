# 03 — La interfaz pasa a ser bilingüe y eso deroga una regla NON-NEGOTIABLE

**Origen**: US-UX-09, 10-ago-2026, decisión del usuario al arrancar la Fase 3.
**Estado**: resuelto dentro de US-UX-09; queda anotado por su alcance transversal.

## Qué pasa

El `AGENTS.md` y el `CLAUDE.md` raíz decían, entre las reglas NON-NEGOTIABLE: *«No hay i18n: la UI es solo en
español»*. El contrato de trabajo de la Fase 3 exigía lo contrario: interfaz en español **e inglés**.

Resuelto por el usuario a favor de i18n. La interfaz de la aplicación es bilingüe con `@nuxtjs/i18n`, estrategia
`no_prefix` y cookie `karisma_locale`.

## Las dos consecuencias que hay que recordar

1. **Las URLs no cambian.** `no_prefix` es deliberado: `RUTAS_CONTRATO` está anclado al mapa de navegación de A3 y
   fijado por `frontend/test/navegacion.spec.ts` y `scripts/smoke_rutas.sh`. Un prefijo `/en/` rompería el contrato
   de rutas del entregable A3 ya calificado.
2. **El PDF sigue siendo solo en español.** i18n aplica a la aplicación, no al documento de la actividad. La
   sección de voz y tono de la guía de estilos sí cubre las dos lenguas, porque describe la interfaz.

## Deuda que deja

Toda US de frontend posterior debe entregar sus cadenas en los **dos** locales. La prueba que lo hace verificable
—paridad de claves entre `es.json` y `en.json`— se entrega en US-UX-09; sin ella, el inglés se degrada solo, una
pantalla por US, y nadie se entera hasta la demostración.
