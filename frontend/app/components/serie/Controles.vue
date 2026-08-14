<script setup lang="ts">
/**
 * Metric, grouping, density and the two window actions.
 *
 * Buttons in a labelled group rather than a `select`, for the same reason the
 * language switcher uses them: every option is visible without opening
 * anything, `aria-pressed` states which one is active, and the whole control is
 * reachable with the keyboard alone, which is the way the drill-down has to be
 * available if it is to be available at all.
 *
 * The component decides nothing. It receives the current values and emits the
 * requested ones; what a density means for the query lives in the composable.
 */
import type { AgrupacionTablero, DensidadTablero, MetricaTablero } from '~/types/tablero'
import { useI18n } from 'vue-i18n'
import {
  AGRUPACIONES,
  CLAVE_AGRUPACION,
  CLAVE_DENSIDAD,
  CLAVE_METRICA,
  DENSIDADES,
  METRICAS,
} from '~/utils/etiquetasTablero'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  metrica: MetricaTablero
  agrupacion: AgrupacionTablero
  densidad: DensidadTablero
  /** True when something narrows the default view, so "clear" is offered. */
  hayFiltros: boolean
}>()

defineEmits<{
  metrica: [valor: MetricaTablero]
  agrupacion: [valor: AgrupacionTablero]
  densidad: [valor: DensidadTablero]
  limpiar: []
  reiniciarZoom: []
}>()

const { t } = useI18n()

/** Classes of one option button, active or not. */
function clases(activo: boolean): string {
  return activo
    ? 'border-corriente-pleno bg-corriente-pleno text-ground'
    : 'border-corriente-apagado text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno'
}
</script>

<template>
  <div class="flex flex-wrap items-end gap-6">
    <fieldset data-control="metrica" class="flex flex-col gap-1">
      <legend class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('dashboard.metric.label') }}
      </legend>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="valor in METRICAS"
          :key="valor"
          type="button"
          :data-opcion="valor"
          :aria-pressed="valor === props.metrica"
          class="min-h-11 rounded-md border px-3 text-etiqueta"
          :class="[clases(valor === props.metrica), ANILLO_FOCO]"
          @click="$emit('metrica', valor)"
        >
          {{ t(CLAVE_METRICA[valor]) }}
        </button>
      </div>
    </fieldset>

    <fieldset data-control="agrupacion" class="flex flex-col gap-1">
      <legend class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('dashboard.grouping.label') }}
      </legend>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="valor in AGRUPACIONES"
          :key="valor"
          type="button"
          :data-opcion="valor"
          :aria-pressed="valor === props.agrupacion"
          class="min-h-11 rounded-md border px-3 text-etiqueta"
          :class="[clases(valor === props.agrupacion), ANILLO_FOCO]"
          @click="$emit('agrupacion', valor)"
        >
          {{ t(CLAVE_AGRUPACION[valor]) }}
        </button>
      </div>
    </fieldset>

    <fieldset data-control="densidad" class="flex flex-col gap-1">
      <legend class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('dashboard.density.label') }}
      </legend>
      <div class="flex flex-wrap gap-1">
        <button
          v-for="valor in DENSIDADES"
          :key="valor"
          type="button"
          :data-opcion="valor"
          :aria-pressed="valor === props.densidad"
          :title="valor === 'completa' ? t('dashboard.density.fullHint') : undefined"
          class="min-h-11 rounded-md border px-3 text-etiqueta"
          :class="[clases(valor === props.densidad), ANILLO_FOCO]"
          @click="$emit('densidad', valor)"
        >
          {{ t(CLAVE_DENSIDAD[valor]) }}
        </button>
      </div>
    </fieldset>

    <div class="flex gap-1">
      <button
        type="button"
        data-accion="reiniciar-zoom"
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="$emit('reiniciarZoom')"
      >
        <Icon name="lucide:maximize" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('dashboard.zoom.reset') }}
      </button>

      <button
        v-if="props.hayFiltros"
        type="button"
        data-accion="limpiar"
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="$emit('limpiar')"
      >
        <Icon name="lucide:filter-x" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('dashboard.drill.clear') }}
      </button>
    </div>
  </div>
</template>
