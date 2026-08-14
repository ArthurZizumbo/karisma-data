/**
 * US-026 - the three predictive cards, as a contract of the interface.
 *
 * The grid renders one card per entry of `METRICAS_PREDICCION` and never one per element
 * of the response. Two consequences the screen depends on: the number of cards
 * cannot change when the request settles, so the grid cannot reflow; and a
 * metric missing from the payload shows its designed empty state instead of
 * disappearing, which would be a layout shift with another name.
 *
 * This module knows no data and no transport. It imports types and nothing
 * else, so nobody can build an import cycle through it.
 */
import type { MetricaTablero } from '~/types/prediccion'

/** Explorer route a level 3 link sends the reader to. */
export const RUTA_EXPLORADOR = '/exploracion'

/**
 * The three cards, in render order.
 *
 * `campoOrigen` is the physical column of the preaggregated series, not a
 * label: it travels as data, it seeds the explorer query and it is what the
 * provenance line of level 2 shows. Translating a column name would invent a
 * field that exists in no silo.
 */
export const METRICAS_PREDICCION: readonly MetricaTablero[] = Object.freeze([
  {
    id: 'cobertura-liquidez',
    claveEtiqueta: 'forecast.metric.liquidityCoverage',
    unidad: 'porcentaje',
    campoOrigen: 'ratio_lcr',
  },
  {
    id: 'saldo-disponible',
    claveEtiqueta: 'forecast.metric.availableBalance',
    unidad: 'millones-mxn',
    campoOrigen: 'saldo_disponible_mxn',
  },
  {
    id: 'concentracion-divisa',
    claveEtiqueta: 'forecast.metric.currencyConcentration',
    unidad: 'porcentaje',
    campoOrigen: 'saldo_disponible_mxn',
  },
] as const satisfies readonly MetricaTablero[])

/**
 * Explorer address for a metric, carrying its physical column as the query.
 *
 * @param metrica - Metric whose source column seeds the search.
 * @returns Contract route with the query string appended.
 */
export function destinoExplorador(metrica: MetricaTablero): string {
  return `${RUTA_EXPLORADOR}?q=${encodeURIComponent(metrica.campoOrigen)}`
}

/**
 * Metric of the grid with a given id.
 *
 * @param id - Identifier as it travels in the published history.
 * @returns The metric, or undefined when the id is not one of the three.
 */
export function metricaPorId(id: string): MetricaTablero | undefined {
  return METRICAS_PREDICCION.find(metrica => metrica.id === id)
}
