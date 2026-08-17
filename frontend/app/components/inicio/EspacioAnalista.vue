<script setup lang="ts">
/**
 * Analyst composition: pick the work up where it was left.
 *
 * It opens with the saved queries and the export jobs, and only then with the
 * search box. The order is the criterion: an analyst who has to search again
 * for the query they built yesterday is paying twice for the same work, and the
 * profiles of data engineering and application integration behave the same way.
 *
 * The blocks and their order come from the composition contract, never from
 * this template.
 */
import type { RolUsuario } from '~/types/sesion'
import { useI18n } from 'vue-i18n'
import BloqueLista from '~/components/inicio/BloqueLista.vue'
import BuscadorUnificado from '~/components/inicio/BuscadorUnificado.vue'
import CabeceraEspacio from '~/components/inicio/CabeceraEspacio.vue'
import { RUTA_EXPLORACION } from '~/utils/espaciosTrabajo'
import { ANILLO_FOCO } from '~/utils/foco'
import { ALERTAS, CONSULTAS_GUARDADAS, EXPORTACIONES, FAVORITOS } from '~/utils/muestrasInicio'

defineProps<{
  /** True while the session has not resolved yet. */
  cargando: boolean
  /** Display name of the reader, empty while unknown. */
  nombre: string
  /** Role of the session, null while unknown. */
  rol: RolUsuario | null
}>()

const { t } = useI18n()
</script>

<template>
  <div data-espacio="analista" class="flex flex-col gap-8">
    <CabeceraEspacio
      composicion="analista"
      :nombre="nombre"
      :rol="rol"
      :cargando="cargando"
    />

    <div class="grid gap-8 lg:grid-cols-2">
      <BloqueLista
        bloque="explorador"
        clave-titulo="workspace.explorer.title"
        clave-vacio="workspace.explorer.empty"
        :elementos="CONSULTAS_GUARDADAS"
        :cargando="cargando"
      >
        <template #accion>
          <NuxtLink
            :to="RUTA_EXPLORACION"
            data-accion-explorador
            class="inline-flex min-h-11 w-fit items-center gap-1.5 text-etiqueta text-corriente-pleno hover:underline"
            :class="ANILLO_FOCO"
          >
            <Icon name="lucide:list-filter" class="size-3.5 shrink-0" aria-hidden="true" />
            {{ t('workspace.explorer.action') }}
          </NuxtLink>
        </template>
      </BloqueLista>

      <BloqueLista
        bloque="exportaciones"
        clave-titulo="workspace.exports.title"
        clave-vacio="workspace.exports.empty"
        :elementos="EXPORTACIONES"
        :cargando="cargando"
      />
    </div>

    <BuscadorUnificado enfasis="normal" />

    <div class="grid gap-8 lg:grid-cols-2">
      <BloqueLista
        bloque="favoritos"
        clave-titulo="workspace.favorites.title"
        clave-vacio="workspace.favorites.empty"
        :elementos="FAVORITOS"
        :cargando="cargando"
      />

      <BloqueLista
        bloque="alertas"
        clave-titulo="workspace.alerts.title"
        clave-vacio="workspace.alerts.empty"
        :elementos="ALERTAS"
        :cargando="cargando"
      />
    </div>

    <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('workspace.sample.hint') }}
    </p>
  </div>
</template>
