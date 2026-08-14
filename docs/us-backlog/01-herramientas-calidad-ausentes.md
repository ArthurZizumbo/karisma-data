# 01 — Las herramientas que `make check` exige no vienen con el repositorio

**Origen**: US-002, 10-ago-2026, al ejecutar el gate de calidad por primera vez en la máquina de trabajo.
**Estado**: mitigado en local, abierto para CI.

## Qué pasa

`make check` invoca `gitleaks` desde el `PATH` del host y falla con un mensaje de instalación si no está. El día 10
de agosto **no estaba instalado** en la máquina, así que el secrets-scan del QA Gate era una puerta que nadie había
cruzado todavía: el objetivo existía, el binario no.

Se instaló `gitleaks 8.28.0` en `~/.local/bin/gitleaks.exe`, fuera del repositorio. Eso deja el gate operando **en
esta máquina y en ninguna otra**. `mypy` sí está, pero dentro del entorno virtual de Poetry, no en el `PATH`, y por
eso `make lint` lo llama con `poetry -P backend run`.

## Por qué no se resolvió en US-002

US-002 entrega reproducibilidad de **dependencias del proyecto** —los candados de Poetry y pnpm— no del **entorno
del desarrollador**. Instalar un binario de Go en tres máquinas distintas no es un cambio de archivo: es una
instrucción de arranque, y su sitio natural es el pipeline, donde se ejecuta una vez y vale para todos.

## Qué lo absorbe

**US-004 (Pipeline CI/CD con GitHub Actions)**, hoy congelada. El paso de `ci.yml` debe instalar `gitleaks` con la
acción oficial en vez de asumirlo en el `PATH`, de modo que el escaneo corra en cada push aunque ninguna máquina
local lo tenga.

Mientras US-004 siga congelada, la mitigación es la que ya está escrita en el propio `Makefile`: si el binario falta,
`check` **se detiene con exit 1** en vez de continuar en silencio. Un gate que se salta sin avisar es peor que un
gate ausente.
