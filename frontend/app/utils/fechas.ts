/**
 * Localised formatting of the instants and the figures the home screen shows.
 *
 * The fixed time zone is the whole reason this module exists. `Intl` with no
 * `timeZone` uses the one of the process, the server and the reader's browser
 * can sit in different ones, and then the server renders "11 ago" where the
 * client renders "12 ago": Vue reports a hydration mismatch on every date and
 * the text visibly swaps after the page settles. Pinning UTC removes the class
 * of defect instead of hiding one instance of it.
 *
 * Scope, on purpose: this module formats ISO INSTANTS. A month of the shape
 * `YYYY-MM` is not an instant and is not handled here; whoever needs one writes
 * their own, because a formatter that guesses which of the two it was given is
 * a formatter that will guess wrong.
 */

/** Day, abbreviated month and year, which is what a cut-off date needs. */
const FORMATO_FECHA: Intl.DateTimeFormatOptions = {
  timeZone: 'UTC',
  day: 'numeric',
  month: 'short',
  year: 'numeric',
}

/** The same, plus the time, for items the reader recognises by when they ran. */
const FORMATO_FECHA_HORA: Intl.DateTimeFormatOptions = {
  ...FORMATO_FECHA,
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
}

/**
 * Formats an ISO instant for a locale, always in UTC.
 *
 * @param iso - ISO 8601 instant.
 * @param idioma - BCP 47 locale code, 'es' or 'en'.
 * @returns Day, short month and year, already localised.
 */
export function formatearFecha(iso: string, idioma: string): string {
  return new Intl.DateTimeFormat(idioma, FORMATO_FECHA).format(new Date(iso))
}

/**
 * Formats an ISO instant with its time, always in UTC.
 *
 * @param iso - ISO 8601 instant.
 * @param idioma - BCP 47 locale code, 'es' or 'en'.
 * @returns Date and time of day, already localised.
 */
export function formatearFechaHora(iso: string, idioma: string): string {
  return new Intl.DateTimeFormat(idioma, FORMATO_FECHA_HORA).format(new Date(iso))
}

/**
 * Formats a number for a locale with a fixed number of decimals.
 *
 * The count is fixed and not "up to": a column where one row reads 118.4 and
 * the next 2 stops being scannable, which is the whole point of a figure on a
 * card.
 *
 * @param valor - Value to format.
 * @param idioma - BCP 47 locale code.
 * @param decimales - Fixed fraction digits. Defaults to 1.
 * @returns The figure, already localised.
 */
export function formatearNumero(valor: number, idioma: string, decimales = 1): string {
  return new Intl.NumberFormat(idioma, {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor)
}

/**
 * Formats a change against a previous period, sign always visible.
 *
 * The explicit plus is not decoration: without it a rise of 2.1 points and an
 * absolute value of 2.1 are the same string, and the card would be claiming
 * something it does not mean.
 *
 * @param valor - Signed change.
 * @param idioma - BCP 47 locale code.
 * @param decimales - Fixed fraction digits. Defaults to 1.
 * @returns The change with its sign, already localised.
 */
export function formatearVariacion(valor: number, idioma: string, decimales = 1): string {
  return new Intl.NumberFormat(idioma, {
    signDisplay: 'exceptZero',
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor)
}
