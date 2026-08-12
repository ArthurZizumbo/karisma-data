<script setup lang="ts">
/**
 * US-026, level 2 - twenty four observed months and the projected one.
 *
 * Drawn with a plain `<svg>` and not with ECharts, and that is a decision and
 * not a shortcut: twenty five points do not need a charting engine, and the
 * engine is installed by US-025 on the same day, so depending on it would be a
 * cross blockage for a picture of five lines of geometry.
 *
 * The projected segment is told apart by THREE channels and never by colour
 * alone: a dashed stroke, a hollow marker and a textual legend. Colour carries
 * no information here on purpose; the system rule is explicit about it.
 *
 * The figure also exists for a reader who cannot see it: `role="img"` with a
 * `<title>` that names it and a `<desc>` that states the numbers, both taken
 * from the catalogues so the summary is not Spanish only.
 */
import type { HistoricoMetrica, MetricaTablero, Proyeccion, PuntoMensual } from '~/types/prediccion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { formatearMes, formatearCifra, formatearCambio } from '~/utils/formatoTablero'

const props = defineProps<{
  metrica: MetricaTablero
  historico: HistoricoMetrica
  proyeccion: Proyeccion
  /** Id of the `<title>` node, so the parent can wire aria-labelledby. */
  idTitulo: string
}>()

const { t, locale } = useI18n()

/** Drawing box. Fixed units with a fluid width: the viewBox does the scaling. */
const ANCHO = 640
const ALTO = 200
const MARGEN_IZQUIERDO = 56
const MARGEN_DERECHO = 16
const MARGEN_SUPERIOR = 16
const MARGEN_INFERIOR = 28

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

/** Id of the textual summary, derived so the parent only has to pass one id. */
const idResumen = computed(() => `${props.idTitulo}-resumen`)

interface PuntoDibujado {
  readonly mes: string
  readonly valor: number
  readonly x: number
  readonly y: number
}

const observados = computed<readonly PuntoMensual[]>(() => props.historico.puntos)

const trazado = computed(() => {
  const puntos = [...observados.value, props.proyeccion.proyectado]
  const valores = puntos.map(punto => punto.valor)
  const minimo = Math.min(...valores)
  const maximo = Math.max(...valores)
  // A flat series would divide by zero; drawing it along the middle is the
  // honest picture of "nothing moved" and keeps the markers on screen.
  const rango = maximo - minimo === 0 ? 1 : maximo - minimo
  const ancho = ANCHO - MARGEN_IZQUIERDO - MARGEN_DERECHO
  const alto = ALTO - MARGEN_SUPERIOR - MARGEN_INFERIOR
  const paso = puntos.length > 1 ? ancho / (puntos.length - 1) : 0

  const dibujados: PuntoDibujado[] = puntos.map((punto, indice) => ({
    mes: punto.mes,
    valor: punto.valor,
    x: MARGEN_IZQUIERDO + indice * paso,
    y: MARGEN_SUPERIOR + alto - ((punto.valor - minimo) / rango) * alto,
  }))

  return { dibujados, minimo, maximo }
})

/** `points` attribute of a polyline. */
function trazo(puntos: readonly PuntoDibujado[]): string {
  return puntos.map(punto => `${punto.x.toFixed(2)},${punto.y.toFixed(2)}`).join(' ')
}

const puntosObservados = computed(() => trazado.value.dibujados.slice(0, -1))
const puntoProyectado = computed(() => trazado.value.dibujados.at(-1)!)
const ultimoObservado = computed(() => puntosObservados.value.at(-1)!)

const cifra = (valor: number): string =>
  formatearCifra(valor, props.metrica.unidad, idioma.value) ?? ''

const titulo = computed(() =>
  t('forecast.chart.title', { metric: t(props.metrica.claveEtiqueta) }),
)

const resumen = computed(() =>
  t('forecast.chart.summary', {
    metric: t(props.metrica.claveEtiqueta),
    points: observados.value.length,
    from: formatearMes(observados.value[0]?.mes ?? '', idioma.value),
    to: formatearMes(props.proyeccion.ultimo.mes, idioma.value),
    min: cifra(trazado.value.minimo),
    max: cifra(trazado.value.maximo),
    last: cifra(props.proyeccion.ultimo.valor),
    next: formatearMes(props.proyeccion.proyectado.mes, idioma.value),
    projected: cifra(props.proyeccion.proyectado.valor),
    change: formatearCambio(props.proyeccion.variacionPct, idioma.value) ?? '',
  }),
)
</script>

<template>
  <figure class="flex flex-col gap-2">
    <svg
      data-grafica="proyeccion"
      role="img"
      :aria-labelledby="`${props.idTitulo} ${idResumen}`"
      :viewBox="`0 0 ${ANCHO} ${ALTO}`"
      class="h-48 w-full"
    >
      <title :id="props.idTitulo">{{ titulo }}</title>
      <desc :id="idResumen">{{ resumen }}</desc>

      <line
        :x1="MARGEN_IZQUIERDO"
        :y1="ALTO - MARGEN_INFERIOR"
        :x2="ANCHO - MARGEN_DERECHO"
        :y2="ALTO - MARGEN_INFERIOR"
        class="stroke-grid"
        stroke-width="1"
      />

      <polyline
        data-tramo="observado"
        :points="trazo(puntosObservados)"
        fill="none"
        class="stroke-serie-1"
        stroke-width="2"
        stroke-linejoin="round"
      />
      <circle
        v-for="punto in puntosObservados"
        :key="punto.mes"
        :cx="punto.x"
        :cy="punto.y"
        r="2.5"
        class="fill-serie-1"
      />

      <polyline
        data-tramo="proyectado"
        :points="trazo([ultimoObservado, puntoProyectado])"
        fill="none"
        class="stroke-serie-1"
        stroke-width="2"
        stroke-dasharray="7 5"
        stroke-linecap="round"
      />
      <circle
        data-marcador="proyectado"
        :cx="puntoProyectado.x"
        :cy="puntoProyectado.y"
        r="5.5"
        fill="none"
        class="stroke-serie-1"
        stroke-width="2"
      />

      <text
        :x="MARGEN_IZQUIERDO - 8"
        :y="MARGEN_SUPERIOR + 4"
        text-anchor="end"
        class="fill-corriente-tenue text-micro"
      >
        {{ cifra(trazado.maximo) }}
      </text>
      <text
        :x="MARGEN_IZQUIERDO - 8"
        :y="ALTO - MARGEN_INFERIOR"
        text-anchor="end"
        class="fill-corriente-tenue text-micro"
      >
        {{ cifra(trazado.minimo) }}
      </text>
      <text
        :x="MARGEN_IZQUIERDO"
        :y="ALTO - 8"
        text-anchor="start"
        class="fill-corriente-tenue text-micro"
      >
        {{ formatearMes(observados[0]?.mes ?? '', idioma) }}
      </text>
      <text
        :x="ANCHO - MARGEN_DERECHO"
        :y="ALTO - 8"
        text-anchor="end"
        class="fill-corriente-tenue text-micro"
      >
        {{ formatearMes(props.proyeccion.proyectado.mes, idioma) }}
      </text>
    </svg>

    <figcaption>
      <ul data-leyenda class="flex flex-wrap gap-4 text-micro text-corriente-tenue">
        <li class="flex items-center gap-2">
          <svg viewBox="0 0 24 8" class="h-2 w-6" aria-hidden="true">
            <line x1="0" y1="4" x2="24" y2="4" class="stroke-serie-1" stroke-width="2" />
          </svg>
          {{ t('forecast.chart.legendObserved') }}
        </li>
        <li class="flex items-center gap-2">
          <svg viewBox="0 0 24 12" class="h-3 w-6" aria-hidden="true">
            <line
              x1="0"
              y1="6"
              x2="16"
              y2="6"
              class="stroke-serie-1"
              stroke-width="2"
              stroke-dasharray="5 4"
            />
            <circle cx="20" cy="6" r="3.5" fill="none" class="stroke-serie-1" stroke-width="2" />
          </svg>
          {{ t('forecast.chart.legendProjected') }}
        </li>
      </ul>
    </figcaption>
  </figure>
</template>
