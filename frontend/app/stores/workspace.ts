/**
 * Shared dashboard-chat workspace (TwinBI pattern, paper 06).
 *
 * The exported name stays English on purpose. Three documents already name this
 * store -frontend/AGENTS.md, the portal-echarts-dashboards skill and the US-027
 * handoff- and US-026 and US-029 will consume it under that name; a fourth
 * spelling for the same thing is the divergence class the previous audit
 * punished. Everything inside follows the repository convention: Spanish
 * identifiers, English prose.
 *
 * The store holds DECISIONS, never DATA. Half a million points live in the
 * shallowRef that `useFetch` owns; parking them here would put deep reactivity
 * over a Float32Array and turn every pan into a proxy walk, which is the exact
 * performance defect this User Story exists to avoid.
 */
import type { ComputedRef, Ref, ShallowRef } from 'vue'
import type {
  AgrupacionTablero,
  ContextoAgente,
  DensidadTablero,
  DimensionDrill,
  FiltrosTablero,
  InteraccionTablero,
  MetricaTablero,
  NivelRevelacion,
  OrigenInteraccion,
  OrigenSerie,
  RangoFechas,
  VentanaTablero,
} from '~/types/tablero'
import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

/**
 * Route the workspace describes.
 *
 * A literal and not a read of the current route: `serializarVista()` must
 * produce the same string for the same view whether it is called from the panel
 * or later from the chat, and `useRoute()` would make it depend on where the
 * reader happened to be standing. `utils/navegacion.ts` is the A3 contract and
 * this User Story adds no route to it, so the constant lives here.
 */
export const RUTA_TABLERO = '/exploracion/tableros'

/** Full window of the x axis, in dataZoom percentages. */
const VENTANA_COMPLETA: VentanaTablero = { inicio: 0, fin: 100 }

/** Dimensions whose value is a list of strings. */
const DIMENSIONES_DE_LISTA = {
  unidadNegocio: 'unidadNegocio',
  divisa: 'divisa',
  bucketVenc: 'bucketVenc',
} as const

type DimensionDeLista = keyof typeof DIMENSIONES_DE_LISTA

/** The exact default view, rebuilt on every call so nothing can be mutated. */
function filtrosPorOmision(): FiltrosTablero {
  return {
    metrica: 'saldo_disponible_mxn',
    agrupacion: 'unidad_negocio',
    unidadNegocio: [],
    divisa: [],
    bucketVenc: [],
    seriesId: [],
    rangoFechas: null,
  }
}

/**
 * Plain deep copy of the filters, with no Vue proxy anywhere inside.
 *
 * `ref()` makes its contents deeply reactive, so handing `filtros.value` to the
 * agent would send it proxies with getters: `JSON.stringify` of one of those can
 * throw or produce a different object on each call, and the prompt hash of the
 * observability span would measure noise instead of the view.
 */
function clonarFiltros(origen: FiltrosTablero): FiltrosTablero {
  return {
    metrica: origen.metrica,
    agrupacion: origen.agrupacion,
    unidadNegocio: [...origen.unidadNegocio],
    divisa: [...origen.divisa],
    bucketVenc: [...origen.bucketVenc],
    seriesId: [...origen.seriesId],
    rangoFechas:
      origen.rangoFechas === null
        ? null
        : { desde: origen.rangoFechas.desde, hasta: origen.rangoFechas.hasta },
  }
}

/** Plain deep copy of the provenance block, for the same reason. */
function clonarOrigen(origen: OrigenSerie | null): OrigenSerie | null {
  return origen === null ? null : { ...origen, transformaciones: [...origen.transformaciones] }
}

/**
 * Same value, with the keys of every object sorted.
 *
 * Insertion order is what `JSON.stringify` follows, and it depends on the order
 * the reader clicked things in. Array order is preserved because in an array it
 * carries meaning.
 */
function conClavesOrdenadas(valor: unknown): unknown {
  if (Array.isArray(valor)) {
    return valor.map(conClavesOrdenadas)
  }
  if (valor === null || typeof valor !== 'object') {
    return valor
  }
  const entradas = Object.entries(valor as Record<string, unknown>).sort(([a], [b]) =>
    a < b ? -1 : a > b ? 1 : 0,
  )
  return Object.fromEntries(entradas.map(([clave, dato]) => [clave, conClavesOrdenadas(dato)]))
}

/** Adds or removes a value of a set-like filter, keeping the list canonical. */
function alternarTexto(lista: readonly string[], valor: string): string[] {
  const presente = lista.includes(valor)
  const siguiente = presente ? lista.filter(actual => actual !== valor) : [...lista, valor]
  return siguiente.sort()
}

/** Same, for the numeric series keys. */
function alternarNumero(lista: readonly number[], valor: number): number[] {
  const presente = lista.includes(valor)
  const siguiente = presente ? lista.filter(actual => actual !== valor) : [...lista, valor]
  return siguiente.sort((a, b) => a - b)
}

/** Public surface of the workspace. Contract for US-026 and US-029. */
export interface EstadoWorkspace {
  /** Active filters. Travel to the agent as context on every chat turn. */
  filtros: Ref<FiltrosTablero>
  /** Reading density; drives how many lines the endpoint is asked for. */
  densidad: Ref<DensidadTablero>
  /** Disclosure level: 1 summary, 2 drilled lines, 3 detail table. */
  nivel: Ref<NivelRevelacion>
  /** Visible window as dataZoom percentages. */
  ventana: Ref<VentanaTablero>
  /** Series the reader kept switched on in the legend. */
  seriesVisibles: Ref<number[]>
  /** Last interaction, with its provenance. Read by US-029. */
  ultimaInteraccion: ShallowRef<InteraccionTablero | null>
  /** Provenance of the loaded frame. Written by the composable, not by fetch. */
  origen: ShallowRef<OrigenSerie | null>
  /** True when anything narrows the default view. Drives the "clear" control. */
  hayFiltros: ComputedRef<boolean>
  /** Plain, stable, serialisable snapshot for the agent. */
  contextoAgente: ComputedRef<ContextoAgente>
  aplicarDrillDown: (
    dimension: DimensionDrill,
    valor: string | number | RangoFechas | null,
    origenInteraccion: OrigenInteraccion,
  ) => void
  fijarVentana: (inicio: number, fin: number, origenInteraccion: OrigenInteraccion) => void
  fijarDensidad: (valor: DensidadTablero) => void
  fijarMetrica: (valor: MetricaTablero) => void
  fijarAgrupacion: (valor: AgrupacionTablero) => void
  fijarNivel: (valor: NivelRevelacion) => void
  alternarSerie: (serieId: number) => void
  registrarOrigen: (valor: OrigenSerie) => void
  /** Back to the exact default, in one call. Nothing survives. */
  limpiarFiltros: () => void
  /** Stable JSON with sorted keys; the base of "summarise the current view". */
  serializarVista: () => string
}

export const useWorkspaceStore = defineStore('workspace', (): EstadoWorkspace => {
  const filtros = ref<FiltrosTablero>(filtrosPorOmision())
  const densidad = ref<DensidadTablero>('resumen')
  const nivel = ref<NivelRevelacion>(1)
  const ventana = ref<VentanaTablero>({ ...VENTANA_COMPLETA })
  const seriesVisibles = ref<number[]>([])

  // shallowRef for both: they are replaced whole and never edited in place, so
  // deep reactivity would only buy proxies that then have to be stripped again
  // before the snapshot can be serialised.
  const ultimaInteraccion = shallowRef<InteraccionTablero | null>(null)
  const origen = shallowRef<OrigenSerie | null>(null)

  const hayFiltros = computed<boolean>(() => {
    const actual = filtros.value
    const omision = filtrosPorOmision()
    return (
      actual.metrica !== omision.metrica
      || actual.agrupacion !== omision.agrupacion
      || actual.unidadNegocio.length > 0
      || actual.divisa.length > 0
      || actual.bucketVenc.length > 0
      || actual.seriesId.length > 0
      || actual.rangoFechas !== null
      || ventana.value.inicio !== VENTANA_COMPLETA.inicio
      || ventana.value.fin !== VENTANA_COMPLETA.fin
      || seriesVisibles.value.length > 0
    )
  })

  const contextoAgente = computed<ContextoAgente>(() => ({
    ruta: RUTA_TABLERO,
    filtros: clonarFiltros(filtros.value),
    densidad: densidad.value,
    nivel: nivel.value,
    ventana: { inicio: ventana.value.inicio, fin: ventana.value.fin },
    seriesVisibles: [...seriesVisibles.value],
    origen: clonarOrigen(origen.value),
  }))

  /** Records what the reader did and when, before anything else changes. */
  function anotar(
    dimension: DimensionDrill,
    valor: string | number | RangoFechas | null,
    origenInteraccion: OrigenInteraccion,
  ): void {
    ultimaInteraccion.value = {
      origen: origenInteraccion,
      dimension,
      valor:
        valor !== null && typeof valor === 'object' ? { desde: valor.desde, hasta: valor.hasta } : valor,
      momento: new Date().toISOString(),
    }
  }

  function aplicarDrillDown(
    dimension: DimensionDrill,
    valor: string | number | RangoFechas | null,
    origenInteraccion: OrigenInteraccion,
  ): void {
    const actual = filtros.value

    if (dimension === 'rangoFechas') {
      filtros.value = {
        ...clonarFiltros(actual),
        rangoFechas:
          valor === null || typeof valor !== 'object'
            ? null
            : { desde: valor.desde, hasta: valor.hasta },
      }
    }
    else if (dimension === 'serie') {
      // A drill-down onto one line only means anything if the endpoint is also
      // asked for individual keys, so the grouping moves with it. Otherwise the
      // filter would be sent and the answer would still be five aggregates.
      filtros.value = {
        ...clonarFiltros(actual),
        agrupacion: 'serie',
        seriesId:
          valor === null || typeof valor !== 'number'
            ? []
            : alternarNumero(actual.seriesId, valor),
      }
    }
    else {
      const clave: DimensionDeLista = DIMENSIONES_DE_LISTA[dimension]
      filtros.value = {
        ...clonarFiltros(actual),
        [clave]:
          valor === null || typeof valor !== 'string' ? [] : alternarTexto(actual[clave], valor),
      }
    }

    anotar(dimension, valor, origenInteraccion)

    // Narrowing the view is what moves the reader off the summary rung. Level 3
    // is the detail table and it is opened explicitly, never as a side effect.
    if (nivel.value === 1 && hayFiltros.value) {
      nivel.value = 2
    }
  }

  function fijarVentana(inicio: number, fin: number, origenInteraccion: OrigenInteraccion): void {
    const acotar = (valor: number): number => Math.min(100, Math.max(0, valor))
    const desde = acotar(inicio)
    const hasta = acotar(fin)
    ventana.value = desde <= hasta ? { inicio: desde, fin: hasta } : { inicio: hasta, fin: desde }
    anotar('rangoFechas', null, origenInteraccion)
  }

  function fijarDensidad(valor: DensidadTablero): void {
    densidad.value = valor
    // The selection is expressed in line identifiers of the current view, and
    // the full load regroups by individual key, so the very same number would
    // mean a different line before and after. Clearing is the only reading that
    // cannot be wrong.
    seriesVisibles.value = []
  }

  function fijarMetrica(valor: MetricaTablero): void {
    filtros.value = { ...clonarFiltros(filtros.value), metrica: valor }
  }

  function fijarAgrupacion(valor: AgrupacionTablero): void {
    // Leaving the per key filter behind when the grouping stops being 'serie'
    // would send the endpoint a list of keys it is no longer grouping by, and
    // the answer would silently drop to zero series.
    const siguiente = clonarFiltros(filtros.value)
    filtros.value = {
      ...siguiente,
      agrupacion: valor,
      seriesId: valor === 'serie' ? siguiente.seriesId : [],
    }
    seriesVisibles.value = []
  }

  function fijarNivel(valor: NivelRevelacion): void {
    nivel.value = valor
  }

  function alternarSerie(serieId: number): void {
    seriesVisibles.value = alternarNumero(seriesVisibles.value, serieId)
    anotar('serie', serieId, 'leyenda')
  }

  function registrarOrigen(valor: OrigenSerie): void {
    origen.value = { ...valor, transformaciones: [...valor.transformaciones] }
  }

  function limpiarFiltros(): void {
    filtros.value = filtrosPorOmision()
    densidad.value = 'resumen'
    nivel.value = 1
    ventana.value = { ...VENTANA_COMPLETA }
    seriesVisibles.value = []
    // Clearing is not a drill-down: keeping the last one would let the lineage
    // overlay explain a filter that is no longer on screen.
    ultimaInteraccion.value = null
  }

  function serializarVista(): string {
    return JSON.stringify(conClavesOrdenadas(contextoAgente.value))
  }

  return {
    filtros,
    densidad,
    nivel,
    ventana,
    seriesVisibles,
    ultimaInteraccion,
    origen,
    hayFiltros,
    contextoAgente,
    aplicarDrillDown,
    fijarVentana,
    fijarDensidad,
    fijarMetrica,
    fijarAgrupacion,
    fijarNivel,
    alternarSerie,
    registrarOrigen,
    limpiarFiltros,
    serializarVista,
  }
})
