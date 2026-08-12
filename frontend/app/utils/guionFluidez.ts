/**
 * The frozen pan and zoom script the fluidity measurement replays.
 *
 * A mouse drag is not evidence: it differs between runs, between machines and
 * between hands, so two measurements taken that way cannot be compared and the
 * figure that reaches the A4 document would be an anecdote. The script is code,
 * it is versioned, and its version travels inside every report: comparing a
 * measurement of version 1 against one of version 2 is a mistake the reader can
 * see instead of one they cannot.
 */

/** Window of the x axis at one step, in dataZoom percentages. */
export interface PasoGuion {
  inicio: number
  fin: number
}

/** Steps of the script. Three seconds at sixty frames per second. */
export const PASOS_GUION = 180

/** Version of the script. Bumped whenever the sequence below changes. */
export const VERSION_GUION = 1

/** Frame budget, in milliseconds, above which a frame counts as a long one. */
export const UMBRAL_CUADRO_MS = 34

/** Steps of each of the three phases: zoom in, pan, zoom out. */
const PASOS_POR_FASE = PASOS_GUION / 3

/** Rounds to four decimals so the script is byte identical on every machine. */
function redondear(valor: number): number {
  return Math.round(valor * 10000) / 10000
}

/** Linear interpolation between two windows. */
function interpolar(desde: PasoGuion, hasta: PasoGuion, avance: number): PasoGuion {
  return {
    inicio: redondear(desde.inicio + (hasta.inicio - desde.inicio) * avance),
    fin: redondear(desde.fin + (hasta.fin - desde.fin) * avance),
  }
}

/**
 * Builds the sequence once, at module load.
 *
 * Zoom in to a fifth of the range, pan that window across most of the series and
 * zoom back out. Those are the three gestures a reader actually performs on a
 * dense time series, and the third one is the expensive one: widening the window
 * puts every hidden point back into the paint.
 */
function construirGuion(): readonly PasoGuion[] {
  const pasos: PasoGuion[] = []
  const completa: PasoGuion = { inicio: 0, fin: 100 }
  const acercada: PasoGuion = { inicio: 40, fin: 60 }
  const desplazada: PasoGuion = { inicio: 78, fin: 98 }

  for (let paso = 0; paso < PASOS_POR_FASE; paso += 1) {
    pasos.push(interpolar(completa, acercada, (paso + 1) / PASOS_POR_FASE))
  }
  for (let paso = 0; paso < PASOS_POR_FASE; paso += 1) {
    pasos.push(interpolar(acercada, desplazada, (paso + 1) / PASOS_POR_FASE))
  }
  for (let paso = 0; paso < PASOS_POR_FASE; paso += 1) {
    pasos.push(interpolar(desplazada, completa, (paso + 1) / PASOS_POR_FASE))
  }

  return Object.freeze(pasos.map(paso => Object.freeze(paso)))
}

/** Frozen zoom-in, pan, zoom-out script. Same sequence on every machine. */
export const GUION_ZOOM: readonly PasoGuion[] = construirGuion()
