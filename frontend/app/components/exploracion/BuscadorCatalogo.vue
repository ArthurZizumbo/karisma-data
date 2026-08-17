<script setup lang="ts">
/**
 * Keyword box of the catalogue screen, branch 2.1 of the A3 map.
 *
 * The box holds a draft and the draft is not the query: typing is not
 * searching. The request leaves on submit, which is what keeps the endpoint
 * from answering a 422 to every keystroke against its two character minimum,
 * and what lets the screen open on a designed initial state instead of on a
 * spinner nobody asked for.
 *
 * Nothing here ever clears the box. An answer that failed has to leave the
 * words the reader typed on screen, because retyping them is the cost the
 * error state exists to avoid.
 *
 * The box is seeded from the term the screen is actually searching with, which
 * is what makes a cold open on `?q=saldo` a screen and not a contradiction: the
 * results answer a question the box would otherwise not be showing.
 *
 * The action is the primary one of this screen. It used to be an outline button
 * on a screen with no primary at all, so the one thing the catalogue exists to
 * do carried less weight than the links beside it.
 */
import { computed, ref, useId, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { MINIMO_TERMINO } from '~/composables/useBusquedaCatalogo'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** True while a search is in flight, so the control says so and locks. */
  cargando: boolean
  /** Term the screen is searching with, which the box has to be showing. */
  termino?: string
}>()

const emit = defineEmits<{ buscar: [termino: string] }>()

const { t } = useI18n()

const idCampo = useId()

/** What the box holds. It becomes the query only when the form is submitted. */
const borrador = ref(props.termino ?? '')

// The term can change without anybody typing: it arrives in the address from
// the header search box and from the Back button.
watch(
  () => props.termino,
  (siguiente) => {
    borrador.value = siguiente ?? ''
  },
)

/** Shorter than the minimum the endpoint accepts: no request may leave. */
const suficiente = computed(() => borrador.value.trim().length >= MINIMO_TERMINO)

function enviar(): void {
  if (!suficiente.value) {
    return
  }
  emit('buscar', borrador.value)
}
</script>

<template>
  <form data-buscador-catalogo class="flex flex-col gap-1" @submit.prevent="enviar">
    <label :for="idCampo" class="text-etiqueta uppercase text-corriente-tenue">
      {{ t('catalog.explore.search.label') }}
    </label>

    <div class="flex flex-wrap items-stretch gap-2">
      <div class="relative flex min-w-64 flex-1 items-center">
        <Icon
          name="lucide:search"
          class="pointer-events-none absolute left-3 size-4 shrink-0 text-corriente-tenue"
          aria-hidden="true"
        />
        <input
          :id="idCampo"
          v-model="borrador"
          data-campo-busqueda
          type="search"
          :placeholder="t('catalog.explore.search.placeholder')"
          class="min-h-11 w-full border border-corriente-medio bg-ground pl-9 pr-3 text-cuerpo text-corriente-pleno placeholder:text-corriente-tenue"
          :class="ANILLO_FOCO"
        >
      </div>

      <button
        type="submit"
        data-accion-busqueda
        :disabled="!suficiente || cargando"
        class="flex min-h-11 items-center gap-2 border border-accion bg-accion px-4 text-etiqueta text-ground hover:border-accion-apoyo hover:bg-accion-apoyo disabled:border-grid disabled:bg-ground-alt disabled:text-corriente-apagado"
        :class="ANILLO_FOCO"
      >
        <Icon
          v-if="cargando"
          name="lucide:loader-circle"
          class="size-4 shrink-0 animate-spin motion-reduce:animate-none"
          aria-hidden="true"
        />
        {{ cargando ? t('catalog.explore.search.busy') : t('catalog.explore.search.action') }}
      </button>
    </div>

    <p class="text-micro text-corriente-tenue">
      {{ t('catalog.explore.search.hint', { min: MINIMO_TERMINO }) }}
    </p>
  </form>
</template>
