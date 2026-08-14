<script setup lang="ts">
/**
 * Executive composition: the figures first, the search reduced to one line.
 *
 * Three present-day cards open the screen because the executive profile of A1
 * asks the portal for a state, not for a dataset. The search box stays -it is
 * the same portal- but it takes one line instead of a panel, which is what the
 * scope of this User Story says literally.
 *
 * These cards are NOT the predictive ones. They show the value at the latest
 * close and its change against the previous month; the projections carry a
 * method label and live in the dashboard, one click away.
 */
import type { RolUsuario } from '~/types/sesion'
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import BloqueLista from '~/components/inicio/BloqueLista.vue'
import BuscadorUnificado from '~/components/inicio/BuscadorUnificado.vue'
import CabeceraEspacio from '~/components/inicio/CabeceraEspacio.vue'
import TarjetaIndicador from '~/components/inicio/TarjetaIndicador.vue'
import { ALERTAS, FAVORITOS, INDICADORES } from '~/utils/muestrasInicio'

const props = defineProps<{
  /** True while the session has not resolved yet. */
  cargando: boolean
  /** Display name of the reader, empty while unknown. */
  nombre: string
  /** Role of the session, null while unknown. */
  rol: RolUsuario | null
}>()

const { t } = useI18n()

const idIndicadores = useId()

const estadoIndicadores = computed(() => (props.cargando ? 'cargando' : 'lista'))
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

      <div class="grid gap-4 md:grid-cols-3">
        <TarjetaIndicador
          v-for="indicador in INDICADORES"
          :key="indicador.id"
          :indicador="indicador"
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
