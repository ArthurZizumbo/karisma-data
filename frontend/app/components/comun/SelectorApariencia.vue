<script setup lang="ts">
/**
 * How the portal looks: theme and colour mode, in one control.
 *
 * They used to be two adjacent groups of naked icon buttons -five tab stops,
 * no visible label- and they are the same axis: one says which product this
 * is, the other says whether the room is lit. Split, the chrome charged the
 * reader five controls to answer one question, and the measurement of the
 * design review counted eleven controls in the bar with not a single label.
 *
 * Folded, the bar carries one labelled disclosure and the five options live
 * inside it. Nothing is lost in the process: the two themes and the three
 * modes -including "follow the system", which is the commonest answer and the
 * one a two way switch would have swallowed- are all offered.
 *
 * The preference still travels in `karisma_tema` and `karisma_modo` and is
 * still applied before the first paint: this component only calls the store,
 * which owns both cookies.
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ModoElegido } from '~/composables/useModo'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()
const sistema = useSistemaDiseno()

/** Each mode carries the shape of its own scene, so the three read at a glance. */
const MODOS: readonly { valor: ModoElegido, icono: string }[] = Object.freeze([
  { valor: 'claro', icono: 'lucide:sun' },
  { valor: 'oscuro', icono: 'lucide:moon' },
  { valor: 'sistema', icono: 'lucide:monitor' },
])

/** Each theme carries the shape of its visual world. */
const ICONO_POR_TEMA: Readonly<Record<string, string>> = Object.freeze({
  corriente: 'lucide:circuit-board',
  institucional: 'lucide:landmark',
})

const abierto = ref<boolean>(false)
const contenedor = ref<HTMLElement | null>(null)

/** What the trigger announces: the pair that is actually painted right now. */
const resumen = computed<string>(() =>
  t('appearance.current', {
    theme: t(`theme.names.${sistema.tema}`),
    mode: t(`chrome.mode.${sistema.eleccion}`),
  }),
)

function cerrar(): void {
  abierto.value = false
}

/**
 * A click anywhere else closes the panel.
 *
 * Registered only while the panel is open and removed with it, so the document
 * never carries a listener for a control that is not on screen. Without this
 * the panel stayed open behind the next screen the reader opened.
 */
function alPulsarFuera(evento: MouseEvent): void {
  const raiz = contenedor.value
  if (raiz !== null && !raiz.contains(evento.target as Node)) {
    cerrar()
  }
}

watch(abierto, (estaAbierto) => {
  if (typeof document === 'undefined') {
    return
  }
  if (estaAbierto) {
    document.addEventListener('click', alPulsarFuera)
  }
  else {
    document.removeEventListener('click', alPulsarFuera)
  }
})

onBeforeUnmount(() => {
  if (typeof document !== 'undefined') {
    document.removeEventListener('click', alPulsarFuera)
  }
})
</script>

<template>
  <div
    ref="contenedor"
    data-selector-apariencia
    class="relative"
    @keydown.escape="cerrar"
  >
    <button
      type="button"
      data-apariencia-abrir
      :aria-expanded="abierto"
      aria-haspopup="true"
      :aria-label="resumen"
      :title="resumen"
      class="flex min-h-11 min-w-11 items-center gap-1.5 rounded-md border border-corriente-apagado px-2 text-etiqueta text-corriente-pleno hover:bg-corriente-apagado"
      :class="ANILLO_FOCO"
      @click="abierto = !abierto"
    >
      <Icon name="lucide:palette" class="size-4 shrink-0" aria-hidden="true" />
      <span>{{ t('appearance.label') }}</span>
      <Icon
        :name="abierto ? 'lucide:chevron-up' : 'lucide:chevron-down'"
        class="size-3 shrink-0"
        aria-hidden="true"
      />
    </button>

    <!--
      Anchored to the right edge of its own trigger. The profile switcher of
      the previous chrome was measured at `left: -144.4` on a 390 px viewport
      -outside the canvas, and the bar does not scroll- and every floating
      panel of this header is anchored the same way so that cannot come back.
    -->
    <div
      v-if="abierto"
      data-apariencia-panel
      class="absolute end-0 top-full z-40 mt-1 flex w-56 flex-col gap-3 rounded-lg border border-grid bg-ground p-3 shadow-menu"
    >
      <fieldset class="flex flex-col gap-1">
        <legend class="mb-1 text-micro uppercase tracking-wide text-corriente-tenue">
          {{ t('theme.groupLabel') }}
        </legend>
        <button
          v-for="opcion in sistema.temas"
          :key="opcion"
          type="button"
          :data-tema-opcion="opcion"
          :aria-pressed="sistema.tema === opcion"
          class="flex min-h-11 items-center gap-2 rounded-md px-2 text-etiqueta text-corriente-pleno hover:bg-corriente-apagado aria-pressed:bg-corriente-pleno aria-pressed:text-ground"
          :class="ANILLO_FOCO"
          @click="sistema.fijarTema(opcion)"
        >
          <Icon
            :name="ICONO_POR_TEMA[opcion] ?? 'lucide:palette'"
            class="size-4 shrink-0"
            aria-hidden="true"
          />
          {{ t(`theme.names.${opcion}`) }}
        </button>
      </fieldset>

      <fieldset class="flex flex-col gap-1">
        <legend class="mb-1 text-micro uppercase tracking-wide text-corriente-tenue">
          {{ t('chrome.mode.aria') }}
        </legend>
        <button
          v-for="opcion in MODOS"
          :key="opcion.valor"
          type="button"
          data-selector-modo
          :data-modo-opcion="opcion.valor"
          :aria-pressed="sistema.eleccion === opcion.valor"
          class="flex min-h-11 items-center gap-2 rounded-md px-2 text-etiqueta text-corriente-pleno hover:bg-corriente-apagado aria-pressed:bg-corriente-pleno aria-pressed:text-ground"
          :class="ANILLO_FOCO"
          @click="sistema.elegir(opcion.valor)"
        >
          <Icon :name="opcion.icono" class="size-4 shrink-0" aria-hidden="true" />
          {{ t(`chrome.mode.${opcion.valor}`) }}
        </button>
      </fieldset>
    </div>
  </div>
</template>
