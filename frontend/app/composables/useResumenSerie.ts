import type { ComputedRef, Ref } from 'vue'
import type { EstadisticaSerie, MarcoSerie } from '~/types/tablero'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { CLAVE_METRICA } from '~/utils/etiquetasTablero'
import {
  fechasDelMarco,
  formatearValor,
  formatearVariacionRelativa,
  estadisticasPorSerie,
  variacionRelativa,
} from '~/utils/serieEstadisticas'

/**
 * The textual summary of the chart, which is the alternative for a reader who
 * cannot see it.
 *
 * It is a visible string even though only a screen reader will ever speak it,
 * so it is assembled from the catalogues like every other one. That is the whole
 * point of putting it here instead of inside the component: a sentence typed in
 * Spanish inside a template would be read in Spanish to an English reader, and
 * the one person who would notice is the one least likely to report it.
 *
 * It describes the highest line rather than an average of all of them: an
 * average across 250 unrelated series is a number that exists nowhere on the
 * chart and that nobody can check.
 */

/** Statistics of the line with the highest maximum, or null when all are holes. */
function lineaMasAlta(estadisticas: readonly EstadisticaSerie[]): EstadisticaSerie | null {
  let cima: EstadisticaSerie | null = null
  for (const estadistica of estadisticas) {
    if (!Number.isFinite(estadistica.maximo)) {
      continue
    }
    if (cima === null || estadistica.maximo > cima.maximo) {
      cima = estadistica
    }
  }
  return cima
}

/**
 * Sentence describing the loaded frame, in the language on screen.
 *
 * @param marco - Decoded frame, or null while there is none.
 * @returns The sentence, recomputed when the frame or the language changes.
 */
export function useResumenSerie(marco: Ref<MarcoSerie | null>): ComputedRef<string> {
  const { t, locale } = useI18n()

  return computed<string>(() => {
    const actual = marco.value
    if (actual === null || actual.conteo.series === 0) {
      return t('dashboard.summary.empty')
    }

    const estadisticas = estadisticasPorSerie(actual)
    const cima = lineaMasAlta(estadisticas)
    if (cima === null) {
      return t('dashboard.summary.empty')
    }

    const idioma = esCodigoIdioma(locale.value) ? locale.value : 'es'
    const fechas = fechasDelMarco(actual)
    const hueco = t('dashboard.table.gap')
    const cifra = (valor: number): string =>
      formatearValor(valor, actual.metrica, idioma) ?? hueco
    const etiqueta = actual.catalogo[cima.indice]
    const nombre = etiqueta === undefined ? '' : idioma === 'en' ? etiqueta.labelEn : etiqueta.labelEs

    return t('dashboard.summary.text', {
      metric: t(CLAVE_METRICA[actual.metrica]),
      from: actual.fechaMin,
      to: actual.fechaMax,
      lines: actual.conteo.series,
      points: actual.conteo.puntos,
      top: nombre,
      change: formatearVariacionRelativa(variacionRelativa(cima), idioma) ?? hueco,
      max: cifra(cima.maximo),
      maxDate: fechas[cima.indiceMaximo] ?? hueco,
      min: cifra(cima.minimo),
      minDate: fechas[cima.indiceMinimo] ?? hueco,
    })
  })
}
