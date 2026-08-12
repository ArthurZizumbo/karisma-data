<script setup lang="ts">
/**
 * The states of the panel that are not the happy one.
 *
 * Three of the four live here -loading, empty and failed- plus the seeded data
 * that is missing, which is the first screen anyone who clones the repository
 * sees and therefore gets the same care as the happy path. The fourth, the
 * closed door, is not here and must not be: the route guard renders it in place
 * of the whole page, so the panel is never mounted for a reader who may not see
 * it. Drawing a second one here would be a chart that fires a request the
 * backend answers with a 403.
 *
 * The skeleton reserves the exact height of the chart. Two different heights is
 * how a layout shift appears the moment the data lands, and that is measured.
 */
import type { EstadoTablero } from '~/types/tablero'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /**
   * Which state to draw.
   *
   * The panel only mounts this component when the state is not 'listo', which is
   * its own content. The type stays the full union because narrowing a `v-if`
   * across a component boundary is not something the template checker can do,
   * and a cast at the call site would be a lie that outlives the reason for it.
   */
  estado: EstadoTablero
  /** Reserved height of the chart area, from `ALTO_GRAFICA`. */
  alto: string
}>()

defineEmits<{ reintentar: [] }>()

const { t } = useI18n()
</script>

<template>
  <div :data-estado="props.estado" class="flex flex-col gap-3">
    <div
      v-if="props.estado === 'cargando'"
      role="status"
      aria-busy="true"
      :style="{ height: props.alto }"
      class="flex w-full items-end gap-1 rounded-lg border border-grid bg-ground-alt p-4"
    >
      <span class="sr-only">{{ t('dashboard.state.loading') }}</span>
      <!--
        Bars of a plausible chart rather than a spinner: the reader sees the
        shape of what is coming, and the block occupies exactly the space the
        chart will, so nothing below it moves when the data arrives.
      -->
      <span
        v-for="barra in 24"
        :key="barra"
        aria-hidden="true"
        class="flex-1 animate-pulse rounded-sm bg-grid"
        :style="{ height: `${20 + ((barra * 37) % 70)}%` }"
      />
    </div>

    <div
      v-else
      class="flex max-w-(--medida-maxima) flex-col gap-2 border-l-2 pl-5"
      :class="props.estado === 'error' ? 'border-error' : 'border-aviso'"
    >
      <h3 class="flex items-start gap-2 font-display text-titulo-2 text-corriente-pleno">
        <Icon
          :name="props.estado === 'error' ? 'lucide:triangle-alert' : 'lucide:database'"
          class="mt-1 size-4 shrink-0"
          :class="props.estado === 'error' ? 'text-error' : 'text-aviso'"
          aria-hidden="true"
        />
        {{
          props.estado === 'error'
            ? t('dashboard.state.error.title')
            : props.estado === 'sin-datos'
              ? t('dashboard.state.seedMissing.title')
              : t('dashboard.state.emptyTitle')
        }}
      </h3>

      <p class="text-cuerpo text-corriente-medio">
        {{
          props.estado === 'error'
            ? t('dashboard.state.error.body')
            : props.estado === 'sin-datos'
              ? t('dashboard.state.seedMissing.body')
              : t('dashboard.state.emptyBody')
        }}
      </p>

      <p v-if="props.estado === 'sin-datos'" data-instruccion class="text-cuerpo text-corriente-tenue">
        {{ t('dashboard.state.seedMissing.command') }}
      </p>

      <!--
        Only the failure offers a retry. Retrying an empty filter or a missing
        seed changes nothing, and a button that cannot work teaches the reader to
        insist against a door that will not open.
      -->
      <button
        v-if="props.estado === 'error'"
        type="button"
        data-reintentar
        class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="$emit('reintentar')"
      >
        <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('dashboard.state.error.retry') }}
      </button>
    </div>
  </div>
</template>
