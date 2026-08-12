import type { ComputedRef } from 'vue'
import type {
  EstadoTarjeta,
  HistoricoMetrica,
  PayloadHistoricos,
  PuntoMensual,
  TarjetaPrediccion,
} from '~/types/prediccion'
import { computed } from 'vue'
import { METRICAS_PREDICCION } from '~/utils/metricasTablero'
import { proyectarLineal } from '~/utils/proyeccion'

/**
 * US-026 - the three predictive cards, from the published history.
 *
 * Three decisions live here and each one closes a defect the screen would
 * otherwise carry:
 *
 * 1. `server: false`. The request is issued from the browser, so the loading
 *    state is reached on every visit instead of being a branch nobody can
 *    trigger. A skeleton that only appears on a cold server render is a
 *    skeleton nobody ever tested.
 * 2. The grid is built from `METRICAS_PREDICCION` and never from the response. The number
 *    of cards cannot change when the request settles, which is the structural
 *    half of "no layout shift"; a metric missing from the payload gets its
 *    designed empty state instead of vanishing.
 * 3. The payload is validated instead of trusted. The history is a static asset
 *    that anybody can regenerate half way, and a `.map` over a string is a
 *    blank screen in the middle of a demo.
 */

/**
 * Path of the published history.
 *
 * A static asset and not a route under `/api`: a Nitro route would be a data
 * surface the scope audit of US-016 cannot see, which is the defect the
 * previous audit found. The degradation is declared in the handoff, and the S5
 * remediation is one line pointing at `GET /api/metrics/series`.
 */
export const RUTA_HISTORICO = '/datos/historicos-tablero.json'

/** What the dashboard section needs in order to render its four states. */
export interface PrediccionesTablero {
  /** Always three entries, one per METRICAS_PREDICCION, whatever the response says. */
  tarjetas: ComputedRef<readonly TarjetaPrediccion[]>
  /** True while the request has not settled. Drives the skeleton. */
  cargando: ComputedRef<boolean>
  /** True on transport failure or malformed payload. */
  hayError: ComputedRef<boolean>
  /** State a given card has to render, derived from the same three signals. */
  estadoDe: (tarjeta: TarjetaPrediccion) => EstadoTarjeta
  /** Re-issues the request. Bound to the retry button of the error state. */
  recargar: () => Promise<void>
}

/** True when the value has the shape of a monthly point. */
function esPunto(valor: unknown): valor is PuntoMensual {
  const punto = valor as PuntoMensual | null
  return (
    punto !== null
    && typeof punto === 'object'
    && typeof punto.mes === 'string'
    && typeof punto.valor === 'number'
  )
}

/** True when the value has the shape of a published metric history. */
function esHistorico(valor: unknown): valor is HistoricoMetrica {
  const historico = valor as HistoricoMetrica | null
  return (
    historico !== null
    && typeof historico === 'object'
    && typeof historico.id === 'string'
    && typeof historico.campoOrigen === 'string'
    && typeof historico.claveAgregacion === 'string'
    && Array.isArray(historico.puntos)
    && historico.puntos.every(esPunto)
  )
}

/**
 * True when the value is the payload this screen consumes.
 *
 * Exported because the spec asserts the published asset satisfies it: the file
 * is versioned, so nothing at build time would notice a regeneration that
 * renamed a field.
 */
export function esPayloadHistoricos(valor: unknown): valor is PayloadHistoricos {
  const payload = valor as PayloadHistoricos | null
  return (
    payload !== null
    && typeof payload === 'object'
    && typeof payload.fuente === 'string'
    && payload.ventana !== null
    && typeof payload.ventana === 'object'
    && typeof payload.ventana.desde === 'string'
    && typeof payload.ventana.hasta === 'string'
    && typeof payload.ventana.meses === 'number'
    && Array.isArray(payload.metricas)
    && payload.metricas.every(esHistorico)
  )
}

/**
 * Projections of the three dashboard cards.
 *
 * @returns The three cards, the two flags the section renders its states from,
 *   and the reload the retry button is bound to.
 */
export function usePrediccionesTablero(): PrediccionesTablero {
  const { data, error, status, refresh } = useFetch(RUTA_HISTORICO, {
    // The loading state has to be real, and the asset is not part of the HTML
    // any SWR rule would cache.
    server: false,
    default: (): unknown => null,
  })

  const payload = computed<PayloadHistoricos | null>(() =>
    esPayloadHistoricos(data.value) ? data.value : null,
  )

  const cargando = computed<boolean>(
    () => status.value === 'idle' || status.value === 'pending',
  )

  const hayError = computed<boolean>(() => {
    if (error.value !== null && error.value !== undefined) {
      return true
    }
    return !cargando.value && payload.value === null
  })

  const tarjetas = computed<readonly TarjetaPrediccion[]>(() =>
    METRICAS_PREDICCION.map((metrica) => {
      const historico = payload.value?.metricas.find(entrada => entrada.id === metrica.id) ?? null
      return {
        metrica,
        historico,
        proyeccion: historico === null ? null : proyectarLineal(metrica.id, historico.puntos),
      }
    }),
  )

  const estadoDe = (tarjeta: TarjetaPrediccion): EstadoTarjeta => {
    if (cargando.value) {
      return 'cargando'
    }
    if (hayError.value) {
      return 'error'
    }
    return tarjeta.proyeccion === null ? 'vacio' : 'listo'
  }

  return {
    tarjetas,
    cargando,
    hayError,
    estadoDe,
    recargar: async () => {
      await refresh()
    },
  }
}
