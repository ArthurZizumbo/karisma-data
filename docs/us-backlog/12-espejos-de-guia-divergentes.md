# 12 — `AGENTS.md` y `CLAUDE.md` de `backend/` y `frontend/` dejaron de ser espejos

**Origen**: agente de pruebas de US-AVANCE-5, 22-ago-2026, al buscar qué defecto real justificaba escribir una prueba.
**Estado**: abierto. La divergencia existe hoy en el árbol.

## Qué pasa

El orquestador de la raíz declara la regla en dos sitios, y la declara sin matices:

> **Guía de carpeta** (`<dir>/AGENTS.md` y `<dir>/CLAUDE.md`, también espejos)… Modificar uno exige sincronizar el otro.

En `backend/` y en `frontend/` esa igualdad ya no se cumple: a los dos `CLAUDE.md` les faltan los párrafos sobre
Cloud Run que sus `AGENTS.md` sí traen. La divergencia entró en `b7b4aca`, durante US-M01, al documentar el
despliegue solo en una de las dos mitades.

La consecuencia no es cosmética. Los dos archivos existen precisamente porque los leen herramientas distintas:
Claude Code carga `CLAUDE.md` y los demás agentes de código cargan `AGENTS.md`. Mientras difieran, **dos agentes
que trabajen sobre la misma carpeta operan bajo instrucciones distintas**, y el que lea la mitad incompleta no
sabrá que esa capa ya está desplegada en Cloud Run.

`docs/AGENTS.md` y `docs/CLAUDE.md` sí están sincronizados: US-AVANCE-5 los reescribió y los dejó byte-idénticos.

## Por qué no se resolvió en US-AVANCE-5

Por dos razones que apuntan en la misma dirección.

La primera es de alcance: US-AVANCE-5 es la entrega final de la actividad 5 y su write-set vive entero dentro de
`docs/`. `backend/` y `frontend/` quedan fuera, y ensanchar el alcance el día antes de una entrega calificada
—para tocar la guía de dos capas que esta US no modifica— habría sido cambiar el riesgo de sitio sin necesidad.

La segunda es de orden. La comprobación automática que cerraría el agujero —difundir los dos archivos de cada
carpeta y fallar si difieren— es de tres líneas y encaja en `make check`. Pero **nacería en rojo**, porque la
divergencia ya está ahí. Un gate que nace rojo sobre archivos ajenos a la US que lo introduce es un gate que
alguien desactiva en la primera prisa. Primero se sincroniza la causa; después se pone la barrera que impide que
vuelva.

## Qué lo absorbe

Una US propia después de la entrega de A5, en dos pasos y en este orden:

1. **Sincronizar** los cuatro archivos, tomando como fuente el `AGENTS.md` de cada carpeta, que es el que tiene
   los párrafos de Cloud Run. Conviene revisar de paso `db/`, `ml/` y `tests/`, que no se auditaron.
2. **Añadir la comprobación** a `make check`: un `diff -q` por carpeta sobre las parejas
   `<dir>/AGENTS.md` y `<dir>/CLAUDE.md`, más la pareja de la raíz. Con la causa ya corregida, el gate nace verde
   y a partir de ahí el desvío se detecta el mismo día en que se introduce.
