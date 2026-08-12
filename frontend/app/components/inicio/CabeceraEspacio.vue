<script setup lang="ts">
/**
 * Greeting of a workspace: who is signed in and why this layout is theirs.
 *
 * It exists as its own component because the three compositions would otherwise
 * repeat the same eight lines, and the day the greeting changes it would change
 * in two of the three. It is also the piece that makes the three figures of the
 * report self-explanatory: without the sentence, a reader looking at three
 * screenshots sees three arrangements and no reason for them.
 *
 * While the session resolves, the greeting keeps its line and shows a bar of
 * the same height. Hiding the paragraph instead would move everything below it
 * the moment the name arrived.
 */
import type { ClaveComposicion } from '~/types/espacios'
import type { RolUsuario } from '~/types/sesion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  /** Composition this greeting introduces. */
  composicion: ClaveComposicion
  /** Display name of the reader, empty while unknown. */
  nombre: string
  /** Role of the session, null while unknown. */
  rol: RolUsuario | null
  /** True while the session has not resolved yet. */
  cargando: boolean
}>()

const { t } = useI18n()

/** The name is only printed once there is one; never "Hola, ". */
const conNombre = computed(() => !props.cargando && props.nombre !== '')
</script>

<template>
  <div data-cabecera-espacio class="flex flex-col gap-1">
    <div class="flex flex-wrap items-center gap-3">
      <p class="font-display text-titulo-2 text-corriente-pleno">
        <span
          v-if="!conNombre"
          class="inline-block h-4 w-48 bg-ground-alt align-middle"
          aria-hidden="true"
        />
        <template v-else>{{ t('workspace.greeting', { name: nombre }) }}</template>
      </p>
      <span
        v-if="rol"
        data-rol-actual
        class="border border-grid px-1.5 text-etiqueta uppercase text-corriente-tenue"
      >
        {{ t(`authz.role.${rol}`) }}
      </span>
    </div>

    <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
      {{ t(`workspace.intro.${composicion}`) }}
    </p>

    <span v-if="cargando" class="sr-only" role="status">{{ t('workspace.loading') }}</span>
  </div>
</template>
