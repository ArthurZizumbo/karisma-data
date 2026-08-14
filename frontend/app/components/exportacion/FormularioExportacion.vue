<script setup lang="ts">
/**
 * First moment: what to extract, in which format and with which filters.
 *
 * The form decides nothing about the export. It collects three values, hands
 * the request over and goes back to waiting: whether the dataset exists, which
 * columns the filter may name and how long the job takes are answers only the
 * backend has, and predicting any of them here would put a second, quieter
 * validator in front of the real one.
 *
 * The syntax of the filter field is explained in the hint below it and not in a
 * placeholder: the example is the same sentence in both catalogues, and a leaf
 * that reads identically in Spanish and English is what the translation check
 * of `idioma.spec.ts` exists to refuse.
 *
 * Both formats are offered and both work. CSV is preselected because it is the
 * one with no ceiling: the spreadsheet writer holds a measured cap of 200,000
 * rows, above which the job ends `fallido`, so the note under the radios names
 * the cap instead of announcing an unavailable format. Refusing the request
 * here would be the second validator this form exists not to be: the row count
 * is a property of the extract, and only the backend knows it.
 */
import type { DatasetExportable, FormatoExportacion, SolicitudExportacion } from '~/types/exportacion'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { analizarFiltros, DATASETS, FORMATOS } from '~/composables/useExportaciones'
import { ANILLO_FOCO } from '~/utils/foco'

defineProps<{
  /** True while a request is on the wire. The control is not offered twice. */
  enviando: boolean
}>()

const emit = defineEmits<{
  /** The reader asked for an extraction with a complete, readable request. */
  enviar: [SolicitudExportacion]
}>()

const { t } = useI18n()

const dataset = ref<DatasetExportable>(DATASETS[0]!)
const formato = ref<FormatoExportacion>(FORMATOS[0]!)
const texto = ref('')

/** True once the reader has tried to send at least once. */
const intentado = ref(false)

const filtros = computed(() => analizarFiltros(texto.value))
const invalido = computed(() => intentado.value && filtros.value === null)

/** Sends the request, or refuses locally without touching the network. */
function enviar(): void {
  intentado.value = true
  const leidos = filtros.value
  if (leidos === null) {
    return
  }
  emit('enviar', { dataset: dataset.value, formato: formato.value, filtros: leidos })
}
</script>

<template>
  <form
    data-formulario="exportacion"
    class="flex max-w-(--medida-maxima) flex-col gap-5 border-l-2 border-info pl-5"
    novalidate
    :aria-busy="enviando"
    @submit.prevent="enviar"
  >
    <div class="flex flex-col gap-1">
      <label for="exportacion-dataset" class="text-etiqueta text-corriente-pleno">
        {{ t('export.form.dataset') }}
      </label>
      <select
        id="exportacion-dataset"
        v-model="dataset"
        data-campo="dataset"
        :disabled="enviando"
        class="min-h-9 w-full border border-corriente-medio bg-ground px-3 text-cuerpo text-corriente-pleno"
        :class="ANILLO_FOCO"
      >
        <option v-for="opcion in DATASETS" :key="opcion" :value="opcion">
          {{ t(`export.dataset.${opcion}`) }}
        </option>
      </select>
    </div>

    <fieldset class="flex flex-col gap-1">
      <legend class="text-etiqueta text-corriente-pleno">
        {{ t('export.form.format') }}
      </legend>
      <div class="flex flex-col gap-1 pt-1">
        <label
          v-for="opcion in FORMATOS"
          :key="opcion"
          :data-formato="opcion"
          class="flex items-center gap-2 text-cuerpo text-corriente-pleno"
        >
          <input
            v-model="formato"
            type="radio"
            name="formato"
            :value="opcion"
            :disabled="enviando"
            :class="ANILLO_FOCO"
          >
          {{ t(`export.format.${opcion}`) }}
        </label>
      </div>
      <p data-aviso="xlsx" class="flex items-start gap-2 text-micro text-corriente-tenue">
        <Icon name="lucide:info" class="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
        {{ t('export.format.xlsxRowLimit') }}
      </p>
    </fieldset>

    <div class="flex flex-col gap-1">
      <label for="exportacion-filtros" class="text-etiqueta text-corriente-pleno">
        {{ t('export.form.filters') }}
      </label>
      <input
        id="exportacion-filtros"
        v-model="texto"
        data-campo="filtros"
        type="text"
        spellcheck="false"
        autocapitalize="none"
        :disabled="enviando"
        :aria-invalid="invalido ? 'true' : undefined"
        aria-describedby="exportacion-filtros-ayuda"
        class="min-h-9 w-full border bg-ground px-3 text-cuerpo text-corriente-pleno"
        :class="[invalido ? 'border-error' : 'border-corriente-medio', ANILLO_FOCO]"
      >
      <p id="exportacion-filtros-ayuda" class="text-micro text-corriente-tenue">
        {{ t('export.form.filtersHint') }}
      </p>
      <p
        v-if="invalido"
        data-error="filtros"
        role="alert"
        class="flex items-center gap-1 text-micro text-error"
      >
        <Icon name="lucide:circle-alert" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('export.form.filtersInvalid') }}
      </p>
    </div>

    <button
      data-accion="solicitar"
      type="submit"
      :disabled="enviando"
      class="flex min-h-9 items-center gap-2 self-start border border-corriente-pleno bg-corriente-pleno px-4 text-cuerpo text-ground hover:bg-corriente-medio disabled:opacity-60"
      :class="ANILLO_FOCO"
    >
      <Icon name="lucide:download" class="size-4 shrink-0" aria-hidden="true" />
      {{ enviando ? t('export.form.sending') : t('export.form.submit') }}
    </button>
  </form>
</template>
