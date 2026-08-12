<script setup lang="ts">
/**
 * A figure of the PRESENT, on a card.
 *
 * Value at the latest close, change against the previous month, cut-off date
 * and one click to the dashboard that explains it. There is no projection here
 * and there will not be one: the forecast cards carry a method label, need an
 * expandable panel and a detail table, and they live in the dashboard. Sharing
 * one component between the two would produce a card with three optional
 * properties that a single consumer uses, and it would let a projection be read
 * as an observation.
 *
 * The change is NOT coloured by sign. A rise in liquidity coverage is good news
 * and a rise in non-performing loans is bad news, so painting both green would
 * be the card asserting a judgement it cannot make. The sign and the sentence
 * carry the meaning, and colour is left to the semantic states.
 */
import type { Indicador, UnidadIndicador } from '~/types/espacios'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatearFecha, formatearNumero, formatearVariacion } from '~/utils/fechas'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** The figure to render, already read from its source. */
  indicador: Indicador
  /** True while the session has not resolved yet. */
  cargando?: boolean
}>()

const { t, locale } = useI18n()

/** Card chrome, shared by the card and its placeholder so neither one jumps. */
const TARJETA = 'flex min-h-40 flex-col justify-between gap-3 border border-grid bg-ground-alt p-4'

/** Translation key of each unit. Written whole so a grep can find them. */
const CLAVE_UNIDAD: Readonly<Record<UnidadIndicador, string>> = {
  'porcentaje': 'workspace.indicators.unit.percent',
  'millones-mxn': 'workspace.indicators.unit.millionsMxn',
  'dias': 'workspace.indicators.unit.days',
}

const valor = computed(() => formatearNumero(props.indicador.valor, locale.value))
const unidad = computed(() => t(CLAVE_UNIDAD[props.indicador.unidad]))
const variacion = computed(() =>
  t('workspace.indicators.change', {
    value: formatearVariacion(props.indicador.variacion, locale.value),
  }),
)
const corte = computed(() =>
  t('workspace.indicators.asOf', { date: formatearFecha(props.indicador.fecha, locale.value) }),
)
</script>

<template>
  <article
    :data-indicador="indicador.id"
    data-origen="ejemplo"
    :aria-busy="cargando ? 'true' : undefined"
    :class="TARJETA"
  >
    <template v-if="cargando">
      <span class="h-3 w-2/3 bg-grid" aria-hidden="true" />
      <span class="h-10 w-1/2 bg-grid" aria-hidden="true" />
      <span class="h-3 w-3/4 bg-grid" aria-hidden="true" />
      <span class="sr-only">{{ t('workspace.loading') }}</span>
    </template>

    <template v-else>
      <h3 class="text-titulo-3 text-corriente-medio">
        {{ t(indicador.claveEtiqueta) }}
      </h3>

      <p class="flex items-baseline gap-2">
        <span class="font-display text-display tabular-nums text-corriente-pleno">{{ valor }}</span>
        <span class="text-etiqueta text-corriente-tenue">{{ unidad }}</span>
      </p>

      <div class="flex flex-col gap-1">
        <p data-variacion class="text-micro tabular-nums text-corriente-medio">
          {{ variacion }}
        </p>
        <p class="flex items-center gap-2 text-micro text-corriente-tenue">
          <time :datetime="indicador.fecha">{{ corte }}</time>
          <span class="border border-grid px-1 uppercase">{{ t('workspace.sample.badge') }}</span>
        </p>
        <NuxtLink
          :to="indicador.destino"
          class="mt-1 inline-flex w-fit items-center gap-1.5 text-etiqueta text-corriente-pleno hover:underline"
          :class="ANILLO_FOCO"
        >
          <Icon name="lucide:chart-line" class="size-3.5 shrink-0" aria-hidden="true" />
          {{ t('workspace.indicators.open') }}
        </NuxtLink>
      </div>
    </template>
  </article>
</template>
