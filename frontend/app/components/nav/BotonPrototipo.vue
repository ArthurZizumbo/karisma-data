<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { EstadoAlcance, Prototipo, RolSugerido } from '~/types/navegacion'
import { ANILLO_FOCO } from '~/utils/foco'

defineProps<{ prototipo: Prototipo }>()

const { t } = useI18n()

/** Honest scope wording. Nothing here promises data that does not exist yet. */
const CLAVE_ALCANCE: Record<EstadoAlcance, string> = {
  'navegable-con-datos': 'prototype.scope.withData',
  'navegable-sin-datos': 'prototype.scope.withoutData',
  'roadmap': 'prototype.scope.roadmap',
}

const CLAVE_ROL: Record<RolSugerido, string> = {
  operativo: 'prototype.profile.operations',
  analista: 'prototype.profile.analyst',
  directivo: 'prototype.profile.executive',
  administrador: 'prototype.profile.administration',
}
</script>

<template>
  <NuxtLink
    :to="prototipo.ruta"
    :data-prototipo="prototipo.numero"
    :data-alcance="prototipo.alcance"
    class="flex h-full flex-col gap-2 rounded-lg border border-line bg-surface-alt p-[var(--card-padding)] hover:border-primary"
    :class="ANILLO_FOCO"
  >
    <span class="flex items-center gap-2">
      <span
        class="flex size-7 shrink-0 items-center justify-center rounded-sm bg-primary-dark text-sm text-surface"
        aria-hidden="true"
      >
        {{ prototipo.numero }}
      </span>
      <span class="font-display text-lg text-primary-dark">
        {{ prototipo.numero }}. {{ t(prototipo.claveNombre) }}
      </span>
    </span>

    <span class="text-sm text-ink">{{ t(prototipo.claveRama) }}</span>

    <span class="mt-auto flex flex-wrap items-center gap-2">
      <span class="rounded-sm border border-accent-text px-2 py-0.5 text-sm text-accent-text">
        {{ t(CLAVE_ALCANCE[prototipo.alcance]) }}
      </span>
      <span class="rounded-sm border border-line px-2 py-0.5 text-sm text-ink">
        {{ t(CLAVE_ROL[prototipo.rolSugerido]) }}
      </span>
    </span>
  </NuxtLink>
</template>
