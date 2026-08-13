<script setup lang="ts">
/**
 * The overlay primitive of the governance screen (US-029).
 *
 * A native `<dialog>` opened with `showModal()`, which is the shared decision
 * of the two overlays of this sprint: the platform gives the top layer, the
 * scrim as `::backdrop`, the inert background and the `cancel` event, so
 * nothing here manages a z-index against the fixed sidebar and nothing has to
 * be teleported. The explicit focus cycle lives in `useFocoAtrapado`, which is
 * what makes the four accessibility criteria verifiable.
 *
 * It holds no lineage logic on purpose. It knows how to open, how to close and
 * where focus goes; what it shows arrives through the slots.
 *
 * Two shapes and one DOM: below 768 px it is a bottom sheet at 80 dvh, and from
 * `sm:` up a right side panel. A full screen dialog reads as a NAVIGATION -the
 * reader loses the screen behind and starts looking for a way back-, which is
 * exactly what the criterion "it does not alter the reading flow" forbids.
 *
 * The three resets are not decoration: `<dialog>` ships `margin: auto`,
 * `width: fit-content` and a `max-width` of its own, so without `m-0`,
 * `w-full` and `max-w-none` the sheet renders centred and narrow. And the unit
 * is `dvh` and not `vh`: on a phone the browser bar retracts, `vh` measures the
 * large viewport and the sheet gets cut exactly where the close button is.
 *
 * Nothing touches `document.body`. Blocking the scroll with `overflow: hidden`
 * removes the scrollbar on the desktop, reflows the content behind and leaves
 * the screen different from how it was found; `showModal()` already prevents
 * any interaction with the background, so the manual block buys nothing and
 * breaks the criterion.
 */
import { computed, ref, useId } from 'vue'
import { useFocoAtrapado } from '~/composables/useFocoAtrapado'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  abierto: boolean
  /** Accessible name of the dialog. Rendered in the heading that takes focus. */
  titulo: string
  /** Visible label of the close control. Text, never an icon. */
  etiquetaCerrar: string
}>()

const emit = defineEmits<{ cerrar: [] }>()

const idTitulo = useId()
const panel = ref<HTMLElement | null>(null)
const encabezado = ref<HTMLElement | null>(null)

const abierto = computed(() => props.abierto)

useFocoAtrapado({
  abierto,
  panel,
  titulo: encabezado,
  alCerrar: () => emit('cerrar'),
})
</script>

<template>
  <dialog
    ref="panel"
    data-linaje-overlay
    :aria-labelledby="idTitulo"
    class="m-0 mt-auto max-h-[80dvh] w-full max-w-none overscroll-contain rounded-t-lg bg-ground text-corriente-pleno shadow-dialogo backdrop:bg-ground-alt/80 sm:ml-auto sm:mt-0 sm:h-full sm:max-h-none sm:w-[28rem] sm:rounded-none sm:rounded-l-lg"
    :class="[
      // Only opacity and transform are animated, per the motion inventory:
      // width, height, top and left force a layout recalculation and the panel
      // would jump. 240 ms is the duration the style guide reserves for exactly
      // this overlay, and `motion-safe` is what makes prefers-reduced-motion
      // switch it off without a hand written media query.
      'translate-y-6 opacity-0 open:translate-y-0 open:opacity-100 sm:translate-x-6 sm:translate-y-0 sm:open:translate-x-0',
      'motion-safe:transition-[opacity,transform,overlay,display] motion-safe:transition-discrete motion-safe:duration-240 motion-safe:ease-out',
    ]"
  >
    <div data-panel class="flex h-full flex-col gap-4 p-(--panel-padding)">
      <header class="flex flex-col gap-3">
        <div class="flex items-start justify-between gap-4">
          <h2
            :id="idTitulo"
            ref="encabezado"
            tabindex="-1"
            class="font-display text-titulo-2 text-corriente-pleno"
          >
            {{ props.titulo }}
          </h2>

          <!--
            Text and not an icon, and that is a decision with a verified cause:
            `lucide:x` is not in the packaged inventory, and an icon resolved
            through the Iconify API renders empty in the production image, which
            is the one the deliverable captures. Text also clears the 44 x 44
            touch target and removes the obligation of an aria-label.
          -->
          <button
            type="button"
            data-cerrar-linaje
            class="min-h-11 shrink-0 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
            :class="ANILLO_FOCO"
            @click="emit('cerrar')"
          >
            {{ props.etiquetaCerrar }}
          </button>
        </div>

        <slot name="encabezado" />
      </header>

      <div class="min-h-0 flex-1 overflow-y-auto">
        <slot />
      </div>
    </div>
  </dialog>
</template>
