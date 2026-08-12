<script setup lang="ts">
/**
 * US-026, level 3 - the twenty four observed months and the projected one.
 *
 * A real `<table>` and not a grid of `<div>`: the chart above is a picture with
 * no structure, so this is the only place where a screen reader can walk the
 * figures row by row. The `<caption>` says what the table is and `scope` ties
 * every cell to its header.
 *
 * The projected row is marked with a word and not only with a shade: it is the
 * one row of the table that is not a measurement, and colour alone cannot carry
 * that difference.
 *
 * The explorer link closes the chain. Three levels of progressive disclosure
 * that end in a dead end would be three levels of nothing: the link carries the
 * physical column of the metric as the search term, so the reader lands on the
 * catalogue entry the figure came from.
 */
import type { HistoricoMetrica, MetricaTablero, Proyeccion } from '~/types/prediccion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { ANILLO_FOCO } from '~/utils/foco'
import { formatearMes, formatearCifra, formatearCambio } from '~/utils/formatoTablero'
import { destinoExplorador } from '~/utils/metricasTablero'
import { variacionPorcentual } from '~/utils/proyeccion'

const props = defineProps<{
  metrica: MetricaTablero
  historico: HistoricoMetrica
  proyeccion: Proyeccion
}>()

const { t, locale } = useI18n()

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

interface FilaDetalle {
  readonly clave: string
  readonly mes: string
  readonly valor: string
  readonly variacion: string
  readonly proyectada: boolean
}

const filas = computed<readonly FilaDetalle[]>(() => {
  const puntos = [...props.historico.puntos, props.proyeccion.proyectado]
  const hueco = t('forecast.table.gap')

  return puntos.map((punto, indice) => {
    const anterior = puntos[indice - 1]
    const cambio
      = anterior === undefined ? null : variacionPorcentual(anterior.valor, punto.valor)
    return {
      clave: punto.mes,
      mes: formatearMes(punto.mes, idioma.value),
      valor: formatearCifra(punto.valor, props.metrica.unidad, idioma.value) ?? hueco,
      variacion: formatearCambio(cambio, idioma.value) ?? hueco,
      proyectada: indice === puntos.length - 1,
    }
  })
})

const destino = computed(() => destinoExplorador(props.metrica))
</script>

<template>
  <div data-nivel="3" class="flex flex-col gap-3">
    <div class="max-w-full overflow-x-auto">
      <table class="w-full border-collapse text-cuerpo">
        <caption class="pb-2 text-left text-micro text-corriente-tenue">
          {{ t('forecast.table.caption', { metric: t(props.metrica.claveEtiqueta) }) }}
        </caption>
        <thead>
          <tr>
            <th
              scope="col"
              class="border-b border-corriente-apagado py-1 text-left text-etiqueta uppercase text-corriente-tenue"
            >
              {{ t('forecast.table.month') }}
            </th>
            <th
              scope="col"
              class="border-b border-corriente-apagado py-1 text-right text-etiqueta uppercase text-corriente-tenue"
            >
              {{ t('forecast.table.value') }}
            </th>
            <th
              scope="col"
              class="border-b border-corriente-apagado py-1 text-right text-etiqueta uppercase text-corriente-tenue"
            >
              {{ t('forecast.table.change') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="fila in filas"
            :key="fila.clave"
            :data-fila="fila.proyectada ? 'proyectada' : 'observada'"
            class="border-b border-grid"
          >
            <th scope="row" class="py-1 text-left font-normal text-corriente-pleno">
              {{ fila.mes }}
              <span v-if="fila.proyectada" class="text-micro text-corriente-tenue">
                {{ t('forecast.table.projectedRow') }}
              </span>
            </th>
            <td class="py-1 text-right tabular-nums text-corriente-medio">
              {{ fila.valor }}
            </td>
            <td class="py-1 text-right tabular-nums text-corriente-medio">
              {{ fila.variacion }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <NuxtLink
      data-accion="explorar"
      :to="destino"
      class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
      :class="ANILLO_FOCO"
    >
      {{ t('forecast.action.explore') }}
    </NuxtLink>
  </div>
</template>
