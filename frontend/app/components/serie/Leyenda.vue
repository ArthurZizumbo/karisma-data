<script setup lang="ts">
/**
 * The legend, in HTML, with the three channels of every line.
 *
 * Colour, marker shape and stroke pattern, side by side: about one reader in
 * twelve cannot separate two of these six hues, and every figure of the A4
 * document is printed in one ink. A legend that only carried colour would
 * satisfy the criterion by name and fail it in the hands of the reader.
 *
 * Each entry is a real button. That is what makes the drill-down of the chart
 * reachable without a pointer, which is the accessible half of the interaction.
 */
import type { EntradaLeyenda } from '~/types/tablero'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  entradas: readonly EntradaLeyenda[]
  /** True when the view holds more lines than the palette can colour. */
  hayApagadas: boolean
}>()

defineEmits<{ alternar: [entrada: EntradaLeyenda] }>()

const { t } = useI18n()
</script>

<template>
  <section data-leyenda class="flex flex-col gap-2">
    <h3 class="text-etiqueta uppercase text-corriente-tenue">
      {{ t('dashboard.legend.title') }}
    </h3>

    <ul class="flex flex-wrap gap-2">
      <li v-for="entrada in props.entradas" :key="entrada.indice">
        <button
          type="button"
          data-leyenda-item
          :data-serie-id="entrada.serieId ?? entrada.indice"
          :aria-pressed="entrada.activa"
          :aria-label="`${entrada.etiqueta}. ${t('dashboard.legend.toggleHint')}`"
          class="flex min-h-11 items-center gap-2 rounded-md border px-2 text-cuerpo"
          :class="[
            entrada.activa
              ? 'border-corriente-medio text-corriente-pleno'
              : 'border-corriente-apagado text-corriente-tenue',
            ANILLO_FOCO,
          ]"
          @click="$emit('alternar', entrada)"
        >
          <Icon
            :name="entrada.icono"
            class="size-3.5 shrink-0"
            :style="{ color: entrada.color }"
            aria-hidden="true"
          />
          <span
            class="h-0.5 w-8 shrink-0"
            :style="{ backgroundImage: entrada.patron }"
            aria-hidden="true"
          />
          {{ entrada.etiqueta }}
        </button>
      </li>
    </ul>

    <p v-if="props.hayApagadas" data-leyenda-nota class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('dashboard.legend.muted') }}
    </p>
  </section>
</template>
