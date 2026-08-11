<script setup lang="ts">
import BarraLateral from '~/components/nav/BarraLateral.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'

const entorno = useRuntimeConfig().public.entorno
</script>

<template>
  <div class="flex min-h-screen bg-surface font-sans text-ink">
    <!--
      First focusable element of the document. Without it, a keyboard user walks
      through the ~20 sidebar links on EVERY one of the seven screens before
      reaching the content. It only becomes visible once it receives focus.
    -->
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-surface"
    >
      Saltar al contenido
    </a>

    <BarraLateral />

    <div class="flex min-w-0 flex-1 flex-col">
      <header
        class="flex h-[var(--header-height)] shrink-0 items-center justify-end border-b border-line bg-surface-alt px-6"
      >
        <span class="rounded-sm border border-line px-2 py-1 text-sm text-muted">
          Entorno: {{ entorno }}
        </span>
      </header>

      <FranjaAlcance />

      <main id="contenido" class="flex-1 px-6 py-8">
        <slot />
      </main>
    </div>
  </div>
</template>
