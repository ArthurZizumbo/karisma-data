<script setup lang="ts">
/**
 * Turn level failure of the assistant, told with its step and its code.
 *
 * There are two errors on this screen and they are not alternatives. A tool
 * that breaks paints its own card in its fourth state (US-028), by id, inside
 * the list of messages; this notice says the *turn* could not be finished, once,
 * at the foot of the thread. Keeping them apart is what lets a reader with two
 * cards in flight see which one failed and still be told that the answer is not
 * coming.
 *
 * There is NO retry control here, and that is a written agreement (cut #4) and
 * not an oversight. `recuperable` travels in the event, so the day the cut is
 * lifted a button is wired to a boolean that is already tested; until then the
 * way out is stated as a sentence. A disabled button would be offering the
 * retry, so the component renders none: no `button`, no `a[href]`, no
 * `[role=button]`.
 *
 * The level a refusal demanded is NOT carried by the contract -five frozen
 * fields and none of them is it- so the caller supplies it. When it does not,
 * the generic copy is used instead of printing an empty slot, which is the only
 * reason `permissionGeneric` exists.
 *
 * Two things this notice owns on the screen, both of them decided rather than
 * inherited. It is the ONLY `role="alert"`: the card of a failed tool call
 * paints its own detail inside the log with a non announcing role, because the
 * backend emits `tool_call(estado:"error")` and the turn `error` on the same
 * tick and two alerts in one tick have a screen reader read one failure twice.
 * And it is the only place where the failed step is written at reading level,
 * because it is the only one that survives a failure with no card behind it:
 * an HTTP 403 or a broken transport produces a typed error and no `tool_call`
 * event at all, so a step written only in the card would disappear exactly
 * when it is the only thing there is to say. `data-prueba="paso-fallido"`
 * therefore stays here and the card carries `paso-fallido-tarjeta`.
 */
import type { PasoDelStream } from '~/types/chat'
import type { RolUsuario } from '~/types/sesion'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { CLAVE_PASO } from '~/types/chat'

const props = defineProps<{
  /** Stream step that failed; drives the step label. */
  paso: PasoDelStream
  /** Error family: recoverable failure or insufficient permission. */
  clase: 'recuperable' | 'permiso'
  /** Stable error code, mirrored from the backend vocabulary. */
  codigo: string
  /** i18n key of the human message; never literal text. */
  mensajeClave: string
  /** Whether the same request could succeed on a second attempt. */
  recuperable: boolean
  /** Required access level, supplied by the caller; never sent by the backend. */
  nivelRequerido?: RolUsuario | null
}>()

/** Copy used when a refusal cannot name the level it demanded. */
const CLAVE_PERMISO_GENERICA = 'chat.error.message.permissionGeneric'

const { t } = useI18n()

const esPermiso = computed(() => props.clase === 'permiso')

const titulo = computed(() =>
  esPermiso.value ? 'chat.error.title.permission' : 'chat.error.title.recoverable',
)

/**
 * Key of the message, with the one substitution the contract cannot make.
 *
 * A refusal whose level nobody supplied would render `{nivel}` raw or an empty
 * gap, so the generic copy takes over. Everything else is the key the event
 * carried, untouched: rewriting it here would be a second vocabulary.
 */
const claveDelMensaje = computed(() =>
  esPermiso.value && (props.nivelRequerido === undefined || props.nivelRequerido === null)
    ? CLAVE_PERMISO_GENERICA
    : props.mensajeClave,
)

/**
 * The message, with the level named in the reader's language.
 *
 * The role travels as a slug and is translated here rather than interpolated
 * raw: `analista` inside an English sentence is the same defect as a literal
 * string in the template.
 */
const mensaje = computed(() =>
  props.nivelRequerido === undefined || props.nivelRequerido === null
    ? t(claveDelMensaje.value)
    : t(claveDelMensaje.value, { nivel: t(`authz.role.${props.nivelRequerido}`) }),
)

/**
 * Border and text tokens of each family.
 *
 * The two variants have to differ by more than their words: a reader who does
 * not read the whole sentence still has to be able to tell the failure that is
 * worth retrying from the one that never will be.
 */
const CLASES_POR_FAMILIA: Readonly<Record<'recuperable' | 'permiso', string>> = Object.freeze({
  recuperable: 'border-aviso',
  permiso: 'border-error',
})

const CLASES_DE_ICONO: Readonly<Record<'recuperable' | 'permiso', string>> = Object.freeze({
  recuperable: 'text-aviso',
  permiso: 'text-error',
})

const ICONO: Readonly<Record<'recuperable' | 'permiso', string>> = Object.freeze({
  recuperable: 'lucide:circle-alert',
  permiso: 'lucide:lock',
})
</script>

<template>
  <section
    data-prueba="aviso-error"
    role="alert"
    :data-recuperable="String(props.recuperable)"
    :data-clase="props.clase"
    :class="CLASES_POR_FAMILIA[props.clase]"
    class="flex max-w-(--medida-maxima) flex-col gap-2 border-l-2 bg-ground-alt py-3 pl-4 pr-3"
  >
    <p class="flex items-start gap-2 text-etiqueta text-corriente-pleno">
      <Icon
        :name="ICONO[props.clase]"
        :class="CLASES_DE_ICONO[props.clase]"
        class="mt-0.5 size-4 shrink-0"
        aria-hidden="true"
      />
      {{ t(titulo) }}
    </p>

    <p data-prueba="mensaje-error" class="text-cuerpo text-corriente-medio">
      {{ mensaje }}
    </p>

    <p
      v-if="props.recuperable"
      data-prueba="via-de-salida"
      class="text-cuerpo text-corriente-medio"
    >
      {{ t('chat.error.action.resend') }}
    </p>

    <p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-micro text-corriente-apagado">
      <span data-prueba="paso-fallido">{{ t(CLAVE_PASO[props.paso]) }}</span>
      <span data-prueba="codigo-error">{{ props.codigo }}</span>
    </p>
  </section>
</template>
