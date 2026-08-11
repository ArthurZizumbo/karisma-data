<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import BarraLateral from '~/components/nav/BarraLateral.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'

const { t } = useI18n()
</script>

<template>
  <div
    class="flex min-h-screen bg-ground font-sans text-corriente-pleno bg-[linear-gradient(to_right,var(--color-grid)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-grid)_1px,transparent_1px)] bg-size-[24px_24px]"
  >
    <!--
      First focusable element of the document. Without it, a keyboard user walks
      through the ~20 sidebar links on EVERY one of the seven screens before
      reaching the content. It only becomes visible once it receives focus.
    -->
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-corriente-pleno focus:px-4 focus:py-2 focus:text-ground"
    >
      {{ t('chrome.skipToContent') }}
    </a>

    <BarraLateral />

    <div class="flex min-w-0 flex-1 flex-col">
      <!-- The sidebar already names the product, so the header does not. -->
      <CabeceraProducto :con-marca="false" />

      <FranjaAlcance />

      <main id="contenido" class="flex-1 px-4 py-8 md:px-8">
        <slot />
      </main>
    </div>
  </div>
</template>
