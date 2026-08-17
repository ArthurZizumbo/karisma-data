<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'

/**
 * Chassis of the screens that carry no navigation: the prototype index.
 *
 * It is the same chassis as the portal minus the sidebar -same ground, same
 * modular grid read from `--color-reticula`, same skip link, same header and
 * same scope band- because two chassis would be two products, and the theme is
 * supposed to be the only thing that changes between them.
 */
const { t } = useI18n()
</script>

<template>
  <div
    class="flex min-h-screen flex-col bg-ground font-sans text-corriente-pleno bg-[linear-gradient(to_right,var(--color-reticula)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-reticula)_1px,transparent_1px)] bg-size-[24px_24px]"
  >
    <!--
      First focusable element of the document, exactly as in the portal: the
      header carries six controls before the content starts, and a keyboard
      reader should not have to walk them on every screen.
    -->
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
      which left the notice 455 px wide over a 1440 px viewport. The band is
      deliberately wider than the `max-w-6xl` content column below it: it
      declares the scope of the whole screen, not of the article.
    -->
    <FranjaAlcance class="max-w-none" />

    <main id="contenido" class="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
      <slot />
    </main>
  </div>
</template>
