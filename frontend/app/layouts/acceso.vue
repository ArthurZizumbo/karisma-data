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
      which left the notice 455 px wide against a 1440 px entry screen. Same
      class and same reason in the three layouts that mount it.
    -->
    <FranjaAlcance class="max-w-none" />

    <main class="flex flex-1 items-start justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <slot />
      </div>
    </main>
  </div>
</template>
