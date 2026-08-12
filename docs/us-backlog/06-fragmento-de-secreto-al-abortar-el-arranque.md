# 06 — Al abortar el arranque, el error imprime un fragmento de un secreto

**Origen**: auditoría de seguridad del diff de US-016 y US-008, 12-ago-2026. Hallazgo fuera del rango auditado.
**Absorbe**: **US-003** (despliegue serverless), que es cuando el mensaje empieza a ir a un log de Cloud Run y deja de verse solo en una terminal local.

## Qué pasa

`backend/app/core/config.py` deja escapar la `ValidationError` de Pydantic tal cual. Pydantic incluye en el mensaje un `repr` truncado del **mapa de entrada completo**, y para un modelo de `pydantic-settings` construido desde un dotenv ese mapa son *todas* las variables del archivo, incluidas las que el modelo ni siquiera declara.

Reproducido: con `APP_ENV=produccion` sobre el `backend/.env.local` de una máquina de desarrollo, la aplicación aborta —que es lo que debe hacer— y el mensaje termina en los últimos 22 caracteres del valor de `KARISMA_DEMO_PASSWORD`. Se identificó comparando el fragmento contra el nombre de la variable, sin imprimir el valor.

Hoy es benigno: el arranque falla en una terminal local y el secreto es una contraseña de demostración. Deja de serlo el día que ese mismo camino corra en Cloud Run con `JWT_SECRET_KEY` de Secret Manager, porque el mensaje de una revisión que no arranca **va derecho al log**, y un log de arranque fallido es justo lo que alguien pega en un chat para pedir ayuda.

## Por qué no se resolvió al encontrarlo

El arreglo es de una línea —`error.errors(include_input=False)`, o `SecretStr` en los campos sensibles— pero **cambia el tipo de excepción que ve quien llama**, y hay cinco aserciones de US-001 escritas contra `pydantic.ValidationError` en `tests/backend/test_config.py` (líneas 36, 74, 104 y 126). `backend/app/core/config.py` y ese archivo de pruebas **no están en el write-set de US-016 ni de US-008**: tocarlos habría sido invadir alcance ajeno para arreglar algo que no es bloqueante, que es exactamente lo que la regla de fronteras del proyecto existe para impedir.

## Qué hay que hacer

1. Envolver `Settings()` en `get_settings()` y relanzar con la entrada omitida, o declarar `JWT_SECRET_KEY`, `GEMINI_API_KEY` y `KARISMA_DEMO_PASSWORD` como `SecretStr`.
2. Actualizar las cinco aserciones de `tests/backend/test_config.py` al tipo nuevo.
3. Añadir una prueba que arranque con un dotenv que contenga una variable ajena con valor reconocible y **asserte que ese valor no aparece en el texto de la excepción**. Sin esa prueba el arreglo se pierde en el primer refactor.
