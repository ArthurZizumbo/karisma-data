<script setup lang="ts">
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-surface font-sans text-ink">
    <CabeceraProducto />

    <FranjaAlcance />

    <main class="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
      <slot />
    </main>
  </div>
</template>
