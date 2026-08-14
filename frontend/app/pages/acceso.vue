<script setup lang="ts">
/**
 * Entry screen of Karisma Data.
 *
 * It owns the state machine of the five designed states and nothing else: the
 * request, the cookie and the token belong to `useSesion` and to Nitro, and the
 * fields belong to the form.
 *
 * The message the reader sees is never the one the backend sent. The 401 of the
 * API carries a Spanish `detail` fixed by the acceptance criteria, and this
 * interface is bilingual: what crosses is a reason, and the key is resolved
 * here, so a reader in English is told "Incorrect credentials" even though the
 * server said it in Spanish.
 *
 * Two of the reasons are not designed states. A server failure and a switched
 * off demonstration door are announced in the same message region while
 * `data-estado` stays `normal`, because inventing a sixth value would break the
 * contract that makes the five verifiable.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import FormularioAcceso from '~/components/acceso/FormularioAcceso.vue'
import SelectorDemostracion from '~/components/acceso/SelectorDemostracion.vue'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import { useSesion, esFalloDeAcceso } from '~/composables/useSesion'
import type {
  AvisoAcceso,
  CredencialesAcceso,
  EstadoAcceso,
  MotivoFalloAcceso,
  RolUsuario,
  SesionUsuario,
} from '~/types/sesion'
import { destinoPorRol, MOTIVO_EXPIRADA } from '~/utils/sesion'

definePageMeta({ layout: 'acceso' })

/**
 * How each reason is announced.
 *
 * A switched off demonstration door is the "no permission" state of the design
 * system and not an error: retrying changes nothing, so it is drawn with the
 * warning colour and the lock instead of the error colour and the alert.
 */
const AVISO_POR_MOTIVO: Readonly<Record<MotivoFalloAcceso, AvisoAcceso>> = Object.freeze({
  'credenciales': { clave: 'access.errors.credentials', tono: 'error' },
  'demo-deshabilitado': { clave: 'access.errors.demoDisabled', tono: 'sin-permiso' },
  'servidor': { clave: 'access.errors.server', tono: 'error' },
})

const { t } = useI18n()
// useRoute and not useTituloDeRuta: that composable titles a screen with its
// branch of the A3 map, which is what a screen still made of scaffolding needs.
// This one is implemented and titles itself with what it asks the reader to do.
const route = useRoute()
const { iniciarSesion, iniciarSesionDemo, cargando } = useSesion()

/**
 * Whether the demonstration selector is offered at all.
 *
 * The real gate is the backend, which does not mount the route unless its own
 * flag is on. This one only decides whether the door is shown, so a deployment
 * with the door closed does not advertise it.
 */
const demoDisponible = useRuntimeConfig().public.demoAcceso === true

const motivoFallo = ref<MotivoFalloAcceso | null>(null)

const estado = computed<EstadoAcceso>(() => {
  if (cargando.value) {
    return 'cargando'
  }
  if (motivoFallo.value === 'credenciales') {
    return 'credencial-invalida'
  }
  if (motivoFallo.value === null && route.query.motivo === MOTIVO_EXPIRADA) {
    return 'sesion-expirada'
  }
  return 'normal'
})

const aviso = computed<AvisoAcceso | null>(() =>
  motivoFallo.value === null ? null : AVISO_POR_MOTIVO[motivoFallo.value],
)

/** Runs one way in, and lands the reader wherever their role belongs. */
async function intentar(abrir: () => Promise<SesionUsuario>): Promise<void> {
  motivoFallo.value = null
  try {
    const sesion = await abrir()
    await navigateTo(destinoPorRol(sesion.rol))
  }
  catch (error) {
    motivoFallo.value = esFalloDeAcceso(error) ? error.motivo : 'servidor'
  }
}

async function entrar(credenciales: CredencialesAcceso): Promise<void> {
  await intentar(() => iniciarSesion(credenciales))
}

async function entrarComoDemo(rol: RolUsuario): Promise<void> {
  await intentar(() => iniciarSesionDemo(rol))
}
</script>

<template>
  <section :data-ruta="route.path" class="flex flex-col gap-6">
    <CabeceraPantalla :titulo="t('access.title')" :descripcion="t('access.subtitle')" />

    <FormularioAcceso :estado="estado" :aviso="aviso" @enviar="entrar" />

    <SelectorDemostracion
      v-if="demoDisponible"
      :deshabilitado="cargando"
      @elegir="entrarComoDemo"
    />
  </section>
</template>
