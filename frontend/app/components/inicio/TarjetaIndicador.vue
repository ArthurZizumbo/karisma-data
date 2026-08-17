<script setup lang="ts">
/**
 * A figure of the PRESENT, on a contained surface.
 *
 * Value at the latest close, change against the previous month, cut-off date
 * and one click to the dashboard that explains it. There is no projection here
 * and there will not be one: the forecast cards carry a method label, need an
 * expandable panel and a detail table, and they live in the dashboard. Sharing
 * one component between the two would produce a card with three optional
 * properties that a single consumer uses, and it would let a projection be read
 * as an observation.
 *
 * Everything arrives ALREADY FORMATTED. The card receives sentences and not an
 * `Indicador`, which is what lets the same component stand for a figure that
 * comes from a sample collection today and from an endpoint tomorrow without
 * learning either shape. Formatting is the job of whoever owns the data.
 *
 * THE FIGURE IS MONOSPACED. Four cards side by side are read as a column of
 * numbers even though they are not one, and proportional digits make two
 * magnitudes of the same width look alike.
 *
 * The change is NOT coloured by sign, and neither is the channel. A rise in
 * liquidity coverage is good news and a rise in non-performing loans is bad
 * news, so painting both green would be the card asserting a judgement it
 * cannot make. The bar on the left carries the action channel of the theme,
 * which is identity and not state; the sign and the sentence carry the meaning.
 */
import type { CanalTarjeta } from '~/types/superficie'

import { useI18n } from 'vue-i18n'

import ComunTarjetaContenida from '~/components/comun/TarjetaContenida.vue'
import { ANILLO_FOCO } from '~/utils/foco'

defineProps<{
  /** Stable identifier of the figure, published as `data-indicador`. */
  identificador: string
  /** Name of the measure, ALREADY TRANSLATED. */
  etiqueta: string
  /** The figure, ALREADY FORMATTED for the language on screen. */
  valor: string
  /** Cut-off sentence, ALREADY TRANSLATED. */
  actualizado: string
  /** Channel of the surface. Absent leaves the card without a bar. */
  canal?: CanalTarjeta
  /** Unit the figure is expressed in, ALREADY TRANSLATED. */
  unidad?: string
  /** Change against the previous period, ALREADY TRANSLATED. */
  variacion?: string
  /** ISO instant behind `actualizado`, so the date is machine readable. */
  momento?: string
  /** Route where the figure is explained. Absent leaves the card without exit. */
  destino?: string
  /** True while the session has not resolved yet. */
  cargando?: boolean
}>()

const { t } = useI18n()

/**
 * Box of the card, shared by the card and its placeholder so neither one jumps.
 *
 * `min-w-0` is not cosmetic: the card is a grid item, and a grid item keeps its
 * `min-width: auto` unless it is told otherwise, so a long figure would widen
 * its track past the viewport instead of wrapping inside it.
 */
const CAJA = 'min-h-36 min-w-0 justify-between'
</script>

<template>
  <ComunTarjetaContenida
    :canal="canal"
    :titulo="cargando === true ? undefined : etiqueta"
    :data-indicador="identificador"
    data-origen="ejemplo"
    :aria-busy="cargando === true ? 'true' : undefined"
    :class="CAJA"
  >
    <template v-if="cargando">
      <span class="h-3 w-2/3 bg-grid" aria-hidden="true" />
      <span class="h-8 w-1/2 bg-grid" aria-hidden="true" />
      <span class="h-3 w-3/4 bg-grid" aria-hidden="true" />
      <span class="sr-only">{{ t('workspace.loading') }}</span>
    </template>

    <template v-else>
      <p class="flex flex-wrap items-baseline gap-2">
        <span
          data-cifra
          class="font-mono text-titulo-1 tabular-nums text-corriente-pleno"
        >{{ valor }}</span>
        <span v-if="unidad !== undefined" class="text-etiqueta text-corriente-tenue">
          {{ unidad }}
        </span>
      </p>

      <div class="flex flex-col gap-1">
        <p v-if="variacion !== undefined" data-variacion class="text-micro tabular-nums text-corriente-medio">
          {{ variacion }}
        </p>
        <p class="flex flex-wrap items-center gap-2 text-micro text-corriente-tenue">
          <time v-if="momento !== undefined" data-marca-tiempo :datetime="momento">
            {{ actualizado }}
          </time>
          <span v-else data-marca-tiempo>{{ actualizado }}</span>
          <span class="border border-grid px-1 uppercase">{{ t('workspace.sample.badge') }}</span>
        </p>
        <NuxtLink
          v-if="destino !== undefined"
          :to="destino"
          class="mt-1 inline-flex min-h-11 w-fit items-center gap-1.5 text-etiqueta text-corriente-pleno hover:underline"
          :class="ANILLO_FOCO"
        >
          <Icon name="lucide:chart-line" class="size-3.5 shrink-0" aria-hidden="true" />
          {{ t('workspace.indicators.open') }}
        </NuxtLink>
      </div>
    </template>
  </ComunTarjetaContenida>
</template>
