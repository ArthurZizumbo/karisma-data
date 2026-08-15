<script setup lang="ts">
/**
 * Visual theme control.
 *
 * Two explicit buttons and not a toggle: the two themes are peers -neither
 * replaces the other- and a switch would name only one of them, leaving the
 * reader to guess what the other side is.
 *
 * Each theme is named after its own visual world and never after a number or an
 * author: the default one is the man-machine line diagram the system declares,
 * and the optional one is the institutional palette of the design file.
 */
import { useI18n } from 'vue-i18n'
import type { TemaPortal } from '~/composables/useTema'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()
const sistema = useSistemaDiseno()

/** Each theme carries the shape of its world, so the pair reads without text. */
const ICONO_POR_TEMA: Readonly<Record<TemaPortal, string>> = {
  corriente: 'lucide:circuit-board',
  institucional: 'lucide:landmark',
}
</script>

<template>
  <div
    data-selector-tema
    role="group"
    :aria-label="t('theme.groupLabel')"
    class="flex items-center rounded-md border border-corriente-apagado"
  >
    <Icon
      name="lucide:palette"
      class="ml-2 size-4 shrink-0 text-corriente-tenue"
      aria-hidden="true"
    />
    <button
      v-for="opcion in sistema.temas"
      :key="opcion"
      type="button"
      :data-tema-opcion="opcion"
      :aria-pressed="sistema.tema === opcion"
      :aria-label="sistema.tema === opcion
        ? t('theme.current', { theme: t(`theme.names.${opcion}`) })
        : t('theme.switchTo', { theme: t(`theme.names.${opcion}`) })"
      :title="t(`theme.names.${opcion}`)"
      class="flex items-center gap-1 px-2 py-1 text-etiqueta text-corriente-tenue aria-pressed:bg-corriente-pleno aria-pressed:text-ground"
      :class="ANILLO_FOCO"
      @click="sistema.fijarTema(opcion)"
    >
      <Icon :name="ICONO_POR_TEMA[opcion]" class="size-4 shrink-0" aria-hidden="true" />
      <span class="sr-only">{{ t(`theme.names.${opcion}`) }}</span>
    </button>
  </div>
</template>
