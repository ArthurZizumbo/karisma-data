<script setup lang="ts">
/**
 * Light and dark mode control.
 *
 * Three states and not a two-way switch: following the operating system is a
 * real option and the commonest one, so hiding it behind a toggle would force a
 * choice the reader did not want to make.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'
import { useModo, type ModoElegido } from '~/composables/useModo'

const { t } = useI18n()
const { eleccion, elegir } = useModo()

const OPCIONES: readonly { valor: ModoElegido, icono: string }[] = [
  { valor: 'claro', icono: 'lucide:sun' },
  { valor: 'oscuro', icono: 'lucide:moon' },
  { valor: 'sistema', icono: 'lucide:monitor' },
]
</script>

<template>
  <div
    class="flex items-center rounded-md border border-corriente-apagado"
    role="group"
    :aria-label="t('chrome.mode.aria')"
  >
    <Icon
      name="lucide:contrast"
      class="ml-2 size-4 shrink-0 text-corriente-tenue"
      aria-hidden="true"
    />
    <button
      v-for="opcion in OPCIONES"
      :key="opcion.valor"
      type="button"
      data-selector-modo
      :aria-pressed="eleccion === opcion.valor"
      :title="t(`chrome.mode.${opcion.valor}`)"
      class="flex items-center gap-1 px-2 py-1 text-etiqueta text-corriente-tenue aria-pressed:bg-corriente-pleno aria-pressed:text-ground"
      :class="ANILLO_FOCO"
      @click="elegir(opcion.valor)"
    >
      <Icon :name="opcion.icono" class="size-4 shrink-0" aria-hidden="true" />
      <span class="sr-only">{{ t(`chrome.mode.${opcion.valor}`) }}</span>
    </button>
  </div>
</template>
