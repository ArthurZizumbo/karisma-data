# 11 — `make tokens` estaba cableado al emisor equivocado y destruía el sistema de diseño del portal

**Origen**: QA de US-023, US-024 y US-028, 14-ago-2026. Descubierto al ejecutar `make tokens`, que es
el comando que la propia guía manda ejecutar. Fuera del alcance de las tres US.
**Estado**: **resuelto el 14-ago-2026**, en la misma rama del QA. Queda anotado por su alcance
transversal: la corrección elige la primera de las dos salidas que
[ADR-002](../decisions/ADR-002-estilo-portal-separado-del-documento.md) dejó abiertas, y ese ADR
todavía no lo refleja (ver «Lo que queda abierto»).

## Qué pasaba

**Dos programas distintos escribían el mismo archivo, y el Makefile solo corría uno.**

`frontend/app/assets/css/main.css` es un artefacto generado, y su propia cabecera declara de dónde
sale:

```
 * Karisma Data - sistema de diseno del portal v2.0 - 2026-08-16
 * Fuente:    design/sistema.py
 * Emisor:    design/emitir.py
 * Regenerar: make tokens
 *
 * El estilo del INFORME vive en docs/entregables/estilo/uxdoc.sty y es otro
 * sistema: esta cadena no lo lee ni lo escribe.
```

Pero `Makefile:147` no corría ese emisor:

```make
tokens:
	poetry -P backend run python docs/entregables/generar_tokens_a4.py
```

Y `docs/entregables/generar_tokens_a4.py` declaraba ese mismo archivo como salida suya (`RUTA_CSS`,
línea 47) y lo escribía en `emitir_theme_css()` (línea 819). El archivo que producía abría así:

```
 * Guia de estilos de Karisma Data v1.0 - 2026-08-16
 * Fuente unica: docs/entregables/estilo/uxdoc.sty
 * Generador:    docs/entregables/generar_tokens_a4.py
```

De modo que ejecutar `make tokens` **sustituía el sistema de diseño del portal (v2.0, derivado de
`design/sistema.py`) por la paleta del informe (v1.0, derivada de `uxdoc.sty`)**, y de paso reescribía
`frontend/app/utils/tokens.generated.ts`.

Eso contradecía de frente la regla NON-NEGOTIABLE de la raíz:

> **El estilo del portal y el del informe son sistemas SEPARADOS.** [...] Prohibido derivar el
> aspecto del portal de esa paleta — está optimizada para tinta sobre papel.

## Por qué no lo detectaba nada

`scripts/verificar_tokens_a4.sh` **no protegía el archivo: lo pisaba**. Su paso 3 («Idempotencia del
generador») ejecutaba `generar_tokens_a4.py` **dos veces sin condición**, así que el propio
verificador —y con él `make verificar`, que lo invoca— dejaba el `main.css` del informe en
`frontend/`.

El mismo paso 3 empezaba corriendo `generar_tokens_a4.py --verificar`, que fallaba siempre: el disco
tenía v2.0 y el generador producía v1.0. El guion traducía ese fallo a
`«alguna difiere: corre 'make tokens' y commitea»`, es decir, **recomendaba exactamente la acción que
consumaba la pérdida**.

Y la sección «No tocar» de `frontend/AGENTS.md` afirmaba algo falso:

> `app/assets/css/main.css` y `app/utils/tokens.generated.ts` — generados; `make tokens` los rehace,
> y `scripts/verificar_tokens_a4.sh` detecta la edición manual regenerando y comparando byte a byte
> contra el disco.

No detectaba edición manual. Detectaba que había dos emisores, y sobrescribía.

## Reproducción — antes de la corrección

```bash
git status --short frontend/app/assets/css/main.css   # limpio
make tokens
git status --short frontend/app/assets/css/main.css   # M
head -8 frontend/app/assets/css/main.css              # ahora dice "Fuente unica: uxdoc.sty"
git checkout -- frontend/app/assets/css/main.css frontend/app/utils/tokens.generated.ts
```

Verificado el 14-ago-2026. Hoy esa secuencia ya no reproduce nada: `make tokens` sobre un árbol
limpio lo deja limpio.

## Cómo se corrigió

**1. Un solo emisor por archivo.** `docs/entregables/generar_tokens_a4.py` pierde `RUTA_CSS` y
`RUTA_TS` y las dos entradas correspondientes de su tabla de salidas: ya solo escribe
`docs/entregables/estilo/a4_tokens.tex` y `docs/entregables/datos/a4_tokens.json`.
`design/emitir.py` es el único dueño de lo que vive en `frontend/`.

**2. `make tokens` corre los dos emisores**, en un orden declarado —primero el portal, después el
informe, que es el sentido en que se lee la cadena de A4: la interfaz se emite, se captura y la
captura entra en el PDF— y con un comentario que explica qué produce cada uno y por qué son dos y no
pueden fundirse.

**3. `scripts/verificar_tokens_a4.sh` dejó de escribir.** La idempotencia se comprueba emitiendo a un
directorio temporal y comparando con `diff -r`, nunca regenerando en sitio. Para eso los dos emisores
reciben una bandera `--destino DIR`, que refleja el árbol de salidas bajo `DIR` conservando la ruta
relativa; `--verificar` acepta la misma bandera. El guion sigue siendo POSIX `sh`, sin argumentos y
sin modos, y borra el temporal con un `trap`. Sus expectativas quedan repartidas por cadena: las once
anclas y el inventario de 37 nombres se comprueban contra `uxdoc.sty`, que sigue siendo la fuente
legítima **del informe**; la versión se comprueba `v1.0` en las salidas del informe y `v2.0` en las
del portal, porque son sistemas separados y no comparten número. Se añade una comprobación que antes
no existía: **cada salida declara su emisor y no lleva la firma del otro**, que es exactamente la
condición que este defecto rompía.

**4. La frase falsa de «No tocar»** de `frontend/AGENTS.md` y su espejo `frontend/CLAUDE.md` dice
ahora quién emite cada archivo y qué comprueba el guion —que compara sin regenerar—, en vez de
prometer una detección que no existía.

### Verificación

```bash
git status --short frontend/app/assets/css/main.css frontend/app/utils/tokens.generated.ts  # vacío
make tokens
git status --short frontend/app/assets/css/main.css frontend/app/utils/tokens.generated.ts  # vacío
bash scripts/verificar_tokens_a4.sh   # 5 bloques en verde, sin ensuciar nada
```

## Lo que queda abierto

- **ADR-002 necesita un sucesor.** Su sección «Discrepancia abierta» ofrecía dos salidas y el código
  ya tomó la primera: `make tokens` emite el portal desde `design/sistema.py` y `generar_tokens_a4.py`
  se queda con las láminas del informe. Un ADR no se edita cuando cambia la realidad, se deroga con
  otro; `docs/decisions/` no estaba en el write-set de esta corrección.
- **`emitir_theme_css` y `emitir_tokens_ts` siguen en `generar_tokens_a4.py`** aunque ya no escriben
  en ningún sitio: sus únicos llamantes son tres pruebas de `tests/entregables/test_tokens_a4.py`, y
  `tests/` tampoco estaba en el write-set. Quedan documentadas como lo que son —una representación de
  la paleta del informe que nadie consume— y US-UX-09 debería decidir si esas aserciones se reapuntan
  a `a4_tokens.tex` y `a4_tokens.json` y las dos funciones se borran.
- **La cabecera compartida** `_cabecera()` de `generar_tokens_a4.py` sigue diciendo que un cambio a
  mano «hace divergir la aplicacion del PDF del curso». Ya solo divergiría el PDF. Corregirla reescribe
  el contenido de dos archivos generados que están versionados, así que se deja para el commit que
  toque esas láminas y no para este, cuya prueba de aceptación es precisamente que el árbol quede
  limpio.
- **`docs/us-handoff/us-009.md` y `docs/us-planning/us-009.md`** describen el guion anterior y su
  CA-6 (`git diff --exit-code` sobre `main.css` tras correr el generador del informe). Son el registro
  de lo que se hizo en US-UX-09 y no se tocaron.
