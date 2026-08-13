<script setup lang="ts">
/**
 * One entry of the field dictionary.
 *
 * The physical name leads and is set in the mono family: it is the string the
 * reader will paste into a query, and it has to be recognisable as a column
 * name rather than as prose. The business name reads underneath, which is the
 * order the metadata panel of the style guide declares.
 *
 * The facet chips carry their group name in the accessible label. A chip that
 * only says "Cartera" is ambiguous the moment a second group produces a similar
 * word, and a screen reader announces a list of loose words with no structure.
 */
import type { CampoCatalogo, GrupoFaceta } from '~/types/linaje'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { claveDeFaceta, CLAVE_GRUPO_FACETA } from '~/types/linaje'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{ campo: CampoCatalogo }>()

const emit = defineEmits<{ verLinaje: [campo: CampoCatalogo] }>()

const { t } = useI18n()

/** One chip: the group it belongs to and the value, already translated. */
interface Chip {
  grupo: GrupoFaceta
  codigo: string
  etiqueta: string
}

/**
 * The facets that carry a value.
 *
 * A null unit or a null aggregation is not rendered as an empty chip: half the
 * catalogue is not a metric, and a chip with nothing in it reads as data that
 * failed to load.
 */
const chips = computed<Chip[]>(() => {
  const facetas = props.campo.facets
  const pares: { grupo: GrupoFaceta, codigo: string | null }[] = [
    { grupo: 'domain', codigo: facetas.domain },
    { grupo: 'dataType', codigo: facetas.dataType },
    { grupo: 'sensitivity', codigo: facetas.sensitivity },
    { grupo: 'refreshFrequency', codigo: facetas.refreshFrequency },
    { grupo: 'unit', codigo: facetas.unit },
    { grupo: 'aggregation', codigo: facetas.metricAgg },
  ]

  return pares
    .filter((par): par is { grupo: GrupoFaceta, codigo: string } => par.codigo !== null)
    .map(({ grupo, codigo }) => {
      const clave = claveDeFaceta(grupo, codigo)
      // An unknown code is shown as it arrived. Printing the dotted key would
      // put `catalog.facet.domain.tesoreria` on screen, in both languages.
      return { grupo, codigo, etiqueta: clave === null ? codigo : t(clave) }
    })
})

/** The certification badge, which is state and therefore never colour alone. */
const certificacion = computed(() => {
  const codigo = props.campo.facets.certification
  const clave = claveDeFaceta('certification', codigo)
  return {
    codigo,
    etiqueta: clave === null ? codigo : t(clave),
    icono: codigo === 'certificado' ? 'lucide:circle-check' : 'lucide:triangle-alert',
    clase: codigo === 'certificado' ? 'border-ok text-ok' : 'border-aviso text-aviso',
  }
})

const vigencia = computed(() => {
  const hasta = props.campo.validity.validTo ?? t('lineage.step.openEnded')
  return `${props.campo.validity.validFrom} · ${hasta}`
})
</script>

<template>
  <article
    data-campo
    :data-campo-id="props.campo.fieldId"
    class="flex flex-col gap-3 rounded-lg border border-grid bg-ground-alt p-4"
  >
    <header class="flex flex-wrap items-start justify-between gap-2">
      <div class="flex flex-col gap-0.5">
        <h3 class="font-mono text-titulo-3 text-corriente-pleno">
          {{ props.campo.physicalName }}
        </h3>
        <p class="text-cuerpo text-corriente-medio">
          {{ props.campo.businessName }}
        </p>
      </div>

      <span
        data-certificacion
        :data-certificacion-codigo="certificacion.codigo"
        class="flex items-center gap-1 rounded-sm border px-2 py-0.5 text-micro uppercase"
        :class="certificacion.clase"
      >
        <Icon :name="certificacion.icono" class="size-3.5 shrink-0" aria-hidden="true" />
        {{ certificacion.etiqueta }}
      </span>
    </header>

    <p class="text-cuerpo text-corriente-medio">
      {{ props.campo.definition }}
    </p>

    <dl class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-micro">
      <dt class="text-corriente-tenue">
        {{ t('lineage.card.source') }}
      </dt>
      <dd class="text-corriente-pleno">
        {{ props.campo.source.displayName }}
      </dd>
      <dt class="text-corriente-tenue">
        {{ t('lineage.card.validity') }}
      </dt>
      <dd data-vigencia-campo class="text-corriente-pleno">
        {{ vigencia }}
      </dd>
    </dl>

    <ul class="flex flex-wrap gap-1.5">
      <li
        v-for="chip in chips"
        :key="chip.grupo"
        data-chip-faceta
        :data-faceta="chip.grupo"
        class="rounded-sm border border-grid px-2 py-0.5 text-micro text-corriente-tenue"
        :title="`${t(CLAVE_GRUPO_FACETA[chip.grupo])}: ${chip.etiqueta}`"
      >
        <span class="sr-only">{{ t(CLAVE_GRUPO_FACETA[chip.grupo]) }}:</span>
        {{ chip.etiqueta }}
      </li>
    </ul>

    <button
      type="button"
      data-disparador-linaje
      class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
      :class="ANILLO_FOCO"
      @click="emit('verLinaje', props.campo)"
    >
      <Icon name="lucide:git-branch" class="size-4 shrink-0" aria-hidden="true" />
      {{ t('lineage.card.openLineage') }}
    </button>
  </article>
</template>
