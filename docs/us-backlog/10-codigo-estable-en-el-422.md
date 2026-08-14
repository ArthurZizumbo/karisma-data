# 10 — El 422 de validación viaja como frase en español, sin código estable

**Origen**: auditoría de documentación del diff de US-023, US-024 y US-028, 14-ago-2026. Hallazgo
transversal, fuera del alcance de las tres.
**Absorbe**: **una US propia**, después de S4. No es candidata al cierre de la semana; el porqué está
en la última sección.

## Qué pasa

`backend/AGENTS.md` fija el contrato en su línea 69: *«✅ Errores con código estable en
`detail.codigo` (`ErrorCode`, `SeriesErrorCode`, `LineageErrorCode`); ❌ nunca una frase en español,
que la interfaz bilingüe no puede traducir»*. La sección 4 de `docs/security.md` dice lo mismo para
el 401 y el 403. **El 422 de validación no cumple ninguna de las dos cosas, y no puede cumplirlas
con la forma que tiene hoy.**

`backend/app/models/chat.py` es el caso que disparó el hallazgo. Su validador `sin_espacios_vacios`
lanza `ValueError("el mensaje no puede ser solo espacios en blanco")`, y FastAPI lo publica como
`msg: "Value error, el mensaje no puede ser solo espacios en blanco"`. La interfaz recibe una frase
en un idioma, sin código con el que elegir la copia del otro.

**No es una regresión de US-023.** Es la forma que tienen los cuatro modelos del portal que declaran
validadores Pydantic, y tres de ellos son anteriores:

| Modelo | Validador | Qué lanza |
|---|---|---|
| `backend/app/models/chat.py` | `sin_espacios_vacios` (campo `mensaje`) | «el mensaje no puede ser solo espacios en blanco» |
| `backend/app/models/series.py` | `check_combination` | «serie_id solo se admite con agrupacion=serie…» y «desde no puede ser posterior a hasta» |
| `backend/app/models/user.py` | `role` en modo `before` | «'…' no es un rol del portal; el literal canonico es '…'» |
| `backend/app/models/user.py` | `at_least_one_change` | `SIN_CAMBIOS_SOLICITADOS: envia al menos uno de 'role' o 'disabled'` |
| `backend/app/models/export.py` | `dataset` | «'…' no es un conjunto exportable. Los exportables son…» |

Son **seis `raise ValueError` repartidos en cuatro modelos**; `catalog.py` y `lineage.py` no
declaran ninguno. De los seis, **uno solo** lleva un código estable: `at_least_one_change` de
`user.py` antepone `UserErrorCode.SIN_CAMBIOS_SOLICITADOS.value` al texto. Y esa excepción prueba el
defecto en lugar de negarlo, porque la única forma de leerla desde una prueba es
`assert UserErrorCode.SIN_CAMBIOS_SOLICITADOS.value in respuesta.text`
(`tests/backend/usuarios/test_users_reglas.py:372`): una búsqueda de subcadena sobre el cuerpo
entero, no un campo del contrato.

La raíz es que **no hay manejador de `RequestValidationError`**. `backend/app/main.py` registra un
solo `add_exception_handler`, el de `InvalidCredentialsError`. Sin manejador, FastAPI responde con su
cuerpo por omisión, donde `detail` es una **lista** de diccionarios `{type, loc, msg, input}`. En esa
forma `detail.codigo` no es que esté vacío: no puede existir. El contrato que el resto de la API
cumple no llega al 422 por construcción.

Lo que sí existe ya es el vocabulario. El repositorio tiene seis enumeraciones de código estable
—`ErrorCode` en `core/scopes.py`, y `ChatErrorCode`, `LineageErrorCode`, `SeriesErrorCode`,
`UserErrorCode` y `ExportErrorCode` en sus módulos—. Lo que falta es la pieza que traduce un fallo
de validación a una de ellas.

## Por qué no se resolvió sobre la marcha

Porque el arreglo correcto no cabe en el write-set de ninguna de las tres US del viernes, y el
arreglo que sí cabría es peor que el defecto.

1. **Tocar solo `chat.py` deja el portal con dos contratos de 422.** Uno tipificado para el
   asistente y cinco frases sueltas en el resto. Un cliente que quiera manejar el 422 tendría que
   preguntar primero a qué endpoint le habló. La incoherencia es más cara que la frase.
2. **El manejador global cambia la forma del cuerpo para todos los endpoints a la vez.** Pasar
   `detail` de lista a objeto rompe cualquier cliente que hoy lea `detail[0].msg`, y hay **22
   menciones de 422 repartidas en 9 archivos de `tests/backend/`** que fijan el comportamiento
   actual, incluidos los de `auth`, `catalog`, `export`, `series` y `usuarios`. Ninguno de esos
   archivos está en el write-set de US-023, US-024 ni US-028.
3. **Hay una decisión de diseño que no es de quien programa el endpoint**: si el 422 conserva la
   lista de errores de campo —que la interfaz necesita para marcar *qué* campo falló— y añade el
   código al lado, o si la sustituye. Es contrato público, y cambiarlo dos veces cuesta más que
   decidirlo una.

## Qué hay que hacer

1. Registrar un manejador de `RequestValidationError` en `create_app()` que emita un cuerpo con
   `detail.codigo` estable, conservando la localización por campo que la interfaz usa para marcar el
   control que falló.
2. Dar código a los seis `raise ValueError` de los cuatro modelos, con la enumeración que ya tiene
   cada módulo, y sacar el texto del mensaje: el código es el contrato, la frase es depuración.
3. Publicar los códigos nuevos en `docs/security.md` §4 —la tabla de código, clave i18n, español e
   inglés— y añadir su clave a `frontend/i18n/locales/{es,en}.json`, que es lo que exige ADR-001.
4. Reescribir la aserción de `tests/backend/usuarios/test_users_reglas.py:372` para que lea el campo
   del contrato y no una subcadena del cuerpo. Mientras siga siendo `in respuesta.text`, la prueba
   pasa aunque el código viaje dentro de una frase.

## Qué lo absorbe

Una US propia después de S4, junto con el resto de deuda de contrato. La regla vigente mientras
tanto, para que el defecto no crezca: **un validador Pydantic nuevo se escribe con el código de su
enumeración dentro del mensaje**, como ya hace `at_least_one_change` de `user.py`. Es un apaño y se
declara como tal, pero deja el trabajo del manejador global reducido a mover un valor que ya está
puesto, en vez de inventar seis códigos a posteriori.
