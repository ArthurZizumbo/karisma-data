<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'

/**
 * Chassis of the entry screen.
 *
 * Same chassis as the portal, without navigation: nobody has a session yet, so
 * the sidebar would offer four doors that all answer the same refusal. Ground,
 * modular grid, skip link, header and scope band are the portal ones, so the
 * reader crosses into the product without the frame changing under them.
 */
const { t } = useI18n()
</script>

<template>
  <div
    class="flex min-h-screen flex-col bg-ground font-sans text-corriente-pleno bg-[linear-gradient(to_right,var(--color-reticula)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-reticula)_1px,transparent_1px)] bg-size-[24px_24px]"
  >
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-corriente-pleno focus:px-4 focus:py-2 focus:text-ground"
    >
      {{ t('chrome.skipToContent') }}
    </a>

    <CabeceraProducto />

    <!--
      `max-w-none` keeps the scope notice a full width band: `FranjaAlcance`
      renders a `<p>` and the system caps prose at `--medida-maxima` (68ch),
      which left the notice 455 px wide against a 1440 px entry screen. Same
      class and same reason in the three layouts that mount it.
    -->
    <FranjaAlcance class="max-w-none" />

    <main id="contenido" class="flex flex-1 items-start justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <slot />
      </div>
    </main>
  </div>
</template>
