<script setup lang="ts">
import type { EstadoAlcance, Prototipo, RolSugerido } from '~/types/navegacion'

defineProps<{ prototipo: Prototipo }>()

/** Honest scope wording. Nothing here promises data that does not exist yet. */
const ETIQUETA_ALCANCE: Record<EstadoAlcance, string> = {
  'navegable-con-datos': 'Navegable con datos de ejemplo',
  'navegable-sin-datos': 'Navegable sin datos',
  'roadmap': 'En hoja de ruta',
}

const ETIQUETA_ROL: Record<RolSugerido, string> = {
  operativo: 'Perfil operativo',
  analista: 'Perfil analista',
  directivo: 'Perfil directivo',
  administrador: 'Perfil de administración',
}
</script>

<template>
  <NuxtLink
    :to="prototipo.ruta"
    :data-prototipo="prototipo.numero"
    :data-alcance="prototipo.alcance"
    class="flex h-full flex-col gap-2 rounded-lg border border-line bg-surface-alt p-[var(--card-padding)] hover:border-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
  >
    <span class="flex items-center gap-2">
      <span
        class="flex size-7 shrink-0 items-center justify-center rounded-sm bg-primary-dark text-sm text-surface"
        aria-hidden="true"
      >
        {{ prototipo.numero }}
      </span>
      <span class="font-display text-lg text-primary-dark">
        {{ prototipo.numero }}. {{ prototipo.nombre }}
      </span>
    </span>

    <span class="text-sm text-muted">{{ prototipo.ramaA3 }}</span>

    <span class="mt-auto flex flex-wrap items-center gap-2">
      <span class="rounded-sm border border-accent-text px-2 py-0.5 text-sm text-accent-text">
        {{ ETIQUETA_ALCANCE[prototipo.alcance] }}
      </span>
      <span class="rounded-sm border border-line px-2 py-0.5 text-sm text-muted">
        {{ ETIQUETA_ROL[prototipo.rolSugerido] }}
      </span>
    </span>
  </NuxtLink>
</template>
