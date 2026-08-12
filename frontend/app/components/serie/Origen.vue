<script setup lang="ts">
/**
 * Where the numbers on this screen come from.
 *
 * Not decoration and not a footnote: no figure of this portal exists without a
 * provenance, and this card is what makes that checkable on the screen itself
 * instead of in a document nobody opens. It is also the payload the lineage
 * overlay of US-029 will paint, which is why it is rendered from the frame
 * header rather than from anything typed here.
 *
 * The three limitations are stated rather than hidden: the transport rounds to
 * 32 bits, the time axis has no holiday calendar, and the exchange rate is a
 * fixed synthetic one. A demo that hides its own edges is what makes an
 * evaluator distrust the parts that are real.
 */
import type { CodigoIdioma } from '~/composables/useIdioma'
import type { OrigenSerie } from '~/types/tablero'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  origen: OrigenSerie
  /** Language on screen, which picks the side of the bilingual note. */
  idioma: CodigoIdioma
}>()

const { t } = useI18n()

/** The exchange rate note as the sidecar of the generator wrote it. */
const notaTipoCambio = computed(() =>
  props.idioma === 'en' ? props.origen.notaTipoCambioEn : props.origen.notaTipoCambioEs,
)

/**
 * The rows with a figure behind them.
 *
 * A row is omitted when its value is null instead of showing a zero: the raw row
 * count and the seed come from the generator manifest, and when the manifest is
 * absent the honest answer is silence, never an invented number.
 */
const filas = computed(() => {
  const entradas: { clave: string, etiqueta: string, valor: string }[] = [
    { clave: 'file', etiqueta: t('dashboard.source.file'), valor: props.origen.archivo },
    {
      clave: 'aggregatedRows',
      etiqueta: t('dashboard.source.aggregatedRows'),
      valor: String(props.origen.filasAgregadas),
    },
  ]
  if (props.origen.filasCrudas !== null) {
    entradas.push({
      clave: 'rawRows',
      etiqueta: t('dashboard.source.rawRows'),
      valor: String(props.origen.filasCrudas),
    })
  }
  if (props.origen.semilla !== null) {
    entradas.push({
      clave: 'seed',
      etiqueta: t('dashboard.source.seed'),
      valor: String(props.origen.semilla),
    })
  }
  entradas.push({
    clave: 'precision',
    etiqueta: t('dashboard.source.precision'),
    valor: t('dashboard.source.precisionValue'),
  })
  entradas.push({
    clave: 'fxNote',
    etiqueta: t('dashboard.source.fxNote'),
    valor: notaTipoCambio.value,
  })
  return entradas
})
</script>

<template>
  <section data-origen-serie class="flex flex-col gap-2 border-l-2 border-info pl-5">
    <h3 class="flex items-center gap-2 text-etiqueta uppercase text-corriente-tenue">
      <Icon name="lucide:git-branch" class="size-3.5 shrink-0" aria-hidden="true" />
      {{ t('dashboard.source.title') }}
    </h3>

    <dl class="grid gap-x-6 gap-y-1 sm:grid-cols-[max-content_1fr]">
      <template v-for="fila in filas" :key="fila.clave">
        <dt :data-origen-campo="fila.clave" class="text-etiqueta text-corriente-tenue">
          {{ fila.etiqueta }}
        </dt>
        <dd class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
          {{ fila.valor }}
        </dd>
      </template>
    </dl>

    <p class="text-etiqueta text-corriente-tenue">
      {{ t('dashboard.source.transformations') }}
    </p>
    <ul class="ml-1 flex flex-col border-l border-corriente-apagado">
      <li
        v-for="transformacion in props.origen.transformaciones"
        :key="transformacion"
        data-transformacion
        class="relative py-0.5 pl-4 text-micro text-corriente-tenue"
      >
        <span class="absolute left-0 top-1/2 h-px w-2.5 bg-corriente-apagado" aria-hidden="true" />
        {{ transformacion }}
      </li>
    </ul>

    <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('dashboard.source.calendar') }}
    </p>
  </section>
</template>
