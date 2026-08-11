<script setup lang="ts">
import BotonPrototipo from '~/components/nav/BotonPrototipo.vue'
import { PROTOTIPOS, RUTA_INDICE } from '~/utils/navegacion'
</script>

<template>
  <section :data-ruta="RUTA_INDICE" class="flex flex-col gap-6">
    <header class="flex flex-col gap-2">
      <h1 class="font-display text-2xl text-primary-dark">
        Prototipos de alta fidelidad
      </h1>
      <p class="max-w-prose text-muted">
        Siete pantallas del mapa de sitio de la Actividad 3. Cada botón declara su alcance
        y su perfil.
      </p>
    </header>

    <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="prototipo in PROTOTIPOS" :key="prototipo.numero">
        <BotonPrototipo :prototipo="prototipo" />
      </li>
    </ul>
  </section>
</template>
