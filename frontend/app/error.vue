<script setup lang="ts">
import type { NuxtError } from '#app'
import { computed } from 'vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { RUTA_INDICE } from '~/utils/navegacion'

const props = defineProps<{ error: NuxtError }>()

/** Cause stated in the reader language, never the raw stack trace. */
const CAUSAS: Record<number, string> = {
  403: 'Tu perfil no tiene permiso para abrir esta pantalla.',
  404: 'La dirección solicitada no corresponde a ninguna pantalla del prototipo.',
  500: 'El servidor no pudo construir la pantalla.',
}

const GENERICA = 'La pantalla no pudo abrirse por un error inesperado.'

// statusCode is optional in NuxtError: an error thrown without a code arrived
// here as undefined and was used to index anyway. nuxt typecheck caught it, and
// until now it was not running in any gate.
const causa = computed(() =>
  props.error.statusCode === undefined
    ? GENERICA
    : CAUSAS[props.error.statusCode] ?? GENERICA,
)

function volverAlIndice(): void {
  clearError({ redirect: RUTA_INDICE })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-surface font-sans text-ink">
    <FranjaAlcance />

    <main class="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-4 px-6 py-12">
      <p class="text-sm text-muted">
        Error {{ error.statusCode }}
      </p>
      <h1 class="font-display text-2xl text-primary-dark">
        No se pudo mostrar esta pantalla
      </h1>
      <p class="text-ink">
        {{ causa }}
      </p>
      <p class="text-sm text-muted">
        Puedes volver al índice de prototipos y entrar por otra pantalla. Si el error se repite,
        anótalo con la dirección que intentabas abrir.
      </p>
      <div>
        <button
          type="button"
          class="rounded-md bg-primary px-4 py-2 text-surface hover:bg-primary-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          @click="volverAlIndice"
        >
          Volver al índice de prototipos
        </button>
      </div>
    </main>
  </div>
</template>
