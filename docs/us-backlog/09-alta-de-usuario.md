# 09 — El alta de usuario está en el «quiero» de la US y no en sus criterios de aceptación

**Origen**: US-018 / US-019, 13-ago-2026. La bifurcación es la ambigüedad 1 de
[`docs/us-planning/us-018.md`](../us-planning/us-018.md).
**Estado**: abierto, por decisión escrita y no por olvido.

## Qué pasa

El bloque de §26 del plan abre con *«quiero dar de alta, cambiar de rol y desactivar usuarios»* y su primer
criterio de aceptación dice *«Listar, cambiar rol y desactivar»*. Son tres verbos contra tres verbos y solo dos
coinciden. **Mandó el criterio de aceptación**, por tres motivos comprobables en el propio plan: el recorte #5 de
§10.2 está escrito en la línea 579 con esas palabras exactas —*«listar + cambiar rol + desactivar»*, sin alta—;
la tarea técnica del mismo bloque enumera *«Endpoints de listar, cambiar rol y desactivar con scope `admin`»*; y
el «quiero» es la narrativa sin recortar de julio, mientras que una degradación acordada de antemano recorta el
alcance, no la motivación.

Consecuencia, dicha sin adornos: **`POST /api/users` no existe**. Hasta que se implemente, el portal solo
administra los siete usuarios que siembra la migración `create_app_user` de US-015.

La fila `POST /api/users` **sí está** en `SCOPE_REGISTRY` de `backend/app/core/permissions.py`, con scope `admin`
y estado `planificado`. No es una violación de la cobertura de scopes: US-016 §4.2 declara explícitamente que una
entrada del registro sin ruta viva es la forma correcta de anotar una ruta prevista, y `assert_scope_coverage`
audita en la dirección contraria —rutas montadas sin fila—, no esta.

## Por qué no se resolvió sobre la marcha

El alta no es un cuarto endpoint junto a los otros tres: arrastra decisiones que ninguno de ellos toca.

1. **La contraseña inicial.** Alguien tiene que fijarla. Si la fija el administrador, hay que decidir la política
   de contraseña, dónde se le comunica a la persona y con qué canal —y el proyecto **descartó por decisión
   irrevocable la recuperación de contraseña y el correo transaccional**, así que no hay canal—. Si la fija la
   persona, hace falta un flujo de invitación con un token de un solo uso, su caducidad y su tabla. Un usuario
   creado sin ninguna de las dos cosas es una cuenta muerta: existe en `app_user` y nadie puede entrar con ella.
2. **El 409 por duplicado.** `username` y `email` son únicos en el esquema. El alta es el **primer** camino del
   portal que puede chocar contra esa restricción, y hoy no hay ningún código de conflicto para eso: los tres de
   `UserErrorCode` que esta US introduce son de autoprotección del administrador, no de unicidad. Habría que
   traducir el error de integridad de PostgreSQL a un código estable sin filtrar el nombre del índice.
3. **La interfaz que lo acompaña.** Un formulario de alta con validación en los dos idiomas, su estado de envío y
   su manejo del 409 es trabajo de pantalla, no un botón. La degradación acordada de S4 lo quitó por eso.

Ninguna de esas tres decisiones cabía en el jueves de una US de 1 SP compartido entre backend, base de datos y
frontend, en la semana del entregable A4.

## Qué lo absorbe

**Una US propia después de S4.** No es candidata a «meterla al cierre de la semana»: el punto 1 obliga a reabrir
una decisión irrevocable —el proyecto no tiene canal para comunicar una credencial— y esa conversación es del
equipo, no de quien programe el endpoint.

Mientras tanto, la fila `planificado` del registro de permisos es el marcador: el día que alguien monte
`POST /api/users`, `assert_scope_coverage` no protestará porque la fila ya está, y quien lo haga tiene que llegar
aquí antes de escribir la primera línea.
