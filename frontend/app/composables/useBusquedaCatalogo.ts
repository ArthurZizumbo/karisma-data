import type { ComputedRef, Ref } from 'vue'
import type { BusquedaCruda, CampoCatalogo, CampoCrudo, EstadoConsulta } from '~/types/linaje'
import { computed, ref, watch } from 'vue'
import { codigoDelFallo } from '~/composables/useSerieTablero'
import { usePermisos } from '~/composables/usePermisos'

/**
 * Keyword search over the seeded catalog, for the governance dictionary.
 *
 * `immediate: false` is what makes the initial state real: the screen opens on
 * a designed empty state instead of firing a request for a query nobody typed,
 * which the endpoint would answer with a 422 the moment the page loads.
 *
 * This composable owns the only conversion of the wire vocabulary: the backend
 * answers in `snake_case` because US-008 froze that contract, and nothing below
 * this file ever sees a `snake_case` key.
 */

/** Route published by the catalogue of US-008. Not invented here. */
export const RUTA_BUSQUEDA = '/api/catalog/search'

/** Shortest term the endpoint accepts. Below it there is nothing to ask for. */
export const MINIMO_TERMINO = 2

/** Page size. Twenty cards is what fits before the list stops being scannable. */
export const LIMITE_PAGINA = 20

/** One domain of the facet counts, with how many fields carry it. */
export interface ConteoDominio {
  codigo: string
  total: number
}

/**
 * Maps one hit of the search endpoint onto the vocabulary of the interface.
 *
 * @param crudo - Hit as the backend spells it.
 * @returns The same field, in the camelCase every component reads.
 */
export function mapearCampo(crudo: CampoCrudo): CampoCatalogo {
  return {
    fieldId: crudo.field_id,
    physicalName: crudo.physical_name,
    businessName: crudo.business_name,
    definition: crudo.definition,
    source: { code: crudo.source.code, displayName: crudo.source.display_name },
    owner: { area: crudo.owner.area, steward: crudo.owner.steward },
    validity: {
      validFrom: crudo.validity.valid_from,
      validTo: crudo.validity.valid_to,
      isCurrent: crudo.validity.is_current,
    },
    facets: {
      domain: crudo.facets.domain,
      dataType: crudo.facets.data_type,
      sensitivity: crudo.facets.sensitivity,
      refreshFrequency: crudo.facets.refresh_frequency,
      certification: crudo.facets.certification,
      unit: crudo.facets.unit,
      metricAgg: crudo.facets.metric_agg,
    },
  }
}

/** One page of the catalogue, already in the vocabulary of the interface. */
export interface PaginaCatalogo {
  total: number
  campos: readonly CampoCatalogo[]
  /** Counted over the whole matching set by the endpoint, never over the page,
   *  so a chip does not change meaning when the reader pages through. */
  dominios: readonly ConteoDominio[]
}

/**
 * Maps one answer of the search endpoint onto the page the dictionary draws.
 *
 * @param crudo - Body as the backend spells it.
 * @returns The page, its total and the domains of the whole matching set.
 */
export function mapearPagina(crudo: BusquedaCruda): PaginaCatalogo {
  return {
    total: crudo.total,
    campos: crudo.results.map(mapearCampo),
    dominios: Object.entries(crudo.facet_counts?.domain ?? {})
      .map(([codigo, conteo]) => ({ codigo, total: conteo }))
      .sort((uno, otro) => otro.total - uno.total || (uno.codigo < otro.codigo ? -1 : 1)),
  }
}

/** What the dictionary needs in order to draw its list and its four states. */
export interface BusquedaCatalogo {
  estado: ComputedRef<EstadoConsulta>
  /** Mapped page of the shallowRef `useFetch` owns. Never wrapped in reactive. */
  resultados: Ref<readonly CampoCatalogo[]>
  total: ComputedRef<number>
  termino: Ref<string>
  /** Domain the reader narrowed to, or null for the whole catalogue. */
  dominio: Ref<string | null>
  /** Domains of the whole matching set, never of the page. */
  dominios: ComputedRef<readonly ConteoDominio[]>
  /** Typed backend code when the state is 'error'. */
  codigo: ComputedRef<string | null>
  buscar: (termino: string) => Promise<void>
  /** Narrows to a domain, or clears the narrowing when given null. */
  filtrarPorDominio: (codigo: string | null) => Promise<void>
  limpiar: () => void
  reintentar: () => Promise<void>
}

/**
 * Search state of the dictionary.
 *
 * @returns The page, its state and the actions the form offers.
 */
export function useBusquedaCatalogo(): BusquedaCatalogo {
  const { expirarSesion } = usePermisos()

  const termino = ref('')
  const dominio = ref<string | null>(null)
  /** Whether a search was ever asked for. Tells 'inicial' from 'cargando'. */
  const pedido = ref(false)

  const consulta = computed<Record<string, string | number>>(() => {
    const parametros: Record<string, string | number> = {
      q: termino.value,
      limit: LIMITE_PAGINA,
    }
    if (dominio.value !== null) {
      parametros.domain = dominio.value
    }
    return parametros
  })

  const { data, error, status, refresh } = useFetch(RUTA_BUSQUEDA, {
    query: consulta,
    // The dictionary is a client side interaction, and there is nothing to
    // render on the server for a query the reader has not typed yet.
    immediate: false,
    server: false,
    // The query is reactive and the request is explicit: without this, typing
    // in the box would fire a request per keystroke against a two character
    // minimum, and the empty term would leave as a 422.
    watch: false,
    // Mapping inside the transform keeps a single source of truth for what
    // `data` holds, and makes a malformed body a fetch error instead of a
    // value every component would have to re-check on render.
    transform: (respuesta: unknown): PaginaCatalogo => mapearPagina(respuesta as BusquedaCruda),
    default: (): PaginaCatalogo | null => null,
  })

  const resultados = computed<readonly CampoCatalogo[]>(() => data.value?.campos ?? [])

  const total = computed<number>(() => data.value?.total ?? 0)

  const dominios = computed<readonly ConteoDominio[]>(() => data.value?.dominios ?? [])

  const codigo = computed<string | null>(() => codigoDelFallo(error.value))

  const estado = computed<EstadoConsulta>(() => {
    if (!pedido.value) {
      return 'inicial'
    }
    if (error.value !== null && error.value !== undefined) {
      return 'error'
    }
    if (data.value === null || status.value === 'pending') {
      return 'cargando'
    }
    return resultados.value.length === 0 ? 'vacio' : 'listo'
  })

  /** Runs the query the current term and domain describe. */
  async function consultar(): Promise<void> {
    pedido.value = true
    await refresh()
  }

  async function buscar(nuevo: string): Promise<void> {
    const limpio = nuevo.trim()
    // Shorter than the minimum the endpoint accepts: the form says so and no
    // request leaves, which is why the screen never shows a 422 to a reader.
    if (limpio.length < MINIMO_TERMINO) {
      return
    }
    termino.value = limpio
    await consultar()
  }

  async function filtrarPorDominio(nuevo: string | null): Promise<void> {
    dominio.value = nuevo
    if (termino.value.length < MINIMO_TERMINO) {
      return
    }
    await consultar()
  }

  function limpiar(): void {
    termino.value = ''
    dominio.value = null
    pedido.value = false
  }

  async function reintentar(): Promise<void> {
    if (termino.value.length < MINIMO_TERMINO) {
      return
    }
    await consultar()
  }

  // The hook US-017 exported for exactly this branch: a session that died while
  // the reader was searching has to end on the entry screen with its reason,
  // not on a dictionary that quietly stops answering.
  watch(error, async (fallo) => {
    if ((fallo as { statusCode?: number } | null)?.statusCode === 401) {
      await navigateTo(expirarSesion())
    }
  })

  return {
    estado,
    resultados,
    total,
    termino,
    dominio,
    dominios,
    codigo,
    buscar,
    filtrarPorDominio,
    limpiar,
    reintentar,
  }
}
