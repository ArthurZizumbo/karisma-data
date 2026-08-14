<script setup lang="ts">
/**
 * Branch 2.3 of the A3 map: extraction in the background and its history.
 *
 * The screen renders ALWAYS from real state. The three moments -the request,
 * the work in flight, the signed link- are derived by the store from the jobs
 * that exist, and this page cannot set them. `?momento=` is accepted so the
 * three can be captured one at a time for the deliverable, and all it does is
 * fix which real job stays expanded and stop the view from advancing on its
 * own: with an empty history, `?momento=enlace` says so instead of drawing a
 * link nobody can download.
 *
 * The reader is not sent anywhere to wait. The request answers with an
 * identifier and the watch lives in the store, so walking to the dashboard and
 * coming back finds the job where it really is.
 */
import type { SolicitudExportacion } from '~/types/exportacion'
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import FormularioExportacion from '~/components/exportacion/FormularioExportacion.vue'
import HistorialExportaciones from '~/components/exportacion/HistorialExportaciones.vue'
import {
  claveDeFallo,
  momentoDeConsulta,
  retrasoDeDemostracion,
  useExportaciones,
} from '~/composables/useExportaciones'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
const route = useRoute()
const exportaciones = useExportaciones()

/**
 * Seconds the deployment stretches a real job by, read from the public runtime
 * configuration. The cast is the honest shape of the fact: the key is declared
 * by whoever deploys the demonstration, not by this build, and an absent key
 * reads as zero -which hides the band instead of announcing a stretch that is
 * not happening.
 */
const publico = useRuntimeConfig().public as unknown as Record<string, unknown>
const retrasoDemo = computed(() => retrasoDeDemostracion(publico))

/** Catalogue leaf that names each moment. */
const CLAVE_DE_MOMENTO = Object.freeze({
  solicitud: 'request',
  proceso: 'progress',
  enlace: 'link',
})

/**
 * True when the pinned moment has no real job behind it.
 *
 * This is the branch that keeps the capture honest: the moment was asked for,
 * the portal has nothing in it, and it says so.
 *
 * Read from `trabajoDelMomento` -the state- and never from `trabajoDestacado`
 * -the expanded row-, because the reader empties the second one with a single
 * click on the card. Derived from the row, the sentence "no export is running
 * right now" appeared over an export that was running, spinning, three rows
 * below: the screen contradicting itself on the one fact it exists to report.
 */
const sinTrabajo = computed(
  () => exportaciones.momentoVisible !== 'solicitud' && exportaciones.trabajoDelMomento === null,
)

// The query is watched rather than read once: moving between the three moments
// during a capture session is a navigation, and a value read at setup would
// leave the screen pinned to whatever the first visit asked for.
watch(
  () => route.query.momento,
  (valor) => {
    exportaciones.fijarMomento(momentoDeConsulta(valor))
  },
  { immediate: true },
)

onMounted(() => {
  void exportaciones.cargarHistorial()
})

/**
 * Sends the request the form assembled.
 *
 * @param solicitud - Dataset, format and filters the reader chose.
 */
async function solicitar(solicitud: SolicitudExportacion): Promise<void> {
  await exportaciones.solicitar(solicitud)
}
</script>

<template>
  <section
    :data-ruta="ruta"
    :data-momento="exportaciones.momentoVisible"
    :data-fijado="exportaciones.momentoFijado !== null"
    class="flex flex-col gap-8"
  >
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.exports.description')" />

    <p
      v-if="retrasoDemo > 0"
      data-franja="demo"
      role="note"
      class="flex max-w-(--medida-maxima) items-start gap-2 border-l-2 border-aviso bg-ground-alt px-4 py-3 text-cuerpo text-corriente-medio"
    >
      <Icon name="lucide:info" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
      {{ t('export.demo.notice', { segundos: retrasoDemo }) }}
    </p>

    <section data-bloque="momento" class="flex flex-col gap-4">
      <p class="flex flex-wrap items-center gap-2 text-etiqueta uppercase text-corriente-tenue">
        <Icon name="lucide:navigation" class="size-3.5 shrink-0" aria-hidden="true" />
        <span data-etiqueta="momento">
          {{ t(`export.moment.${CLAVE_DE_MOMENTO[exportaciones.momentoVisible]}`) }}
        </span>
        <span v-if="exportaciones.momentoFijado !== null" data-etiqueta="fijado" class="text-info">
          {{ t('export.moment.pinned') }}
        </span>
      </p>

      <p
        v-if="exportaciones.fallo !== null"
        data-fallo
        role="alert"
        class="flex max-w-(--medida-maxima) items-start gap-2 border-l-2 border-error bg-ground-alt px-4 py-3 text-cuerpo text-corriente-pleno"
      >
        <Icon
          name="lucide:circle-alert"
          class="mt-0.5 size-4 shrink-0 text-error"
          aria-hidden="true"
        />
        {{ t(claveDeFallo(exportaciones.fallo)) }}
      </p>

      <FormularioExportacion :enviando="exportaciones.enviando" @enviar="solicitar" />

      <p
        v-if="sinTrabajo"
        data-vacio="momento"
        class="max-w-(--medida-maxima) border-l-2 border-corriente-apagado pl-4 text-cuerpo text-corriente-tenue"
      >
        {{ t('export.moment.empty') }}
      </p>
    </section>

    <HistorialExportaciones
      :trabajos="exportaciones.trabajos"
      :estado="exportaciones.estado"
      :destacado-id="exportaciones.trabajoDestacado?.job_id ?? null"
      @alternar="exportaciones.destacar"
      @reintentar="exportaciones.cargarHistorial"
    />
  </section>
</template>
