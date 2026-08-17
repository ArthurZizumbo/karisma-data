<script setup lang="ts">
/**
 * Executive composition: the figures first, the search reduced to one line.
 *
 * Four present-day cards open the screen because the executive profile of A1
 * asks the portal for a state, not for a dataset. The search box stays -it is
 * the same portal- but it takes one line instead of a panel, which is what the
 * scope of this User Story says literally.
 *
 * These cards are NOT the predictive ones. They show the value at the latest
 * close and its change against the previous month; the projections carry a
 * method label and live in the dashboard, one click away.
 *
 * The formatting happens HERE and not in the card. The card receives sentences
 * because whoever owns the data owns its language: a card that formatted
 * numbers would have to know the locale, the unit vocabulary and the sign
 * convention, and it would have to learn them again the day the figures come
 * from an endpoint instead of from the sample module.
 */
import type { RolUsuario } from '~/types/sesion'
import type { UnidadIndicador } from '~/types/espacios'

import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'

import BloqueLista from '~/components/inicio/BloqueLista.vue'
import BuscadorUnificado from '~/components/inicio/BuscadorUnificado.vue'
import CabeceraEspacio from '~/components/inicio/CabeceraEspacio.vue'
import TarjetaIndicador from '~/components/inicio/TarjetaIndicador.vue'
import { formatearFecha, formatearNumero, formatearVariacion } from '~/utils/fechas'
import { ALERTAS, FAVORITOS, INDICADORES } from '~/utils/muestrasInicio'

const props = defineProps<{
  /** True while the session has not resolved yet. */
  cargando: boolean
  /** Display name of the reader, empty while unknown. */
  nombre: string
  /** Role of the session, null while unknown. */
  rol: RolUsuario | null
}>()

const { t, locale } = useI18n()

const idIndicadores = useId()

const estadoIndicadores = computed(() => (props.cargando ? 'cargando' : 'lista'))

/** Translation key of each unit. Written whole so a grep can find them. */
const CLAVE_UNIDAD: Readonly<Record<UnidadIndicador, string>> = {
  'porcentaje': 'workspace.indicators.unit.percent',
  'millones-mxn': 'workspace.indicators.unit.millionsMxn',
  'dias': 'workspace.indicators.unit.days',
}

/**
 * The four figures, already turned into sentences.
 *
 * All four carry the ACTION channel and not one chosen by sign. A card that
 * painted a rise green would be judging, and a rise in non-performing loans is
 * not good news; the bar here is the accent of the theme and says only that
 * these are the figures the composition is built around.
 */
const tarjetas = computed(() =>
  INDICADORES.map(indicador => ({
    id: indicador.id,
    etiqueta: t(indicador.claveEtiqueta),
    valor: formatearNumero(indicador.valor, locale.value),
    unidad: t(CLAVE_UNIDAD[indicador.unidad]),
    variacion: t('workspace.indicators.change', {
      value: formatearVariacion(indicador.variacion, locale.value),
    }),
    actualizado: t('workspace.indicators.asOf', {
      date: formatearFecha(indicador.fecha, locale.value),
    }),
    momento: indicador.fecha,
    destino: indicador.destino,
  })),
)
</script>

<template>
  <div data-espacio="directivo" class="flex flex-col gap-8">
    <CabeceraEspacio
      composicion="directivo"
      :nombre="nombre"
      :rol="rol"
      :cargando="cargando"
    />

    <section
      data-bloque="indicadores"
      :data-estado="estadoIndicadores"
      :aria-labelledby="idIndicadores"
      :aria-busy="cargando ? 'true' : undefined"
      class="flex flex-col gap-3"
    >
      <h2 :id="idIndicadores" class="text-titulo-3 text-corriente-pleno">
        {{ t('workspace.indicators.title') }}
      </h2>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <TarjetaIndicador
          v-for="tarjeta in tarjetas"
          :key="tarjeta.id"
          :identificador="tarjeta.id"
          :etiqueta="tarjeta.etiqueta"
          :valor="tarjeta.valor"
          :unidad="tarjeta.unidad"
          :variacion="tarjeta.variacion"
          :actualizado="tarjeta.actualizado"
          :momento="tarjeta.momento"
          :destino="tarjeta.destino"
          canal="accion"
          :cargando="cargando"
        />
      </div>
    </section>

    <BuscadorUnificado enfasis="reducido" />

    <div class="grid gap-8 lg:grid-cols-2">
      <BloqueLista
        bloque="alertas"
        clave-titulo="workspace.alerts.title"
        clave-vacio="workspace.alerts.empty"
        :elementos="ALERTAS"
        :cargando="cargando"
      />

      <BloqueLista
        bloque="favoritos"
        clave-titulo="workspace.favorites.title"
        clave-vacio="workspace.favorites.empty"
        :elementos="FAVORITOS"
        :cargando="cargando"
      />
    </div>

    <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('workspace.sample.hint') }}
    </p>
  </div>
</template>
