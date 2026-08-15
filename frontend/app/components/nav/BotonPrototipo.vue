<script setup lang="ts">
/**
 * Entry to one of the seven high fidelity prototypes.
 *
 * Rebuilt in the diagram world: the number is a node, the branch of the A3 map
 * is the connector it hangs from, and the scope reads as a state on the current
 * ramp rather than as two coloured pills. The measured version wrapped every
 * entry in a card with the same border weight as everything else on the page,
 * which is what made the index read as a grid of identical boxes.
 *
 * The scope wording is load bearing and not decoration: the A4 rubric asks for
 * a three state scope table, and a prototype that claims data it does not have
 * costs more than one that declares itself empty.
 *
 * With the demonstration door open the card mints the session of its own
 * profile before navigating, so one click from the index lands inside the
 * screen with a real token. Without the flag it is the link it always was: the
 * guard bounces the reader to the entry screen, which now says why and takes
 * them back. The card never decides permissions -it opens a session and lets
 * the guard decide- and it never swallows a click meant for a new tab.
 */
import { useI18n } from 'vue-i18n'
import type { EstadoAlcance, Prototipo, RolSugerido } from '~/types/navegacion'
import { useRolDemo } from '~/composables/useRolDemo'
import { ANILLO_FOCO } from '~/utils/foco'
import { MOTIVO_SESION_REQUERIDA, PARAMETRO_DESTINO } from '~/utils/guarda'
import { RUTA_ACCESO } from '~/utils/navegacion'

const props = defineProps<{ prototipo: Prototipo }>()

const { t } = useI18n()

/** Honest scope wording. Nothing here promises data that does not exist yet. */
const CLAVE_ALCANCE: Record<EstadoAlcance, string> = {
  'navegable-con-datos': 'prototype.scope.withData',
  'navegable-sin-datos': 'prototype.scope.withoutData',
  'roadmap': 'prototype.scope.roadmap',
}

/** Scope on the luminance ramp: lit means live, dim means declared. */
const TONO_ALCANCE: Record<EstadoAlcance, string> = {
  'navegable-con-datos': 'text-corriente-pleno',
  'navegable-sin-datos': 'text-corriente-tenue',
  'roadmap': 'text-corriente-apagado',
}

const CLAVE_ROL: Record<RolSugerido, string> = {
  operativo: 'prototype.profile.operations',
  analista: 'prototype.profile.analyst',
  directivo: 'prototype.profile.executive',
  admin: 'prototype.profile.administration',
}

const { disponible, entrarComoRol } = useRolDemo()

/**
 * Opens the prototype with the session of its own profile.
 *
 * Bound in the CAPTURE phase, and that is the whole reason this works. The
 * anchor is a `NuxtLink`, and the click handler vue-router puts on it calls
 * `preventDefault()` itself before navigating. Bound the ordinary way this
 * handler runs after that one, sees `defaultPrevented` already true, returns,
 * and the card degrades into the plain link it used to be: the reader lands on
 * the entry form and no session is ever minted. Running first inverts the
 * order. `guardEvent` of vue-router returns early on an event that is already
 * prevented, so calling `preventDefault()` here also stops its navigation and
 * only one of the two moves the reader.
 *
 * A click carrying a modifier, or one that is not the main button, is left
 * alone: opening in a new tab is a legitimate way to read an index of seven
 * screens, and intercepting it would take that away. Returning without
 * preventing is enough -vue-router skips those clicks by the same rule- so the
 * browser gets the native behaviour of a real `href`.
 *
 * @param evento - Click on the card.
 */
async function abrirConPerfil(evento: MouseEvent): Promise<void> {
  if (
    !disponible
    || evento.defaultPrevented
    || evento.button !== 0
    || evento.metaKey
    || evento.ctrlKey
    || evento.shiftKey
    || evento.altKey
  ) {
    return
  }

  evento.preventDefault()
  const resultado = await entrarComoRol(props.prototipo.rolSugerido, props.prototipo.ruta)

  if (resultado.tipo === 'fallo') {
    // The door answered no. The reader is handed to the entry screen with the
    // route they asked for, which is the same bounce the guard would produce.
    await navigateTo({
      path: RUTA_ACCESO,
      query: {
        [PARAMETRO_DESTINO]: props.prototipo.ruta,
        motivo: MOTIVO_SESION_REQUERIDA,
      },
    })
    return
  }

  await navigateTo(resultado.ruta)
}
</script>

<template>
  <NuxtLink
    :to="prototipo.ruta"
    :data-prototipo="prototipo.numero"
    :data-alcance="prototipo.alcance"
    class="group flex h-full items-start gap-3 border-t border-grid py-3 hover:border-corriente-medio"
    :class="ANILLO_FOCO"
    @click.capture="abrirConPerfil"
  >
    <span
      class="mt-0.5 flex size-6 shrink-0 items-center justify-center border border-corriente-medio font-mono text-micro text-corriente-pleno group-hover:bg-corriente-pleno group-hover:text-ground"
      aria-hidden="true"
    >
      {{ prototipo.numero }}
    </span>

    <span class="flex min-w-0 flex-col gap-0.5">
      <span class="text-titulo-3 text-corriente-pleno">
        {{ t(prototipo.claveNombre) }}
      </span>
      <span class="text-cuerpo text-corriente-tenue">{{ t(prototipo.claveRama) }}</span>
      <span class="mt-1 flex flex-wrap items-center gap-x-3 text-micro">
        <span :class="TONO_ALCANCE[prototipo.alcance]">
          {{ t(CLAVE_ALCANCE[prototipo.alcance]) }}
        </span>
        <span class="text-corriente-tenue">{{ t(CLAVE_ROL[prototipo.rolSugerido]) }}</span>
      </span>
    </span>
  </NuxtLink>
</template>
