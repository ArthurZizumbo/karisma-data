<script setup lang="ts">
/**
 * Designed state for a screen whose content arrives in a later User Story.
 *
 * This is not a placeholder in the lazy sense: it is one of the four unhappy
 * states, and it is the one the A4 scope table needs. The alternative -leaving
 * a title over an empty page- reads as a screen that failed to load, which is
 * exactly the reading the deliverable cannot afford. Naming the User Story that
 * delivers it turns "unfinished" into "scheduled", and it is honest either way.
 *
 * The layout is the diagram: a dim rule with nodes tapping off it, one per
 * capability, drawn at the dimmest rung of the current ramp because none of
 * them is live yet. When the story lands, the node lights.
 */
import { useI18n } from 'vue-i18n'

defineProps<{
  /** Capabilities this screen will hold, already translated. */
  capacidades: readonly string[]
  /** Identifier of the User Story that delivers them, e.g. "US-027". */
  us: string
}>()

const { t } = useI18n()
</script>

<template>
  <section data-pendiente class="flex flex-col gap-3">
    <p class="flex items-center gap-2 text-etiqueta uppercase text-corriente-tenue">
      <Icon name="lucide:circle-dashed" class="size-3.5 shrink-0" aria-hidden="true" />
      {{ t('screen.pending.heading', { us }) }}
    </p>

    <ul class="ml-1 flex flex-col border-l border-corriente-apagado">
      <li
        v-for="capacidad in capacidades"
        :key="capacidad"
        data-capacidad
        class="relative py-1.5 pl-5 text-cuerpo text-corriente-tenue"
      >
        <span
          class="absolute left-0 top-1/2 h-px w-3 bg-corriente-apagado"
          aria-hidden="true"
        />
        {{ capacidad }}
      </li>
    </ul>

    <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('screen.pending.note') }}
    </p>
  </section>
</template>
