# ADR-001 — La interfaz web es bilingüe con i18n real

**Fecha**: 10-ago-2026
**Estado**: vigente
**Deroga**: la regla anterior de «UI solo en español»

## Contexto

Hasta el 10-ago-2026 la regla transversal decía que la interfaz se escribía solo en español, y
en consecuencia las cadenas visibles se escribían directamente en los componentes Vue. Eso es
lo que cualquier desarrollador haría por defecto y lo que el modelo propone por inercia, pero
cerraba la puerta a mostrar el producto a un evaluador que no lea español y volvía imposible
auditar qué texto ve el usuario sin abrir cada `.vue`.

## Decisión

La interfaz es bilingüe **español + inglés** con i18n real: `@nuxtjs/i18n`,
`strategy: 'no_prefix'`, `defaultLocale: 'es'`, idioma en la cookie `karisma_locale`.

Ninguna cadena visible se escribe en un componente. Viven en
`frontend/i18n/locales/{es,en}.json` con claves jerárquicas en inglés y se resuelven con
`useI18n()`.

`strategy: 'no_prefix'` no es un detalle cosmético: mantiene las URLs estables, y por eso el
mapa de rutas acordado en A3 sigue siendo válido sin reescribirlo.

## Consecuencias

- Una clave nueva se agrega a `es.json` **y** a `en.json`; una sola locale deja la UI a medias.
- Los entregables PDF del curso siguen siendo **solo en español**. Esta decisión aplica al
  producto, no a los documentos.
- Hoy nada mecánico impide escribir un string suelto en un template: no hay regla de eslint que
  lo detecte. Mientras no la haya, la prohibición vive en `frontend/AGENTS.md` y depende de la
  revisión. Añadir `@intlify/eslint-plugin-vue-i18n` con `no-raw-text` cerraría el hueco.

## Dónde vive la regla

[`frontend/AGENTS.md`](../../frontend/AGENTS.md) — sección Convenciones.
