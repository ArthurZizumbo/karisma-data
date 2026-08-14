# Espacios de trabajo por rol — Karisma Data

> Artefacto normativo de **US-027** (E4, sprint S4). Es la fuente que el documento de A4 cita cuando
> describe la Pantalla 1 del prototipo. La tabla de abajo es la misma que consume el código:
> `frontend/app/utils/espaciosTrabajo.ts` la implementa y `frontend/test/espaciosTrabajo.spec.ts` la
> fija, de modo que este documento y la pantalla no pueden divergir sin que la suite se ponga roja.

## 1. Por qué hay tres composiciones y no una

El portal atiende ocho perfiles con cuatro roles. La tentación de diseño es publicar una única
pantalla de inicio «bien resuelta» y dejar que cada persona se acostumbre. El fundamento empírico
dice que esa apuesta no se puede ganar.

Y.-H. Peng, S. Das, J. P. Bigham y J. Wu (Carnegie Mellon University), *Efficient Personalization of
Generative User Interfaces*, arXiv:**2604.09876**, abril de 2026 — paper 09 del corpus, archivo
[`papers/09_efficient-personalization-generative-ui_arxiv-2604.09876.pdf`](papers/09_efficient-personalization-generative-ui_arxiv-2604.09876.pdf).

Sobre **20 diseñadores** que emitieron juicios pareados sobre **600 interfaces generadas**, el
acuerdo entre evaluadores fue de **kappa 0.25**: desacuerdo sustancial. Los diseñadores apelan a los
mismos conceptos —jerarquía, limpieza, densidad— y difieren en cómo los definen y en qué orden los
priorizan.

La consecuencia de diseño que esta US ejecuta es directa: **si ni los expertos comparten una
definición única de «buen layout», un portal con ocho perfiles no puede imponer una vista única.**
Se parte de *defaults* por rol —tres composiciones sensatas, no una— y el control fino del usuario
(reordenar y ocultar bloques con arrastre) queda **declarado como trabajo posterior y congelado**,
no simulado. La honestidad de esa frontera importa: una pantalla que insinúa personalización que no
existe enseña al lector a buscar un control que nunca va a encontrar.

## 2. La tabla perfil → espacio → pantalla principal

Los nombres de perfil son literales de `docs/entregables/contenido/a1_cuerpo.tex` §1.1; las personas
son las de la §5 del mismo archivo; los roles son los cuatro *scopes* del token, con la grafía del
backend (`admin`, nunca `administrador`); los usuarios sembrados son los de la migración
`create_app_user`. Ni un nombre inventado.

| # | Perfil de A1 (§1.1) | Persona de A1 | Espacio | Rol (claim `scope`) | Usuario sembrado | Pantalla principal | Composición |
|---|---|---|---|---|---|---|---|
| 1 | Operativo, consulta rápida | Laura Méndez *(persona primaria)* | `operativo` | `operativo` | `lmendez` | `/inicio` | operativa |
| 2 | Analista de datos, profundidad | Diego Hernández | `analista` | `analista` | `dhernandez` | `/inicio` | analista |
| 3 | Propietario de datos, gobierno y calidad | Roberto Valdez | `directivo` | `directivo` | `rvaldez` | `/inicio` | directiva |
| 4 | Riesgos, cumplimiento y auditoría | Elena Ruiz | `operativo` | `operativo` | `eruiz` | `/inicio` | operativa |
| 5 | Ingeniería y administración de datos | Jorge Mendieta | `analista` | `analista` | `jmendieta` | `/inicio` | analista |
| 6 | Directivo, abstracción | Arturo Castañeda | `directivo` | `directivo` | `acastaneda` | `/inicio` | directiva |
| 7 | Administración de la plataforma | Mariana Ovalle | `admin` | `admin` | `movalle` | **`/administracion`** | — *(recae en la operativa si abre `/inicio`)* |
| 8 | Integración de aplicaciones, consumo programático | Ximena Solís | `analista` | — | **ninguno en S4** | `/inicio` | analista |

**Ocho perfiles, cuatro espacios, dos pantallas principales.** Las tres asignaciones que no se
pueden dejar implícitas:

- **Roberto Valdez es `directivo`, no `analista`.** Gobierno y calidad lee indicadores consolidados y
  responde por cifras ante terceros; es la asignación que US-015 fijó al sembrar los usuarios, y
  esta US no la reabre para no crear dos verdades sobre el mismo usuario.
- **Elena Ruiz es `operativo`.** Control y auditoría valida cifras puntuales: su modo dominante es
  localizar y comprobar, que es exactamente el buscador dominante de la composición operativa.
- **Ximena Solís no tiene usuario de acceso en S4.** Consume el portal por API y US-015 la excluyó
  del *seed* con ese argumento. La cobertura que exige el criterio es de **correspondencia** —su
  perfil tiene espacio y pantalla principal asignados—, no de demostrabilidad con acceso. Inventarle
  un octavo usuario rompería el contrato de identidad, que dice que cualquier documento que nombre
  un usuario distinto está citando algo que no existe.

## 3. Las tres composiciones, bloque por bloque

El orden **es** el criterio de aceptación: lo que se prueba es la secuencia de `[data-bloque]` en el
DOM, que coincide con el orden de foco del teclado. La fuente es `ESPACIOS` en
`frontend/app/utils/espaciosTrabajo.ts`.

| Orden | Operativo | Analista | Directivo |
|---|---|---|---|
| 1 | `buscador` — dominante, ancho completo | `explorador` — 3 consultas guardadas | `indicadores` — 3 tarjetas en rejilla |
| 2 | `recientes` — 5 búsquedas | `exportaciones` — 4 trabajos con su estado | `buscador` — reducido, una línea |
| 3 | `favoritos` — 4 fuentes | `buscador` — normal | `alertas` — 3 señales |
| 4 | `alertas` — 3 señales | `favoritos` — 4 fuentes | `favoritos` — 4 fuentes |
| 5 | `perfil` — rol y último acceso | `alertas` — 3 señales | — |

**Por qué cada una abre por donde abre:**

- **Operativa.** La persona primaria localiza una cifra y la comprueba. Cualquier cosa por encima del
  buscador le cuesta un desplazamiento en la única acción que siempre ejecuta. El bloque `perfil` es
  exclusivo de esta composición: es la rama 1.5 del mapa de A3 y es la única persona que lo nombró
  como parte de su inicio en el *card sorting*.
- **Analista.** Retoma trabajo. Un analista que tiene que volver a buscar la consulta que construyó
  ayer paga dos veces por el mismo trabajo, así que las consultas guardadas y las exportaciones van
  antes que el buscador.
- **Directiva.** Pide un estado, no un conjunto de datos. Tres cifras del último corte abren la
  pantalla y el buscador se reduce a una línea —sigue estando, porque es el mismo portal.

En las composiciones analista y directiva el nombre y el rol viajan en el saludo de encabezado; en
la operativa, además, en el bloque `perfil`.

## 4. Las tarjetas de indicador son del presente

| | `/inicio`, composición directiva (US-027) | Tablero (US-026) |
|---|---|---|
| Qué muestra | Valor **actual**, variación contra el mes anterior, fecha de corte | **Proyección** al mes siguiente |
| Etiqueta obligatoria | «Datos de ejemplo» | Etiqueta de método: «proyección simulada» |
| Componente | `components/inicio/TarjetaIndicador.vue` | Propio, bajo `components/tablero/` |

**No se comparte componente**, y no por descuido: la tarjeta predictiva necesita etiqueta de método,
panel expandible y tabla de detalle, y una tarjeta con tres propiedades opcionales que sólo un
consumidor usa es peor que dos componentes de veinticinco líneas. Mezclarlas dejaría que una
proyección se leyera como una observación, que es la confusión que este portal existe para quitar.

La variación **no se colorea por signo**. Una subida de la cobertura de liquidez es buena noticia y
una subida de la cartera vencida es mala: pintar las dos de verde sería la tarjeta afirmando un
juicio que no puede hacer. El signo y la frase llevan el significado.

## 5. Honestidad de la demostración

Ninguna cifra ni ninguna lista de esta pantalla sale de un sistema real, y la pantalla lo dice tres
veces con distinto grano:

1. La **franja de alcance** del layout del portal, presente en las nueve rutas.
2. Una **insignia «Datos de ejemplo»** en cada bloque con muestras, más el atributo
   `data-origen="ejemplo"` que las pruebas y el guion de captura consumen.
3. Un **pie de composición** que explica que las listas son sintéticas y que no sostienen decisiones.

El vocabulario sí es real: los nombres físicos (`ratio_lcr`, `sdo_cap`, `dias_mora`, `nocional_usd`,
`mto_disp`) y los códigos de fuente (`liquidez`, `creditos`, `derivados`, `regulatorio`) son los del
catálogo sembrado en `db/seeds/catalog.sql`. Es una dependencia de **contenido**, no de código: si el
catálogo no estuviera sembrado, la pantalla de inicio se vería idéntica.

## 6. Lo que esta entrega no hace, dicho de frente

| Fuera de alcance | Estado |
|---|---|
| Reordenar u ocultar bloques con arrastre | STRETCH congelado. Cero ocurrencias de API de arrastre en la aplicación |
| Persistir preferencias del usuario | Sin tabla, sin *endpoint* y sin `localStorage`. Cuando dejen de ser muestras, la migración se llamará `create_user_preference` con clave foránea a `app_user` |
| Consultar datos por red desde `/inicio` | La pantalla no hace ni una petición. Por eso no tiene estado de error de red: fabricar uno sería probar algo que el código no puede alcanzar |
| Acceso con usuario para el octavo perfil | Ximena Solís queda documentada y declarada como no demostrable con acceso en S4 |

## 7. Cómo se verifica en un solo comando

```bash
bash scripts/capturar_espacios.sh
```

Acuña una sesión de demostración por cada uno de los cuatro perfiles, pide su pantalla principal y
comprueba en el **HTML servido** que la composición es la esperada —incluido el quinto caso, el
administrador que abre `/inicio` a mano y recae en la operativa. Que la marca esté en el HTML del
servidor y no sólo tras hidratar es lo que garantiza que las capturas del informe no salgan vacías.
