<script setup lang="ts">
/**
 * Lineage plate.
 *
 * The gap the design review called the most serious of the document: "Ver
 * linaje" existed as a button label and nothing behind it was specified. Roberto
 * Valdez, whose job is to answer for a figure, was handed a design system that
 * documented five status chips and zero ways to defend a number.
 *
 * This is where the world stops being decoration. A lineage IS a chain of nodes
 * with current running through it, so the plate draws the actual thing rather
 * than a picture of it: each hop carries its system of origin, the
 * transformation applied, the owner who answers for it and the date it stopped
 * being valid.
 *
 * Two rules the plate has to demonstrate and not merely state:
 *
 * 1.  Every figure cites the catalogue source it came from. The last hop shows
 *     the number and the source together, never the number alone.
 * 2.  When two systems disagree, the canonical one is named. Silence about the
 *     conflict is what sends Laura back to email.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()

/**
 * One hop of the chain.
 *
 * `corriente` is the rung the node sits on: the origin is dim and the figure
 * the reader sees is at full current, so the eye follows the same ramp the rest
 * of the system uses for state.
 */
const SALTOS = Object.freeze([
  { id: 'origen', corriente: 'bg-corriente-apagado', icono: 'lucide:database' },
  { id: 'ingesta', corriente: 'bg-corriente-tenue', icono: 'lucide:download' },
  { id: 'transformacion', corriente: 'bg-corriente-medio', icono: 'lucide:function-square' },
  { id: 'publicacion', corriente: 'bg-corriente-pleno', icono: 'lucide:check' },
])
</script>

<template>
  <section data-lamina="linaje" class="flex flex-col gap-6">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.lineage') }}
    </h2>

    <p class="text-cuerpo text-corriente-medio">
      {{ t('guide.lineage.description') }}
    </p>

    <!-- The chain, drawn as the chain it is. -->
    <ol class="ml-2 flex flex-col border-l border-corriente-apagado">
      <li
        v-for="salto in SALTOS"
        :key="salto.id"
        :data-salto="salto.id"
        class="relative py-4 pl-6"
      >
        <span
          class="absolute -left-[5px] top-6 size-2.5 rounded-full"
          :class="salto.corriente"
          aria-hidden="true"
        />
        <p class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
          <Icon :name="salto.icono" class="size-4 shrink-0" aria-hidden="true" />
          {{ t(`guide.lineage.hop.${salto.id}.title`) }}
        </p>
        <p class="mt-1 font-mono text-micro text-corriente-tenue">
          {{ t(`guide.lineage.hop.${salto.id}.system`) }}
        </p>
        <p class="mt-1 text-cuerpo text-corriente-medio">
          {{ t(`guide.lineage.hop.${salto.id}.transform`) }}
        </p>
        <dl class="mt-2 flex flex-wrap gap-x-6 gap-y-1 text-micro">
          <div class="flex gap-1">
            <dt class="text-corriente-tenue">{{ t('guide.lineage.owner') }}</dt>
            <dd class="text-corriente-pleno">{{ t(`guide.lineage.hop.${salto.id}.owner`) }}</dd>
          </div>
          <div class="flex gap-1">
            <dt class="text-corriente-tenue">{{ t('guide.lineage.validity') }}</dt>
            <dd class="font-mono text-corriente-pleno">
              {{ t(`guide.lineage.hop.${salto.id}.validity`) }}
            </dd>
          </div>
        </dl>
      </li>
    </ol>

    <!--
      The figure and its source in the same block. A number without its
      provenance is the defect the whole product exists to remove.
    -->
    <div data-cifra-con-fuente class="flex flex-col gap-1 border-l-2 border-info pl-5">
      <p class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('guide.lineage.figure.label') }}
      </p>
      <p class="font-mono text-display tabular-nums text-corriente-pleno">
        12 405 780.40
      </p>
      <p class="flex items-center gap-1 text-micro text-corriente-tenue">
        <Icon name="lucide:database" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('guide.lineage.figure.source') }}
      </p>
    </div>

    <!--
      The conflict. Two systems disagreeing is the ordinary case in a bank, and
      staying silent about it is what sends the reader back to email.
    -->
    <div data-conflicto class="flex flex-col gap-2">
      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:triangle-alert" class="size-4 shrink-0 text-aviso" aria-hidden="true" />
        {{ t('guide.lineage.conflict.title') }}
      </h3>
      <ul class="flex flex-col divide-y divide-grid">
        <li
          v-for="lado in (['canonical', 'divergent'] as const)"
          :key="lado"
          :data-lado="lado"
          class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-2"
        >
          <span class="text-cuerpo text-corriente-pleno">
            {{ t(`guide.lineage.conflict.${lado}.system`) }}
          </span>
          <span class="font-mono text-dato tabular-nums text-corriente-pleno">
            {{ t(`guide.lineage.conflict.${lado}.value`) }}
          </span>
          <span
            class="flex items-center gap-1 text-micro"
            :class="lado === 'canonical' ? 'text-ok' : 'text-corriente-tenue'"
          >
            <Icon
              :name="lado === 'canonical' ? 'lucide:check' : 'lucide:circle-dashed'"
              class="size-3 shrink-0"
              aria-hidden="true"
            />
            {{ t(`guide.lineage.conflict.${lado}.verdict`) }}
          </span>
        </li>
      </ul>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('guide.lineage.conflict.rule') }}
      </p>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 text-cuerpo text-corriente-medio">
        {{ t('guide.lineage.rationale') }}
      </p>
    </details>
  </section>
</template>
