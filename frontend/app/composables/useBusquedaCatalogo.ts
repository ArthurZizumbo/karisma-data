import type { ComputedRef, Ref } from 'vue'
import type { BusquedaCruda, CampoCatalogo, CampoCrudo, EstadoConsulta } from '~/types/linaje'
import type { EstadoCertificacion } from '~/utils/tokens.generated'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { codigoDelFallo } from '~/composables/useSerieTablero'
import { usePermisos } from '~/composables/usePermisos'
import { ESTADOS_CERTIFICACION } from '~/utils/tokens.generated'

/**
 * Keyword search over the seeded catalog, for the governance dictionary.
 *
 * `immediate: false` is what makes the initial state real: the screen opens on
 * a designed empty state instead of firing a request for a query nobody typed,
 * which the endpoint would answer with a 422 the moment the page loads.
 *
 * This composable owns the only conversion of the wire vocabulary: the backend
 * answers in `snake_case` because US-008 froze that contract, and nothing below
 * this file ever sees a `snake_case` key. The certification state is part of
 * that vocabulary and is resolved here too, against the generated tokens.
 */

/** Route published by the catalogue of US-008. Not invented here. */
export const RUTA_BUSQUEDA = '/api/catalog/search'

/** Shortest term the endpoint accepts. Below it there is nothing to ask for. */
export const MINIMO_TERMINO = 2

/** Page size. Twenty cards is what fits before the list stops being scannable. */
export const LIMITE_PAGINA = 20

/**
 * Query parameter the address carries the term in.
 *
 * It is the same letter the product header writes when it sends a reader to the
 * catalogue, and it is exported so no second file has to spell it: a search box
 * that navigates with `q` towards a screen that reads `termino` loses the term
 * with nothing broken to look at.
 */
export const PARAMETRO_TERMINO = 'q'

/**
 * Certification state of a field, resolved from the generated tokens.
 *
 * The catalogue spells the value with an underscore -`en_revision`, which is
 * what the CHECK constraint of the migration stores- and the design system
 * spells the token with a hyphen. Normalising here is what keeps the hyphen out
 * of the wire vocabulary and the underscore out of the token names.
 *
 * @param codigo - Certification value as the backend spells it.
 * @returns The state with its colour and its icon, or null when the code is not
 *   one the design system declares: painting an unknown state with the icon of
 *   a known one is the defect this replaces.
 */
export function certificacionDeCampo(codigo: string): EstadoCertificacion | null {
  const normalizado = codigo.replace(/_/g, '-')
  return ESTADOS_CERTIFICACION.find(estado => estado.codigo === normalizado) ?? null
}

/** How the search behaves beyond fetching, which today is only the address. */
export interface OpcionesBusqueda {
  /**
   * True to seed the term from the address and write every search back into it.
   *
   * The catalogue screen turns it on: its term arrives from the product header,
   * has to survive a round trip through the screens the catalogue itself offers
   * and has to be shareable as a link. The governance dictionary leaves it off:
   * its box is a component of its own and an address that carried a term the
   * box never shows would be a screen contradicting its own URL.
   */
  sincronizarUrl?: boolean
}

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
  reintentar: () => Promise<void>
}

/**
 * Search state of the dictionary.
 *
 * @param opciones - How the search behaves beyond fetching.
 * @returns The page, its state and the actions the form offers.
 */
export function useBusquedaCatalogo(opciones: OpcionesBusqueda = {}): BusquedaCatalogo {
  const { expirarSesion } = usePermisos()

  /**
   * The address, when this search is the one that owns it.
   *
   * Read at setup and only then: `useRoute` and `useRouter` are injections, and
   * a consumer that does not synchronise must not be made to require a router
   * it never uses.
   */
  const sincroniza = opciones.sincronizarUrl === true
  const route = sincroniza ? useRoute() : null
  const router = sincroniza ? useRouter() : null

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

  /** Term the address is carrying right now, trimmed and never null. */
  function terminoDeLaDireccion(): string {
    const crudo = route?.query[PARAMETRO_TERMINO]
    return typeof crudo === 'string' ? crudo.trim() : ''
  }

  /**
   * Writes the term into the address, replacing instead of pushing.
   *
   * `replace` and not `push` is the whole point of the round trip: with a push,
   * every search would leave an entry behind and the Back button of a reader
   * who went to the dashboards would land on the catalogue WITHOUT the term,
   * which is the exact defect this closes.
   *
   * @param valor - Term to publish, or the empty string to drop it.
   */
  async function publicarEnLaDireccion(valor: string): Promise<void> {
    if (router === null || route === null || terminoDeLaDireccion() === valor) {
      return
    }
    // Rebuilt without the parameter instead of deleting it: the term is dropped
    // by not copying it, and the rest of the address travels untouched.
    const consulta = Object.fromEntries(
      Object.entries(route.query).filter(([nombre]) => nombre !== PARAMETRO_TERMINO),
    )
    await router.replace({
      query: valor === '' ? consulta : { ...consulta, [PARAMETRO_TERMINO]: valor },
    })
  }

  /**
   * Applies the term the address carries, which is where a cold open starts.
   *
   * The domain narrowing is dropped on purpose: a term that arrives from the
   * address comes from outside this screen -the header search box, a shared
   * link, the Back button- and answering it through a filter the reader set for
   * a previous term would return an empty result nobody asked for.
   */
  async function aplicarDireccion(): Promise<void> {
    const pedidoEnLaDireccion = terminoDeLaDireccion()
    if (pedidoEnLaDireccion === termino.value) {
      return
    }
    termino.value = pedidoEnLaDireccion
    dominio.value = null
    if (pedidoEnLaDireccion.length < MINIMO_TERMINO) {
      // The address lost the term: the screen goes back to the state it opens
      // in instead of keeping a result that no longer answers any question.
      pedido.value = false
      return
    }
    await consultar()
  }

  async function buscar(nuevo: string): Promise<void> {
    const limpio = nuevo.trim()
    // Shorter than the minimum the endpoint accepts: the form says so and no
    // request leaves, which is why the screen never shows a 422 to a reader.
    if (limpio.length < MINIMO_TERMINO) {
      return
    }
    termino.value = limpio
    await publicarEnLaDireccion(limpio)
    await consultar()
  }

  async function filtrarPorDominio(nuevo: string | null): Promise<void> {
    dominio.value = nuevo
    if (termino.value.length < MINIMO_TERMINO) {
      return
    }
    await consultar()
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

  if (route !== null) {
    // On mount and not during setup: the fetch is client only, and a request
    // fired while the server renders would answer into a component nobody has
    // hydrated yet.
    onMounted(() => {
      void aplicarDireccion()
    })

    // The address can change without this screen unmounting: the header search
    // box navigates to the catalogue from the catalogue itself.
    watch(() => route.query[PARAMETRO_TERMINO], () => {
      void aplicarDireccion()
    })
  }

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
    reintentar,
  }
}
