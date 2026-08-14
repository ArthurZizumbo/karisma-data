<script setup lang="ts">
/**
 * Confirmation of an administrative action, in the platform's own dialog.
 *
 * `<dialog>` with `showModal()` and not a hand written overlay: the browser
 * gives the top layer, the focus trap, `Esc` and the inert background for free.
 * A shared modal component would have been two agents writing the same
 * primitive on the same afternoon, and this one is not shared on purpose.
 *
 * The two tones are a property of the component and not a convention each
 * screen has to remember: disabling an account is drawn as the guide draws a
 * destructive action, and changing a role or re-enabling an account is drawn as
 * an ordinary one. The tone travels to the DOM as `data-tono` so the difference
 * is verifiable instead of asserted.
 *
 * Three things happen here and are the component's own: the cancel button, the
 * `cancel` event -which is what `Esc` produces- and a click that lands on the
 * backdrop. The parent owns `abierto`, so all three report and none of them
 * closes anything by itself: a dialog that closed on its own would leave the
 * screen believing it is open.
 */
import { nextTick, onMounted, ref, useId, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  abierto: boolean
  /** Question, already translated. */
  titulo: string
  /** Consequence of confirming, already translated. */
  cuerpo: string
  /** Label of the confirming button, already translated. */
  etiquetaConfirmar: string
  tono: 'normal' | 'destructivo'
}>()

const emit = defineEmits<{ confirmar: [], cancelar: [] }>()

const { t } = useI18n()

const dialogo = ref<HTMLDialogElement | null>(null)
const botonCancelar = ref<HTMLButtonElement | null>(null)

const idTitulo = useId()
const idCuerpo = useId()

/**
 * The destructive variant of the button plate, copied and not reinvented.
 *
 * An action that cannot be undone with one click has to read as one, and the
 * only definition of that lives in the style guide.
 */
const CONFIRMAR_POR_TONO = Object.freeze({
  normal: 'border border-corriente-pleno bg-corriente-pleno text-ground hover:bg-corriente-medio hover:border-corriente-medio',
  destructivo: 'border border-error text-error hover:bg-error hover:text-ground',
})

/**
 * Opens or closes the element to match the property.
 *
 * @param abierto - Whether the parent wants the dialog on screen.
 */
async function sincronizar(abierto: boolean): Promise<void> {
  const elemento = dialogo.value
  if (elemento === null) {
    return
  }
  if (!abierto) {
    if (elemento.open) {
      elemento.close()
    }
    return
  }
  if (!elemento.open) {
    elemento.showModal()
  }
  await nextTick()
  // Focus lands on the way out, never on the irreversible action: a reader who
  // opened this with the keyboard must not confirm by pressing space.
  botonCancelar.value?.focus()
}

watch(() => props.abierto, sincronizar)

onMounted(() => {
  void sincronizar(props.abierto)
})

/**
 * Reports `Esc`, which the platform delivers as a `cancel` event.
 *
 * The default is prevented so the element does not close behind the parent's
 * back: the parent lowers `abierto` and the watcher above does the closing.
 *
 * @param evento - The `cancel` event of the dialog.
 */
function alCancelarNativo(evento: Event): void {
  evento.preventDefault()
  emit('cancelar')
}

/**
 * Reports a click that landed on the backdrop.
 *
 * Two conditions, because the `<dialog>` is the target of two very different
 * clicks. There is no node for `::backdrop`, so a click outside the card
 * reports the element itself; but the card's own padding is 24 px of visible
 * box that belongs to no child, and a click there reports the element itself
 * too. Comparing only the target closes the dialog on a reader who pressed the
 * inner edge of the very question they were reading, and loses the destructive
 * action they were about to confirm.
 *
 * The geometry alone would not do either, and that is why the target check
 * stays: a button activated with the keyboard produces a click at (0, 0) that
 * bubbles up to this handler, and every point is outside the box when the box
 * is somewhere else on the screen. So the target rules out everything that
 * happened inside the content, and the box rules out what the dialog receives
 * on its own padding. The remaining case -a point outside the box on an element
 * that is the dialog- is the backdrop and nothing else.
 *
 * Moving the padding to the inner `<div>` would make the target comparison
 * exact again and is the other half of this fix; it is not taken because the
 * behaviour would then depend on a class staying where it is, and the next
 * person to restyle the card has no way of knowing that.
 *
 * @param evento - Click received by the dialog.
 */
function alClicFuera(evento: MouseEvent): void {
  const elemento = dialogo.value
  if (elemento === null || evento.target !== elemento) {
    return
  }
  const caja = elemento.getBoundingClientRect()
  const fuera = evento.clientX < caja.left
    || evento.clientX > caja.right
    || evento.clientY < caja.top
    || evento.clientY > caja.bottom
  if (fuera) {
    emit('cancelar')
  }
}
</script>

<template>
  <dialog
    ref="dialogo"
    data-dialogo-confirmacion
    :data-tono="tono"
    :aria-labelledby="idTitulo"
    :aria-describedby="idCuerpo"
    class="w-96 max-w-full rounded-lg border border-grid bg-ground p-6 text-corriente-pleno shadow-dialogo backdrop:bg-corriente-pleno/40"
    @cancel="alCancelarNativo"
    @click="alClicFuera"
  >
    <div class="flex flex-col gap-4">
      <h2 :id="idTitulo" class="text-titulo-2 text-corriente-pleno">
        {{ titulo }}
      </h2>

      <p :id="idCuerpo" class="text-cuerpo text-corriente-medio">
        {{ cuerpo }}
      </p>

      <div class="flex flex-wrap justify-end gap-2">
        <button
          ref="botonCancelar"
          type="button"
          data-accion="cancelar"
          class="inline-flex min-h-11 items-center rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-ground-alt"
          :class="ANILLO_FOCO"
          @click="emit('cancelar')"
        >
          {{ t('admin.users.confirm.cancel') }}
        </button>

        <button
          type="button"
          data-accion="confirmar"
          class="inline-flex min-h-11 items-center gap-2 rounded-md px-3 text-etiqueta"
          :class="[CONFIRMAR_POR_TONO[tono], ANILLO_FOCO]"
          @click="emit('confirmar')"
        >
          <Icon
            v-if="tono === 'destructivo'"
            name="lucide:trash-2"
            class="size-3.5 shrink-0"
            aria-hidden="true"
          />
          {{ etiquetaConfirmar }}
        </button>
      </div>
    </div>
  </dialog>
</template>
