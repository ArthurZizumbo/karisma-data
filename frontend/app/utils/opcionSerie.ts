/**
 * The ECharts option of the dashboard, built as a pure function.
 *
 * Pure so that the two switches the acceptance criteria measure -`sampling`
 * and `large`- can be asserted without a DOM, and so that the component stays a
 * component: it receives an option and mounts a chart, and it decides nothing.
 *
 * Measured on 12-ago-2026 with ECharts 6.1.0, because R-02 of the plan required
 * a result and not an assumption: a one dimensional `Float32Array` handed to
 * `series.data` on a category axis makes ECharts throw
 * `RangeError: Invalid array length` inside `DataStore.prepareStore`. The store
 * asks for two dimensions -the ordinal x plus the value y- and
 * `countForTypedArray` divides the length by two, so the row count comes out
 * fractional. An interleaved two dimensional typed array does work, and it was
 * rejected: it doubles the payload and destroys the zero copy `subarray`, which
 * is the entire argument for the binary frame. The decided fallback is used
 * instead: `Array.from` over the view of each visible line, measured at 12.8 ms
 * for the whole 250 x 2 000 grid, well inside the 40 ms the plan budgeted. The
 * frame itself stays a `Float32Array`: statistics, the table and the summary all
 * read it without copying, and only the lines actually drawn are materialised.
 */
import type { CodigoIdioma } from '~/composables/useIdioma'
import type { DensidadTablero, MarcoSerie, VentanaTablero } from '~/types/tablero'
import type { EstiloSerie, ModoColor, SimboloSerie, TrazoSerie } from '~/utils/paletaSeries'
import { colorDeSerie, estiloDeSerie, MAXIMO_SERIES_COLOREADAS } from '~/utils/paletaSeries'
import {
  fechasDelMarco,
  formatearValor,
  formatearValorCompacto,
} from '~/utils/serieEstadisticas'
import { TOKENS } from '~/utils/tokens.generated'

/**
 * Reserved height of the chart.
 *
 * A single constant because the skeleton uses this very value: two heights is
 * how a layout shift appears the moment the data lands, and A4 measures that.
 */
export const ALTO_GRAFICA = '420px'

/** Same height as a number, for the chart container and for the tests. */
export const ALTO_GRAFICA_PX = 420

/** Point count above which ECharts is told the series is a large one. */
const UMBRAL_GRANDE = 1000

/** One line of the dashboard chart, with the two performance switches. */
export type SerieGrafica = {
  id: string
  name: string
  type: 'line'
  data: readonly number[]
  /**
   * Largest triangle three buckets. It is a painting defence and not a
   * transport one: the reduction that matters already happened in Polars.
   */
  sampling: 'lttb'
  /**
   * `large` is not declared by the line series type of ECharts 6, and it is
   * emitted anyway because `frontend/AGENTS.md` and CA-3 require it on every
   * series this builder produces. It is inert for a line today and free, and
   * the switch that does carry the weight here is `sampling` together with
   * `showSymbol: false` and `progressive`.
   */
  large: true
  largeThreshold: number
  progressive: number
  showSymbol: boolean
  symbol: SimboloSerie | 'none'
  symbolSize: number
  lineStyle: { color: string, width: number, type: TrazoSerie, opacity: number }
  itemStyle: { color: string }
  emphasis: { focus: 'series', lineStyle: { width: number, opacity: number } }
  z: number
}

/** The option handed to `setOption`. A type alias, so it stays assignable. */
export type OpcionTablero = {
  animation: boolean
  grid: Record<string, unknown>
  xAxis: Record<string, unknown>
  yAxis: Record<string, unknown>
  tooltip: Record<string, unknown>
  dataZoom: readonly Record<string, unknown>[]
  series: readonly SerieGrafica[]
}

/** What the builder needs beyond the frame itself. */
export interface OpcionesGrafica {
  densidad: DensidadTablero
  idioma: CodigoIdioma
  /**
   * Colour mode on screen. The palette declares a value per mode, and painting
   * the light blues over the near black ground is a contrast defect the design
   * system already measured.
   */
  modo: ModoColor
  ventana: VentanaTablero
  seriesVisibles: readonly number[]
}

/**
 * Hex of a design token in the mode on screen.
 *
 * @param nombre - Token name as the generator emits it.
 * @param modo - Colour mode.
 * @returns The hex, and it throws on an unknown name rather than returning a
 *   silent fallback that would paint an invisible axis.
 */
function colorDeToken(nombre: string, modo: ModoColor): string {
  const token = TOKENS.find(candidato => candidato.nombre === nombre)
  if (token === undefined) {
    throw new Error(`token de color desconocido: ${nombre}`)
  }
  return modo === 'oscuro' ? token.oscuro : token.claro
}

/**
 * Identifier of a line inside the current view.
 *
 * The key of the series when the frame carries one, and the position within the
 * frame when the line is an aggregate of several -where there is no key to
 * carry. Both the legend and the store speak this identifier, and the store
 * clears its selection whenever the grouping or the density changes, which is
 * what keeps the two namespaces from ever being compared against each other.
 *
 * @param marco - Decoded frame.
 * @param indice - Position of the line within the frame.
 * @returns The identifier the reader's selection is expressed in.
 */
export function identificadorDeLinea(marco: MarcoSerie, indice: number): number {
  return marco.catalogo[indice]?.serieId ?? indice
}

/**
 * Lines that get a colour, in the order the frame declares them.
 *
 * With a selection, it is the selection, capped at the six categorical tokens.
 * Without one, the reading densities colour the first six lines and the full
 * view colours none: 250 hues cannot be mapped back to any legend, so the cloud
 * stays grey and reads as aggregate behaviour, which is what it is.
 *
 * @param marco - Decoded frame.
 * @param opciones - Density and current selection.
 * @returns Frame positions of the coloured lines, in palette order.
 */
export function indicesColoreados(
  marco: MarcoSerie,
  opciones: Pick<OpcionesGrafica, 'densidad' | 'seriesVisibles'>,
): readonly number[] {
  const total = marco.conteo.series

  if (opciones.seriesVisibles.length > 0) {
    const elegidas: number[] = []
    for (let indice = 0; indice < total; indice += 1) {
      if (
        opciones.seriesVisibles.includes(identificadorDeLinea(marco, indice))
        && elegidas.length < MAXIMO_SERIES_COLOREADAS
      ) {
        elegidas.push(indice)
      }
    }
    return elegidas
  }

  if (opciones.densidad === 'completa') {
    return []
  }
  return Array.from({ length: Math.min(total, MAXIMO_SERIES_COLOREADAS) }, (_, i) => i)
}

/** Label of one line in the language on screen. */
function etiquetaDe(marco: MarcoSerie, indice: number, idioma: CodigoIdioma): string {
  const entrada = marco.catalogo[indice]
  if (entrada === undefined) {
    return ''
  }
  return idioma === 'en' ? entrada.labelEn : entrada.labelEs
}

/** Values of one line, materialised for ECharts. */
function valoresDeLinea(marco: MarcoSerie, indice: number): number[] {
  const anchura = marco.conteo.fechas
  return Array.from(marco.valores.subarray(indice * anchura, (indice + 1) * anchura))
}

/**
 * Builds the option for a decoded frame.
 *
 * @param marco - Decoded frame, whose typed arrays are read and never copied
 *   except for the lines that are actually drawn.
 * @param opciones - Density, language, mode, window and reader selection.
 * @returns The option, ready for `setOption`.
 */
export function construirOpcionSerie(
  marco: MarcoSerie,
  opciones: OpcionesGrafica,
): OpcionTablero {
  const fechas = fechasDelMarco(marco)
  const coloreadas = indicesColoreados(marco, opciones)
  const apagado = colorDeToken('corriente-apagado', opciones.modo)
  const tenue = colorDeToken('corriente-tenue', opciones.modo)
  const reticula = colorDeToken('grid', opciones.modo)
  const anchura = marco.conteo.fechas

  const series: SerieGrafica[] = []
  for (let indice = 0; indice < marco.conteo.series; indice += 1) {
    const posicion = coloreadas.indexOf(indice)
    const estilo: EstiloSerie | null = posicion === -1 ? null : estiloDeSerie(posicion)
    const color = estilo === null ? apagado : colorDeSerie(estilo, opciones.modo)

    series.push({
      id: `serie-${indice}`,
      name: etiquetaDe(marco, indice, opciones.idioma),
      type: 'line',
      data: valoresDeLinea(marco, indice),
      sampling: 'lttb',
      large: true,
      largeThreshold: UMBRAL_GRANDE,
      // Paint in chunks so a 250 line load never blocks the main thread for a
      // whole frame budget at once.
      progressive: 2000,
      // Two thousand markers per line is what turns a pan into a slide show.
      // The shape channel lives in the legend and in the tooltip marker, and the
      // in chart redundant channel is the stroke pattern.
      showSymbol: false,
      symbol: estilo === null ? 'none' : estilo.simbolo,
      symbolSize: 7,
      lineStyle: {
        color,
        width: estilo === null ? 1 : 2,
        type: estilo === null ? 'solid' : estilo.trazo,
        opacity: estilo === null ? 0.35 : 1,
      },
      itemStyle: { color },
      emphasis: { focus: 'series', lineStyle: { width: 3, opacity: 1 } },
      // Selected lines are drawn over the muted cloud, never under it.
      z: estilo === null ? 2 : 5,
    })
  }

  return {
    // Half a million points and an entry animation are incompatible: the first
    // pan would compete with a transition nobody asked for.
    animation: false,
    grid: {
      left: 72,
      right: 24,
      top: 16,
      bottom: 72,
      // ECharts 6 deprecates `containLabel` in favour of the outer bounds. The
      // replacement is TWO keys and not one: `outerBounds` is a rect object
      // -{left, right, top, bottom, width, height}- and the string goes in
      // `outerBoundsMode`. Writing `outerBounds: 'same'` throws
      // "Cannot create property 'width' on string 'same'" inside
      // mergeLayoutParam, setOption aborts, and the chart never paints: the
      // host div stays empty with no canvas. Nothing in the suite saw it
      // because no test mounts ECharts against a real DOM, and typecheck let it
      // pass because the option is typed as Record<string, unknown>.
      // The docs state the equivalence: containLabel: true is exactly
      // {outerBoundsMode: 'same', outerBoundsContain: 'axisLabel'}.
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: fechas,
      boundaryGap: false,
      axisLine: { lineStyle: { color: apagado } },
      axisTick: { show: false },
      axisLabel: { color: tenue, hideOverlap: true, fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      scale: marco.metrica !== 'n_posiciones',
      axisLine: { show: false },
      axisLabel: {
        color: tenue,
        fontSize: 11,
        // Short form on the axis and the full one in the tooltip, on purpose:
        // the axis is a scale to read against, the tooltip is the figure.
        formatter: (valor: number) =>
          formatearValorCompacto(valor, marco.metrica, opciones.idioma) ?? '',
      },
      splitLine: { lineStyle: { color: reticula } },
    },
    tooltip: {
      // With 250 lines an axis tooltip lists 250 rows, which is not a tooltip.
      trigger: marco.conteo.series > MAXIMO_SERIES_COLOREADAS ? 'item' : 'axis',
      axisPointer: { type: 'line', lineStyle: { color: apagado } },
      confine: true,
      order: 'valueDesc',
      valueFormatter: (valor: unknown) =>
        typeof valor === 'number'
          ? formatearValor(valor, marco.metrica, opciones.idioma) ?? ''
          : '',
    },
    dataZoom: [
      { type: 'inside', start: opciones.ventana.inicio, end: opciones.ventana.fin },
      {
        type: 'slider',
        start: opciones.ventana.inicio,
        end: opciones.ventana.fin,
        height: 24,
        bottom: 16,
        borderColor: reticula,
        fillerColor: `${apagado}33`,
        handleStyle: { color: tenue },
        // The slider draws a preview of the first series; with 2 000 points per
        // line that preview is another full render on every drag.
        showDataShadow: anchura <= 1000,
      },
    ],
    series,
  }
}
