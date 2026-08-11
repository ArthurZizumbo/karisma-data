<script setup lang="ts">
/**
 * Entry form of Karisma Data.
 *
 * The root publishes `data-estado`, which is the contract that turns the five
 * designed states of this screen into something verifiable. Four of them are
 * driven by the page -normal, loading, rejected credential, expired session-
 * and the fifth is produced here, because whether a field is empty is knowable
 * where the fields are and nowhere else.
 *
 * The message region keeps its height whether or not there is a message: a form
 * whose fields jump down when an error appears makes the reader lose the caret
 * exactly when they are about to retype.
 *
 * The two icons of the password toggle are `lucide:eye` and `lucide:lock`,
 * both already in the bundled inventory of the design system. A name assembled
 * in a binding is invisible to the icon scanner and would ship as an empty box
 * in the production build, which is why they are two literal elements and not
 * one ternary.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import type { AvisoAcceso, CredencialesAcceso, EstadoAcceso } from '~/types/sesion'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Designed state decided by the page. Never `campo-invalido`. */
  estado: EstadoAcceso
  /** Refusal to announce, or null when there is none. */
  aviso: AvisoAcceso | null
}>()

const emit = defineEmits<{
  /** The reader asked to enter with a complete pair of credentials. */
  enviar: [CredencialesAcceso]
}>()

const { t } = useI18n()

const usuario = ref('')
const contrasena = ref('')
const contrasenaVisible = ref(false)

/** True once the reader has tried to send at least once. */
const intentado = ref(false)

const cargando = computed(() => props.estado === 'cargando')
const faltaUsuario = computed(() => intentado.value && usuario.value.trim() === '')
const faltaContrasena = computed(() => intentado.value && contrasena.value === '')

/**
 * State published to the outside.
 *
 * Loading wins because it is the only one the reader can do nothing about, and
 * an empty field wins over a rejected credential because the reader is already
 * fixing that field.
 */
const estadoVisible = computed<EstadoAcceso>(() => {
  if (cargando.value) {
    return 'cargando'
  }
  if (faltaUsuario.value || faltaContrasena.value) {
    return 'campo-invalido'
  }
  return props.estado
})

/** Sends the pair, or refuses locally without touching the network. */
function enviar(): void {
  intentado.value = true
  if (usuario.value.trim() === '' || contrasena.value === '') {
    return
  }
  emit('enviar', { usuario: usuario.value.trim(), contrasena: contrasena.value })
}
</script>

<template>
  <form
    :data-estado="estadoVisible"
    :aria-busy="cargando"
    class="flex flex-col gap-5"
    novalidate
    @submit.prevent="enviar"
  >
    <p
      v-if="estadoVisible === 'sesion-expirada'"
      data-aviso="expirada"
      role="status"
      class="flex items-start gap-2 border-l-2 border-aviso pl-3 text-cuerpo text-corriente-medio"
    >
      <Icon name="lucide:clock" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
      <span>
        <span class="block text-titulo-3 text-corriente-pleno">{{ t('access.expired.title') }}</span>
        {{ t('access.expired.detail') }}
      </span>
    </p>

    <div class="flex flex-col gap-1">
      <label for="acceso-usuario" class="text-etiqueta text-corriente-pleno">
        {{ t('access.fields.username') }}
      </label>
      <input
        id="acceso-usuario"
        v-model="usuario"
        data-campo="usuario"
        type="text"
        name="username"
        autocomplete="username"
        autocapitalize="none"
        spellcheck="false"
        :disabled="cargando"
        :aria-invalid="faltaUsuario ? 'true' : undefined"
        :aria-describedby="faltaUsuario ? 'acceso-usuario-error' : undefined"
        class="min-h-9 w-full border bg-ground px-3 text-cuerpo text-corriente-pleno"
        :class="[faltaUsuario ? 'border-error' : 'border-corriente-medio', ANILLO_FOCO]"
      >
      <p
        v-if="faltaUsuario"
        id="acceso-usuario-error"
        data-error="usuario"
        class="flex items-center gap-1 text-micro text-error"
      >
        <Icon name="lucide:circle-alert" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('access.errors.usernameRequired') }}
      </p>
    </div>

    <div class="flex flex-col gap-1">
      <label for="acceso-contrasena" class="text-etiqueta text-corriente-pleno">
        {{ t('access.fields.password') }}
      </label>
      <div class="flex items-stretch gap-1">
        <input
          id="acceso-contrasena"
          v-model="contrasena"
          data-campo="contrasena"
          :type="contrasenaVisible ? 'text' : 'password'"
          name="password"
          autocomplete="current-password"
          :disabled="cargando"
          :aria-invalid="faltaContrasena ? 'true' : undefined"
          :aria-describedby="faltaContrasena ? 'acceso-contrasena-error' : undefined"
          class="min-h-9 w-full border bg-ground px-3 text-cuerpo text-corriente-pleno"
          :class="[faltaContrasena ? 'border-error' : 'border-corriente-medio', ANILLO_FOCO]"
        >
        <button
          data-accion="ver-contrasena"
          type="button"
          :aria-pressed="contrasenaVisible"
          :aria-label="contrasenaVisible ? t('access.fields.hidePassword') : t('access.fields.showPassword')"
          class="flex min-h-9 items-center border border-corriente-medio px-3 text-corriente-pleno hover:bg-ground-alt"
          :class="ANILLO_FOCO"
          @click="contrasenaVisible = !contrasenaVisible"
        >
          <Icon v-if="contrasenaVisible" name="lucide:lock" class="size-4 shrink-0" aria-hidden="true" />
          <Icon v-else name="lucide:eye" class="size-4 shrink-0" aria-hidden="true" />
        </button>
      </div>
      <p
        v-if="faltaContrasena"
        id="acceso-contrasena-error"
        data-error="contrasena"
        class="flex items-center gap-1 text-micro text-error"
      >
        <Icon name="lucide:circle-alert" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('access.errors.passwordRequired') }}
      </p>
    </div>

    <!-- Height reserved whether or not there is a message: nothing below moves. -->
    <div class="min-h-10">
      <p
        v-if="aviso !== null"
        :data-aviso="aviso.tono"
        role="alert"
        class="flex items-start gap-2 text-cuerpo"
        :class="aviso.tono === 'sin-permiso' ? 'text-aviso' : 'text-error'"
      >
        <!--
          Colour never travels alone: in light mode the semantic marks separate
          by dE 13.4 under simulated dichromacy, so the shape is what carries
          the difference between a refused credential and a closed door.
        -->
        <Icon
          v-if="aviso.tono === 'sin-permiso'"
          name="lucide:lock"
          class="mt-0.5 size-4 shrink-0"
          aria-hidden="true"
        />
        <Icon v-else name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0" aria-hidden="true" />
        {{ t(aviso.clave) }}
      </p>
    </div>

    <button
      data-accion="entrar"
      type="submit"
      :disabled="cargando"
      class="flex min-h-9 min-w-32 items-center justify-center gap-2 border border-corriente-pleno bg-corriente-pleno px-3 text-etiqueta text-ground hover:bg-corriente-medio hover:border-corriente-medio disabled:border-grid disabled:bg-ground-alt disabled:text-corriente-apagado"
      :class="ANILLO_FOCO"
    >
      <Icon
        v-if="cargando"
        name="lucide:loader-circle"
        class="size-4 shrink-0 animate-spin motion-reduce:animate-none"
        aria-hidden="true"
      />
      {{ cargando ? t('access.actions.entering') : t('access.actions.enter') }}
    </button>
  </form>
</template>
