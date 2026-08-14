<script setup lang="ts">
/**
 * One tool call, drawn as an auditable card in its four contract states.
 *
 * The component is pure with respect to its props: no fetch, no store and no
 * timer of its own. The clock ticks in the container -one interval for every
 * card in flight, never one per card- and arrives here as `ahoraMs`. That is
 * what keeps a long conversation from turning into a fan, and it is also what
 * makes the card trivially renderable in the style guide with a frozen
 * instant.
 *
 * The rule the card exists for: a figure is never shown without saying where
 * it came from. The citation lives at level 1 and is never folded, the figure
 * is never folded either -hiding it would annul the acceptance criterion that
 * justifies the User Story- and a card that ends in error shows no figure at
 * all.
 *
 * State is told by icon plus text and never by colour alone. In dichromacy the
 * resolved and the failed badge are the same hue, and a reader would take a
 * query that failed for one that was audited.
 */
import type { EstadoTarjeta, TarjetaToolCall } from '~/types/chat'

import { computed, ref, useId, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { CLAVE_PASO } from '~/types/chat'
import { ANILLO_FOCO } from '~/utils/foco'

/** Renders one tool call as an auditable card in its four contract states. */
interface ToolCallCardProps {
  /** Card state as produced by the SSE reducer; owned by useChatStream (US-023). */
  tarjeta: TarjetaToolCall
  /** Shared clock tick in ms, injected by the parent; the card keeps no timer. */
  ahoraMs: number
  /** True when the stream was cancelled before this card reached a terminal state. */
  interrumpida?: boolean
  /** Opens the result table on mount; the gallery in /guia uses it for captures. */
  desplegadaPorDefecto?: boolean
}

/** Emitted when the reader expands or collapses the result table. */
interface ToolCallCardEmits {
  (evento: 'plegado', abierta: boolean): void
}

/** Badge of one state: its copy, its shape and its semantic colour. */
interface AspectoDeEstado {
  /** Translation key of the state name. Written literally so the scan sees it. */
  readonly clave: string
  /** Icon of the state. The channel no dichromacy loses. */
  readonly icono: string
  /** Semantic colour, which never travels alone. */
  readonly color: string
}

/**
 * Badge of each contract state.
 *
 * The keys are spelled out instead of composed from the state so that the
 * contract check of `contratos.spec.ts` can read them: a key assembled at run
 * time is invisible to that scan and would ship missing copy.
 */
const ASPECTO: Readonly<Record<EstadoTarjeta, AspectoDeEstado>> = Object.freeze({
  anuncio: {
    clave: 'chat.toolCall.state.announced',
    icono: 'lucide:circle-dashed',
    color: 'text-corriente-tenue',
  },
  ejecucion: {
    clave: 'chat.toolCall.state.running',
    icono: 'lucide:loader-circle',
    color: 'text-info',
  },
  resultado: {
    clave: 'chat.toolCall.state.done',
    icono: 'lucide:circle-check',
    color: 'text-ok',
  },
  error: {
    clave: 'chat.toolCall.state.failed',
    icono: 'lucide:circle-alert',
    color: 'text-error',
  },
})

/**
 * Badge of a card the reader stopped before it resolved.
 *
 * It is not a fifth value of `estado`: the contract has four, and
 * `data-estado-tool-call` keeps carrying the contract one. "You stopped it"
 * and "it failed" are different things, and painting the first as the second
 * is the interface lie this badge exists to prevent.
 */
const ASPECTO_INTERRUMPIDA: AspectoDeEstado = Object.freeze({
  clave: 'chat.toolCall.state.interrupted',
  icono: 'lucide:square',
  color: 'text-corriente-medio',
})

/**
 * Icon of each tool of the scripted provider.
 *
 * Only names already declared in `icon.clientBundle.icons` are used: this map
 * is read through a binding, and the icon scanner cannot see a name it does
 * not find written literally in a source. Adding one here without adding it to
 * the inventory ships an empty box in production and a correct icon in dev.
 */
const ICONO_POR_HERRAMIENTA: Readonly<Record<string, string>> = Object.freeze({
  consultar_metrica: 'lucide:gauge',
  agregar_serie: 'lucide:chart-line',
  consultar_catalogo: 'lucide:book-open',
})

/** Icon of a tool the map does not know yet. */
const ICONO_GENERICO = 'lucide:bot'

/** Icon of a figure that can be traced back to the catalogue. */
const ICONO_FUENTE = 'lucide:database'

/** Icon of a resolved card that arrived without a catalogue field. */
const ICONO_SIN_FUENTE = 'lucide:triangle-alert'

/** Icon of a citation still pending because the card has not resolved. */
const ICONO_FUENTE_PENDIENTE = 'lucide:circle-dashed'

/**
 * Rows of the mini-table shown before the disclosure.
 *
 * Three is what fits next to a figure without turning the thread into a
 * spreadsheet; the rest is one click away and the count is in the label, so
 * nobody has to expand in order to learn there is more.
 */
const FILAS_VISIBLES = 3

/** Milliseconds in the unit the elapsed time is read in. */
const SEGUNDO_MS = 1000

/** Decimals of the elapsed time. One is enough to show that it advances. */
const DECIMALES = 1

/*
 * Height budget of the card, and why its root reserves `min-h-38`.
 *
 * Measured at 1440x900 the card used to SHRINK on `anuncio` -> `ejecucion`,
 * 146 px down to 131 px, and the log of the page has neither a height of its
 * own nor a scroller, so every transition dragged the Detener button
 * vertically at the exact second the reader was aiming at it.
 *
 * Adding up the tokens of `main.css` (`--spacing` 4 px, so p-3 = 12, gap-2 =
 * 8, gap-1 = 4; `--text-cuerpo` 14/21, `--text-etiqueta` 12/16, `--text-micro`
 * 11/15, icons 20, 16 and 12):
 *
 *   frame     1 px border x 2 + 12 px padding x 2                   = 26
 *   header    max(icon 20, cuerpo 21, micro 15)                     = 21
 *   state     badge 16, plus gap-1 4 + announcement 21 in `anuncio` = 16 | 41
 *   progress  h-0.5, drawn only while the query runs                =  2
 *   failure   the hint alone, in micro, only in `error`             = 15
 *   source    max(icon 12, micro 15)                                = 15
 *   detail    border-t 1 + pt-1 4 + summary in micro                = 20
 *
 * Branch by branch, with gap-2 between children:
 *
 *   anuncio       26 + (21 + 41 + 15 + 20)      + 3 x 8 = 147
 *   ejecucion     26 + (21 + 16 + 2 + 15 + 20)  + 4 x 8 = 132
 *   interrumpida  26 + (21 + 16 + 15 + 20)      + 3 x 8 = 122
 *   error         26 + (21 + 16 + 15 + 15 + 20) + 4 x 8 = 145
 *   resultado     26 + (21 + 16 + R + 15 + 20)  + 4 x 8 = 130 + R
 *
 * The model lands within 3 px of the browser -147 and 132 modelled against 146
 * and 131 measured- so the floor goes just above the tallest branch that is
 * not an answer: `min-h-38` is 38 x --spacing = 152 px, five over `anuncio`
 * and a multiple of the 8 px rhythm the card already gaps with. With it the
 * three states before the answer render at exactly the same height, the shrink
 * is gone and nothing below the card moves while the query runs.
 *
 * `resultado` still grows, and it should: that growth IS the progressive
 * disclosure. What it can no longer do is bounce, because a floor only ever
 * lets the box get taller. For the C1 turn the answer adds 106 px -figure 41,
 * gap 8, one-row table 57- so what is left is a single jump of 152 -> 236.
 *
 * What the floor does not cover, written down instead of hidden: under roughly
 * 500 px of card width the announcement wraps to a second line and `anuncio`
 * passes 152 px again. Sizing the floor for the wrapped case would leave 36 px
 * of blank inside `ejecucion` at the 1440 px the screen is captured at, so the
 * residual is accepted at phone widths and paid nowhere else.
 */

const props = withDefaults(defineProps<ToolCallCardProps>(), {
  interrumpida: false,
  desplegadaPorDefecto: false,
})

const emit = defineEmits<ToolCallCardEmits>()

const { t } = useI18n()

const idNombre = useId()
const idTabla = useId()

const abierta = ref(props.desplegadaPorDefecto)

/**
 * True once the card can no longer change state.
 *
 * It decides whose clock is authoritative. While the card runs the server may
 * not have emitted a single `transcurrido_ms` yet and the reader still needs
 * to see that something advances, so the client counts; once the card
 * resolves, the server figure is the one that gets read.
 */
const resuelta = computed(
  () => props.tarjeta.estado === 'resultado' || props.tarjeta.estado === 'error',
)

/** True while the query is actually running, which a cancelled one is not. */
const corriendo = computed(() => props.tarjeta.estado === 'ejecucion' && !props.interrumpida)

const aspecto = computed(() =>
  props.tarjeta.estado === 'ejecucion' && props.interrumpida
    ? ASPECTO_INTERRUMPIDA
    : ASPECTO[props.tarjeta.estado],
)

const iconoDeHerramienta = computed(
  () => ICONO_POR_HERRAMIENTA[props.tarjeta.herramienta] ?? ICONO_GENERICO,
)

const transcurridoMs = computed(() => {
  const delServidor = props.tarjeta.transcurrido_ms
  if (resuelta.value && delServidor !== null) {
    return delServidor
  }
  // Clamped at zero: a card rebuilt after a reconnection can carry an instant
  // later than the tick the parent last wrote.
  return Math.max(0, props.ahoraMs - props.tarjeta.iniciadaEnMs)
})

/**
 * Elapsed time in seconds, formatted here and not by the catalogue.
 *
 * `toFixed` and not a localized number formatter on purpose: the value is the
 * duration of a technical trace, and a decimal comma in one language and a
 * point in the other would make the same card read as two different figures.
 */
const segundos = computed(() => (transcurridoMs.value / SEGUNDO_MS).toFixed(DECIMALES))

const filas = computed(() => props.tarjeta.resultado?.filas ?? [])

const filasVisibles = computed(() =>
  abierta.value ? filas.value : filas.value.slice(0, FILAS_VISIBLES),
)

const hayFilasOcultas = computed(() => filas.value.length > FILAS_VISIBLES)

/** True when the missing citation is a defect and not merely a pending one. */
const faltaLaFuente = computed(() => resuelta.value && props.tarjeta.fuente === null)

const iconoDeFuente = computed(() => {
  if (props.tarjeta.fuente !== null) {
    return ICONO_FUENTE
  }
  return faltaLaFuente.value ? ICONO_SIN_FUENTE : ICONO_FUENTE_PENDIENTE
})

/**
 * Name of the failed step, already translated, or null when there is none.
 *
 * The raw contract value is never interpolated: `verificacion_de_permiso` on
 * screen, in both languages, is exactly the defect `CLAVE_PASO` exists to
 * prevent.
 *
 * The state is part of the guard and not only the field: the contract carries
 * `paso` for a card that ends in error and for no other one, and reading that
 * rule here rather than in the template keeps it in a single place.
 */
const pasoFallido = computed(() =>
  props.tarjeta.estado !== 'error' || props.tarjeta.paso === null
    ? null
    : t(CLAVE_PASO[props.tarjeta.paso]),
)

function alternar(): void {
  abierta.value = !abierta.value
  emit('plegado', abierta.value)
}

// The gallery of the guide mounts the same card with the disclosure already
// open. Without this the prop would be read once and a plate that swapped its
// sample would keep the previous fold.
watch(
  () => props.desplegadaPorDefecto,
  (porDefecto) => {
    abierta.value = porDefecto
  },
)
</script>

<template>
  <article
    :data-estado-tool-call="tarjeta.estado"
    :data-interrumpida="interrumpida ? 'true' : undefined"
    data-prueba="tarjeta-tool-call"
    role="group"
    :aria-labelledby="idNombre"
    class="flex min-h-38 flex-col gap-2 border border-grid bg-ground-alt p-3"
  >
    <header class="flex flex-wrap items-center gap-x-3 gap-y-1">
      <Icon
        :name="iconoDeHerramienta"
        data-prueba="icono-herramienta"
        class="size-5 shrink-0 text-corriente-medio"
        aria-hidden="true"
      />
      <p :id="idNombre" data-prueba="nombre-herramienta" class="text-cuerpo text-corriente-pleno">
        {{ t(tarjeta.etiqueta) }}
      </p>
      <!--
        The elapsed time is NOT a live region, and it used to be one. It is
        rewritten at the cadence of the shared clock, four times a second, and
        `role="status"` carries an implicit `aria-live="polite"`; polite defers
        instead of merging, so the queue drains the moment the reader goes idle
        and the duration gets read out tick by tick. It is the same reasoning
        with which the page refuses a polite log for forty fragments a second,
        reintroduced at 4 Hz. The time stays visible and in the accessibility
        tree as the ordinary paragraph it is; that the turn is running is
        announced once, by the status region of the page.
      -->
      <p
        data-prueba="transcurrido"
        class="ml-auto font-mono text-micro tabular-nums text-corriente-tenue"
      >
        {{ t('chat.toolCall.elapsed', { seconds: segundos }) }}
      </p>
    </header>

    <!--
      The state of the card is not a live region, and that is a decision and
      not an omission. Three transitions per card reads as bounded until the
      contract cap of five tool calls a turn turns it into fifteen
      announcements stacked on top of the ones the turn already makes. And the
      thread that holds this card is a `role="log"` with `aria-live="off"`,
      chosen so the history is browsed and not recited: a polite region nested
      inside it would undo that decision one level down. What the reader has to
      be told without asking -the turn is generating, the turn stopped, the
      turn failed- is said once, by the status region and by the error notice.
    -->
    <div data-prueba="estado-tarjeta" class="flex flex-col gap-1">
      <p
        data-prueba="insignia-estado"
        class="inline-flex w-fit items-center gap-1.5 text-etiqueta"
        :class="aspecto.color"
      >
        <Icon
          :name="aspecto.icono"
          class="size-4 shrink-0"
          :class="corriendo ? 'animate-spin motion-reduce:animate-none' : ''"
          aria-hidden="true"
        />
        {{ t(aspecto.clave) }}
      </p>

      <p
        v-if="tarjeta.estado === 'anuncio'"
        data-prueba="anuncio"
        class="max-w-(--medida-maxima) text-cuerpo text-corriente-tenue"
      >
        {{ t('chat.toolCall.announce') }}
      </p>
    </div>

    <!-- Progress is drawn only while there is progress to draw. -->
    <div
      v-if="corriendo"
      data-prueba="progreso"
      class="h-0.5 w-full overflow-hidden bg-grid"
      aria-hidden="true"
    >
      <span class="block h-full w-1/3 animate-pulse bg-info motion-reduce:animate-none" />
    </div>

    <div v-if="tarjeta.resultado !== null" class="flex flex-col gap-2">
      <!-- Level 1. The figure is the acceptance criterion: it is never folded. -->
      <p v-if="tarjeta.resultado.cifra !== null" data-prueba="cifra" class="flex flex-col">
        <span class="text-micro text-corriente-tenue">{{ t('chat.toolCall.result.figure') }}</span>
        <span class="font-mono text-titulo-2 tabular-nums text-corriente-pleno">
          {{ tarjeta.resultado.cifra }}
        </span>
      </p>

      <div v-if="filas.length > 0" class="overflow-x-auto border border-grid">
        <table :id="idTabla" data-prueba="tabla-resultado" class="w-full border-collapse text-left">
          <caption class="sr-only">
            {{ t('chat.toolCall.result.rows', { count: filas.length }) }}
          </caption>
          <thead>
            <tr class="bg-ground">
              <th
                v-for="columna in tarjeta.resultado.columnas"
                :key="columna"
                scope="col"
                class="px-2 py-1 text-etiqueta text-corriente-pleno"
              >
                {{ t(columna) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(fila, indice) in filasVisibles"
              :key="indice"
              data-fila
              class="border-t border-grid"
            >
              <td
                v-for="(celda, columna) in fila"
                :key="columna"
                class="px-2 py-1 font-mono text-dato tabular-nums text-corriente-pleno"
              >
                {{ celda }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Level 2. A button and not a div: the fold has to be reachable by keyboard. -->
      <button
        v-if="hayFilasOcultas"
        type="button"
        data-prueba="plegable"
        :aria-expanded="abierta ? 'true' : 'false'"
        :aria-controls="idTabla"
        class="inline-flex w-fit items-center gap-1 text-etiqueta text-corriente-medio hover:text-corriente-pleno"
        :class="ANILLO_FOCO"
        @click="alternar"
      >
        <Icon
          name="lucide:chevron-right"
          class="size-3 shrink-0"
          :class="abierta ? 'rotate-90' : ''"
          aria-hidden="true"
        />
        {{ abierta ? t('chat.toolCall.result.collapse') : t('chat.toolCall.result.expand', { count: filas.length }) }}
      </button>
    </div>

    <!--
      The failure of a card interrupts nobody: `role="note"`, never
      `role="alert"`. The turn notice (`AvisoError`) is the one that says the
      answer is not coming, it fires on the same tick as this block, and two
      alerts in one tick have a screen reader read a single failure twice.

      The step is not spelled here either. The backend publishes it in both
      events, so the same step used to be written twice with two different
      wordings. The one that survives at reading level is the notice's, because
      it is the only one that still exists when there is no card behind the
      failure -an HTTP 403 or a broken transport produces a typed error and no
      `tool_call` at all-, while the card keeps its own wording in the
      technical detail below: one click away for the auditor, and outside the
      accessibility tree while that disclosure stays closed.
    -->
    <p
      v-if="tarjeta.estado === 'error'"
      data-prueba="fallo"
      role="note"
      class="max-w-(--medida-maxima) text-micro text-corriente-medio"
    >
      {{ t('chat.toolCall.error.hint') }}
    </p>

    <!--
      Level 1 as well, and never folded: a figure whose source is not written
      next to it is the hallucination this card exists to make visible.
    -->
    <p
      data-prueba="fuente"
      class="flex items-center gap-1 text-micro"
      :class="faltaLaFuente ? 'text-aviso' : 'text-corriente-tenue'"
    >
      <Icon :name="iconoDeFuente" class="size-3 shrink-0" aria-hidden="true" />
      {{ tarjeta.fuente === null ? t('chat.toolCall.source.missing') : t('chat.toolCall.source.cited', { source: tarjeta.fuente }) }}
    </p>

    <!-- Level 3: what an auditor asks for and a reader never needs. -->
    <details data-prueba="detalle-tecnico" class="border-t border-grid pt-1">
      <summary class="cursor-pointer text-micro text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('chat.toolCall.detail.title') }}
      </summary>
      <p class="mt-1 font-mono text-micro text-corriente-tenue">
        {{ t('chat.toolCall.detail.tool', { tool: tarjeta.herramienta }) }}
      </p>
      <p class="font-mono text-micro text-corriente-tenue">
        {{ t('chat.toolCall.detail.field', { field: tarjeta.fuente ?? tarjeta.id }) }}
      </p>
      <!--
        `paso-fallido-tarjeta` and not `paso-fallido`: the notice owns that
        name, both components live on the same screen, and a spec that mounts
        the whole page had two elements answering to one selector.
      -->
      <p
        v-if="pasoFallido !== null"
        data-prueba="paso-fallido-tarjeta"
        class="font-mono text-micro text-corriente-tenue"
      >
        {{ t('chat.toolCall.error.step', { step: pasoFallido }) }}
      </p>
    </details>
  </article>
</template>
