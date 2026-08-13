<script setup lang="ts">
/**
 * Content of the lineage overlay: the header of the field and its journey.
 *
 * It owns no transport and no focus. `PanelLinaje` is the surface and
 * `useLinajeCampo` is the request; this component only decides which of the
 * three states the reader is looking at, which is what keeps the state machine
 * out of a template.
 *
 * The field header is rendered from the card the reader clicked and not from
 * the answer, so the title and the name are on screen while the journey is
 * still travelling: a title that appears only when the payload lands is a jump
 * in the middle of the opening animation.
 */
import type { CampoCatalogo, EstadoConsulta, LinajeCampo } from '~/types/linaje'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GobiernoPanelLinaje from '~/components/gobierno/PanelLinaje.vue'
import GobiernoRecorridoLinaje from '~/components/gobierno/RecorridoLinaje.vue'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  abierto: boolean
  campo: CampoCatalogo | null
  linaje: LinajeCampo | null
  estado: EstadoConsulta
  codigo: string | null
}>()

const emit = defineEmits<{ cerrar: [], reintentar: [] }>()

const { t } = useI18n()

const titulo = computed(() =>
  t('lineage.panel.title', { field: props.campo?.physicalName ?? '' }),
)

const vigencia = computed(() => {
  const validez = props.campo?.validity
  if (validez === undefined) {
    return ''
  }
  const hasta = validez.validTo ?? t('lineage.step.openEnded')
  return `${validez.validFrom} · ${hasta}`
})
</script>

<template>
  <GobiernoPanelLinaje
    :abierto="props.abierto"
    :titulo="titulo"
    :etiqueta-cerrar="t('lineage.panel.closeLabel')"
    @cerrar="emit('cerrar')"
  >
    <template #encabezado>
      <dl v-if="props.campo !== null" data-encabezado-linaje class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-micro">
        <dt class="text-corriente-tenue">
          {{ t('lineage.card.businessName') }}
        </dt>
        <dd class="text-corriente-pleno">
          {{ props.campo.businessName }}
        </dd>

        <dt class="text-corriente-tenue">
          {{ t('lineage.panel.sourceLabel') }}
        </dt>
        <dd class="text-corriente-pleno">
          {{ props.campo.source.displayName }}
        </dd>

        <dt class="text-corriente-tenue">
          {{ t('lineage.panel.ownerLabel') }}
        </dt>
        <dd class="text-corriente-pleno">
          {{ props.campo.owner.steward }} · {{ props.campo.owner.area }}
        </dd>

        <dt class="text-corriente-tenue">
          {{ t('lineage.panel.validityLabel') }}
        </dt>
        <dd class="text-corriente-pleno">
          {{ vigencia }}
        </dd>
      </dl>
    </template>

    <div :data-estado="props.estado" class="flex flex-col gap-4">
      <!--
        The skeleton reserves the height of five hops. A spinner of unknown
        height moves the close button the moment the answer lands, and the
        reader who was about to press it presses something else.
      -->
      <div v-if="props.estado === 'cargando'" role="status" aria-busy="true" class="flex flex-col gap-3">
        <span class="sr-only">{{ t('lineage.panel.state.loading') }}</span>
        <span
          v-for="fila in 5"
          :key="fila"
          aria-hidden="true"
          class="h-16 animate-pulse rounded-md bg-ground-alt"
        />
      </div>

      <div
        v-else-if="props.estado === 'error'"
        class="flex flex-col gap-2 border-l-2 border-error pl-4"
      >
        <h3 class="flex items-start gap-2 text-titulo-3 text-corriente-pleno">
          <Icon name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
          {{ t('lineage.panel.state.error.title') }}
        </h3>
        <p class="text-cuerpo text-corriente-medio">
          {{ t('lineage.panel.state.error.body') }}
        </p>
        <p v-if="props.codigo !== null" data-codigo-error class="font-mono text-micro text-corriente-tenue">
          {{ props.codigo }}
        </p>
        <button
          type="button"
          data-reintentar-linaje
          class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
          :class="ANILLO_FOCO"
          @click="emit('reintentar')"
        >
          <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
          {{ t('lineage.panel.state.error.retry') }}
        </button>
      </div>

      <template v-else-if="props.estado === 'listo' && props.linaje !== null">
        <h3 class="sr-only">
          {{ t('lineage.panel.journeyLabel') }}
        </h3>
        <GobiernoRecorridoLinaje :pasos="props.linaje.steps" />
        <p data-nota-derivado class="border-l-2 border-info pl-4 text-micro text-corriente-tenue">
          {{ t('lineage.panel.derivedNote') }}
        </p>
      </template>
    </div>
  </GobiernoPanelLinaje>
</template>
