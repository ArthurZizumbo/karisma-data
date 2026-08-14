# 05 — La limitación de intentos de acceso está prometida en un comentario y no existe

**Origen**: US-015, 11-ago-2026. La promesa la escribió US-001 en `frontend/server/api/[...].ts`.
**Estado**: abierto, deliberadamente.

## Qué pasa

El comentario que justifica la reescritura de las cabeceras de reenvío en el proxy de Nitro cerraba diciendo que
el spoof de `X-Forwarded-For` «envenena tanto los registros como la limitación de intentos de acceso que US-015
colgará de la IP del cliente». Ese segundo motivo describía trabajo futuro como si fuera un requisito adquirido.

**US-015 no implementa ninguna limitación de intentos**, y no es un olvido: §26 del plan, que manda durante S4, no
la lista entre los criterios de aceptación de la US, y ninguno de los veinte CA de
[`docs/us-planning/us-015.md`](../us-planning/us-015.md) la pide. Añadirla habría sido alcance inventado sobre una
US de 1.5 SP en la semana del entregable mejor pagado (R11 del plan, guardia contra el scope creep).

Lo que sí quedó cerrado en US-015 es la otra mitad de esa frase: la reescritura de las cabeceras sigue en pie y el
proxy ganó la verificación de origen de QA-M2, así que la superficie CSRF que el comentario mencionaba de paso ya
no está abierta. El comentario se corrigió para decir lo que el código hace hoy y para apuntar aquí.

## Por qué no se resolvió sobre la marcha

Una limitación de intentos que valga algo no son cuatro líneas. Necesita decidir el contador (por IP, por usuario,
o por el par), dónde vive el estado —y el proyecto descartó Redis por decisión irrevocable, así que sería memoria
del proceso, que no sobrevive al escalado a cero de Cloud Run, o una tabla, que mete una escritura en el camino
caliente del login—, la ventana, el castigo, y qué se le dice a la persona bloqueada sin revelarle que su usuario
existe, que es justo la neutralidad que CA-7 protege.

Ninguna de esas decisiones cabía en el martes de US-015 sin desplazar trabajo que sí está en la rúbrica.

## Qué lo absorbe

**US-016 o el cierre de S4**, y solo si aparece la necesidad. Hoy el prototipo tiene siete usuarios sintéticos, una
puerta de demostración sin credencial —`DEMO_LOGIN_ENABLED`, apagada por omisión— y ningún dato real: un ataque de
fuerza bruta contra el login no obtiene nada que la propia pantalla de demostración no regale.

El día que la bandera de demostración se apague porque hay un dato que proteger, esta entrada deja de ser una
mejora y pasa a ser un requisito. Ese mismo día es el gate que
[`docs/security.md`](../security.md) (US-016) y US-003 tienen que verificar.

## Adenda del 11-ago-2026: no es solo fuerza bruta, también es disponibilidad

La auditoría de seguridad de US-015 señaló un segundo motivo que este archivo no recogía. `argon2id`
está configurado con el perfil recomendado de pwdlib —64 MiB de memoria y cuatro hilos por
verificación— y ese costo se paga **en el camino no autenticado**, una vez por intento, incluidos
los fallidos. Es exactamente lo que hace fuerte al hash y exactamente lo que lo vuelve un
amplificador: unas pocas peticiones por segundo contra `POST /api/auth/token` agotan la memoria de
una instancia de Cloud Run mucho antes de que nadie adivine una contraseña.

Cambia dos cosas de esta entrada:

1. **El umbral de urgencia.** El razonamiento de arriba —«un ataque de fuerza bruta no obtiene nada
   que la puerta de demostración no regale»— sigue siendo cierto y sigue sin justificar la
   limitación **por confidencialidad**. No dice nada sobre **disponibilidad**, y por ese lado la
   deuda sí muerde el día del despliegue, aunque los datos sigan siendo sintéticos.
2. **Qué mide el contador.** Una limitación pensada contra la adivinación cuenta por usuario; una
   pensada contra el agotamiento cuenta por IP y por proceso. Quien la construya tiene que decidir
   las dos, y el diseño sin estado del proyecto —sin Redis, escalado a cero— hace que la segunda
   no sea trivial: un contador en memoria del proceso no sobrevive a un arranque en frío.

Hoy sigue siendo **baja**: no hay nada desplegado. Se vuelve un gate de US-003, junto con el apagado
de `DEMO_LOGIN_ENABLED`.
