<script setup lang="ts">
/**
 * Screen of the conversational agent.
 *
 * The page owns the draft question and nothing else: the request, the framing
 * of the stream, the thread and the cancellation belong to `useChatStream`.
 * What is decided here is only what the reader sees, and the two decisions
 * worth naming are these.
 *
 * The honesty band is permanent and lives in this file rather than in a
 * component of its own, because `components/chat/` belongs to US-028 and to
 * US-024. It is drawn in every state -idle, generating, cancelled- so the
 * warning cannot disappear exactly when the scripted content appears, and its
 * key comes from the provider constant: the day the provider changes, the
 * sentence changes with it instead of being deleted.
 *
 * Two blocks are delimited with comments because they are provisional by
 * agreement, not by neglect: the textual history is replaced by
 * `HistorialConversacion` (US-028) and the error notice by `AvisoError`
 * (US-024), each of them an import plus one line inside its own block, so the
 * substitution is verifiable with `git diff -U0` and never a rewrite of the
 * page.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import ContextoPanelContextoTablero from '~/components/contexto/PanelContextoTablero.vue'
import { useChatStream } from '~/composables/useChatStream'
import { CLAVE_AVISO_DEMO, CLAVE_ESTADO_CHAT, CLAVE_PASO, PROVEEDOR_DE_CHAT } from '~/types/chat'
import { ANILLO_FOCO } from '~/utils/foco'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
// useRoute and not useTituloDeRuta: that composable titles a screen with its
// branch of the A3 map, which is what a screen still made of scaffolding needs.
// This one is implemented and titles itself with what it does.
const route = useRoute()

const { estado, hilo, ultimoError, enviar, detener } = useChatStream()

/**
 * Lines of the skeleton drawn while the first fragment is on its way.
 *
 * Three and not a spinner: the shape of a paragraph is what is coming, and
 * three lines fit inside the height the log already reserves, so the block
 * never grows when the text lands on top of it.
 */
const LINEAS_DE_ESPERA = 3

/** Question being typed. The only state this page owns. */
const pregunta = ref('')

const generando = computed(() => estado.value === 'generando')

/** Copy of the current state, or null for the one state that has none. */
const claveDeEstado = computed(() => CLAVE_ESTADO_CHAT[estado.value])

/** Key of the honesty band, decided by the provider behind the stream. */
const claveDelAviso = CLAVE_AVISO_DEMO[PROVEEDOR_DE_CHAT]

const puedePreguntar = computed(() => pregunta.value.trim() !== '')

/** Sends the draft, or refuses locally without touching the network. */
async function preguntar(): Promise<void> {
  const mensaje = pregunta.value.trim()
  if (mensaje === '') {
    return
  }
  pregunta.value = ''
  await enviar(mensaje)
}
</script>

<template>
  <section :data-ruta="route.path" class="flex flex-col gap-6">
    <CabeceraPantalla :titulo="t('chat.page.title')" :descripcion="t('chat.page.description')" />

    <p
      data-prueba="aviso-demo"
      role="note"
      class="flex items-start gap-2 border-l-2 border-aviso bg-ground-alt px-4 py-2 text-etiqueta text-corriente-medio"
    >
      <Icon name="lucide:info" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
      {{ t(claveDelAviso) }}
    </p>

    <!--
      `aria-live="off"` on the log is deliberate. Forty fragments a second in a
      polite region reads every one of them aloud; the three transitions of the
      turn are announced once each by the status region below.
    -->
    <section
      data-prueba="hilo"
      role="log"
      aria-live="off"
      :aria-busy="generando"
      :data-estado="estado"
      class="flex min-h-24 flex-col gap-3 border border-grid bg-ground-alt p-4"
    >
      <!--
        "There is no conversation yet" and "the answer has not started to
        arrive" are two different truths, and the log used to tell the first
        one during the second: between the submit and the first token the
        server is already answering, so the empty state was contradicting the
        Detener button drawn right below it.

        The skeleton is exactly `min-h-24` minus the `p-4` of the log, so the
        block that waits occupies the height the log already reserves and the
        first fragment writes over it instead of pushing the form down.
      -->
      <p
        v-if="hilo.length === 0 && !generando"
        data-prueba="hilo-vacio"
        class="text-cuerpo text-corriente-medio"
      >
        {{ t('chat.page.emptyState') }}
      </p>

      <div
        v-else-if="hilo.length === 0"
        data-prueba="hilo-esperando"
        aria-busy="true"
        class="flex h-16 flex-col gap-3"
      >
        <!--
          The sentence is for the reader who does not see the bars. It is not
          announced twice: this region is `aria-live="off"` and the status
          below already says the turn is generating.
        -->
        <span class="sr-only">{{ t('chat.page.waitingFirstToken') }}</span>
        <span
          v-for="linea in LINEAS_DE_ESPERA"
          :key="linea"
          aria-hidden="true"
          class="h-3 animate-pulse rounded-sm bg-grid motion-reduce:animate-none"
          :class="linea === LINEAS_DE_ESPERA ? 'w-2/3' : 'w-full'"
        />
      </div>

      <!-- fallback US-023: lo sustituye US-028 -->
      <article
        v-for="item in hilo"
        :key="item.id"
        :data-item="item.tipo"
        class="flex flex-col gap-1"
      >
        <template v-if="item.tipo === 'tarjeta'">
          <p
            :data-estado-tarjeta="item.tarjeta.estado"
            class="border-l-2 border-info pl-3 text-etiqueta text-corriente-pleno"
          >
            {{ t('chat.stream.toolCallFallback', { tool: item.tarjeta.herramienta }) }}
          </p>
          <p
            v-if="item.tarjeta.resultado?.cifra"
            data-prueba="cifra"
            class="pl-3 text-titulo-3 text-corriente-pleno"
          >
            {{ item.tarjeta.resultado.cifra }}
          </p>
          <p v-if="item.tarjeta.fuente" data-prueba="fuente" class="pl-3 text-micro text-corriente-medio">
            {{ item.tarjeta.fuente }}
          </p>
        </template>
        <p v-else class="max-w-(--medida-maxima) text-cuerpo text-corriente-pleno">
          {{ item.texto }}
        </p>
      </article>
      <!-- fin del fallback US-023: lo sustituye US-028 -->
    </section>

    <!-- fallback US-023: lo sustituye US-024 -->
    <p
      v-if="ultimoError !== null"
      data-prueba="aviso-error"
      role="alert"
      class="flex flex-wrap items-center gap-2 border-l-2 border-error pl-3 text-cuerpo text-error"
    >
      <Icon name="lucide:circle-alert" class="size-4 shrink-0" aria-hidden="true" />
      <span>{{ t('chat.stream.errorFallback') }}</span>
      <span data-prueba="paso-fallido" class="text-etiqueta">
        {{ t(CLAVE_PASO[ultimoError.paso]) }}
      </span>
      <span data-prueba="codigo-error" class="text-micro text-corriente-medio">
        {{ ultimoError.codigo }}
      </span>
    </p>
    <!-- fin del fallback US-023: lo sustituye US-024 -->

    <form class="flex flex-col gap-2" novalidate @submit.prevent="preguntar">
      <label for="chat-pregunta" class="text-etiqueta text-corriente-pleno">
        {{ t('chat.controls.inputLabel') }}
      </label>
      <div class="flex items-stretch gap-2">
        <input
          id="chat-pregunta"
          v-model="pregunta"
          data-prueba="pregunta"
          type="text"
          name="pregunta"
          autocomplete="off"
          :placeholder="t('chat.controls.inputPlaceholder')"
          :disabled="generando"
          class="min-h-9 w-full border border-corriente-medio bg-ground px-3 text-cuerpo text-corriente-pleno disabled:border-grid disabled:text-corriente-apagado"
          :class="ANILLO_FOCO"
        >
        <!--
          The stop button is in the DOM from the first tick of the generation and
          never next to the send one. Waiting for the first token would remove it
          during the second in which the reader most wants to abort.
        -->
        <button
          v-if="generando"
          data-prueba="detener"
          type="button"
          class="flex min-h-9 min-w-32 items-center justify-center gap-2 border border-corriente-pleno px-3 text-etiqueta text-corriente-pleno hover:bg-ground-alt"
          :class="ANILLO_FOCO"
          @click="detener"
        >
          <Icon name="lucide:square" class="size-4 shrink-0" aria-hidden="true" />
          {{ t('chat.controls.stop') }}
        </button>
        <button
          v-else
          data-prueba="enviar"
          type="submit"
          :disabled="!puedePreguntar"
          class="flex min-h-9 min-w-32 items-center justify-center gap-2 border border-corriente-pleno bg-corriente-pleno px-3 text-etiqueta text-ground hover:border-corriente-medio hover:bg-corriente-medio disabled:border-grid disabled:bg-ground-alt disabled:text-corriente-apagado"
          :class="ANILLO_FOCO"
        >
          {{ t('chat.controls.send') }}
        </button>
      </div>
    </form>

    <p
      v-if="claveDeEstado !== null"
      data-prueba="estado-stream"
      role="status"
      class="flex items-center gap-2 text-micro text-corriente-medio"
    >
      <Icon
        v-if="generando"
        name="lucide:loader-circle"
        class="size-3 shrink-0 animate-spin motion-reduce:animate-none"
        aria-hidden="true"
      />
      {{ t(claveDeEstado) }}
    </p>

    <ContextoPanelContextoTablero />
  </section>
</template>
