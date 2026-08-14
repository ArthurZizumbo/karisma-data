<script setup lang="ts">
/**
 * The export history, with its four states.
 *
 * It renders one `TarjetaTrabajo` per `job_id` and nothing else: the link and
 * its deadline are drawn where the job is drawn, so the list and the moment
 * cannot disagree about whether a file can still be downloaded.
 *
 * The empty state is a sentence and not an absence. A heading over nothing
 * reads as a list that failed to load, and this screen has a real empty case:
 * an analyst who has not exported anything yet.
 */
import type { EstadoHistorial, TrabajoVigilado } from '~/types/exportacion'
import { useI18n } from 'vue-i18n'
import TarjetaTrabajo from '~/components/exportacion/TarjetaTrabajo.vue'
import { ANILLO_FOCO } from '~/utils/foco'

defineProps<{
  /** Jobs of the caller, newest first. */
  trabajos: readonly TrabajoVigilado[]
  /** State of the history request, decided by the store. */
  estado: EstadoHistorial
  /** Row the current moment expands, or null when none is expanded. */
  destacadoId: string | null
}>()

const emit = defineEmits<{
  /** The reader asked to open or close a row. Carries the job id. */
  alternar: [string]
  /** The reader asked to load the history again after a failure. */
  reintentar: []
}>()

const { t } = useI18n()

/** Skeleton rows drawn while the first load is in flight. */
const ESQUELETO = [0, 1, 2]
</script>

<template>
  <section data-historial :data-estado="estado" class="flex flex-col gap-3">
    <h2 class="font-display text-titulo-2 text-corriente-pleno">
      {{ t('export.history.title') }}
    </h2>

    <div v-if="estado === 'cargando'" aria-busy="true" class="flex flex-col gap-2">
      <span
        v-for="fila in ESQUELETO"
        :key="fila"
        data-esqueleto
        class="h-16 w-full animate-pulse bg-ground-alt"
      />
    </div>

    <div
      v-else-if="estado === 'error'"
      role="alert"
      class="flex flex-col items-start gap-2 border-l-2 border-error pl-4"
    >
      <p class="flex items-start gap-2 text-cuerpo text-corriente-medio">
        <Icon
          name="lucide:circle-alert"
          class="mt-0.5 size-4 shrink-0 text-error"
          aria-hidden="true"
        />
        {{ t('export.history.error') }}
      </p>
      <button
        data-accion="reintentar"
        type="button"
        class="flex min-h-9 items-center gap-2 border border-corriente-medio px-4 text-cuerpo text-corriente-pleno hover:bg-ground-alt"
        :class="ANILLO_FOCO"
        @click="emit('reintentar')"
      >
        <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('export.history.retry') }}
      </button>
    </div>

    <p
      v-else-if="estado === 'vacio'"
      data-vacio="historial"
      class="max-w-(--medida-maxima) border-l-2 border-corriente-apagado pl-4 text-cuerpo text-corriente-tenue"
    >
      {{ t('export.history.empty') }}
    </p>

    <ul v-else class="flex flex-col gap-2">
      <li v-for="trabajo in trabajos" :key="trabajo.job_id">
        <TarjetaTrabajo
          :trabajo="trabajo"
          :expandido="trabajo.job_id === destacadoId"
          @alternar="emit('alternar', $event)"
        />
      </li>
    </ul>
  </section>
</template>
