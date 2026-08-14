# 04 — El PDF que se entrega está en `.gitignore` y los seis anteriores entraron a la fuerza

**Origen**: US-UX-09, 11-ago-2026, al commitear el documento de A4.
**Estado**: abierto. Tiene fecha límite real: dom 16-ago 23:59.

## Qué pasa

`.gitignore:28` ignora `docs/entregables/*.pdf`. Es una regla razonable: el PDF es una salida de `latexmk` y
versionar un binario que se regenera ensucia el historial.

Pero **el PDF es el entregable**. Los seis PDF de A1, A2 y A3 están versionados, lo que significa que alguien los
añadió con `git add -f` y no lo escribió en ningún sitio. `docs/entregables/main_a4.pdf` existe hoy en disco —32
páginas, compilado— y `git status` **no lo menciona**: quien mire el estado del repositorio el sábado por la noche
va a creer que no hay nada que subir.

## Por qué no se resolvió en US-UX-09

Esta US produce las 13 secciones de la guía de estilos, no el documento completo: `main_a4.tex` todavía tiene que
recibir las siete pantallas de US-UX-07. Commitear ahora un PDF que va a cambiar entero no aporta nada.

## Qué lo absorbe

**US-UX-07**, y conviene que sea un paso explícito de su lista de cierre, no una corazonada:

```bash
latexmk -xelatex main_a4.tex
git add -f docs/entregables/main_a4.pdf
```

La alternativa —quitar la línea de `.gitignore`— se rechaza: volvería a meter en el historial cada PDF intermedio de
cada compilación de prueba. La excepción explícita en el momento de entregar es más barata que la regla laxa todo el
tiempo.

**El riesgo concreto que esto evita**: entregar en Canvas un PDF que no está en el repositorio, y que por tanto
nadie más del equipo puede regenerar ni revisar.
