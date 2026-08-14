# Versión preliminar de la Actividad 4

Esta carpeta conserva **íntegra** la versión del documento de A4 que se publicó en `main` los días
previos al cierre, construida a partir del archivo de Figma. Se guarda aquí, y no se pierde en el
historial, porque es trabajo del equipo y porque su contenido alimenta la consolidación.

**No es la entrega.** La entrega es la que vive en las rutas canónicas —`../main_a4.tex` y
`../contenido/a4_*.tex`—, que es la que se compila, se renombra y se sube. Esta copia es un registro.

## Qué contiene

| Archivo | Qué aporta que la versión canónica no tenga |
|---|---|
| `contenido/a4_00_preliminares.tex` | Introducción centrada en el archivo de diseño y sus cifras |
| `contenido/a4_01_metodo_prototipado.tex` | Método de prototipado en Figma y acceso al archivo de trabajo |
| `contenido/a4_02_prototipos.tex` | **Los cinco flujos de tarea**, con persona, objetivo y secuencia |
| `contenido/a4_03_guia_estilos.tex` | Guía en once apartados, con la lámina de paleta del archivo |
| `contenido/a4_04_prevalidacion.tex` | Revisión y verificación técnica del archivo de diseño |
| `contenido/a4_05_alcance.tex` | Alcance y continuidad de la versión 1.0 |
| `contenido/a4_06_cierre.tex` | Conclusiones y referencias de esa versión |
| `contenido/a4_07_anexo.tex` | **Inventario técnico**: las tres páginas del archivo con sus nodos |
| `main_a4.tex` | Su envoltorio, con la macro `\figuraaiv` para figuras no flotantes |

Las figuras que acompañan a esta versión **no** están aquí: viven en `../figuras/a4/` con sus
nombres propios —`flujo_*`, `secuencia_*`, `guia_*`, `componente_*`— y las usa la consolidación.
Su PDF compilado se conserva en `../output/pdf/Karisma_Data_Actividad_4.pdf`.

## Por qué se conserva

`docs/us-planning/us-entrega-a4.md` consolida las dos mitades del trabajo en una sola entrega: la
construida en el stack del producto y la construida en Figma. Varias piezas de esta versión entran
a la entrega final —los cinco flujos como diseño de alta fidelidad, el inventario técnico del
archivo y el acceso al archivo de trabajo— y conviene poder citarlas contra su original en lugar
de contra un recuerdo.

## Nota de compilación

Los archivos se conservan **tal como estaban**, sin ajustar rutas. `main_a4.tex` de esta carpeta
referencia `estilo/uxdoc` y `contenido/a4_*`, que resuelven desde `docs/entregables/` y no desde
aquí, así que esta copia **no compila en su sitio**: es un registro, no un objetivo de construcción.
Para reconstruirla, su PDF ya compilado está en `../output/pdf/`.
