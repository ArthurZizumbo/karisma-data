<script lang="ts">
import type { EstadoTarjeta, ItemHilo, MotivoCierre } from '~/types/chat'

import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import ToolCallCard from '~/components/chat/ToolCallCard.vue'

/**
 * States a card can no longer leave once it reaches them.
 *
 * The reducer of US-023 applies a precedence in which these two are final, so
 * anything else is a card that is still in flight.
 */
const ESTADOS_TERMINALES: readonly EstadoTarjeta[] = Object.freeze(['resultado', 'error'])

/**
 * Ids of the cards that never reached a terminal state.
 *
 * It lives in the module and not in the component because it is what drives
 * `interrumpida`, and a cancellation that marked every card -including the
 * ones that had already answered- would turn "you stopped it" into "it failed"
 * on a query that did resolve.
 *
 * @param hilo - Thread items in arrival order.
 * @returns The ids of the cards still running, in thread order.
 */
export function tarjetasEnVuelo(hilo: readonly ItemHilo[]): readonly string[] {
  const enVuelo: string[] = []
  for (const item of hilo) {
    if (item.tipo === 'tarjeta' && !ESTADOS_TERMINALES.includes(item.tarjeta.estado)) {
      enVuelo.push(item.id)
    }
  }
  return enVuelo
}
</script>

<script setup lang="ts">
/**
 * The conversation thread, with card updates that cost the same at 200 and 800.
 *
 * Three techniques carry the restriction and none of them is redundant. The
 * `key` is the stable id of the item, so an insertion does not reconcile the
 * tail by position. The reducer replaces the object of the affected card and
 * keeps the identity of every other one, and Vue compares props with `===`, so
 * an untouched child never enters the update queue. `v-memo` on the row is the
 * belt: it cuts the re-render even if somebody later passes an extra prop by
 * accident.
 *
 * The clock is here and not in the card. One `setInterval` feeds every card in
 * flight and switches itself off when none is left; N cards with N timers is
 * the classic way a long chat turns into a fan. Cards that already resolved
 * are handed a frozen value instead of the tick, so one running query does not
 * repaint the two hundred that already answered.
 *
 * The imports and `tarjetasEnVuelo` sit in the plain `script` block above
 * because a module level function cannot be exported from `script setup`, and
 * the test of the cancellation calls it directly rather than inferring it from
 * the markup.
 */

/** Renders the conversation thread keeping card updates O(1) in its length. */
interface HistorialConversacionProps {
  /** Discriminated thread items in arrival order; owned by useChatStream (US-023). */
  hilo: readonly ItemHilo[]
  /** Closing reason of the stream, or null while it is open. */
  motivoCierre: MotivoCierre | null
}

/**
 * Cadence of the shared clock.
 *
 * 250 ms is four readings a second: enough for the elapsed time to visibly
 * advance, and slow enough that the tenth of a second it prints never lands
 * mid-change.
 */
const PULSO_MS = 250

/**
 * Instant handed to a card whose clock the server already closed.
 *
 * A constant, so the prop of a resolved card is identical on every tick and
 * Vue skips it. The value is never read: a resolved card takes its elapsed
 * time from `transcurrido_ms`.
 */
const RELOJ_DETENIDO = 0

/** No card was in flight, so no card was interrupted. */
const NINGUNA: ReadonlySet<string> = new Set<string>()

const props = defineProps<HistorialConversacionProps>()

const ahoraMs = ref(Date.now())

let reloj: ReturnType<typeof setInterval> | null = null

const enVuelo = computed(() => new Set(tarjetasEnVuelo(props.hilo)))

/** True while there is something whose elapsed time the client has to count. */
const contando = computed(() => props.motivoCierre === null && enVuelo.value.size > 0)

/**
 * Cards the reader stopped before they resolved.
 *
 * Only on a cancellation: a stream that ended in error already published a
 * typed failure, and a stream that completed left nothing in flight.
 */
const interrumpidas = computed(() =>
  props.motivoCierre === 'cancelado' ? enVuelo.value : NINGUNA,
)

/**
 * Instant a given item is rendered against.
 *
 * A card still running reads the shared tick; everything else reads the frozen
 * constant, which is what keeps a thread of two hundred resolved cards from
 * repainting four times a second while one query is open.
 *
 * @param item - Thread item being rendered.
 * @returns The tick for a card in flight, or the frozen instant.
 */
function relojDe(item: ItemHilo): number {
  return item.tipo === 'tarjeta' && enVuelo.value.has(item.id) ? ahoraMs.value : RELOJ_DETENIDO
}

function detenerReloj(): void {
  if (reloj !== null) {
    clearInterval(reloj)
    reloj = null
  }
}

function arrancarReloj(): void {
  if (reloj !== null) {
    return
  }
  ahoraMs.value = Date.now()
  reloj = setInterval(() => {
    ahoraMs.value = Date.now()
  }, PULSO_MS)
}

// Started from `onMounted` and never from setup: on the server there is no
// frame to paint and an interval created there would outlive the render.
onMounted(() => {
  if (contando.value) {
    arrancarReloj()
  }
})

watch(contando, (sigue) => {
  if (sigue) {
    arrancarReloj()
    return
  }
  detenerReloj()
})

// A reader who walks away mid-answer leaves the interval behind otherwise, and
// it keeps writing into a ref nobody renders.
onBeforeUnmount(detenerReloj)
</script>

<template>
  <div data-prueba="historial" class="flex flex-col gap-3">
    <div
      v-for="item in hilo"
      :key="item.id"
      v-memo="[item, relojDe(item), interrumpidas.has(item.id)]"
      :data-item="item.tipo"
    >
      <ToolCallCard
        v-if="item.tipo === 'tarjeta'"
        :tarjeta="item.tarjeta"
        :ahora-ms="relojDe(item)"
        :interrumpida="interrumpidas.has(item.id)"
      />
      <!--
        The answer of the assistant is long prose and takes the token that
        `main.css` declares for exactly this use: `--text-cuerpo-amplio`, 16/26,
        commented there as "Parrafo largo: ayuda y respuesta del asistente".
        `text-cuerpo` is 14/21, the density of the dense interface -a table, a
        label, a control- and reading a paragraph at it was a token declared and
        not applied. The measure stays capped at `--medida-maxima`: 68
        characters at 16 px, not at 14.
      -->
      <p v-else class="max-w-(--medida-maxima) text-cuerpo-amplio text-corriente-pleno">
        {{ item.texto }}
      </p>
    </div>
  </div>
</template>
