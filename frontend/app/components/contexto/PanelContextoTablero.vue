<script setup lang="ts">
/**
 * What the dashboard would send to the assistant, shown before it is sent.
 *
 * The workspace store is read and never written: this panel has no action that
 * changes the view, and that is the agreed degradation of this delivery -the
 * filters travel as context, the agent does not move the dashboard-. Saying it
 * in a comment is not enough, so the notice is rendered on screen in both
 * languages whenever there is context, and an acceptance criterion greps this
 * directory for every write action of the store.
 *
 * Three rungs, two clicks: the chips answer "what is on the dashboard right
 * now" with no click at all, the first disclosure answers "where did this come
 * from" and the second shows the exact text that would travel. The raw JSON is
 * not an interface string and therefore is not in the catalogues: they are
 * identifiers of the agent contract, the same way a metric code is data.
 */
import type { CodigoIdioma } from '~/composables/useIdioma'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import SerieOrigen from '~/components/serie/Origen.vue'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { RUTA_TABLERO, useWorkspaceStore } from '~/stores/workspace'
import { CLAVE_AGRUPACION, CLAVE_DENSIDAD, CLAVE_METRICA } from '~/utils/etiquetasTablero'
import { ANILLO_FOCO } from '~/utils/foco'

const { t, locale } = useI18n()
const espacio = useWorkspaceStore()

const idioma = computed<CodigoIdioma>(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

/** Whether each disclosure is open. Controlled so the body renders only then. */
const interaccionAbierta = ref(false)
const payloadAbierto = ref(false)

/** One chip of the active context. */
interface ChipContexto {
  clave: string
  etiqueta: string
  valor: string
}

/** Catalogue key of the label of each dimension. */
const CLAVE_DIMENSION: Record<string, string> = {
  unidadNegocio: 'sharedContext.chip.businessUnit',
  divisa: 'sharedContext.chip.currency',
  bucketVenc: 'sharedContext.chip.maturityBucket',
  serie: 'sharedContext.chip.series',
  rangoFechas: 'sharedContext.chip.dateRange',
}

/** Catalogue key of the control the reader used. */
const CLAVE_INTERACCION: Record<string, string> = {
  grafica: 'sharedContext.interaction.grafica',
  tabla: 'sharedContext.interaction.tabla',
  leyenda: 'sharedContext.interaction.leyenda',
  control: 'sharedContext.interaction.control',
}

const hayContexto = computed(() => espacio.hayFiltros)

/**
 * The chips of the current view.
 *
 * A dimension with nothing in it produces no chip: painting the default values
 * as if they were choices would tell the reader they narrowed something they
 * never touched.
 */
const chips = computed<ChipContexto[]>(() => {
  const contexto = espacio.contextoAgente
  const filtros = contexto.filtros
  const lista: ChipContexto[] = [
    { clave: 'metric', etiqueta: t('sharedContext.chip.metric'), valor: t(CLAVE_METRICA[filtros.metrica]) },
    { clave: 'grouping', etiqueta: t('sharedContext.chip.grouping'), valor: t(CLAVE_AGRUPACION[filtros.agrupacion]) },
  ]

  if (filtros.unidadNegocio.length > 0) {
    lista.push({ clave: 'businessUnit', etiqueta: t('sharedContext.chip.businessUnit'), valor: filtros.unidadNegocio.join(', ') })
  }
  if (filtros.divisa.length > 0) {
    lista.push({ clave: 'currency', etiqueta: t('sharedContext.chip.currency'), valor: filtros.divisa.join(', ') })
  }
  if (filtros.bucketVenc.length > 0) {
    lista.push({ clave: 'maturityBucket', etiqueta: t('sharedContext.chip.maturityBucket'), valor: filtros.bucketVenc.join(', ') })
  }
  if (filtros.seriesId.length > 0) {
    lista.push({ clave: 'series', etiqueta: t('sharedContext.chip.series'), valor: filtros.seriesId.join(', ') })
  }
  if (filtros.rangoFechas !== null) {
    lista.push({
      clave: 'dateRange',
      etiqueta: t('sharedContext.chip.dateRange'),
      valor: t('sharedContext.value.dateRange', {
        from: filtros.rangoFechas.desde,
        to: filtros.rangoFechas.hasta,
      }),
    })
  }
  if (contexto.ventana.inicio !== 0 || contexto.ventana.fin !== 100) {
    lista.push({
      clave: 'window',
      etiqueta: t('sharedContext.chip.window'),
      valor: t('sharedContext.value.window', {
        start: contexto.ventana.inicio,
        end: contexto.ventana.fin,
      }),
    })
  }

  lista.push({ clave: 'density', etiqueta: t('sharedContext.chip.density'), valor: t(CLAVE_DENSIDAD[contexto.densidad]) })
  lista.push({ clave: 'level', etiqueta: t('sharedContext.chip.level'), valor: String(contexto.nivel) })

  if (contexto.seriesVisibles.length > 0) {
    lista.push({
      clave: 'visibleSeries',
      etiqueta: t('sharedContext.chip.visibleSeries'),
      valor: String(contexto.seriesVisibles.length),
    })
  }

  return lista
})

const interaccion = computed(() => espacio.ultimaInteraccion)
const origen = computed(() => espacio.origen)

/**
 * The exact text that would accompany the question.
 *
 * Taken from the store and never rebuilt here: a second serialisation of the
 * same state diverges the first time a key is added, and then the panel would
 * be showing something that is not what travels.
 */
const payload = computed(() => espacio.serializarVista())
</script>

<template>
  <section data-contexto-tablero class="flex flex-col gap-4">
    <header class="flex flex-col gap-1">
      <h2 class="flex items-center gap-2 font-display text-titulo-2 text-corriente-pleno">
        <Icon name="lucide:gauge" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('sharedContext.title') }}
      </h2>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('sharedContext.hint') }}
      </p>
    </header>

    <div v-if="!hayContexto" data-estado="sin-contexto" class="flex flex-col gap-2 border-l-2 border-grid pl-5">
      <h3 class="text-titulo-3 text-corriente-pleno">
        {{ t('sharedContext.empty.title') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('sharedContext.empty.hint') }}
      </p>
      <NuxtLink
        data-abrir-tablero
        :to="RUTA_TABLERO"
        class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
      >
        {{ t('sharedContext.empty.action') }}
      </NuxtLink>
    </div>

    <template v-else>
      <ul data-estado="con-contexto" class="flex flex-wrap gap-2">
        <li
          v-for="chip in chips"
          :key="chip.clave"
          data-chip-contexto
          :data-dimension="chip.clave"
          class="flex items-baseline gap-1.5 rounded-sm border border-grid px-2 py-1 text-micro"
        >
          <span class="text-corriente-tenue">{{ chip.etiqueta }}</span>
          <span class="text-corriente-pleno">{{ chip.valor }}</span>
        </li>
      </ul>

      <!--
        The one sided arrow is written on screen, not only in the plan: an
        interface that shows a context block without saying it travels in a
        single direction lets the reader believe the assistant can move the
        dashboard back, which in this delivery it cannot.
      -->
      <p data-aviso-estatico class="flex items-start gap-2 border-l-2 border-info pl-4 text-micro text-corriente-tenue">
        <Icon name="lucide:info" class="mt-0.5 size-3.5 shrink-0 text-info" aria-hidden="true" />
        {{ t('sharedContext.static.notice') }}
      </p>

      <details data-detalle-interaccion :open="interaccionAbierta" class="border-t border-grid pt-3">
        <summary
          class="w-fit cursor-pointer rounded-sm text-etiqueta text-corriente-medio"
          :class="ANILLO_FOCO"
          @click.prevent="interaccionAbierta = !interaccionAbierta"
        >
          {{ t('sharedContext.details.lastInteraction') }}
        </summary>

        <div v-if="interaccionAbierta" class="mt-2 flex flex-col gap-3">
          <dl v-if="interaccion !== null" data-ultima-interaccion class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-micro">
            <dt class="text-corriente-tenue">
              {{ t('sharedContext.details.provenance') }}
            </dt>
            <dd class="text-corriente-pleno">
              {{ t(CLAVE_INTERACCION[interaccion.origen] ?? 'sharedContext.interaction.control') }}
            </dd>
            <dt class="text-corriente-tenue">
              {{ t('sharedContext.details.dimension') }}
            </dt>
            <dd class="text-corriente-pleno">
              {{ t(CLAVE_DIMENSION[interaccion.dimension] ?? 'sharedContext.chip.series') }}
            </dd>
            <dt class="text-corriente-tenue">
              {{ t('sharedContext.details.value') }}
            </dt>
            <dd class="text-corriente-pleno">
              {{ interaccion.valor === null ? '-' : String(interaccion.valor) }}
            </dd>
            <dt class="text-corriente-tenue">
              {{ t('sharedContext.details.moment') }}
            </dt>
            <dd class="font-mono text-corriente-pleno">
              {{ interaccion.momento }}
            </dd>
          </dl>

          <SerieOrigen v-if="origen !== null" :origen="origen" :idioma="idioma" />
        </div>
      </details>

      <details data-payload-estatico :open="payloadAbierto" class="border-t border-grid pt-3">
        <summary
          class="w-fit cursor-pointer rounded-sm text-etiqueta text-corriente-medio"
          :class="ANILLO_FOCO"
          @click.prevent="payloadAbierto = !payloadAbierto"
        >
          {{ t('sharedContext.details.payload') }}
        </summary>

        <div v-if="payloadAbierto" class="mt-2 flex flex-col gap-2">
          <p class="text-micro text-corriente-tenue">
            {{ t('sharedContext.details.payloadHint') }}
          </p>
          <pre class="overflow-x-auto rounded-md bg-ground-alt p-3 font-mono text-micro text-corriente-pleno">{{ payload }}</pre>
        </div>
      </details>
    </template>
  </section>
</template>
