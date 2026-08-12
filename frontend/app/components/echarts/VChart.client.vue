<script setup lang="ts">
/**
 * The only file of the repository that imports `vue-echarts` or ECharts itself.
 *
 * Everything ECharts specific stops here: the modular registration, the shape of
 * its events and the imperative call that moves the window. The panel above
 * receives a normalised `ventana` and a series index, and would not have to
 * change if the chart library did.
 *
 * The registration is modular and never the barrel. Importing the package root
 * pulls every chart type and every component into the bundle -maps, graphs,
 * gauges, none of which this portal draws- and the acceptance criterion measures
 * the absence of that import with a grep over the whole application, so this
 * comment does not spell it out either.
 *
 * The `.client` suffix keeps ECharts out of the server render, where there is no
 * canvas to draw on, and the `Lazy` form the panel uses keeps it out of the
 * initial bundle.
 */
import type { VentanaTablero } from '~/types/tablero'
import type { OpcionTablero } from '~/utils/opcionSerie'
import { LineChart } from 'echarts/charts'
import { DataZoomComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { shallowRef } from 'vue'
import VueECharts from 'vue-echarts'

/**
 * The five modules this chart needs, and not one more.
 *
 * There is no `LegendComponent` on purpose: the legend is HTML, rendered by
 * `SerieLeyenda`, because an ECharts legend is painted into the canvas and a
 * canvas legend cannot be reached by the keyboard, cannot be read by a screen
 * reader and cannot carry the marker shape next to a translated label.
 */
use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer])

const props = defineProps<{
  /** Option built by `construirOpcionSerie`. */
  opcion: OpcionTablero
  /** Reserved height, shared with the skeleton so nothing shifts on load. */
  alto: string
  /** What a screen reader announces before the description. */
  etiqueta: string
  /** Id of the node holding the textual summary of this chart. */
  describePor: string
}>()

const emit = defineEmits<{
  /** A line was activated; the index is the position within the frame. */
  serie: [indice: number]
  /** The visible window changed, already normalised to percentages. */
  ventana: [ventana: VentanaTablero]
}>()

const grafica = shallowRef<InstanceType<typeof VueECharts> | null>(null)

/** Shape of the click payload this component cares about. */
interface EventoClic {
  seriesIndex?: number
}

/** Shape of the dataZoom payload, in both of the forms ECharts emits it. */
interface EventoZoom {
  start?: number
  end?: number
  batch?: { start?: number, end?: number }[]
}

function alHacerClic(parametros: unknown): void {
  const indice = (parametros as EventoClic | null)?.seriesIndex
  if (typeof indice === 'number') {
    emit('serie', indice)
  }
}

function alCambiarZoom(parametros: unknown): void {
  const evento = parametros as EventoZoom | null
  const primero = evento?.batch?.[0]
  const inicio = primero?.start ?? evento?.start
  const fin = primero?.end ?? evento?.end
  if (typeof inicio === 'number' && typeof fin === 'number') {
    emit('ventana', { inicio, fin })
  }
}

/**
 * Moves the window without rebuilding the option.
 *
 * This is why the meter is imperative. Rebuilding the option on every animation
 * frame would re-materialise 250 lines per frame, so the measurement would be
 * measuring the option builder instead of the renderer.
 */
function aplicarVentana(inicio: number, fin: number): void {
  grafica.value?.dispatchAction({ type: 'dataZoom', start: inicio, end: fin })
}

defineExpose({ aplicarVentana })
</script>

<template>
  <div
    role="img"
    :aria-label="props.etiqueta"
    :aria-describedby="props.describePor"
    :style="{ height: props.alto }"
    class="w-full"
  >
    <VueECharts
      ref="grafica"
      :option="props.opcion"
      :autoresize="true"
      class="h-full w-full"
      @click="alHacerClic"
      @datazoom="alCambiarZoom"
    />
  </div>
</template>
