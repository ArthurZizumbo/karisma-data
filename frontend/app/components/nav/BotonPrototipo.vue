<script setup lang="ts">
/**
 * Entry to one of the seven high fidelity prototypes.
 *
 * Rebuilt in the diagram world: the number is a node, the branch of the A3 map
 * is the connector it hangs from, and the scope reads as a state on the current
 * ramp rather than as two coloured pills. The measured version wrapped every
 * entry in a card with the same border weight as everything else on the page,
 * which is what made the index read as a grid of identical boxes.
 *
 * The scope wording is load bearing and not decoration: the A4 rubric asks for
 * a three state scope table, and a prototype that claims data it does not have
 * costs more than one that declares itself empty.
 */
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

/** Scope on the luminance ramp: lit means live, dim means declared. */
const TONO_ALCANCE: Record<EstadoAlcance, string> = {
  'navegable-con-datos': 'text-corriente-pleno',
  'navegable-sin-datos': 'text-corriente-tenue',
  'roadmap': 'text-corriente-apagado',
}

const CLAVE_ROL: Record<RolSugerido, string> = {
  operativo: 'prototype.profile.operations',
  analista: 'prototype.profile.analyst',
  directivo: 'prototype.profile.executive',
  admin: 'prototype.profile.administration',
}
</script>

<template>
  <NuxtLink
    :to="prototipo.ruta"
    :data-prototipo="prototipo.numero"
    :data-alcance="prototipo.alcance"
    class="group flex h-full items-start gap-3 border-t border-grid py-3 hover:border-corriente-medio"
    :class="ANILLO_FOCO"
  >
    <span
      class="mt-0.5 flex size-6 shrink-0 items-center justify-center border border-corriente-medio font-mono text-micro text-corriente-pleno group-hover:bg-corriente-pleno group-hover:text-ground"
      aria-hidden="true"
    >
      {{ prototipo.numero }}
    </span>

    <span class="flex min-w-0 flex-col gap-0.5">
      <span class="text-titulo-3 text-corriente-pleno">
        {{ t(prototipo.claveNombre) }}
      </span>
      <span class="text-cuerpo text-corriente-tenue">{{ t(prototipo.claveRama) }}</span>
      <span class="mt-1 flex flex-wrap items-center gap-x-3 text-micro">
        <span :class="TONO_ALCANCE[prototipo.alcance]">
          {{ t(CLAVE_ALCANCE[prototipo.alcance]) }}
        </span>
        <span class="text-corriente-tenue">{{ t(CLAVE_ROL[prototipo.rolSugerido]) }}</span>
      </span>
    </span>
  </NuxtLink>
</template>
