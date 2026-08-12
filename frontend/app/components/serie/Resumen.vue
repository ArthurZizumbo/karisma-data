<script setup lang="ts">
/**
 * The textual summary of the chart, always visible.
 *
 * Always visible and not hidden behind `sr-only`, which was the tempting
 * alternative: a sentence that states the period, the number of lines, the
 * highest one and where its extremes fall is useful to everybody, and a text
 * only one technology can reach is a text nobody proofreads.
 *
 * The chart points at this node through `aria-describedby`, which is why the id
 * is a property and not a literal: two charts on one screen would otherwise
 * describe themselves with the same paragraph.
 */
const props = defineProps<{
  /** Sentence already assembled by `useResumenSerie`, in the active language. */
  texto: string
  /** Id the chart references. */
  id: string
}>()
</script>

<template>
  <p
    :id="props.id"
    data-resumen
    class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio"
  >
    {{ props.texto }}
  </p>
</template>
