<script setup lang="ts">
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { RUTA_INDICE } from '~/utils/navegacion'

const entorno = useRuntimeConfig().public.entorno
</script>

<template>
  <div class="flex min-h-screen flex-col bg-surface font-sans text-ink">
    <header
      class="flex h-[var(--header-height)] shrink-0 items-center justify-between border-b border-line bg-surface-alt px-6"
    >
      <NuxtLink
        :to="RUTA_INDICE"
        class="font-display text-lg text-primary-dark underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
      >
        Karisma Data
      </NuxtLink>
      <span class="rounded-sm border border-line px-2 py-1 text-sm text-muted">
        Entorno: {{ entorno }}
      </span>
    </header>

    <FranjaAlcance />

    <main class="flex flex-1 items-start justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <slot />
      </div>
    </main>
  </div>
</template>
