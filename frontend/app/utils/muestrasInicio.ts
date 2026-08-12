import type { ElementoLista, Indicador } from '~/types/espacios'

/**
 * Sample content of the home screen, and nothing else.
 *
 * No table in the database holds a recent search, a favourite, an alert or an
 * export job on the day this screen ships: the catalogue is seeded, but none of
 * the migrations creates user preferences. So the six collections below are
 * sample data, they are declared as such on screen, and they travel in the
 * bundle. This module is deliberately the only place that has to disappear when
 * the endpoints exist: the composition contract next door survives untouched.
 *
 * Two properties are load bearing rather than tidy:
 *
 * 1. NO CLOCK. Every date is anchored to `INSTANTE_DE_REFERENCIA`, so the
 *    figure captured for the report on Saturday is byte for byte the one
 *    captured on Wednesday. Reading the system clock here would silently
 *    invalidate the deliverable.
 * 2. THE VOCABULARY IS REAL. The physical names and the source codes come from
 *    the seeded catalogue, so clicking a recent search lands on a query that
 *    returns rows instead of on the empty screen that gives a mock away.
 *
 * The visible label of every item is a translation key; the physical name is
 * data, because `ratio_lcr` has no English spelling and a catalogue key with
 * the same text in both languages is what `test/idioma.spec.ts` refuses.
 */

/** Frozen clock of the prototype. Every sample date is anchored here. */
export const INSTANTE_DE_REFERENCIA = '2026-08-12T09:00:00Z'

/** Previous session of the reader, shown by the profile block. */
export const ULTIMO_ACCESO = '2026-08-11T17:40:00Z'

/** Cut-off of the three present-day figures: the close of the previous month. */
export const CORTE_DE_INDICADORES = '2026-07-31T00:00:00Z'

/** The five most recent searches of the reader, newest first. */
export const BUSQUEDAS_RECIENTES: readonly ElementoLista[] = Object.freeze([
  {
    id: 'lcr',
    claveEtiqueta: 'workspace.samples.recent.lcr',
    termino: 'ratio_lcr',
    destino: '/exploracion?q=ratio_lcr',
    fecha: '2026-08-12T08:20:00Z',
  },
  {
    id: 'capital',
    claveEtiqueta: 'workspace.samples.recent.capital',
    termino: 'sdo_cap',
    destino: '/exploracion?q=sdo_cap',
    fecha: '2026-08-11T16:05:00Z',
  },
  {
    id: 'mora',
    claveEtiqueta: 'workspace.samples.recent.mora',
    termino: 'dias_mora',
    destino: '/exploracion?q=dias_mora',
    fecha: '2026-08-11T11:42:00Z',
  },
  {
    id: 'nocional',
    claveEtiqueta: 'workspace.samples.recent.nocional',
    termino: 'nocional_usd',
    destino: '/exploracion?q=nocional_usd',
    fecha: '2026-08-10T18:15:00Z',
  },
  {
    id: 'disponible',
    claveEtiqueta: 'workspace.samples.recent.disponible',
    termino: 'mto_disp',
    destino: '/exploracion?q=mto_disp',
    fecha: '2026-08-10T09:30:00Z',
  },
])

/** The four sources the reader pinned, by their catalogue code. */
export const FAVORITOS: readonly ElementoLista[] = Object.freeze([
  {
    id: 'liquidez',
    claveEtiqueta: 'workspace.samples.favorite.liquidez',
    termino: 'liquidez',
    destino: '/exploracion?q=liquidez',
  },
  {
    id: 'creditos',
    claveEtiqueta: 'workspace.samples.favorite.creditos',
    termino: 'creditos',
    destino: '/exploracion?q=creditos',
  },
  {
    id: 'derivados',
    claveEtiqueta: 'workspace.samples.favorite.derivados',
    termino: 'derivados',
    destino: '/exploracion?q=derivados',
  },
  {
    id: 'regulatorio',
    claveEtiqueta: 'workspace.samples.favorite.regulatorio',
    termino: 'regulatorio',
    destino: '/exploracion?q=regulatorio',
  },
])

/**
 * The three signals waiting for the reader.
 *
 * Each one links to the evidence and not to a detail screen that does not
 * exist: a threshold breach opens the query that shows it, and a definition
 * change opens the dictionary that holds it.
 */
export const ALERTAS: readonly ElementoLista[] = Object.freeze([
  {
    id: 'lcrBajoUmbral',
    claveEtiqueta: 'workspace.samples.alert.lcrBajoUmbral',
    destino: '/exploracion?q=ratio_lcr',
    fecha: '2026-08-12T07:05:00Z',
    insignia: { claveTexto: 'workspace.severity.high', tono: 'peligro' },
  },
  {
    id: 'cargaRetrasada',
    claveEtiqueta: 'workspace.samples.alert.cargaRetrasada',
    destino: '/gobierno',
    fecha: '2026-08-12T05:40:00Z',
    insignia: { claveTexto: 'workspace.severity.medium', tono: 'atencion' },
  },
  {
    id: 'definicionActualizada',
    claveEtiqueta: 'workspace.samples.alert.definicionActualizada',
    destino: '/gobierno',
    fecha: '2026-08-11T14:10:00Z',
    insignia: { claveTexto: 'workspace.severity.low', tono: 'neutro' },
  },
])

/** The four export jobs of the analyst, with the state each one is in. */
export const EXPORTACIONES: readonly ElementoLista[] = Object.freeze([
  {
    id: 'carteraMensual',
    claveEtiqueta: 'workspace.samples.export.carteraMensual',
    destino: '/exploracion/exportar',
    fecha: '2026-08-12T08:05:00Z',
    insignia: { claveTexto: 'workspace.exportStatus.ready', tono: 'exito' },
  },
  {
    id: 'posicionesDerivados',
    claveEtiqueta: 'workspace.samples.export.posicionesDerivados',
    destino: '/exploracion/exportar',
    fecha: '2026-08-12T08:55:00Z',
    insignia: { claveTexto: 'workspace.exportStatus.running', tono: 'atencion' },
  },
  {
    id: 'moraPorSucursal',
    claveEtiqueta: 'workspace.samples.export.moraPorSucursal',
    destino: '/exploracion/exportar',
    fecha: '2026-08-11T19:20:00Z',
    insignia: { claveTexto: 'workspace.exportStatus.ready', tono: 'exito' },
  },
  {
    id: 'liquidezDiaria',
    claveEtiqueta: 'workspace.samples.export.liquidezDiaria',
    destino: '/exploracion/exportar',
    fecha: '2026-08-05T07:00:00Z',
    insignia: { claveTexto: 'workspace.exportStatus.expired', tono: 'neutro' },
  },
])

/** The three queries the analyst saved and reopens by name. */
export const CONSULTAS_GUARDADAS: readonly ElementoLista[] = Object.freeze([
  {
    id: 'moraMayor90',
    claveEtiqueta: 'workspace.samples.query.moraMayor90',
    termino: 'dias_mora',
    destino: '/exploracion?q=dias_mora',
    fecha: '2026-08-11T10:00:00Z',
  },
  {
    id: 'lcrPorUnidad',
    claveEtiqueta: 'workspace.samples.query.lcrPorUnidad',
    termino: 'ratio_lcr',
    destino: '/exploracion?q=ratio_lcr',
    fecha: '2026-08-07T15:25:00Z',
  },
  {
    id: 'exposicionContraparte',
    claveEtiqueta: 'workspace.samples.query.exposicionContraparte',
    termino: 'nocional_usd',
    destino: '/exploracion?q=nocional_usd',
    fecha: '2026-08-04T12:35:00Z',
  },
])

/**
 * The three present-day figures of the executive composition.
 *
 * Value today, change against the previous month and cut-off date. No
 * projection: the forecast cards carry a method label and live in the
 * dashboard, and a figure that mixes the two cannot be read honestly.
 */
export const INDICADORES: readonly Indicador[] = Object.freeze([
  {
    id: 'lcr',
    claveEtiqueta: 'workspace.samples.indicator.lcr',
    valor: 118.4,
    unidad: 'porcentaje',
    variacion: 2.1,
    fecha: CORTE_DE_INDICADORES,
    destino: '/exploracion/tableros',
  },
  {
    id: 'carteraVencida',
    claveEtiqueta: 'workspace.samples.indicator.carteraVencida',
    valor: 2.7,
    unidad: 'porcentaje',
    variacion: -0.3,
    fecha: CORTE_DE_INDICADORES,
    destino: '/exploracion/tableros',
  },
  {
    id: 'exposicionNeta',
    claveEtiqueta: 'workspace.samples.indicator.exposicionNeta',
    valor: 1284.5,
    unidad: 'millones-mxn',
    variacion: 64.2,
    fecha: CORTE_DE_INDICADORES,
    destino: '/exploracion/tableros',
  },
])
