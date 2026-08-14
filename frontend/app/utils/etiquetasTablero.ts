/**
 * Catalogue keys of the closed vocabularies of the dashboard.
 *
 * The controls, the summary sentence, the figure caption and the table all name
 * the same metric and the same grouping. Four components each writing their own
 * `t('dashboard.metric.' + valor)` is how one of them ends up pointing at a key
 * nobody wrote, which vue-i18n renders as the dotted path itself, in both
 * languages, on screen.
 *
 * Explicit maps and not string concatenation: the scan of `test/contratos.spec`
 * only sees keys written as literals, so a key assembled at run time would be
 * invisible to the check that every used key exists.
 */
import type { AgrupacionTablero, DensidadTablero, MetricaTablero } from '~/types/tablero'

/** The three metrics, in the order the control offers them. */
export const METRICAS: readonly MetricaTablero[] = Object.freeze([
  'saldo_disponible_mxn',
  'ratio_lcr',
  'n_posiciones',
])

/** The four groupings, in the order the control offers them. */
export const AGRUPACIONES: readonly AgrupacionTablero[] = Object.freeze([
  'unidad_negocio',
  'divisa',
  'bucket_venc',
  'serie',
])

/** The three reading densities, from the cheapest to the evidence load. */
export const DENSIDADES: readonly DensidadTablero[] = Object.freeze([
  'resumen',
  'detalle',
  'completa',
])

/** Catalogue key of each metric. */
export const CLAVE_METRICA: Record<MetricaTablero, string> = Object.freeze({
  saldo_disponible_mxn: 'dashboard.metric.balance',
  ratio_lcr: 'dashboard.metric.lcrRatio',
  n_posiciones: 'dashboard.metric.positions',
})

/** Catalogue key of each grouping. */
export const CLAVE_AGRUPACION: Record<AgrupacionTablero, string> = Object.freeze({
  unidad_negocio: 'dashboard.grouping.businessUnit',
  divisa: 'dashboard.grouping.currency',
  bucket_venc: 'dashboard.grouping.maturity',
  serie: 'dashboard.grouping.series',
})

/** Catalogue key of each density. */
export const CLAVE_DENSIDAD: Record<DensidadTablero, string> = Object.freeze({
  resumen: 'dashboard.density.summary',
  detalle: 'dashboard.density.detail',
  completa: 'dashboard.density.full',
})
