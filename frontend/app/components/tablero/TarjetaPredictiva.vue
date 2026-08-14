<script setup lang="ts">
/**
 * US-026, level 1 - one predictive card.
 *
 * Two properties of this file are the User Story itself, and both are readable
 * from the props alone.
 *
 * The first is honesty. There is NO prop carrying the text of a method: the
 * card receives `proyeccion` and derives the label with `etiquetaMetodo`, which
 * is the only function that knows the templates. There is therefore no place in
 * the tree where somebody could hand this card a sentence the computation did
 * not produce, which is the defect the whole mechanism exists to close.
 *
 * The second is the absence of a layout shift. The card renders the SAME five
 * `[data-caja]` boxes with the SAME class attribute in every state, and only
 * their content changes: the title shows the real metric name while loading,
 * the figure and the change carry a filler inside the very same typographic
 * paragraph, the method label is clamped to two lines and the skeleton spends
 * exactly two, and the button exists in all four states, disabled outside the
 * ready one. A skeleton with a height of its own is what makes the card grow
 * when the data lands, and that is what these boxes are for.
 */
import type { EstadoTarjeta, MetricaId, MetricaTablero, Proyeccion } from '~/types/prediccion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { ANILLO_FOCO } from '~/utils/foco'
import { formatearMes, formatearCifra, formatearCambio } from '~/utils/formatoTablero'
import { etiquetaMetodo, MINIMO_PUNTOS } from '~/utils/proyeccion'

const props = defineProps<{
  metrica: MetricaTablero
  /** The projection, or null when there is nothing to project. */
  proyeccion: Proyeccion | null
  estado: EstadoTarjeta
  abierta: boolean
  /** Id of the heading, so the revealed panel can be named by this card. */
  idTitulo: string
  /** Id of the panel this card controls, for aria-controls. */
  idPanel: string
}>()

defineEmits<{ alternar: [metricaId: MetricaId] }>()

const { t, locale } = useI18n()

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

const listo = computed(() => props.estado === 'listo' && props.proyeccion !== null)

const valor = computed(() =>
  props.proyeccion === null
    ? null
    : formatearCifra(props.proyeccion.proyectado.valor, props.metrica.unidad, idioma.value),
)

const unidad = computed(() =>
  props.metrica.unidad === 'millones-mxn' ? t('forecast.unit.millionsMxn') : '',
)

const variacion = computed(() =>
  props.proyeccion === null
    ? null
    : formatearCambio(props.proyeccion.variacionPct, idioma.value),
)

const contra = computed(() =>
  props.proyeccion === null
    ? ''
    : t('forecast.projection.change', {
        month: formatearMes(props.proyeccion.ultimo.mes, idioma.value),
      }),
)

/** Green for a rise and red for a fall, always next to the sign Intl writes. */
const claseVariacion = computed(() => {
  if (props.proyeccion === null || props.proyeccion.variacionPct === 0) {
    return 'text-corriente-medio'
  }
  return props.proyeccion.variacionPct > 0 ? 'text-ok' : 'text-error'
})

const etiqueta = computed(() =>
  props.proyeccion === null
    ? ''
    : etiquetaMetodo(props.proyeccion.metodo, idioma.value, (clave, parametros) =>
        t(clave, parametros),
      ),
)
</script>

<template>
  <article
    :data-tarjeta="props.metrica.id"
    :data-estado="props.estado"
    data-nivel="1"
    :aria-busy="props.estado === 'cargando' ? 'true' : undefined"
    class="flex flex-col gap-2 rounded-lg border border-grid bg-ground-alt p-4"
  >
    <div data-caja="titulo">
      <h3 :id="props.idTitulo" class="font-display text-titulo-3 text-corriente-pleno">
        {{ t(props.metrica.claveEtiqueta) }}
      </h3>
    </div>

    <p data-caja="valor" class="whitespace-nowrap text-dato tabular-nums text-corriente-pleno">
      <template v-if="listo && valor !== null">
        {{ valor }}<span
          v-if="unidad !== ''"
          class="text-etiqueta text-corriente-medio"
        >&nbsp;{{ unidad }}</span>
      </template>
      <span
        v-else
        aria-hidden="true"
        class="inline-block w-28 rounded-sm bg-grid"
        :class="props.estado === 'cargando' ? 'animate-pulse' : 'opacity-0'"
      >&nbsp;</span>
    </p>

    <p data-caja="variacion" class="text-cuerpo text-corriente-medio">
      <template v-if="listo && variacion !== null">
        <span :class="claseVariacion">{{ variacion }}</span> {{ contra }}
      </template>
      <template v-else-if="props.estado === 'vacio'">
        {{ t('forecast.state.emptyTitle') }}
      </template>
      <template v-else-if="props.estado === 'error'">
        {{ t('forecast.state.errorTitle') }}
      </template>
      <span
        v-else
        aria-hidden="true"
        class="inline-block w-20 rounded-sm bg-grid animate-pulse"
      >&nbsp;</span>
    </p>

    <p data-caja="metodo" class="line-clamp-2 text-micro text-corriente-tenue">
      <template v-if="listo">
        {{ etiqueta }}
      </template>
      <template v-else-if="props.estado === 'vacio'">
        {{ t('forecast.state.emptyHint', { minimum: MINIMO_PUNTOS }) }}
      </template>
      <template v-else-if="props.estado === 'error'">
        {{ t('forecast.state.errorHint') }}
      </template>
      <template v-else>
        <span aria-hidden="true" class="block animate-pulse rounded-sm bg-grid">&nbsp;</span>
        <span aria-hidden="true" class="block animate-pulse rounded-sm bg-grid">&nbsp;</span>
      </template>
    </p>

    <div data-caja="accion" class="flex">
      <button
        type="button"
        data-accion-revelacion
        data-nivel-destino="2"
        :disabled="!listo"
        :aria-disabled="!listo"
        :aria-expanded="props.abierta"
        :aria-controls="props.idPanel"
        class="inline-flex min-h-11 w-fit items-center rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno disabled:text-corriente-apagado"
        :class="ANILLO_FOCO"
        @click="$emit('alternar', props.metrica.id)"
      >
        {{ props.abierta ? t('forecast.action.collapse') : t('forecast.action.expand') }}
      </button>
    </div>
  </article>
</template>
