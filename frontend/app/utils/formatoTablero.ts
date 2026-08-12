/**
 * US-026 - how the predictive cards write a month, a figure and a change.
 *
 * `Intl` with an explicit locale and a fixed time zone, never the ambient ones.
 * The fixed zone is not cosmetic: without it the server pass and the browser can
 * format the same month differently and Vue reports a hydration mismatch on a
 * node nobody touched.
 *
 * `frontend/app/utils/fechas.ts` (US-027) is a separate module on purpose and
 * this one does not import it: that one formats ISO instants down to the day,
 * these inputs are calendar months with no instant behind them, and the two
 * User Stories land on the same day. The handoff records the merge for S5.
 */
import type { CodigoIdioma } from '~/composables/useIdioma'
import type { UnidadMetrica } from '~/types/prediccion'

/** Locale used to format, per interface language. */
export const LOCALE_POR_IDIOMA: Record<CodigoIdioma, string> = { es: 'es-MX', en: 'en-US' }

/**
 * Fraction digits of a figure, per presentation unit.
 *
 * The balance is published in millions and reaches eight digits, so a decimal
 * there buys no precision and costs the width that keeps the figure on one
 * line, which is half of what stops the card from growing when the data lands.
 */
const DECIMALES_POR_UNIDAD: Record<UnidadMetrica, number> = {
  porcentaje: 1,
  'millones-mxn': 0,
}

/**
 * Fraction digits of a change.
 *
 * Two, because the synthetic series moves by hundredths of a point between
 * consecutive months and one decimal would print every card as "+0.0 %".
 */
const DECIMALES_VARIACION = 2

/** A month written as YYYY-MM, which is the only shape the history publishes. */
const PATRON_MES = /^(\d{4})-(\d{2})$/

/**
 * Formats a YYYY-MM month for a locale, always in UTC.
 *
 * @param mes - Month as YYYY-MM.
 * @param idioma - Interface language.
 * @returns Short month and year, already localised, or the raw input when it is
 *   not a month: printing the raw string is how a malformed payload stays
 *   visible instead of turning into "Invalid Date".
 */
export function formatearMes(mes: string, idioma: CodigoIdioma): string {
  const partes = PATRON_MES.exec(mes)
  if (partes === null) {
    return mes
  }
  const instante = Date.UTC(Number(partes[1]), Number(partes[2]) - 1, 1)
  return new Intl.DateTimeFormat(LOCALE_POR_IDIOMA[idioma], {
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(instante)
}

/**
 * Formats a metric value according to its unit.
 *
 * The percentage is emitted by `Intl` and never by appending a sign written in
 * a template: the symbol is spelled the same way in both catalogues, so a key
 * for it would be the one string that breaks the "nothing reads alike in the
 * two languages" rule of the bilingual contract.
 *
 * @param valor - Raw value as published in the history.
 * @param unidad - Presentation unit of the metric.
 * @param idioma - Interface language.
 * @returns The formatted figure, or null when the value is not a number. The
 *   caller renders the hole with a translated string.
 */
export function formatearCifra(
  valor: number | null | undefined,
  unidad: UnidadMetrica,
  idioma: CodigoIdioma,
): string | null {
  if (valor === null || valor === undefined || !Number.isFinite(valor)) {
    return null
  }
  const decimales = DECIMALES_POR_UNIDAD[unidad]
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    style: unidad === 'porcentaje' ? 'percent' : 'decimal',
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor)
}

/**
 * Formats a percentage change with an explicit sign.
 *
 * The sign is textual and not only colour: colour alone cannot carry the
 * direction of a change, and half of the reader profiles of A1 would lose it.
 *
 * @param variacionPct - Change in percentage points, as `Proyeccion` carries it.
 * @param idioma - Interface language.
 * @returns The signed percentage, or null when there is no change to state.
 */
export function formatearCambio(
  variacionPct: number | null | undefined,
  idioma: CodigoIdioma,
): string | null {
  if (variacionPct === null || variacionPct === undefined || !Number.isFinite(variacionPct)) {
    return null
  }
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    style: 'percent',
    signDisplay: 'exceptZero',
    minimumFractionDigits: DECIMALES_VARIACION,
    maximumFractionDigits: DECIMALES_VARIACION,
  }).format(variacionPct / 100)
}

/**
 * Formats a whole count, which is what the method label interpolates.
 *
 * @param valor - Count of months or of horizon steps.
 * @param idioma - Interface language.
 */
export function formatearEntero(valor: number, idioma: CodigoIdioma): string {
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    maximumFractionDigits: 0,
  }).format(valor)
}

/**
 * Formats a goodness of fit coefficient with two decimals.
 *
 * Two and not four: the label states how well the line fits, not the fit
 * itself, and four decimals of an R squared read as a precision the synthetic
 * history does not have.
 *
 * @param valor - Coefficient between 0 and 1.
 * @param idioma - Interface language.
 */
export function formatearCoeficiente(valor: number, idioma: CodigoIdioma): string {
  return new Intl.NumberFormat(LOCALE_POR_IDIOMA[idioma], {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(valor)
}
