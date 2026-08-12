<script setup lang="ts">
/**
 * Panel of the fluidity measurement, mounted only with `?medicion=1`.
 *
 * It is behind a query parameter because it is instrumentation and not a
 * feature: a reader of the dashboard has no use for a p95, and a demo that
 * shows its own instrumentation reads as a laboratory rather than a product.
 * What it produces is the evidence file the A4 document cites, so the report is
 * copied whole, with its script version and its machine, and never retyped.
 */
import type { InformeFluidez } from '~/composables/useMedidorFluidez'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { PASOS_GUION, VERSION_GUION } from '~/utils/guionFluidez'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  midiendo: boolean
  informe: InformeFluidez | null
}>()

defineEmits<{ medir: [] }>()

const { t, locale } = useI18n()

const copiado = ref(false)

/**
 * Milliseconds written with the unit, in the language on screen.
 *
 * `style: 'unit'` and not a literal "ms" in the template: the symbol is the
 * same in both languages, so a catalogue key for it would be the one thing the
 * bilingual check forbids, and a literal in the template is the other.
 */
const milisegundos = computed(
  () =>
    new Intl.NumberFormat(locale.value === 'en' ? 'en-US' : 'es-MX', {
      style: 'unit',
      unit: 'millisecond',
      maximumFractionDigits: 1,
    }),
)

/** Plain counts, with the separators of the language on screen. */
const conteo = computed(() => new Intl.NumberFormat(locale.value === 'en' ? 'en-US' : 'es-MX'))

/** The five figures of the report, in the order they are read. */
const cifras = computed(() => {
  const informe = props.informe
  if (informe === null) {
    return []
  }
  return [
    {
      clave: 'frames',
      etiqueta: t('dashboard.measure.frames'),
      valor: conteo.value.format(informe.muestra.cuadros),
    },
    {
      clave: 'p50',
      etiqueta: t('dashboard.measure.p50'),
      valor: milisegundos.value.format(informe.muestra.p50),
    },
    {
      clave: 'p95',
      etiqueta: t('dashboard.measure.p95'),
      valor: milisegundos.value.format(informe.muestra.p95),
    },
    {
      clave: 'worst',
      etiqueta: t('dashboard.measure.worst'),
      valor: milisegundos.value.format(informe.muestra.peor),
    },
    {
      clave: 'longFrames',
      etiqueta: t('dashboard.measure.longFrames'),
      valor: conteo.value.format(informe.muestra.largos),
    },
  ]
})

async function copiar(): Promise<void> {
  if (props.informe === null) {
    return
  }
  await navigator.clipboard.writeText(JSON.stringify(props.informe, null, 2))
  copiado.value = true
}
</script>

<template>
  <section data-medicion class="flex flex-col gap-3 rounded-lg border border-grid bg-ground-alt p-4">
    <h3 class="flex items-center gap-2 font-display text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:gauge" class="size-4 shrink-0" aria-hidden="true" />
      {{ t('dashboard.measure.title') }}
    </h3>

    <p class="text-micro text-corriente-tenue">
      {{ t('dashboard.measure.script', { version: VERSION_GUION, steps: PASOS_GUION }) }}
    </p>

    <div class="flex flex-wrap gap-2">
      <button
        type="button"
        data-accion="medir"
        :disabled="props.midiendo"
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground disabled:opacity-60"
        :class="ANILLO_FOCO"
        @click="$emit('medir')"
      >
        <Icon name="lucide:gauge" class="size-4 shrink-0" aria-hidden="true" />
        {{ props.midiendo ? t('dashboard.measure.running') : t('dashboard.measure.run') }}
      </button>

      <button
        v-if="props.informe !== null"
        type="button"
        data-accion="copiar"
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="copiar"
      >
        <Icon name="lucide:copy" class="size-4 shrink-0" aria-hidden="true" />
        {{ copiado ? t('dashboard.measure.copied') : t('dashboard.measure.copy') }}
      </button>
    </div>

    <dl v-if="props.informe !== null" class="grid gap-x-6 gap-y-1 sm:grid-cols-[max-content_1fr]">
      <template v-for="cifra in cifras" :key="cifra.clave">
        <dt :data-medida="cifra.clave" class="text-etiqueta text-corriente-tenue">
          {{ cifra.etiqueta }}
        </dt>
        <dd class="text-dato tabular-nums text-corriente-pleno">
          {{ cifra.valor }}
        </dd>
      </template>
    </dl>

    <p
      v-if="props.informe !== null"
      data-veredicto
      class="text-cuerpo"
      :class="props.informe.veredicto === 'cumple' ? 'text-ok' : 'text-error'"
    >
      {{
        props.informe.veredicto === 'cumple'
          ? t('dashboard.measure.verdict.pass')
          : t('dashboard.measure.verdict.fail')
      }}
    </p>
  </section>
</template>
