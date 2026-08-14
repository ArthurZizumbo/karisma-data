<script setup lang="ts">
/**
 * The journey of one field, hop by hop (US-029).
 *
 * Five steps: four seeded and one composed. Every hop answers for itself -what
 * was done to the data, who is accountable and until when it is valid- because
 * the criterion asks for the owner OF EACH HOP, and the owner of the extraction
 * job is not the owner of the source.
 *
 * The technical detail sits behind a `<details>` and not in the open: the third
 * rung of the disclosure pattern is reached in one more click, and a panel that
 * shows the system codes of five hops at once is a wall, not an explanation.
 */
import type { PasoLinaje } from '~/types/linaje'
import { useI18n } from 'vue-i18n'
import { CLAVE_ETAPA, CLAVE_TRANSFORMACION } from '~/types/linaje'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{ pasos: readonly PasoLinaje[] }>()

const { t } = useI18n()

/** Icon of the hop. Literals only: a name composed at run time ships empty. */
function iconoDeEtapa(paso: PasoLinaje): string {
  if (paso.stage === 'origen') {
    return 'lucide:database'
  }
  if (paso.stage === 'calidad') {
    return 'lucide:shield-check'
  }
  return paso.stage === 'presentacion' ? 'lucide:eye' : 'lucide:git-branch'
}
</script>

<template>
  <ol data-recorrido class="flex flex-col">
    <li
      v-for="paso in props.pasos"
      :key="paso.order"
      data-paso-linaje
      :data-etapa="paso.stage"
      :data-derivado="paso.stored ? 'false' : 'true'"
      class="relative flex flex-col gap-2 border-l-2 border-grid py-3 pl-5 last:border-transparent"
    >
      <span
        class="absolute -left-[5px] top-5 size-2 rounded-full bg-info"
        aria-hidden="true"
      />

      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon :name="iconoDeEtapa(paso)" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t(CLAVE_ETAPA[paso.stage]) }}
        <!--
          Whether the hop is stored or composed is said out loud. It is the
          honesty commitment of this User Story: the last step is derived from
          the catalogue entry on every request, and hiding that would let the
          reader believe the portal keeps a record it does not keep.
        -->
        <span
          class="rounded-sm border px-1.5 text-micro uppercase"
          :class="paso.stored ? 'border-grid text-corriente-tenue' : 'border-info text-info'"
        >
          {{ paso.stored ? t('lineage.step.stored') : t('lineage.step.derived') }}
        </span>
      </h3>

      <p class="text-cuerpo text-corriente-pleno">
        {{ paso.systemName }}
      </p>

      <p data-transformacion class="text-cuerpo text-corriente-medio">
        {{ t(CLAVE_TRANSFORMACION[paso.transformationCode], { detail: paso.transformationDetail }) }}
      </p>

      <p data-propietario class="text-micro text-corriente-tenue">
        {{ t('lineage.step.ownerOf') }}: {{ paso.owner.steward }} · {{ paso.owner.area }}
      </p>

      <p data-vigencia class="text-micro text-corriente-tenue">
        {{ t('lineage.step.effectiveFrom') }} {{ paso.effectiveFrom }} ·
        {{ t('lineage.step.effectiveTo') }}
        {{ paso.effectiveTo ?? t('lineage.step.openEnded') }} ·
        {{ paso.isCurrent ? t('lineage.panel.currentYes') : t('lineage.panel.currentNo') }}
      </p>

      <details class="text-micro text-corriente-tenue">
        <summary class="w-fit cursor-pointer rounded-sm py-1 text-corriente-medio" :class="ANILLO_FOCO">
          {{ t('lineage.step.open') }}
        </summary>
        <dl class="mt-1 grid grid-cols-[auto_1fr] gap-x-3">
          <dt>{{ t('lineage.panel.sourceLabel') }}</dt>
          <dd class="font-mono">
            {{ paso.systemCode }}
          </dd>
          <dt>{{ t('lineage.step.technicalDetail') }}</dt>
          <dd class="font-mono">
            {{ paso.transformationCode }}
          </dd>
        </dl>
      </details>
    </li>
  </ol>
</template>
