<script setup lang="ts">
/**
 * US-026 - the predictive block of zone C of screen 2.
 *
 * It composes and it does not decide. The request, the validation and the
 * projection belong to `usePrediccionesTablero`; the arithmetic belongs to
 * `utils/proyeccion`; what is left here is the grid, which card is open, and
 * the four states.
 *
 * The grid renders one card per entry of `METRICAS_PREDICCION` and never one per element
 * of the response, so the number of cards is the same while loading, when it is
 * ready, when a metric is missing and when the request failed. That is the
 * structural half of "no layout shift"; the other half is inside the card.
 *
 * Only one card can be open at a time and the panel lives at full width under
 * the grid, so revealing never stretches a row and never moves the other two
 * cards. The open card is a local `ref` and not a Pinia store: what is open is
 * local to one subtree of one screen, and an event nobody listens to would be
 * scaffolding. The S5 hook - carrying the open metric into the assistant
 * context - is written in the handoff, not coded here.
 */
import type { MetricaId } from '~/types/prediccion'
import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import TableroPanelRevelacion from '~/components/tablero/PanelRevelacion.vue'
import TableroTarjetaPredictiva from '~/components/tablero/TarjetaPredictiva.vue'
import { usePrediccionesTablero } from '~/composables/usePrediccionesTablero'
import { ANILLO_FOCO } from '~/utils/foco'

/** Id of the single panel every card points at through aria-controls. */
const ID_PANEL = 'panel-prediccion'

const { t } = useI18n()
const { tarjetas, cargando, hayError, estadoDe, recargar } = usePrediccionesTablero()

const raiz = ref<HTMLElement | null>(null)
const abierta = ref<MetricaId | null>(null)

/** Heading id of a card, which is what names the panel it opens. */
function idTituloDe(metricaId: MetricaId): string {
  return `tarjeta-prediccion-${metricaId}`
}

/**
 * Card currently revealed, or null.
 *
 * Derived and not stored: if a reload leaves the open metric without a
 * projection, the panel closes on its own instead of rendering against a value
 * that is no longer there.
 */
const tarjetaAbierta = computed(() => {
  const encontrada = tarjetas.value.find(tarjeta => tarjeta.metrica.id === abierta.value)
  if (encontrada === undefined || encontrada.historico === null || encontrada.proyeccion === null) {
    return null
  }
  return encontrada
})

const estadoSeccion = computed(() => {
  if (cargando.value) {
    return 'cargando'
  }
  return hayError.value ? 'error' : 'listo'
})

function alternar(metricaId: MetricaId): void {
  abierta.value = abierta.value === metricaId ? null : metricaId
}

/**
 * Closes the panel and gives the focus back to the button that opened it.
 *
 * Without the second half, closing with Escape would drop the reader at the top
 * of the document, which is the classic way a disclosure pattern becomes
 * unusable with a keyboard alone.
 */
async function cerrar(): Promise<void> {
  const metricaId = abierta.value
  abierta.value = null
  await nextTick()
  raiz.value
    ?.querySelector<HTMLElement>(`[data-tarjeta="${metricaId}"] [data-accion-revelacion]`)
    ?.focus()
}
</script>

<template>
  <section
    ref="raiz"
    data-zona="predicciones"
    :data-estado="estadoSeccion"
    class="flex flex-col gap-4"
  >
    <header class="flex flex-col gap-1">
      <div class="flex flex-wrap items-baseline gap-3">
        <h2 class="font-display text-titulo-2 text-corriente-pleno">
          {{ t('forecast.section.title') }}
        </h2>
        <span
          data-origen="sintetico"
          class="rounded-full border border-aviso px-2 text-micro text-aviso"
        >
          {{ t('forecast.sample.badge') }}
        </span>
      </div>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-tenue">
        {{ t('forecast.section.description') }}
      </p>
    </header>

    <p v-if="cargando" role="status" class="sr-only">
      {{ t('forecast.state.loading') }}
    </p>

    <div
      v-if="hayError"
      data-error
      class="flex max-w-(--medida-maxima) flex-col gap-2 border-l-2 border-error pl-5"
    >
      <h3 class="flex items-start gap-2 font-display text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:triangle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
        {{ t('forecast.state.errorTitle') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('forecast.state.errorHint') }}
      </p>
      <button
        type="button"
        data-reintentar
        class="inline-flex min-h-11 w-fit items-center rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="recargar"
      >
        {{ t('forecast.action.retry') }}
      </button>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <TableroTarjetaPredictiva
        v-for="tarjeta in tarjetas"
        :key="tarjeta.metrica.id"
        :metrica="tarjeta.metrica"
        :proyeccion="tarjeta.proyeccion"
        :estado="estadoDe(tarjeta)"
        :abierta="abierta === tarjeta.metrica.id"
        :id-titulo="idTituloDe(tarjeta.metrica.id)"
        :id-panel="ID_PANEL"
        @alternar="alternar"
      />
    </div>

    <div :id="ID_PANEL">
      <TableroPanelRevelacion
        v-if="tarjetaAbierta !== null"
        :key="tarjetaAbierta.metrica.id"
        :metrica="tarjetaAbierta.metrica"
        :historico="tarjetaAbierta.historico!"
        :proyeccion="tarjetaAbierta.proyeccion!"
        :id-titulo="idTituloDe(tarjetaAbierta.metrica.id)"
        @cerrar="cerrar"
      />
    </div>
  </section>
</template>
