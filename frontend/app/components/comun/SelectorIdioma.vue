<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useIdioma } from '~/composables/useIdioma'
import { ANILLO_FOCO } from '~/utils/foco'

/**
 * Two explicit buttons instead of a select: the whole control is one tab stop
 * away, the active language is announced through aria-pressed and the option
 * that is not active reads as an action, not as a value in a closed list.
 *
 * The two buttons are the last targets of the chrome that measured under 44
 * pixels at 390: their label is two letters, so the size has to be declared and
 * cannot be inherited from the text. `size-11` and not padding, because padding
 * around a two character label does not produce a square.
 */
const { t } = useI18n()
const { idiomaActual, opciones, cambiarIdioma } = useIdioma()
</script>

<template>
  <div
    data-selector-idioma
    role="group"
    :aria-label="t('language.groupLabel')"
    class="flex items-center gap-1 rounded-md border border-grid px-1 py-0.5"
  >
    <Icon
      name="lucide:languages"
      class="size-4 shrink-0 text-corriente-pleno"
      aria-hidden="true"
    />
    <button
      v-for="opcion in opciones"
      :key="opcion.codigo"
      type="button"
      :data-idioma="opcion.codigo"
      :lang="opcion.codigo"
      :aria-pressed="idiomaActual === opcion.codigo"
      :aria-label="idiomaActual === opcion.codigo
        ? t('language.current', { language: opcion.endonimo })
        : t('language.switchTo', { language: opcion.endonimo })"
      class="flex size-11 items-center justify-center rounded-sm text-sm text-corriente-pleno hover:bg-corriente-apagado aria-pressed:bg-corriente-medio aria-pressed:text-ground"
      :class="ANILLO_FOCO"
      @click="cambiarIdioma(opcion.codigo)"
    >
      {{ opcion.abreviatura }}
    </button>
  </div>
</template>
