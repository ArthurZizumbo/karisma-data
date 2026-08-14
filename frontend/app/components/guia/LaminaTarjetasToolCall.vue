<script setup lang="ts">
/**
 * Style-guide plate: the four contract states of a tool call card.
 *
 * The plate owns nothing but its samples: the card itself is the real
 * component, so the guide documents the shipped system and not a drawing of
 * it. If the card drifts, this plate drifts with it, which is the only way a
 * capture taken for A4 keeps saying something true about the product.
 *
 * The samples are frozen and the clock is a constant. A plate fed from the
 * live chat would produce a different image every run, and a capture of A4 has
 * to be reproducible byte for byte the day it is redone.
 *
 * `LaminaTarjetas.vue` (US-UX-09) already carries a conceptual chain of the
 * same four moments with a vocabulary of its own. It is read here as a
 * reference and deliberately not edited: it belongs to another User Story, and
 * the two galleries coexist during A4 by an accepted decision.
 */
import type { EstadoTarjeta, TarjetaToolCall } from '~/types/chat'

import { useI18n } from 'vue-i18n'

import ToolCallCard from '~/components/chat/ToolCallCard.vue'

/**
 * Instant every sample is measured against.
 *
 * Frozen rather than `Date.now()`: the elapsed time of the running sample has
 * to read the same in every capture, and a plate that printed a live clock
 * would change under the camera.
 */
const AHORA_FIJO = 1_755_100_000_000

/** The four contract states, in the order the plate walks them. */
const ESTADOS: readonly EstadoTarjeta[] = Object.freeze([
  'anuncio',
  'ejecucion',
  'resultado',
  'error',
])

/**
 * Deterministic samples, one per state.
 *
 * Typed as a total record of the contract state, so a state added to the
 * contract without a sample here fails to compile instead of quietly leaving
 * the gallery incomplete.
 */
const POR_ESTADO: Readonly<Record<EstadoTarjeta, TarjetaToolCall>> = Object.freeze({
  anuncio: {
    id: 'muestra-anuncio',
    estado: 'anuncio',
    herramienta: 'consultar_metrica',
    etiqueta: 'chat.toolCall.tool.consultar_metrica',
    transcurrido_ms: null,
    resultado: null,
    fuente: null,
    paso: null,
    iniciadaEnMs: AHORA_FIJO,
  },
  ejecucion: {
    id: 'muestra-ejecucion',
    estado: 'ejecucion',
    herramienta: 'consultar_metrica',
    etiqueta: 'chat.toolCall.tool.consultar_metrica',
    transcurrido_ms: null,
    resultado: null,
    fuente: null,
    paso: null,
    iniciadaEnMs: AHORA_FIJO - 1200,
  },
  resultado: {
    id: 'muestra-resultado',
    estado: 'resultado',
    herramienta: 'agregar_serie',
    etiqueta: 'chat.toolCall.tool.agregar_serie',
    transcurrido_ms: 1240,
    resultado: {
      columnas: ['chat.toolCall.column.close', 'chat.toolCall.column.coefficient'],
      filas: [
        ['2026-04', 1.19],
        ['2026-05', 1.22],
        ['2026-06', 1.28],
        ['2026-07', 1.31],
        ['2026-08', 1.24],
      ],
      cifra: '1.24',
    },
    fuente: 'catalogo.liquidez.coeficiente_cobertura',
    paso: null,
    iniciadaEnMs: AHORA_FIJO - 1240,
  },
  error: {
    id: 'muestra-error',
    estado: 'error',
    herramienta: 'consultar_catalogo',
    etiqueta: 'chat.toolCall.tool.consultar_catalogo',
    transcurrido_ms: 820,
    resultado: null,
    fuente: 'catalogo.derivados.exposicion_nocional',
    paso: 'recuperacion_de_datos',
    iniciadaEnMs: AHORA_FIJO - 820,
  },
})

/** Deterministic samples, one per state, frozen so captures are reproducible. */
const MUESTRAS: readonly TarjetaToolCall[] = Object.freeze(
  ESTADOS.map(estado => POR_ESTADO[estado]),
)

const { t } = useI18n()
</script>

<template>
  <section data-lamina="tarjetas-tool-call" class="flex flex-col gap-6">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.toolCall') }}
    </h2>

    <h3 class="text-titulo-3 text-corriente-pleno">
      {{ t('chat.toolCall.gallery.title') }}
    </h3>
    <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
      {{ t('chat.toolCall.gallery.caption') }}
    </p>

    <!--
      One capture anchor per state, set on the card itself. Putting it on a
      wrapper would double the number of elements carrying the contract state
      and make "there are four cards" ambiguous to anything that counts them.
    -->
    <ul class="grid items-start gap-6 md:grid-cols-2">
      <li v-for="muestra in MUESTRAS" :key="muestra.id">
        <ToolCallCard
          :id="`lamina-tool-call--${muestra.estado}`"
          :tarjeta="muestra"
          :ahora-ms="AHORA_FIJO"
          :desplegada-por-defecto="muestra.estado === 'resultado'"
        />
      </li>
    </ul>
  </section>
</template>
