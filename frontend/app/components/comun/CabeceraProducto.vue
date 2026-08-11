<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectorIdioma from '~/components/comun/SelectorIdioma.vue'
import { ANILLO_FOCO } from '~/utils/foco'
import { RUTA_INDICE } from '~/utils/navegacion'

/**
 * Product header shared by the four chromes of the prototype.
 *
 * The three layouts had each grown their own header, and the language selector
 * ended up mounted in two of them: an English speaking evaluator opened the
 * prototype index -the first screen, framed by the `default` layout- and found
 * no way to leave Spanish, because `detectBrowserLanguage` is off and the
 * selector is the only route to English. The header is a single component so
 * that the next control added to it cannot reach three surfaces and miss the
 * fourth.
 *
 * The environment chip is ink and not the muted neutral: over `surface-alt`
 * the muted neutral measures 4.27:1, below the 4.5:1 that normal text needs.
 */
withDefaults(defineProps<{
  /** The portal names the product in its sidebar, so its header omits it. */
  conMarca?: boolean
}>(), { conMarca: true })

const { t } = useI18n()
const entorno = useRuntimeConfig().public.entorno
</script>

<template>
  <header
    data-cabecera-producto
    class="flex h-[var(--header-height)] shrink-0 items-center gap-3 border-b border-line bg-surface-alt px-6"
    :class="conMarca ? 'justify-between' : 'justify-end'"
  >
    <NuxtLink
      v-if="conMarca"
      :to="RUTA_INDICE"
      class="font-display text-lg text-primary-dark underline-offset-4 hover:underline"
      :class="ANILLO_FOCO"
    >
      {{ t('brand.name') }}
    </NuxtLink>

    <div class="flex items-center gap-3">
      <SelectorIdioma />
      <span class="rounded-sm border border-line px-2 py-1 text-sm text-ink">
        {{ t('chrome.environment', { environment: entorno }) }}
      </span>
    </div>
  </header>
</template>
