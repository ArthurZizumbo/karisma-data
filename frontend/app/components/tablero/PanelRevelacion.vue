<script setup lang="ts">
/**
 * US-026, levels 2 and 3 - what one click and two clicks reveal.
 *
 * The panel is rendered at full width UNDER the grid and never inside the card.
 * In a three column grid, expanding inside a cell stretches the whole row and
 * the other two cards change height, which would be a layout shift caused by
 * the very function this User Story delivers.
 *
 * Level 3 is not rendered until it is asked for, with `v-if` and not `v-show`:
 * a node that is in the DOM from the start makes "two clicks" trivially true
 * and simultaneously false, because the reader never saw it. It is also what
 * gives the assertion "before the click it does not exist" something to say.
 *
 * Provenance and disclaimer live here and not in the card. Level 1 answers what
 * the figure is; level 2 answers where it comes from and how it was produced,
 * which is the moment the journey map of A2 marks as the point where a reader
 * decides whether to trust a number.
 */
import type { HistoricoMetrica, MetricaTablero, Proyeccion } from '~/types/prediccion'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { esCodigoIdioma } from '~/composables/useIdioma'
import TableroSerieProyectada from '~/components/tablero/SerieProyectada.vue'
import TableroTablaDetalleSerie from '~/components/tablero/TablaDetalleSerie.vue'
import { ANILLO_FOCO } from '~/utils/foco'
import { formatearMes } from '~/utils/formatoTablero'
import { etiquetaMetodo } from '~/utils/proyeccion'

const props = defineProps<{
  metrica: MetricaTablero
  historico: HistoricoMetrica
  proyeccion: Proyeccion
  /** Id of the card heading that names this region, for aria-labelledby. */
  idTitulo: string
}>()

defineEmits<{ cerrar: [] }>()

const { t, locale } = useI18n()

const region = ref<HTMLElement | null>(null)
const detalleAbierto = ref(false)

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

/** Ids derived from the card id, so the container only has to hand over one. */
const idGrafica = computed(() => `${props.idTitulo}-grafica`)
const idDetalle = computed(() => `${props.idTitulo}-detalle`)

const etiqueta = computed(() =>
  etiquetaMetodo(props.proyeccion.metodo, idioma.value, (clave, parametros) =>
    t(clave, parametros),
  ),
)

// Focus enters the panel it just opened. Without this the reader who pressed
// Enter is left at the top of the page while new content appeared below them.
onMounted(() => {
  region.value?.focus()
})
</script>

<template>
  <section
    ref="region"
    data-nivel="2"
    role="region"
    tabindex="-1"
    :aria-labelledby="props.idTitulo"
    class="flex flex-col gap-4 rounded-lg border border-grid bg-ground-alt p-4"
    @keydown.esc="$emit('cerrar')"
  >
    <header class="flex flex-wrap items-baseline justify-between gap-2">
      <h3 class="font-display text-titulo-2 text-corriente-pleno">
        {{
          t('forecast.projection.title', {
            month: formatearMes(props.proyeccion.proyectado.mes, idioma),
          })
        }}
      </h3>
      <button
        type="button"
        data-accion="cerrar"
        class="inline-flex min-h-11 items-center rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="$emit('cerrar')"
      >
        {{ t('forecast.action.collapse') }}
      </button>
    </header>

    <TableroSerieProyectada
      :metrica="props.metrica"
      :historico="props.historico"
      :proyeccion="props.proyeccion"
      :id-titulo="idGrafica"
    />

    <p data-observado class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
      {{ t('forecast.observed.label', { month: formatearMes(props.proyeccion.ultimo.mes, idioma) }) }}
    </p>

    <dl class="flex flex-col gap-2 text-cuerpo">
      <div class="flex flex-col gap-0.5">
        <dt class="text-etiqueta uppercase text-corriente-tenue">
          {{ t('forecast.source.label') }}
        </dt>
        <dd data-procedencia class="max-w-(--medida-maxima) text-corriente-medio">
          {{
            t('forecast.source.detail', {
              field: props.historico.campoOrigen,
              aggregation: t(props.historico.claveAgregacion),
            })
          }}
        </dd>
      </div>

      <div class="flex flex-col gap-0.5">
        <dt class="text-etiqueta uppercase text-corriente-tenue">
          {{ t('forecast.method.label') }}
        </dt>
        <dd data-metodo class="max-w-(--medida-maxima) text-corriente-medio">
          {{ etiqueta }}
        </dd>
      </div>
    </dl>

    <p
      data-descargo
      data-origen="sintetico"
      class="max-w-(--medida-maxima) border-l-2 border-aviso pl-3 text-micro text-corriente-tenue"
    >
      {{ t('forecast.method.disclaimer') }}
    </p>

    <div class="flex flex-col gap-3">
      <button
        type="button"
        data-accion-revelacion
        data-nivel-destino="3"
        :aria-expanded="detalleAbierto"
        :aria-controls="idDetalle"
        class="inline-flex min-h-11 w-fit items-center rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="detalleAbierto = !detalleAbierto"
      >
        {{ detalleAbierto ? t('forecast.action.hideDetail') : t('forecast.action.detail') }}
      </button>

      <div :id="idDetalle">
        <TableroTablaDetalleSerie
          v-if="detalleAbierto"
          :metrica="props.metrica"
          :historico="props.historico"
          :proyeccion="props.proyeccion"
        />
      </div>
    </div>
  </section>
</template>
