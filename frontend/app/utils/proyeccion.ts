/**
 * US-026 - the only module of the screen with business arithmetic.
 *
 * It exists to close one concrete defect: somebody lowers the regression window
 * from twelve months to six, or swaps least squares for "last against previous",
 * and the card keeps claiming the old method. From that commit on the screen
 * lies, and none of the tests usually written would notice.
 *
 * Four locks, and all four are verifiable:
 *
 *   1. The visible label is not an input of any component. `TarjetaPredictiva`
 *      receives `proyeccion` and nothing else, so there is no place to hand it
 *      a sentence the computation did not produce.
 *   2. `proyectarLineal` emits the descriptor with the parameters it really
 *      used: `points` is the length of the slice it fitted, never the window it
 *      was asked for, and `r2` is the coefficient it computed.
 *   3. `etiquetaMetodo` is the only function in the application that knows
 *      `PLANTILLAS_METODO`, and it lives next to the computation. `grep -rn
 *      "forecast.method" app/components` returns nothing.
 *   4. `PLANTILLAS_METODO` is a total record over `IdMetodo`, so a new method
 *      without a template does not compile, and a spec walks its values to check
 *      that every template exists in both catalogues.
 */
import type { CodigoIdioma } from '~/composables/useIdioma'
import type { IdMetodo, MetodoAplicado, MetricaId, Proyeccion, PuntoMensual } from '~/types/prediccion'
import { formatearCoeficiente, formatearEntero } from '~/utils/formatoTablero'

/**
 * Months below which no projection is published.
 *
 * Six and not three. A straight line fitted to three points, wearing a label
 * that names a method, reads as a measurement; saying there is not enough
 * history is the honest answer and it is also the shorter one.
 */
export const MINIMO_PUNTOS = 6

/** Default regression window, in months. */
export const VENTANA_POR_DEFECTO = 12

/** Projection horizon, in months. One: the criterion asks for the next month. */
export const HORIZONTE_MESES = 1

/**
 * Visible label template of every registered method.
 *
 * Typed as a total record on purpose: this is the first of the four locks, and
 * it is enforced by the compiler rather than by a review.
 */
export const PLANTILLAS_METODO: Record<IdMetodo, string> = Object.freeze({
  'ols-lineal': 'forecast.method.olsLinear',
})

export interface OpcionesProyeccion {
  /** Months fed to the regression. Defaults to VENTANA_POR_DEFECTO. */
  readonly ventana?: number
}

/** Signature of the translator a component hands over. */
export type TraductorMensaje = (clave: string, parametros: Record<string, string>) => string

/** A month written as YYYY-MM. */
const PATRON_MES = /^(\d{4})-(\d{2})$/

/**
 * Next calendar month of a YYYY-MM string.
 *
 * Written with plain arithmetic and not with `Date`: December of any year is
 * where the naive version produces month thirteen, and a `Date` built from a
 * local instant would also drag the reader time zone into a value that has no
 * instant behind it.
 *
 * @param mes - Month as YYYY-MM.
 * @returns The following month, also as YYYY-MM.
 */
export function mesSiguiente(mes: string): string {
  const partes = PATRON_MES.exec(mes)
  if (partes === null) {
    return mes
  }
  const anio = Number(partes[1])
  const numeroMes = Number(partes[2])
  const siguiente = numeroMes === 12 ? 1 : numeroMes + 1
  const anioSiguiente = numeroMes === 12 ? anio + 1 : anio
  return `${String(anioSiguiente).padStart(4, '0')}-${String(siguiente).padStart(2, '0')}`
}

/**
 * Relative change of one value against another, in percentage points.
 *
 * Shared by the card and by the detail table so the two can never state a
 * different change for the same pair of months, which is how a screen ends up
 * contradicting itself one level down.
 *
 * @param anterior - Reference value the change is measured against.
 * @param actual - Value being compared.
 * @returns The change, or null when the reference is zero or not a number and
 *   a relative change is undefined.
 */
export function variacionPorcentual(anterior: number, actual: number): number | null {
  if (!Number.isFinite(anterior) || !Number.isFinite(actual) || anterior === 0) {
    return null
  }
  return ((actual - anterior) / Math.abs(anterior)) * 100
}

/** True when a point can take part in a regression. */
function puntoUtilizable(punto: PuntoMensual | undefined): punto is PuntoMensual {
  return (
    punto !== undefined
    && typeof punto.mes === 'string'
    && PATRON_MES.test(punto.mes)
    && typeof punto.valor === 'number'
    && Number.isFinite(punto.valor)
  )
}

/**
 * Ordinary least squares projection of a monthly series, one month ahead.
 *
 * The returned descriptor carries the parameters the regression really used, so
 * the visible label cannot claim something the computation did not do.
 *
 * @param metricaId - Metric the series belongs to.
 * @param historico - Monthly points, oldest first.
 * @param opciones - Regression window.
 * @returns The projection, or null when there are fewer than MINIMO_PUNTOS
 *   usable points, when the fitted line is degenerate, or when the last
 *   observed value is zero and a relative change would be undefined.
 */
export function proyectarLineal(
  metricaId: MetricaId,
  historico: readonly PuntoMensual[],
  opciones?: OpcionesProyeccion,
): Proyeccion | null {
  if (!Array.isArray(historico)) {
    return null
  }

  const ventana = Math.max(1, Math.trunc(opciones?.ventana ?? VENTANA_POR_DEFECTO))
  const utilizables = historico.filter(puntoUtilizable)
  const serieUsada = utilizables.slice(-ventana)
  const total = serieUsada.length

  if (total < MINIMO_PUNTOS) {
    return null
  }

  let sumaX = 0
  let sumaY = 0
  let sumaXY = 0
  let sumaXX = 0
  for (let indice = 0; indice < total; indice += 1) {
    const valor = serieUsada[indice]!.valor
    sumaX += indice
    sumaY += valor
    sumaXY += indice * valor
    sumaXX += indice * indice
  }

  const denominador = total * sumaXX - sumaX * sumaX
  if (denominador === 0) {
    return null
  }

  const pendiente = (total * sumaXY - sumaX * sumaY) / denominador
  const ordenada = (sumaY - pendiente * sumaX) / total

  const media = sumaY / total
  let sumaCuadradosTotal = 0
  let sumaCuadradosResiduo = 0
  for (let indice = 0; indice < total; indice += 1) {
    const valor = serieUsada[indice]!.valor
    const ajustado = ordenada + pendiente * indice
    sumaCuadradosTotal += (valor - media) ** 2
    sumaCuadradosResiduo += (valor - ajustado) ** 2
  }

  // A flat series has no variance to explain: R squared would be 0/0 and the
  // card would print "R2 NaN", which is worse than admitting there is no trend.
  if (sumaCuadradosTotal === 0) {
    return null
  }

  const r2 = 1 - sumaCuadradosResiduo / sumaCuadradosTotal
  const ultimo = serieUsada[total - 1]!
  const valorProyectado = ordenada + pendiente * (total - 1 + HORIZONTE_MESES)

  if (!Number.isFinite(r2) || !Number.isFinite(valorProyectado) || ultimo.valor === 0) {
    return null
  }

  const metodo: MetodoAplicado = {
    id: 'ols-lineal',
    clavePlantilla: PLANTILLAS_METODO['ols-lineal'],
    parametros: {
      // Measured, never requested: this is lock 2.
      points: total,
      horizon: HORIZONTE_MESES,
      r2,
    },
  }

  return {
    metricaId,
    ultimo,
    proyectado: { mes: mesSiguiente(ultimo.mes), valor: valorProyectado },
    variacionPct: variacionPorcentual(ultimo.valor, valorProyectado) ?? 0,
    serieUsada,
    metodo,
  }
}

/**
 * Renders the visible method label from the descriptor the computation emitted.
 *
 * The only place in the application that knows `PLANTILLAS_METODO`. Components
 * call this and never a translation key of their own, which is lock 3.
 *
 * @param metodo - Descriptor returned inside a Proyeccion.
 * @param idioma - Interface language.
 * @param t - Translator, injected so this stays a pure function.
 * @returns The label, already interpolated with the measured parameters.
 */
export function etiquetaMetodo(
  metodo: MetodoAplicado,
  idioma: CodigoIdioma,
  t: TraductorMensaje,
): string {
  return t(metodo.clavePlantilla, {
    points: formatearEntero(metodo.parametros.points, idioma),
    horizon: formatearEntero(metodo.parametros.horizon, idioma),
    r2: formatearCoeficiente(metodo.parametros.r2, idioma),
  })
}
