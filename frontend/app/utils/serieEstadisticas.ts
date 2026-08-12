/**
 * Descriptive statistics of a decoded frame, and the one way its numbers are
 * written on screen.
 *
 * Pure and free of Vue on purpose: these are the figures the summary sentence,
 * the table and the tooltip all repeat, and three components computing them
 * separately is how a screen ends up stating two different maxima for the same
 * line.
 */
import type { EstadisticaSerie, MarcoSerie, MetricaTablero } from '~/types/tablero'
import type { CodigoIdioma } from '~/composables/useIdioma'

/** Locale used to format numbers, per interface language. */
const LOCALE_POR_IDIOMA: Record<CodigoIdioma, string> = { es: 'es-MX', en: 'en-US' }

/** Fraction digits each metric is worth showing. */
const DECIMALES_POR_METRICA: Record<MetricaTablero, number> = {
  saldo_disponible_mxn: 0,
  ratio_lcr: 3,
  n_posiciones: 0,
}

/**
 * Statistics of every line, each computed over that line alone.
 *
 * Never over the flat array: the maximum of 500 000 concatenated values belongs
 * to no line, and a summary that quoted it would be a number the reader cannot
 * find anywhere on the chart.
 *
 * Holes -NaN, which is how the frame carries "no data"- are skipped rather than
 * counted as zero. A line with nothing but holes comes back with NaN in every
 * field and -1 in both indices, which is what lets the caller say "no data"
 * instead of drawing a flat line at zero.
 *
 * @param marco - Decoded frame.
 * @returns One entry per line, in the order of the frame catalogue.
 */
export function estadisticasPorSerie(marco: MarcoSerie): readonly EstadisticaSerie[] {
  const anchura = marco.conteo.fechas
  const total = marco.conteo.series
  const estadisticas: EstadisticaSerie[] = []

  for (let indice = 0; indice < total; indice += 1) {
    const inicio = indice * anchura
    let minimo = Number.POSITIVE_INFINITY
    let maximo = Number.NEGATIVE_INFINITY
    let indiceMinimo = -1
    let indiceMaximo = -1
    let suma = 0
    let contados = 0
    let primero = Number.NaN
    let ultimo = Number.NaN

    for (let posicion = 0; posicion < anchura; posicion += 1) {
      const valor = marco.valores[inicio + posicion]
      if (valor === undefined || Number.isNaN(valor)) {
        continue
      }
      if (contados === 0) {
        primero = valor
      }
      ultimo = valor
      suma += valor
      contados += 1
      if (valor < minimo) {
        minimo = valor
        indiceMinimo = posicion
      }
      if (valor > maximo) {
        maximo = valor
        indiceMaximo = posicion
      }
    }

    estadisticas.push({
      indice,
      minimo: contados === 0 ? Number.NaN : minimo,
      maximo: contados === 0 ? Number.NaN : maximo,
      media: contados === 0 ? Number.NaN : suma / contados,
      primero,
      ultimo,
      indiceMinimo,
      indiceMaximo,
    })
  }

  return estadisticas
}

/**
 * Relative change between the first and the last value of a line.
 *
 * @param estadistica - Statistics of one line.
 * @returns The change as a fraction, or null when it cannot be stated: with a
 *   first value of zero the quotient is infinite, and "+Inf %" is worse than
 *   admitting there is no percentage to give.
 */
export function variacionRelativa(estadistica: EstadisticaSerie): number | null {
  const { primero, ultimo } = estadistica
  if (!Number.isFinite(primero) || !Number.isFinite(ultimo) || primero === 0) {
    return null
  }
  return (ultimo - primero) / Math.abs(primero)
}

/**
 * Writes one value of a metric the way every surface of the screen writes it.
 *
 * @param valor - Value as the frame carries it.
 * @param metrica - Metric being displayed, which decides the precision.
 * @param idioma - Interface language, which decides the separators.
 * @returns The formatted number, or null when the value is a hole. The caller
 *   renders the hole with a translated string: a dash typed here would be a
 *   visible literal living outside the catalogues.
 */
export function formatearValor(
  valor: number | null | undefined,
  metrica: MetricaTablero,
  idioma: CodigoIdioma,
): string | null {
  if (valor === null || valor === undefined || !Number.isFinite(valor)) {
    return null
  }
  const decimales = DECIMALES_POR_METRICA[metrica]
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor)
}

/**
 * Writes one value the short way, for the axis labels only.
 *
 * The balance metric reaches the order of 10^12, so the full form is fourteen
 * characters wide and the axis alone was eating a quarter of the plotting area,
 * with five stacked labels nobody can compare at a glance. Everywhere exactness
 * matters -tooltip, detail table, textual summary- keeps using
 * `formatearValor`: the short form is a reading aid on the scale, never the
 * figure a reader would quote.
 *
 * `Intl` picks the abbreviation of each locale on its own, which is the reason
 * not to hand roll this: Spanish shortens a thousand million differently from
 * English, and a table of suffixes typed here would be a second translation
 * catalogue living outside the locale files.
 *
 * @param valor - Value as the frame carries it.
 * @param metrica - Metric being displayed, which decides whether shortening
 *   applies at all.
 * @param idioma - Interface language, which decides separators and suffixes.
 * @returns The shortened number, or null when the value is a hole.
 */
export function formatearValorCompacto(
  valor: number | null | undefined,
  metrica: MetricaTablero,
  idioma: CodigoIdioma,
): string | null {
  if (valor === null || valor === undefined || !Number.isFinite(valor)) {
    return null
  }
  // Ratios live between 0 and 3 and counts stay in the hundreds: shortening
  // them would print "0" where the reader needs two decimals.
  if (Math.abs(valor) < 10_000) {
    return formatearValor(valor, metrica, idioma)
  }
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(valor)
}

/**
 * Writes a relative change as a signed percentage.
 *
 * @param variacion - Change as a fraction, as `variacionRelativa` returns it.
 * @param idioma - Interface language.
 * @returns The formatted percentage, or null when there is no change to state.
 */
export function formatearVariacionRelativa(
  variacion: number | null,
  idioma: CodigoIdioma,
): string | null {
  if (variacion === null || !Number.isFinite(variacion)) {
    return null
  }
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    style: 'percent',
    signDisplay: 'exceptZero',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(variacion)
}

/** Days since the Unix epoch as an ISO date, which is how the axis labels read. */
export function fechaDeDia(dia: number): string {
  return new Date(dia * 86400000).toISOString().slice(0, 10)
}

/**
 * ISO labels of every column of the grid.
 *
 * Built once per frame and shared by the axis, the tooltip and the table: three
 * conversions of the same 2 000 integers is 6 000 Date objects per render.
 *
 * @param marco - Decoded frame.
 * @returns One ISO date per column, in the order of the frame.
 */
export function fechasDelMarco(marco: MarcoSerie): readonly string[] {
  const fechas: string[] = Array.from({ length: marco.fechas.length })
  for (let indice = 0; indice < marco.fechas.length; indice += 1) {
    fechas[indice] = fechaDeDia(marco.fechas[indice] ?? 0)
  }
  return fechas
}
