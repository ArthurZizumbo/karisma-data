<script setup lang="ts">
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-ground font-sans text-corriente-pleno">
    <CabeceraProducto />

    <!--
      `max-w-none` keeps the scope notice a full width band: `FranjaAlcance`
      renders a `<p>` and the system caps prose at `--medida-maxima` (68ch),
      which left the notice 455 px wide over a 1440 px viewport. The band is
      deliberately wider than the `max-w-6xl` content column below it: it
      declares the scope of the whole screen, not of the article.
    -->
    <FranjaAlcance class="max-w-none" />

    <main class="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
      <slot />
    </main>
  </div>
</template>
