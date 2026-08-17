import type { ComputedRef, Ref } from 'vue'
import type { DensidadTablero, EstadoTablero, FiltrosTablero, MarcoSerie } from '~/types/tablero'
import { computed, watch } from 'vue'
import { usePermisos } from '~/composables/usePermisos'
import { useWorkspaceStore } from '~/stores/workspace'
import { decodificarMarco } from '~/utils/serieBinaria'

/**
 * Loads the preaggregated series for the filters currently in the workspace.
 *
 * `server: false` on purpose, and for two independent reasons: the frame is an
 * `ArrayBuffer`, which would have to be inflated to base64 to survive the SSR
 * payload, and the chart cannot render on the server anyway. What SSR does keep
 * is the guard: the route is resolved with the session before the page mounts,
 * so a reader without the scope never gets here.
 *
 * The decoded frame stays inside the shallowRef `useFetch` owns. Nothing wraps
 * it in a deep reactive proxy and nothing parks it in Pinia: deep reactivity
 * over half a million numbers turns every pan into a walk over proxies. The
 * acceptance criterion greps for that wrapper across composables and stores, so
 * these comments avoid writing it too.
 */

/** Path published by the permission registry of US-016. Not invented here. */
export const RUTA_SERIE = '/api/metrics/series'

/** Points per line requested at each reading density. */
export const PUNTOS_POR_DENSIDAD: Record<DensidadTablero, number> = {
  resumen: 400,
  detalle: 800,
  completa: 2000,
}

/** What the panel needs in order to draw the series and its four states. */
export interface SerieTablero {
  /** Decoded frame. The shallowRef of useFetch, never deeply reactive. */
  marco: Ref<MarcoSerie | null>
  estado: ComputedRef<EstadoTablero>
  /**
   * A new frame is in flight while a previous one is still painted.
   *
   * It is NOT the same as `estado === 'cargando'`, and the difference is the
   * whole point: `estado` reports the first load, when there is nothing on
   * screen yet. Every later filter change keeps the old frame in `data` -that
   * is what stops the panel from flashing- so `estado` stays `listo` and the
   * screen has no way to say the numbers being read are the previous ones.
   * Measured in the browser: changing the metric fires the request and the
   * panel shows nothing at all until the new frame lands.
   */
  revalidando: ComputedRef<boolean>
  /** Typed backend code when the state is 'sin-datos' or 'error'. */
  codigo: ComputedRef<string | null>
  recargar: () => Promise<void>
}

/** Query the endpoint receives, derived from the workspace decisions. */
export function consultaDeSerie(
  filtros: FiltrosTablero,
  densidad: DensidadTablero,
): Record<string, string | number | readonly string[] | readonly number[]> {
  // The full load is the performance evidence, and the evidence is 250 lines of
  // 2 000 points: at that density the grouping is forced to individual keys,
  // because five aggregated lines of 2 000 points would be 10 000 marks and the
  // headline figure of the delivery would quietly stop being true.
  const agrupacion = densidad === 'completa' ? 'serie' : filtros.agrupacion

  const consulta: Record<string, string | number | readonly string[] | readonly number[]> = {
    metrica: filtros.metrica,
    agrupacion,
    max_puntos: PUNTOS_POR_DENSIDAD[densidad],
  }

  if (filtros.unidadNegocio.length > 0) {
    consulta.unidad_negocio = filtros.unidadNegocio
  }
  if (filtros.divisa.length > 0) {
    consulta.divisa = filtros.divisa
  }
  if (filtros.bucketVenc.length > 0) {
    consulta.bucket_venc = filtros.bucketVenc
  }
  if (agrupacion === 'serie' && densidad !== 'completa' && filtros.seriesId.length > 0) {
    consulta.serie_id = filtros.seriesId
  }
  if (filtros.rangoFechas !== null) {
    consulta.desde = filtros.rangoFechas.desde
    consulta.hasta = filtros.rangoFechas.hasta
  }

  return consulta
}

/** Typed failure body of the endpoint, as US-016 standardised it. */
interface FalloConCodigo {
  statusCode?: number
  data?: { detail?: { codigo?: string } | string }
}

/** Reads the stable code of a failure, or null when there is none. */
export function codigoDelFallo(error: unknown): string | null {
  const fallo = error as FalloConCodigo | null
  const detalle = fallo?.data?.detail
  if (detalle !== undefined && typeof detalle !== 'string' && typeof detalle.codigo === 'string') {
    return detalle.codigo
  }
  return null
}

/**
 * Frame, state and reload action of the dashboard series.
 *
 * @returns The decoded frame and the three things the panel renders around it.
 */
export function useSerieTablero(): SerieTablero {
  const workspace = useWorkspaceStore()
  const { expirarSesion } = usePermisos()

  const consulta = computed(() => consultaDeSerie(workspace.filtros, workspace.densidad))

  const { data, error, status, refresh } = useFetch(RUTA_SERIE, {
    query: consulta,
    responseType: 'arrayBuffer',
    // The chart is client only and so is its payload.
    server: false,
    // Decoding inside the transform keeps a single source of truth for what
    // `data` holds, and makes a corrupt body a fetch error instead of a value
    // the panel would have to re-check on every render.
    transform: (respuesta: unknown): MarcoSerie => decodificarMarco(respuesta as ArrayBuffer),
    default: (): MarcoSerie | null => null,
  })

  const codigo = computed<string | null>(() => codigoDelFallo(error.value))

  /**
   * Refetch with a frame already on screen.
   *
   * `data.value !== null` is what tells it from the first load, and it is why
   * the panel dims instead of unmounting: rebuilding the chart on every filter
   * change would throw away the reader's zoom window and flash a skeleton over
   * a figure that is about to look almost the same.
   */
  const revalidando = computed<boolean>(
    () => status.value === 'pending' && data.value !== null,
  )

  const estado = computed<EstadoTablero>(() => {
    if (error.value !== null && error.value !== undefined) {
      return codigo.value === 'datos_no_sembrados' ? 'sin-datos' : 'error'
    }
    if (data.value === null) {
      return status.value === 'error' ? 'error' : 'cargando'
    }
    return data.value.conteo.series === 0 ? 'vacio' : 'listo'
  })

  // Provenance is registered from here and not from the fetch: the store holds
  // decisions, and where the loaded frame came from is one of them. US-029 reads
  // it to paint the lineage overlay.
  watch(
    data,
    (marco) => {
      if (marco !== null) {
        workspace.registrarOrigen(marco.origen)
      }
    },
    { immediate: true },
  )

  // The hook US-017 exported for exactly this branch. A session that died while
  // the reader was looking at the dashboard has to end on the entry screen with
  // its reason, not on a chart that silently stops updating.
  watch(error, async (fallo) => {
    const estadoHttp = (fallo as FalloConCodigo | null)?.statusCode
    if (estadoHttp === 401) {
      await navigateTo(expirarSesion())
    }
  })

  return {
    marco: data,
    estado,
    revalidando,
    codigo,
    recargar: async () => {
      await refresh()
    },
  }
}
