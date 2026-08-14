# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Siete personas de trabajo confirmadas en A1, agrupadas en cuatro roles que el sistema
reconoce como *scopes*: `operativo`, `analista`, `directivo`, `admin`.

| Persona | Rol | Situación y trabajo |
|---|---|---|
| **Laura Méndez** | operativo | Recibe una cifra que no cuadra y tiene que decidir si es correcta antes de responder. Hoy eso le cuesta correos y esperas de días. Es la persona primaria. |
| **Diego Hernández** | analista | Necesita extracciones grandes que hoy le bloquean la jornada mientras corren. |
| **Arturo Castañeda** | directivo | Revisa el comportamiento completo de una serie larga, no una muestra recortada, y decide sobre riesgo. |
| **Roberto Valdez** | analista, propietario del dato | Tiene que responder por una cifra: de dónde viene y qué le pasó por el camino. |
| **Mariana Ovalle** | admin | Gobierna el acceso: da de alta, cambia de rol y desactiva. Necesita que sea demostrable. |
| **Jorge Mendieta** | directivo | Perfil de supervisión recogido en A1. |

**Cuando las dos necesidades chocan, gana el usuario trabajando, no el evaluador.**
Decisión del 11-ago-2026. La interfaz se optimiza para densidad de datos, escaneabilidad y
consistencia; el carácter vive en la precisión del detalle, no en el espectáculo.

## Product Purpose

Karisma Data reúne silos financieros dispersos —créditos, liquidez y derivados— en un único
punto donde una cifra se puede encontrar, entender y defender.

El éxito no es que la pantalla se vea bien: es que **Laura deje de mandar correos para validar un
número**, que Diego siga trabajando mientras su extracción corre, y que Roberto pueda responder
por un dato sin abrir otro sistema.

## Positioning

Tres cosas que un tablero de BI vecino no puede copiar sin rehacer su arquitectura:

1. **Ninguna cifra aparece sin su procedencia.** El asistente conversacional no responde números
   que no vengan de una llamada a herramienta visible, y cada una cita su fuente del catálogo.
   Sin tarjeta de herramienta, no hay número, aunque el modelo «sepa» la respuesta.
2. **El agente nunca ve datos que el usuario no puede ver.** El JWT del usuario se propaga a cada
   llamada de herramienta, así que los permisos del humano son los permisos del agente.
3. **El lenguaje del negocio, no el del sistema de origen.** El catálogo semántico deja buscar por
   cómo la gente llama a las cosas, no por `cli_ref` ni `ctpty_cd`.

## Operating Context

- Contexto académico: proyecto del curso TC4032 (MNA, ITESM), Equipo 8. Entregas dominicales
  A1–A5; A4 el 16-ago-2026 y A5, con prueba SUS, el 23-ago-2026.
- Los datos son **sintéticos con semilla fija**, con esquemas deliberadamente crípticos y
  heterogéneos entre silos porque ese es el problema que el producto resuelve. Las anomalías
  inyectadas están documentadas. Toda previsión se rotula como proyección simulada.
- **Honestidad de demostración**: lo que está guionizado se declara guionizado, en pantalla y en
  el documento. Nunca se finge aprendizaje automático.
- El prototipo lleva una franja permanente que declara que usa datos sintéticos y no está
  conectado a sistemas reales.

## Capabilities and Constraints

**Rutas confirmadas** (contrato anclado al mapa de navegación de A3; los slugs no cambian sin
romper un entregable ya calificado): `/`, `/acceso`, `/inicio`, `/exploracion`,
`/exploracion/tableros`, `/exploracion/exportar`, `/gobierno`, `/asistente`, `/administracion`,
más `/guia`, que es el sistema de diseño vivo y **no** es un prototipo.

**Capacidades**: descubrimiento por catálogo semántico · consultas gobernadas por capa semántica ·
tablero de 500 000 puntos preagregados · exportación en segundo plano con enlace firmado ·
asistente con streaming real y cancelación · administración de usuarios con borrado lógico.

**Restricciones que el trabajo futuro debe preservar**:

- **La interfaz es bilingüe español/inglés** con i18n real y estrategia sin prefijo de ruta: las
  URL no cambian, porque el contrato de rutas está anclado a A3. Los PDF del curso son solo en
  español. Ninguna cadena visible se escribe en un componente.
- **Todo endpoint de datos declara su *scope***. 401 sin sesión, 403 sin permiso. Los módulos sin
  permiso no se muestran; no basta con deshabilitarlos.
- **Accesibilidad verificada por cálculo, no a ojo.** La matriz de contraste WCAG se computa y las
  reglas se derivan de ella. Ya refutó cuatro reglas que se habían dado por buenas. Ninguna gráfica
  depende solo del color: llevan forma de marcador, patrón de línea, alternativa en tabla y resumen
  textual.
- **Los cuatro estados no felices** —vacío, cargando sin desplazamiento de maquetación, error y sin
  permiso— son parte de cada pantalla, no un extra.
- Presupuesto de nube por debajo de 45 USD al mes.

## Brand Commitments

- **Nombre**: Karisma Data. Fijado el 26-jul-2026. No se traduce ni se altera.
- **Tipografías**: Lexend Deca (display) y Fira Sans (texto), ya servidas desde el propio origen.
- **Iconografía**: familia única Lucide.
- **Fuente única, con la dirección invertida el 11-ago-2026**: el sistema de diseño del producto
  es el origen y el generador **exporta** hacia la hoja LaTeX de los entregables. Antes corría al
  revés y la aplicación heredaba una paleta pensada para un documento académico. La tesis se
  conserva —un solo origen, nada se teclea dos veces, el documento no puede contradecir a la
  aplicación— pero ahora el producto manda.
- **Restricción heredada que no se puede romper**: los 11 colores originales de `uxdoc.sty`
  conservan su valor byte a byte, porque A1, A2 y A3 ya están entregados y calificados. El sistema
  nuevo crece sobre ellos de forma aditiva; no los renombra ni los redefine.
- Sin emojis en producto, código ni documentos.

## Evidence on Hand

- Investigación de A1 con las siete personas y sus mapas de empatía; escenarios y *journey maps*
  de A2 con trazabilidad de cita a dolor; análisis competitivo, *card sorting* y arquitectura de
  información de A3, ya calificados.
- Prueba de árbol de A3 con dos tareas que A4 debe repetir sobre la arquitectura revisada: la del
  indicador de riesgo y la del acceso cruzado a la bitácora.
- Matriz de contraste calculada sobre 37 pares, con cuatro defectos encontrados y corregidos.
- Rúbrica de A4 publicada y absorbida. Rúbrica de A5 pendiente.

## Open Decisions

- La prueba SUS de A5 necesita cinco participantes o más, con meta de 75. **Sin confirmar** si son
  profesionales del sector o compañeros de curso; cambia cuánto pesa el vocabulario financiero real
  frente a la claridad general.
- No hay logotipo: hoy la marca es texto plano. **Sin decidir** si se produce una marca gráfica.
