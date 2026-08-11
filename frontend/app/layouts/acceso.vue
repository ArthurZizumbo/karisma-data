<script setup lang="ts">
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-surface font-sans text-ink">
    <CabeceraProducto />

    <FranjaAlcance />

    <main class="flex flex-1 items-start justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <slot />
      </div>
    </main>
  </div>
</template>
