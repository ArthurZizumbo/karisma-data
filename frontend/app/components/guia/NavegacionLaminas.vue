<script setup lang="ts">
/**
 * Persistent navigation of the guide, with the current plate lit.
 *
 * Two defects the design review measured, and they are the same one. The index
 * was a flat list at the top of a document nearly 6000 pixels tall: it scrolled
 * away, so past the first viewport there was no navigation at all, and it never
 * said which plate the reader was on. Nielsen's first heuristic, visibility of
 * system status, scored 2 of 4 for exactly this.
 *
 * The current plate is marked on the luminance ramp rather than with a colour:
 * lit is where you are, dim is where you are not. It is the same channel the
 * rest of the system uses for state, and the one no dichromacy loses.
 *
 * `IntersectionObserver` rather than a scroll listener: a listener runs on every
 * frame and the project bans it. The top margin biases the observer so that a
 * plate counts as current once its heading reaches the upper third, which is
 * where a reader is actually looking.
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** The plates, in the order the page renders them. */
  laminas: readonly { id: string, clave: string }[]
}>()

const { t } = useI18n()

const actual = ref<string>(props.laminas[0]?.id ?? '')
let observador: IntersectionObserver | undefined

/**
 * Recompute the current plate from the position of every section.
 *
 * A first version took the first *intersecting* entry, and a tall plate still
 * touching the observation band won over the one the reader had just reached:
 * scrolling to the cards plate marked the tables plate. Reading all positions is
 * deterministic and does not depend on which entries the observer happened to
 * report on a given callback.
 */
function recalcular(): void {
  const umbral = window.innerHeight * 0.25
  let elegida = props.laminas[0]?.id ?? ''
  for (const lamina of props.laminas) {
    const nodo = document.getElementById(`lamina-${lamina.id}`)
    if (nodo !== null && nodo.getBoundingClientRect().top <= umbral) {
      elegida = lamina.id
    }
  }
  actual.value = elegida
}

onMounted(() => {
  // The observer is the trigger, never the source of the answer: it fires only
  // when a boundary is crossed, which is cheaper than a scroll listener and is
  // what the project bans one in favour of.
  observador = new IntersectionObserver(recalcular, {
    threshold: [0, 0.25, 0.5, 0.75, 1],
  })
  for (const lamina of props.laminas) {
    const nodo = document.getElementById(`lamina-${lamina.id}`)
    if (nodo !== null) observador.observe(nodo)
  }

  // With smooth scrolling the observer fires while the animation is still in
  // flight and then stops, because the settled position crosses no further
  // boundary: the mark stayed one plate behind on every jump. `scrollend` fires
  // once when the scroll comes to rest, so it is not the per-frame listener the
  // project bans.
  window.addEventListener('scrollend', recalcular)
  recalcular()
})

onBeforeUnmount(() => {
  observador?.disconnect()
  window.removeEventListener('scrollend', recalcular)
})
</script>

<template>
  <nav
    data-navegacion-laminas
    :aria-label="t('guide.index.aria')"
    class="sticky top-0 z-10 -mx-4 border-b border-grid bg-ground px-4 py-2 md:-mx-8 md:px-8"
  >
    <ul class="flex flex-wrap gap-x-4 gap-y-1">
      <li v-for="lamina in laminas" :key="lamina.id">
        <a
          :href="`#lamina-${lamina.id}`"
          :data-indice-lamina="lamina.id"
          :aria-current="actual === lamina.id ? 'true' : undefined"
          class="inline-flex items-center gap-1.5 text-etiqueta text-corriente-tenue hover:text-corriente-pleno aria-[current]:font-semibold aria-[current]:text-corriente-pleno"
          :class="ANILLO_FOCO"
        >
          <!-- The node of the diagram: lit where you are, dim where you are not. -->
          <span
            class="size-1.5 rounded-full"
            :class="actual === lamina.id ? 'bg-corriente-pleno' : 'bg-corriente-apagado'"
            aria-hidden="true"
          />
          {{ t(lamina.clave) }}
        </a>
      </li>
    </ul>
  </nav>
</template>
