<script setup lang="ts">
/**
 * Demonstration profile control.
 *
 * Every button mints a real session through `POST /api/auth/demo`. The role is
 * never changed in the browser: the guard decides on the server, and a role
 * held in client state would leave that decision running on the old token.
 *
 * The control disappears without the demonstration flag, because a deployment
 * with the door closed answers 404 and offering it would advertise something
 * that cannot work.
 *
 * The role literals are the vocabulary of the backend and travel unchanged as
 * `data-rol-demo`; only their reading name is translated. The attribute is not
 * `data-rol` on purpose: that one belongs to the entry screen, and two controls
 * answering the same selector is how a test starts measuring the wrong one.
 */
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import type { MotivoFalloAcceso, RolUsuario } from '~/types/sesion'
import { useRolDemo } from '~/composables/useRolDemo'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()
const route = useRoute()
const { rolActual, roles, disponible, cambiando, motivoFallo, entrarComoRol } = useRolDemo()

/** One shape per profile, so the four are told apart without reading. */
const ICONO_POR_ROL: Readonly<Record<RolUsuario, string>> = {
  operativo: 'lucide:search',
  analista: 'lucide:chart-line',
  directivo: 'lucide:gauge',
  admin: 'lucide:shield-check',
}

/**
 * How each failure is announced.
 *
 * A closed door is a configuration and not a fault of the reader, so it reuses
 * the wording the entry screen already publishes for it.
 */
const CLAVE_POR_MOTIVO: Readonly<Record<MotivoFalloAcceso, string>> = {
  'credenciales': 'roleSwitch.failed',
  'demo-deshabilitado': 'access.errors.demoDisabled',
  'servidor': 'roleSwitch.failed',
}

async function elegir(rol: RolUsuario): Promise<void> {
  if (rol === rolActual.value || cambiando.value) {
    return
  }

  const resultado = await entrarComoRol(rol, route.path)
  if (resultado.tipo === 'fallo' || resultado.ruta === route.path) {
    return
  }

  // The new profile cannot open the screen the reader is standing on, so the
  // guard would refuse it in place. Landing on their own space is the same
  // decision the guard makes, taken before the refusal is painted.
  await navigateTo(resultado.ruta)
}
</script>

<template>
  <div v-if="disponible" class="flex items-center gap-2">
    <div
      data-selector-rol
      role="group"
      :aria-label="t('roleSwitch.groupLabel')"
      class="flex items-center rounded-md border border-corriente-apagado"
    >
      <Icon
        name="lucide:user-round-cog"
        class="ml-2 size-4 shrink-0 text-corriente-tenue"
        aria-hidden="true"
      />
      <button
        v-for="rol in roles"
        :key="rol"
        type="button"
        :data-rol-demo="rol"
        :disabled="cambiando"
        :aria-pressed="rolActual === rol"
        :aria-label="rolActual === rol
          ? t('roleSwitch.current', { profile: t(`authz.role.${rol}`) })
          : t('roleSwitch.enterAs', { profile: t(`authz.role.${rol}`) })"
        :title="t(`authz.role.${rol}`)"
        class="flex items-center gap-1 px-2 py-1 text-etiqueta text-corriente-tenue disabled:text-corriente-apagado aria-pressed:bg-corriente-pleno aria-pressed:text-ground"
        :class="ANILLO_FOCO"
        @click="elegir(rol)"
      >
        <Icon :name="ICONO_POR_ROL[rol]" class="size-4 shrink-0" aria-hidden="true" />
        <span class="sr-only">{{ t(`authz.role.${rol}`) }}</span>
      </button>
    </div>

    <span
      v-if="motivoFallo !== null"
      data-fallo-rol
      role="alert"
      class="hidden text-micro text-error md:inline"
    >
      {{ t(CLAVE_POR_MOTIVO[motivoFallo]) }}
    </span>
  </div>
</template>
