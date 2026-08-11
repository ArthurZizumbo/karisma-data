<script setup lang="ts">
/**
 * Credential-free entry for the four demonstration profiles.
 *
 * The honesty label is not decoration and not a footnote: it is an acceptance
 * criterion of the User Story, in both languages, and it sits above the buttons
 * because the reader has to know what this door is before using it.
 *
 * The four buttons carry the outline variant on purpose. The screen already has
 * one primary action -entering with a password- and rule 8 of the interface
 * checklist allows exactly one per screen.
 *
 * The role literals are the vocabulary of the backend and travel unchanged as
 * `data-rol`; only their reading name is translated.
 */
import { useI18n } from 'vue-i18n'

import type { RolUsuario } from '~/types/sesion'
import { ANILLO_FOCO } from '~/utils/foco'
import { ROLES } from '~/utils/sesion'

defineProps<{
  /** True while an entry request is in flight; the four buttons rest. */
  deshabilitado: boolean
}>()

const emit = defineEmits<{
  /** The reader chose a profile to enter as. */
  elegir: [RolUsuario]
}>()

const { t } = useI18n()
</script>

<template>
  <section data-demostracion class="flex flex-col gap-3 border-t border-grid pt-5">
    <h2 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:users" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
      {{ t('access.demo.title') }}
    </h2>

    <p class="flex items-start gap-2 text-micro text-aviso">
      <Icon name="lucide:triangle-alert" class="mt-0.5 size-3 shrink-0" aria-hidden="true" />
      {{ t('access.demo.label') }}
    </p>

    <ul class="grid grid-cols-2 gap-2">
      <li v-for="rol in ROLES" :key="rol">
        <button
          :data-rol="rol"
          type="button"
          :disabled="deshabilitado"
          class="flex min-h-9 w-full items-center justify-center border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-ground-alt disabled:border-grid disabled:text-corriente-apagado"
          :class="ANILLO_FOCO"
          @click="emit('elegir', rol)"
        >
          {{ t(`access.demo.roles.${rol}`) }}
        </button>
      </li>
    </ul>
  </section>
</template>
