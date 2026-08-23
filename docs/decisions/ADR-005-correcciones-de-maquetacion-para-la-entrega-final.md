# ADR-005: Correcciones de maquetación sobre fuentes ya calificadas, para la entrega final

**Estado**: Aceptado · **Fecha**: 22-ago-2026 · **US**: US-AVANCE-5 · **Actividad**: A5

## Contexto y Problema

`docs/AGENTS.md` congela las fuentes de las actividades entregadas. Su sección
**Convenciones** lo dice sin matices:

> ❌ Tocar los entregables ya calificados: `contenido/a1_*.tex`, `a2_*.tex`, `a3_*.tex` y los
> PDF de `semana_1..3`. Ya se entregaron y se calificaron; ese PDF es el registro de lo evaluado.

La regla es correcta y la razón por la que existe no ha cambiado: el PDF subido a Canvas es el
único registro de lo que el evaluador tuvo delante, y reescribir su fuente después de la
calificación destruye esa correspondencia.

La Actividad 5 introduce un hecho nuevo que la regla no previó. El aviso del profesor pide
revisar la retroalimentación de A1 a A4 «para hacer las mejoras necesarias **previo a la
integración de su documento final**», y el vehículo de entrega de A5 es el documento acumulado
`main_completo.tex`, que **recompone esos mismos `.tex`** en un volumen nuevo. Una de las
observaciones recibidas es de maquetación y solo puede cerrarse en la fuente:

> A3: «hubiera sido muy bueno que cada competidor quedara todo dentro de una página».

Hoy los siete `\subsubsection` de `contenido/a3_01_analisis_competitivo.tex` fluyen sin salto de
página. Sin tocar ese archivo, el documento integrado repite en A5 el defecto que el evaluador ya
señaló en A3, y lo repite en el entregable que vale 15 puntos.

Quedan entonces dos lecturas de la regla en conflicto: «no se toca lo calificado» y «se aplica la
retroalimentación antes de integrar». Este ADR resuelve cuál gana y con qué límite.

## Decisión

Los PDF de `semana_1`, `semana_2` y `semana_3` **permanecen intactos** como registro de lo
evaluado. No se recompilan, no se sustituyen y no se renombran.

Sus fuentes `.tex` admiten **únicamente correcciones de maquetación derivadas de
retroalimentación explícita del evaluador**, aplicadas para la integración de A5. El contenido
evaluado no se reescribe.

Qué cuenta como corrección de maquetación, exhaustivamente:

- Saltos de página (`\clearpage`, `\needspace`) y reserva de espacio.
- Ajuste de espaciado vertical propio de un bloque.
- Recorte de viñetas redundantes **solo** cuando un bloque rebasa su página por poco y no hay
  otra forma de que quepa.

Qué **no** cuenta, y por tanto sigue prohibido:

- Reescribir, ampliar o mejorar un párrafo, una tabla o una conclusión.
- Añadir o quitar datos, fechas, cifras o fuentes.
- Corregir errores de contenido que el evaluador no señaló.
- Insertar etiquetas (`\label`) u otros ganchos técnicos para el documento nuevo: el mapa de
  cumplimiento de A5 resuelve esas filas leyendo `main_completo.toc`, precisamente para no
  tener que abrir los archivos congelados.

Cada corrección queda anotada en el handoff de la US con el texto de la retroalimentación que la
justifica. Sin retroalimentación citada, no hay excepción.

## Alcance ejecutado en A5

| Retroalimentación | Archivo | Acción | Estado |
|---|---|---|---|
| A3: un competidor por página | `contenido/a3_01_analisis_competitivo.tex` | `\clearpage` antes de cada competidor y ajuste fino de espaciado | Aplicada bajo este ADR |
| A1/A2: mapas de empatía partidos en dos páginas | `estilo/uxdoc.sty` (`\mapaempatia`) | Ya corregida el 29-jul-2026 | Solo verificación en el PDF |
| A3: tablas con fechas de obtención (elogiada) | `contenido/a3_01_*` | Ninguna; se verifica que sobreviva a los saltos | Verificación |
| A4: punto 9.5 sin iconos | `estilo/a4_iconos.tex` | Ya corregida el 19-ago-2026 | Solo verificación |
| A4: seguimiento de versiones innecesario | `contenido/a4_03_guia_estilos.tex` | Ya corregida | Verificación |
| General: cuidado con los saltos de página | acumulado completo | Pase de maquetación sobre el PDF integrado | Verificación |

Solo la primera fila consume la excepción. Las demás ya estaban resueltas o son comprobaciones
sobre el PDF compilado.

## Consecuencias

**A favor.** La retroalimentación del evaluador se cierra donde se puede cerrar, y el documento
integrado no arrastra a un entregable de 15 puntos un defecto ya señalado. El límite queda
escrito, así que la excepción no se puede estirar por analogía en la siguiente US.

**En contra.** A partir de esta fecha, la fuente de A3 y el PDF de `semana_3` dejan de ser
byte-idénticos en su maquetación. Quien compare ambos verá los mismos párrafos repartidos en
distinto número de páginas. Es el costo aceptado: la correspondencia que importa es la del
contenido evaluado, y esa se conserva intacta.

**Riesgo residual.** «Corrección de maquetación» es una categoría con borde difuso, y la
tentación de mejorar una frase mientras se ajusta una página es real. La mitigación es el
registro por escrito: cada cambio se anota con la retroalimentación que lo justifica, y un cambio
sin retroalimentación citada es una violación de este ADR, no una interpretación de él.

## Regla que queda en la guía

`docs/AGENTS.md` y `docs/CLAUDE.md` (espejos byte-idénticos) recogen la versión corta:

> ❌ Tocar los entregables ya calificados: `contenido/a1_*.tex`, `a2_*.tex`, `a3_*.tex` y los PDF
> de `semana_1..3`. **Única excepción, ADR-005**: correcciones de maquetación derivadas de
> retroalimentación explícita del evaluador y aplicadas para la integración de A5. El contenido
> evaluado no se reescribe y los PDF entregados no se regeneran.
