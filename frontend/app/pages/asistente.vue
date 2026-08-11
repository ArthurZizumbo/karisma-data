<script setup lang="ts">
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { titulo, ruta } = useTituloDeRuta()
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-2">
    <h1 class="font-display text-2xl text-primary-dark">
      {{ titulo }}
    </h1>
    <p class="max-w-prose text-muted">
      Contendrá la conversación con el agente, las tarjetas de cada consulta que ejecuta y el
      detalle de linaje de la respuesta.
    </p>
  </section>
</template>
