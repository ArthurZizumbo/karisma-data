<script setup lang="ts">
/**
 * The dashboard panel: controls, chart, legend, summary, table and provenance.
 *
 * It orchestrates and does not decide. The query is the composable's, the
 * statistics and the option are pure functions, the filters live in the store,
 * and what is left here is wiring an event to the call that belongs to it.
 *
 * Two decisions in this file are worth stating because they look like
 * oversights and are not:
 *
 * 1. The option does NOT read the window from the store. Rebuilding it on every
 *    animation frame of a pan would re-materialise every drawn line sixty times
 *    a second, so the window travels imperatively -`dispatchAction`- while the
 *    store is written on the trailing edge for provenance. The window is read
 *    from a plain variable, so the rebuild that a filter change causes still
 *    restores the slice the reader was looking at.
 * 2. There is no "no permission" state here. The route guard renders it in place
 *    of the whole page, so this panel is never mounted for a reader who may not
 *    see it; drawing a second one would be a chart that fires a request the
 *    backend answers with a 403.
 */
import type {
  DimensionDrill,
  EntradaLeyenda,
  FilaTabla,
  OrigenInteraccion,
  VentanaTablero,
} from '~/types/tablero'
import type { PasoGuion } from '~/utils/guionFluidez'
import { useDebounceFn } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { useMedidorFluidez } from '~/composables/useMedidorFluidez'
import { useResumenSerie } from '~/composables/useResumenSerie'
import { useSerieTablero } from '~/composables/useSerieTablero'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { useWorkspaceStore } from '~/stores/workspace'
import SerieControles from '~/components/serie/Controles.vue'
import SerieEstado from '~/components/serie/Estado.vue'
import SerieLeyenda from '~/components/serie/Leyenda.vue'
import SerieMedidor from '~/components/serie/Medidor.vue'
import SerieOrigen from '~/components/serie/Origen.vue'
import SerieResumen from '~/components/serie/Resumen.vue'
import SerieTabla from '~/components/serie/Tabla.vue'
import { CLAVE_AGRUPACION, CLAVE_METRICA } from '~/utils/etiquetasTablero'
import { ANILLO_FOCO } from '~/utils/foco'
import {
  ALTO_GRAFICA,
  construirOpcionSerie,
  identificadorDeLinea,
  indicesColoreados,
} from '~/utils/opcionSerie'
import { colorDeSerie, estiloDeSerie, patronCss } from '~/utils/paletaSeries'
import {
  estadisticasPorSerie,
  fechasDelMarco,
  formatearValor,
  formatearVariacionRelativa,
  variacionRelativa,
} from '~/utils/serieEstadisticas'

/** Id the chart points at through `aria-describedby`. */
const ID_RESUMEN = 'resumen-serie'

const { t, locale } = useI18n()
const ruta = useRoute()
const workspace = useWorkspaceStore()
const sistema = useSistemaDiseno()
const { marco, estado, revalidando, recargar } = useSerieTablero()
const resumen = useResumenSerie(marco)
const { midiendo, informe, medir: ejecutarGuion } = useMedidorFluidez()

const grafica = ref<{ aplicarVentana: (inicio: number, fin: number) => void } | null>(null)

/**
 * Window of the chart, deliberately outside reactivity.
 *
 * Reading it inside the option builder would make every pan rebuild the option,
 * which is the one thing the whole binary transport exists to avoid.
 */
let ventanaActual: VentanaTablero = { ...workspace.ventana }

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

/** Instrumentation is opt in: `?medicion=1` and nothing else shows it. */
const midiendoDisponible = computed(() => ruta.query.medicion === '1')

const opcion = computed(() =>
  marco.value === null
    ? null
    : construirOpcionSerie(marco.value, {
        densidad: workspace.densidad,
        idioma: idioma.value,
        modo: sistema.modo,
        ventana: ventanaActual,
        seriesVisibles: workspace.seriesVisibles,
      }),
)

const estadisticas = computed(() =>
  marco.value === null ? [] : estadisticasPorSerie(marco.value),
)

const fechas = computed(() => (marco.value === null ? [] : fechasDelMarco(marco.value)))

const coloreadas = computed(() =>
  marco.value === null
    ? []
    : indicesColoreados(marco.value, {
        densidad: workspace.densidad,
        seriesVisibles: workspace.seriesVisibles,
      }),
)

const entradasLeyenda = computed<readonly EntradaLeyenda[]>(() => {
  const actual = marco.value
  if (actual === null) {
    return []
  }
  return coloreadas.value.map((indice, posicion) => {
    const estilo = estiloDeSerie(posicion)
    const color = estilo === null ? '' : colorDeSerie(estilo, sistema.modo)
    const entrada = actual.catalogo[indice]
    return {
      indice,
      serieId: entrada?.serieId ?? null,
      etiqueta:
        entrada === undefined ? '' : idioma.value === 'en' ? entrada.labelEn : entrada.labelEs,
      color,
      icono: estilo?.icono ?? 'lucide:circle',
      patron: estilo === null ? '' : patronCss(estilo.trazo, color),
      activa: workspace.seriesVisibles.includes(identificadorDeLinea(actual, indice)),
      coloreada: estilo !== null,
    }
  })
})

const hayApagadas = computed(
  () => marco.value !== null && marco.value.conteo.series > coloreadas.value.length,
)

/** True when the frame holds exactly one line, which is when points are worth listing. */
const unaSolaLinea = computed(() => marco.value !== null && marco.value.conteo.series === 1)

const columnasTabla = computed<readonly string[]>(() =>
  unaSolaLinea.value
    ? [t('dashboard.table.column.date'), t('dashboard.table.column.value')]
    : [
        t('dashboard.table.column.series'),
        t('dashboard.table.column.min'),
        t('dashboard.table.column.max'),
        t('dashboard.table.column.mean'),
        t('dashboard.table.column.last'),
        t('dashboard.table.column.change'),
      ],
)

const filasTabla = computed<readonly FilaTabla[]>(() => {
  const actual = marco.value
  if (actual === null) {
    return []
  }
  const hueco = t('dashboard.table.gap')
  const cifra = (valor: number): string =>
    formatearValor(valor, actual.metrica, idioma.value) ?? hueco

  if (unaSolaLinea.value) {
    const filas: FilaTabla[] = []
    for (let punto = 0; punto < actual.conteo.fechas; punto += 1) {
      filas.push({
        clave: `punto-${punto}`,
        encabezado: fechas.value[punto] ?? '',
        indiceLinea: null,
        identificador: null,
        celdas: [cifra(actual.valores[punto] ?? Number.NaN)],
      })
    }
    return filas
  }

  return estadisticas.value.map((estadistica) => {
    const entrada = actual.catalogo[estadistica.indice]
    return {
      clave: `serie-${estadistica.indice}`,
      encabezado:
        entrada === undefined ? '' : idioma.value === 'en' ? entrada.labelEn : entrada.labelEs,
      indiceLinea: estadistica.indice,
      identificador: identificadorDeLinea(actual, estadistica.indice),
      celdas: [
        cifra(estadistica.minimo),
        cifra(estadistica.maximo),
        cifra(estadistica.media),
        cifra(estadistica.ultimo),
        formatearVariacionRelativa(variacionRelativa(estadistica), idioma.value) ?? hueco,
      ],
    }
  })
})

const pieDeFigura = computed(() => {
  const actual = marco.value
  if (actual === null) {
    return ''
  }
  return t('dashboard.chart.figcaption', {
    metric: t(CLAVE_METRICA[actual.metrica]),
    grouping: t(CLAVE_AGRUPACION[actual.agrupacion]),
    from: actual.fechaMin,
    to: actual.fechaMax,
    lines: actual.conteo.series,
    points: actual.conteo.puntos,
  })
})

const tituloTabla = computed(() => {
  const actual = marco.value
  if (actual === null) {
    return ''
  }
  return t('dashboard.table.caption', {
    metric: t(CLAVE_METRICA[actual.metrica]),
    from: actual.fechaMin,
    to: actual.fechaMax,
  })
})

/** Which dimension a click on a line narrows, given the active grouping. */
function dimensionDeAgrupacion(): DimensionDrill {
  switch (workspace.filtros.agrupacion) {
    case 'divisa':
      return 'divisa'
    case 'bucket_venc':
      return 'bucketVenc'
    case 'serie':
      return 'serie'
    default:
      return 'unidadNegocio'
  }
}

/**
 * A line was activated, from the chart or from the table.
 *
 * The two paths end in the same call on purpose: a drill-down available only
 * with a pointer would leave the main function of this screen out of reach of
 * the keyboard.
 */
function seleccionarLinea(indice: number, origen: OrigenInteraccion): void {
  const actual = marco.value
  if (actual === null) {
    return
  }
  const entrada = actual.catalogo[indice]
  if (entrada === undefined) {
    return
  }
  const dimension = dimensionDeAgrupacion()
  const valor = dimension === 'serie' ? entrada.serieId : entrada.clave
  workspace.aplicarDrillDown(dimension, valor, origen)
}

// Written on the trailing edge: a pan emits a dataZoom event per frame, and one
// store write per frame would be sixty provenance records for one gesture.
const anotarVentana = useDebounceFn((ventana: VentanaTablero) => {
  workspace.fijarVentana(ventana.inicio, ventana.fin, 'grafica')
}, 150)

function alCambiarVentana(ventana: VentanaTablero): void {
  ventanaActual = ventana
  anotarVentana(ventana)
}

function reiniciarZoom(): void {
  ventanaActual = { inicio: 0, fin: 100 }
  grafica.value?.aplicarVentana(0, 100)
  workspace.fijarVentana(0, 100, 'control')
}

function limpiar(): void {
  workspace.limpiarFiltros()
  ventanaActual = { inicio: 0, fin: 100 }
  grafica.value?.aplicarVentana(0, 100)
}

function alternarTabla(): void {
  workspace.fijarNivel(workspace.nivel === 3 ? 2 : 3)
}

function seleccionarFila(fila: FilaTabla): void {
  if (fila.indiceLinea !== null) {
    seleccionarLinea(fila.indiceLinea, 'tabla')
  }
}

async function medir(): Promise<void> {
  await ejecutarGuion((paso: PasoGuion) => {
    grafica.value?.aplicarVentana(paso.inicio, paso.fin)
  })
  // The script ends on the full window; the store is told once, at the end.
  ventanaActual = { inicio: 0, fin: 100 }
  workspace.fijarVentana(0, 100, 'control')
}
</script>

<template>
  <section
    data-zona="serie"
    :data-estado="estado"
    :data-densidad="workspace.densidad"
    class="flex flex-col gap-6"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-corriente-pleno">
        {{ t('dashboard.title') }}
      </h2>
      <p
        v-if="marco !== null"
        data-degradacion
        class="flex max-w-(--medida-maxima) items-start gap-2 text-micro text-corriente-tenue"
      >
        <Icon name="lucide:info" class="mt-0.5 size-3.5 shrink-0 text-aviso" aria-hidden="true" />
        {{ t('dashboard.degradation.notice') }}
      </p>
    </header>

    <SerieControles
      :metrica="workspace.filtros.metrica"
      :agrupacion="workspace.filtros.agrupacion"
      :densidad="workspace.densidad"
      :hay-filtros="workspace.hayFiltros"
      @metrica="workspace.fijarMetrica($event)"
      @agrupacion="workspace.fijarAgrupacion($event)"
      @densidad="workspace.fijarDensidad($event)"
      @limpiar="limpiar"
      @reiniciar-zoom="reiniciarZoom"
    />

    <SerieEstado
      v-if="estado !== 'listo'"
      :estado="estado"
      :alto="ALTO_GRAFICA"
      @reintentar="recargar"
    />

    <template v-if="estado === 'listo' && marco !== null && opcion !== null">
      <!--
        Refiltering is announced without unmounting the chart. `estado` only
        reports the first load -a later filter change keeps the previous frame
        painted- so without this the reader changed the metric and the screen
        said nothing at all while the request was in flight, which is the defect
        measured in the browser. A skeleton here would be worse than silence: it
        would drop the ECharts instance, lose the zoom window and flash a grey
        box over a figure that is about to look almost the same.
      -->
      <figure
        class="relative flex flex-col gap-2"
        :aria-busy="revalidando ? 'true' : undefined"
      >
        <div
          v-if="revalidando"
          data-revalidando
          class="pointer-events-none absolute inset-x-0 top-0 z-10 h-0.5 overflow-hidden rounded-full bg-grid"
        >
          <span class="block h-full w-full animate-pulse rounded-full bg-accion motion-reduce:animate-none" />
        </div>
        <p v-if="revalidando" role="status" class="sr-only">
          {{ t('dashboard.state.refreshing') }}
        </p>
        <LazyVChart
          ref="grafica"
          :opcion="opcion"
          :alto="ALTO_GRAFICA"
          :etiqueta="t('dashboard.chart.ariaLabel')"
          :describe-por="ID_RESUMEN"
          :class="revalidando ? 'opacity-60 transition-opacity' : 'transition-opacity'"
          @serie="seleccionarLinea($event, 'grafica')"
          @ventana="alCambiarVentana"
        />
        <figcaption class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
          {{ pieDeFigura }}
        </figcaption>
      </figure>

      <SerieLeyenda
        :entradas="entradasLeyenda"
        :hay-apagadas="hayApagadas"
        @alternar="workspace.alternarSerie($event.serieId ?? $event.indice)"
      />

      <SerieResumen :id="ID_RESUMEN" :texto="resumen" />

      <div class="flex flex-col gap-2">
        <button
          type="button"
          data-accion="tabla"
          :aria-expanded="workspace.nivel === 3"
          class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
          :class="ANILLO_FOCO"
          @click="alternarTabla"
        >
          <Icon name="lucide:table" class="size-4 shrink-0" aria-hidden="true" />
          {{ workspace.nivel === 3 ? t('dashboard.table.hide') : t('dashboard.table.toggle') }}
        </button>

        <SerieTabla
          v-if="workspace.nivel === 3"
          :titulo="tituloTabla"
          :nota="t('dashboard.table.note')"
          :columnas="columnasTabla"
          :filas="filasTabla"
          @seleccionar="seleccionarFila"
        />
      </div>

      <SerieOrigen :origen="marco.origen" :idioma="idioma" />

      <SerieMedidor
        v-if="midiendoDisponible"
        :midiendo="midiendo"
        :informe="informe"
        @medir="medir"
      />
    </template>
  </section>
</template>
