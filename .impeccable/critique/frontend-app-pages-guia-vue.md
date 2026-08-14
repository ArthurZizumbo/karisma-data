# Critique — /guia (frontend/app/pages/guia.vue)

**Fecha**: 11-ago-2026 · **Modo**: Operate · **Provenance**: dos subagentes aislados en paralelo
(Assessment A revisión de diseño, Assessment B detector y navegador). Sin degradación.

**Media de heurísticas de Nielsen: 2.0 / 4** (una marcada n/a: prevención de errores, la única
acción mutante es un copiado no destructivo).

## Veredicto de especificidad

El contenido es de este producto; la composición no. Quitando el texto quedan ocho rectángulos
idénticos de 1137 px, radio 10 px y filete de 1 px, que un CRM o un panel de RRHH podrían usar sin
tocar nada. La especificidad vive al 100 % en el contenido y al 0 % en la forma.

## Los cinco números que explican «se ve plano»

| Medición | Valor | Consecuencia |
|---|---|---|
| Nodos de texto en peso 400 | **750 / 750**, encabezados incluidos | La jerarquía tiene un solo canal: el tamaño |
| Paso entre título y cuerpo | **1.71**; entre h1 y h2, **1.2** | Ningún salto se lee como salto |
| Color en banda de matiz 190-260 grados | **953 / 1016 = 93.8 %** | Monocromo azul. **Cero neutros puros**: los «neutros» son slate teñido |
| Contraste tarjeta contra su suelo | **1.00:1** | El contenedor no existe visualmente; todo lo carga un filete a 1.42:1 |
| Relleno de tarjeta sobre su ancho | 12 px sobre 1137 px = **1.05 %** | Firma visual de maqueta sin terminar |

Corolario: `main.css:86-113` fija peso 400 en los nueve roles, con el comentario «El peso no
construye jerarquía». La causa está declarada en el generador, no es un descuido de plantilla.

## Defectos con consecuencia, por prioridad

**P1 · A 390 px la maqueta no existe.** La barra lateral no colapsa: `BarraLateral.vue:37` usa
`w-[var(--sidebar-width)]` sin un solo modificador responsivo. Medido: barra 240 px de 375
(**64 %**), contenido **135 px**, `scrollWidth` 487 contra 375, **480 elementos desbordan**, y el
documento pasa de 8 176 a **37 185 px**. `main.css:130` promete que a 768 px colapsa: nunca se
implementó.

**P2 · Jerarquía de un solo canal.** Ver tabla. Además `guia.vue:73` invierte el nivel: el h2 del
índice mide 16 px sobre láminas cuyos h2 miden 20.

**P3 · Los contenedores no tienen límite perceptible.** 212 elementos con filete; las ocho láminas
usan `line` (1.42:1) donde la regla propia exige `line-strong` (3:1). De tres niveles de elevación
la página usa uno.

**P4 · La guía incumple las reglas que publica.** **113 nodos** de `muted` por debajo de 14 px
cuando `main.css:52` lo prohíbe; `muted` sobre `surface-alt` dos veces, prohibido en DESIGN.md. Un
evaluador que aplique la sección 8 de la página a la página misma la reprueba con sus propios
números.

**P5 · El sistema y las pantallas que gobierna ya divergen.** Las nueve pantallas titulan con
`text-2xl` de Tailwind, no con el rol; su cuerpo hereda 16 px donde el sistema documenta 14. Las
dos únicas apariciones de `font-medium` del producto están en `BarraLateral.vue:59,105`, fuera del
sistema. Y `guide.source` sigue declarando la dirección de derivación que se invirtió el 11-ago.

## Defectos mecánicos

- **Error de hidratación**: `LaminaPaleta.vue:92`, `v-if="!isSupported"` de `useClipboard` vale
  `false` en servidor y `true` en cliente sin aislarse en `ClientOnly`. SSR emite 1534 nodos, el
  cliente 1533.
- **15 de 83 elementos focalizables** caen al anillo por omisión del navegador, entre ellos los 12
  botones congelados de la lámina de Botones. La corrección de anillo único cubrió los controles
  reales y no los especímenes.
- **12 objetivos táctiles** por debajo de 44 px.
- **59 % de los párrafos** superan 75 caracteres por línea; el peor, 179.
- Detector estático: **cero hallazgos** sobre el objetivo, verificado contra falso positivo.

## Fortalezas reales

1. La lámina de tarjetas de llamada a herramienta hace **inspeccionable** la regla antialucinación
   en vez de enunciarla. Es el único sitio donde la forma hace un trabajo que solo este producto
   necesita.
2. La lámina de accesibilidad publica la **refutación**, no solo la regla: qué par falló, con qué
   número y qué lo sustituyó. Por encima de lo que hacen la mayoría de los sistemas comerciales.
3. Los huesos son honestos: todo hexadecimal viene del generador, el orden de tabla es real y
   actualiza `aria-sort`, la denegación del portapapeles se atiende.

## Bandera roja que no es de estilo

**No hay lámina de linaje.** «Ver linaje» existe como rótulo de botón y detrás no hay nada
especificado: ni superposición, ni formato de cita de la fuente, ni cómo se muestra cuál de dos
valores en conflicto es el canónico. Roberto Valdez, cuyo trabajo es responder por una cifra,
recibe un sistema que documenta cinco chips de estado y cero maneras de defender un número.

## Decisiones abiertas que bloquean el rediseño

1. Si los nueve roles están todos en peso 400, ¿por qué son nueve? O el sistema admite un segundo
   canal de jerarquía, o la escala real tiene cuatro roles y cinco son inventario muerto.
2. La regla «`muted` solo a partir de 14 px» se incumple 113 veces en la propia página. ¿Está mal
   la regla o la implementación? Si se relaja, hay que reimprimir una sección ya entregada.
3. ¿Para quién es `/guia`? Hoy la prosa de justificación va primero y el espécimen cuarto, a 718 px
   del inicio. Es la única superficie donde el usuario es a la vez el evaluador y el equipo.
