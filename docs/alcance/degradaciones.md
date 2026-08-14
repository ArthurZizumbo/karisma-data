# Degradaciones acordadas del alcance

Registro de lo que **se decidió no construir** y por qué. Una degradación no es una tarea pendiente
ni un defecto: es alcance recortado por escrito, con su motivo, su fecha y la condición que la
levantaría. Lo que no esté aquí y no esté construido es una omisión, no una degradación.

La tabla de alcance de cada entregable (A4, A5) se arma leyendo este archivo: si una fila no está
escrita aquí, no puede declararse en el documento del curso.

| US | Qué queda fuera | Por qué | Qué la levanta | Fecha |
|---|---|---|---|---|
| US-024 | **Botón «Reintentar»** en el aviso de error del asistente (recorte #4) | Reintentar exige reenviar el turno completo con el contexto ya consumido y una política de idempotencia que S4 no tiene. Un botón desactivado no es una versión reducida: ofrecer el reintento y negarlo sigue siendo ofrecerlo | El campo `recuperable` ya viaja en el evento `error` y está probado. Levantarlo es enchufar un control a un booleano existente, sin tocar el contrato SSE v1 | 14-ago-2026 |
| US-024 | El error de permiso **no abre un flujo de solicitud de acceso**: nombra el nivel requerido y remite al administrador | El flujo de solicitud toca la administración de usuarios (US-018) y queda fuera de S4 | Una US que conecte el aviso con la alta de solicitud de US-018 | 14-ago-2026 |
| US-024 | El evento de turno **no distingue cuál de varias tools falló** | Esa correlación vive en el `id` de la tarjeta (US-028). Duplicarla en el evento de turno sería un segundo vocabulario para el mismo dato | Nada pendiente: es una decisión de diseño del contrato, no una carencia | 14-ago-2026 |
| US-024 | Los errores del asistente **no se persisten ni se agregan** | No hay tabla ni US de observabilidad en S4; el error es efímero por diseño y no toca esquema | Una US de observabilidad con su migración dbmate reversible | 14-ago-2026 |
| US-024 | El **nivel exigido** que muestra el aviso de permiso es una constante de la pantalla, no un dato del evento | El contrato SSE v1 congela cinco campos y ninguno transporta el nivel: el backend no publica lo que le habría hecho falta a quien no puede ver el dato. Con el proveedor guionizado hay un solo rechazo (C4) y es de nivel `analista` | Un proveedor real que derive el nivel de la consulta que falló; el aviso ya cae a su copia genérica cuando nadie se lo aporta | 14-ago-2026 |
