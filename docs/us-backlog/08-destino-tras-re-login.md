# 08 — Tras el re-login no se vuelve a la ruta que se intentaba abrir

**Origen**: US-017, 12-ago-2026.
**Estado**: abierto, y es una decisión tomada, no un olvido.

## Qué pasa

La guarda de sesión rebota a `/acceso` cualquier ruta de producto abierta sin sesión, y añade
`?motivo=expirada` cuando la sesión existía y se perdió. Lo que **no** hace es recordar a dónde iba
el lector: tras autenticarse, `destinoPorRol()` lo deja en el espacio de trabajo de su perfil, no en
`/exploracion/tableros`, que era lo que había escrito en la barra de direcciones.

## Por qué no se resolvió sobre la marcha

Por tres razones, en este orden:

1. **Ningún criterio lo pide.** §26 del plan enumera tres criterios para esta US —guarda de sesión,
   ocultamiento por rol y estado sin permiso sin botón de reintento— y ninguno menciona el destino
   posterior al re-login.
2. **Obliga a abrir un archivo de otra US.** Implementarlo exige que `frontend/app/pages/acceso.vue`
   lea un parámetro `destino` y lo use tras autenticar. Esa pantalla, con sus cinco estados y su
   selector de demostración, es la entrega central de US-015: tocarla desde aquí es exactamente la
   clase de defecto de frontera que la auditoría del lote anterior contabilizó tres veces.
3. **El valor es pequeño y el riesgo no.** Un parámetro de destino que no se valide contra
   `RUTAS_CONTRATO` es un *open redirect*: `/acceso?destino=https://otro-sitio` convierte la
   pantalla de entrada del portal en un trampolín. Hacerlo bien es una lista blanca, su prueba y su
   caso negativo, y eso no cabía en una US de 0.5 SP.

## Qué costaría

Tres cambios pequeños y una prueba que no es pequeña:

- La guarda añade `destino` al `query` de la redirección, solo cuando la ruta pertenece a
  `RUTAS_CONTRATO`.
- `pages/acceso.vue` lo lee y lo prefiere sobre `destinoPorRol()`.
- Una prueba parametrizada de rechazo: rutas absolutas, rutas con `//`, rutas fuera del contrato y
  la propia `/acceso`, que produciría un ciclo.

## Qué lo absorbe

**US-027**, que ya toca `frontend/app/utils/sesion.ts` y los espacios de trabajo por rol, o el cierre
de S4 si aparece en una prueba con usuarios. Hoy la prioridad es baja: `destinoPorRol()` deja a
alguien que acaba de rebotar en su propio espacio de trabajo, que para esa persona es el sitio
correcto la mayor parte de las veces.
