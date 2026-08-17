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
 * contract that makes the five verifiable. The bounce of the guard is announced
 * the same way and for the same reason: it is a message, not a sixth state.
 *
 * With the demonstration door open the four profiles come first and the
 * credential form is the secondary way in. Whoever arrives here bounced from a
 * prototype has no password, and a form on top tells them to look for one that
 * does not exist. With the door closed the screen is exactly what it was,
 * because then the form is the only way in and there is nothing to put first.
 *
 * THE EMPHASIS USED TO BE INVERTED, which is what the design review found: the
 * recommended way in was framed in the warning colour -a triangle and amber, as
 * if entering were a risk- and the only filled button of the screen belonged to
 * the form nobody in a demonstration has credentials for. The profiles now sit
 * on a surface of the action channel, and the credential form is a disclosure:
 * one click for whoever does have an account, and no primary button spent on a
 * door most readers cannot open. With the door closed the form is not a
 * disclosure at all, because then it is the only way in.
 *
 * The refusal of the demonstration door is announced by the PAGE and not by the
 * form. Both refusals used to share the message region of the form, and with
 * the form collapsed the reader would press a profile, fail, and see nothing.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import FormularioAcceso from '~/components/acceso/FormularioAcceso.vue'
import SelectorDemostracion from '~/components/acceso/SelectorDemostracion.vue'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import TarjetaContenida from '~/components/comun/TarjetaContenida.vue'
import { usePermisos } from '~/composables/usePermisos'
import { useRolDemo } from '~/composables/useRolDemo'
import { useSesion, esFalloDeAcceso } from '~/composables/useSesion'
import type {
  AvisoAcceso,
  CredencialesAcceso,
  EstadoAcceso,
  MotivoFalloAcceso,
  RolUsuario,
} from '~/types/sesion'
import { ANILLO_FOCO } from '~/utils/foco'
import { destinoDeRetorno, MOTIVO_SESION_REQUERIDA, PARAMETRO_DESTINO } from '~/utils/guarda'
import { claveDeRuta } from '~/utils/navegacion'
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

/** A profile that entered, and the screen it could not open with it. */
interface Desvio {
  readonly rol: RolUsuario
  readonly pedida: string
  readonly ruta: string
  readonly scopeExigido: RolUsuario
}

const { t } = useI18n()
// useRoute and not useTituloDeRuta: that composable titles a screen with its
// branch of the A3 map, which is what a screen still made of scaffolding needs.
// This one is implemented and titles itself with what it asks the reader to do.
const route = useRoute()
const { iniciarSesion, cargando } = useSesion()
const { puedeVerRuta } = usePermisos()
const { disponible: demoDisponible, entrarComoRol } = useRolDemo()

const motivoFallo = ref<MotivoFalloAcceso | null>(null)
/** Which of the two doors produced the failure, so it is announced where it is. */
const origenFallo = ref<'credenciales' | 'demostracion' | null>(null)
const desvio = ref<Desvio | null>(null)

/**
 * Route the guard was asked for, already validated.
 *
 * It is read through the same allowlist the guard writes it with: a path taken
 * from the query string and navigated to without checking is an open redirect
 * that any link can drive.
 */
const destinoSolicitado = computed<string | null>(() =>
  destinoDeRetorno(route.query[PARAMETRO_DESTINO]),
)

/** True when the reader is here because a screen asked for a session. */
const rebotePorSesion = computed<boolean>(() => route.query.motivo === MOTIVO_SESION_REQUERIDA)

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

/** The refusal of the credential form, which is the one the form announces. */
const avisoDeCredenciales = computed<AvisoAcceso | null>(() =>
  origenFallo.value === 'credenciales' ? aviso.value : null,
)

/** The refusal of the demonstration door, announced next to the four profiles. */
const avisoDeDemostracion = computed<AvisoAcceso | null>(() =>
  origenFallo.value === 'demostracion' ? aviso.value : null,
)

/**
 * Whether the credential form opens expanded.
 *
 * It is a disclosure only while the demonstration door is open, and it starts
 * expanded when the guard sent the reader here because their session expired:
 * that explanation lives inside the form, and a collapsed panel would hide the
 * one sentence that says why they are looking at this screen again.
 */
const credencialesAbiertas = ref<boolean>(route.query.motivo === MOTIVO_EXPIRADA)

/** Name of a screen as the navigation contract publishes it. */
function nombreDePantalla(ruta: string): string | null {
  const clave = claveDeRuta(ruta)
  return clave === undefined ? null : t(clave)
}

/** Where a session that just opened belongs: what was asked for, or its space. */
function aterrizaje(rol: RolUsuario): string {
  const pedida = destinoSolicitado.value
  return pedida !== null && puedeVerRuta(pedida) ? pedida : destinoPorRol(rol)
}

async function entrar(credenciales: CredencialesAcceso): Promise<void> {
  motivoFallo.value = null
  origenFallo.value = null
  desvio.value = null
  try {
    const sesion = await iniciarSesion(credenciales)
    await navigateTo(aterrizaje(sesion.rol))
  }
  catch (error) {
    motivoFallo.value = esFalloDeAcceso(error) ? error.motivo : 'servidor'
    origenFallo.value = 'credenciales'
  }
}

/**
 * Opens a demonstration session and returns the reader to what they asked for.
 *
 * When the chosen profile does not reach that screen nobody is moved silently:
 * the session is already open and the screen names the profile that screen
 * needs, with the way into the one that was just opened. Landing somewhere else
 * without saying so is the mute bounce this User Story removes, one step later.
 */
async function entrarComoPerfil(rol: RolUsuario): Promise<void> {
  motivoFallo.value = null
  origenFallo.value = null
  desvio.value = null

  const resultado = await entrarComoRol(rol, destinoSolicitado.value ?? destinoPorRol(rol))

  if (resultado.tipo === 'fallo') {
    motivoFallo.value = resultado.motivo
    origenFallo.value = 'demostracion'
    return
  }

  if (resultado.tipo === 'desviada' && resultado.scopeExigido !== null) {
    desvio.value = {
      rol: resultado.sesion.rol,
      pedida: resultado.pedida,
      ruta: resultado.ruta,
      scopeExigido: resultado.scopeExigido,
    }
    return
  }

  await navigateTo(resultado.ruta)
}
</script>

<template>
  <section :data-ruta="route.path" class="flex flex-col gap-6">
    <CabeceraPantalla :titulo="t('access.title')" :descripcion="t('access.subtitle')" />

    <p
      v-if="rebotePorSesion && desvio === null"
      data-aviso="sesion-requerida"
      role="status"
      class="flex items-start gap-2 border-l-2 border-info pl-3 text-cuerpo text-corriente-medio"
    >
      <Icon name="lucide:log-in" class="mt-0.5 size-4 shrink-0 text-info" aria-hidden="true" />
      <span>
        {{
          destinoSolicitado !== null && nombreDePantalla(destinoSolicitado) !== null
            ? t('roleSwitch.bounce.notice', { screen: nombreDePantalla(destinoSolicitado) })
            : t('roleSwitch.bounce.noticeGeneric')
        }}
      </span>
    </p>

    <div
      v-if="desvio !== null"
      data-aviso="desviado"
      role="status"
      class="flex flex-col gap-2 border-l-2 border-aviso pl-3"
    >
      <p class="flex items-start gap-2 text-cuerpo text-corriente-medio">
        <Icon name="lucide:lock" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
        <span>
          {{ t('roleSwitch.bounce.diverted', {
            screen: nombreDePantalla(desvio.pedida) ?? desvio.pedida,
            current: t(`authz.role.${desvio.rol}`),
            required: t(`authz.role.${desvio.scopeExigido}`),
          }) }}
        </span>
      </p>
      <NuxtLink
        :to="desvio.ruta"
        data-accion="ir-a-mi-espacio"
        class="inline-flex min-h-9 w-fit items-center gap-2 border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
      >
        {{ t('authz.noPermission.exit') }}
      </NuxtLink>
    </div>

    <!--
      The profiles come first when the door is open, and the order is the DOM
      order and not a CSS one: reordering with `order` would leave the tab
      sequence reading the form first, which is the opposite of what is shown.

      The surface carries the action channel because this is the recommended
      way in, and the review found it framed as a caution.
    -->
    <TarjetaContenida v-if="demoDisponible" canal="accion">
      <p data-recomendado class="text-cuerpo text-corriente-medio">
        {{ t('access.demo.recommended') }}
      </p>

      <SelectorDemostracion :deshabilitado="cargando" @elegir="entrarComoPerfil" />

      <p
        v-if="avisoDeDemostracion !== null"
        :data-aviso="avisoDeDemostracion.tono"
        role="alert"
        class="flex items-start gap-2 text-cuerpo"
        :class="avisoDeDemostracion.tono === 'sin-permiso' ? 'text-aviso' : 'text-error'"
      >
        <!-- Same pairing as the form: colour never travels without a shape. -->
        <Icon
          v-if="avisoDeDemostracion.tono === 'sin-permiso'"
          name="lucide:lock"
          class="mt-0.5 size-4 shrink-0"
          aria-hidden="true"
        />
        <Icon v-else name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0" aria-hidden="true" />
        {{ t(avisoDeDemostracion.clave) }}
      </p>
    </TarjetaContenida>

    <details
      v-if="demoDisponible"
      data-credenciales
      :open="credencialesAbiertas"
      class="border-t border-grid pt-5"
      @toggle="credencialesAbiertas = ($event.target as HTMLDetailsElement).open"
    >
      <summary
        data-abrir-credenciales
        class="flex min-h-11 cursor-pointer items-center gap-2 text-titulo-3 text-corriente-pleno"
        :class="ANILLO_FOCO"
      >
        {{ t('roleSwitch.credentials.heading') }}
      </summary>
      <p class="pb-3 text-cuerpo text-corriente-medio">
        {{ t('access.credentials.hint') }}
      </p>
      <FormularioAcceso :estado="estado" :aviso="avisoDeCredenciales" @enviar="entrar" />
    </details>

    <FormularioAcceso v-else :estado="estado" :aviso="avisoDeCredenciales" @enviar="entrar" />
  </section>
</template>
