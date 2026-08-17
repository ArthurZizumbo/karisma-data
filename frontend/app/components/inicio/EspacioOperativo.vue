<script setup lang="ts">
/**
 * Operative composition: find a figure and check it.
 *
 * It opens with the search box at full width because that is what the primary
 * persona of A1 does on entering, and because the profile that validates
 * figures -risk and audit- works the same way: locate, then confirm. Everything
 * else on the screen is a shortcut back to something already located.
 *
 * It is also the composition an administrator sees if they open the home screen
 * by hand. Their workspace is the administration one, but the home screen is
 * not forbidden to them, and the most general layout is the honest default.
 *
 * The blocks and their order are NOT decided here: they come from the
 * composition contract, and `test/inicio.spec.ts` compares this DOM against it.
 */
import type { RolUsuario } from '~/types/sesion'
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import BloqueLista from '~/components/inicio/BloqueLista.vue'
import BuscadorUnificado from '~/components/inicio/BuscadorUnificado.vue'
import CabeceraEspacio from '~/components/inicio/CabeceraEspacio.vue'
import { formatearFechaHora } from '~/utils/fechas'
import { ALERTAS, BUSQUEDAS_RECIENTES, FAVORITOS, ULTIMO_ACCESO } from '~/utils/muestrasInicio'

const props = defineProps<{
  /** True while the session has not resolved yet. */
  cargando: boolean
  /** Display name of the reader, empty while unknown. */
  nombre: string
  /** Role of the session, null while unknown. */
  rol: RolUsuario | null
}>()

const { t, locale } = useI18n()

const idPerfil = useId()

const ultimoAcceso = computed(() => formatearFechaHora(ULTIMO_ACCESO, locale.value))
const claveRol = computed(() => (props.rol === null ? '' : `authz.role.${props.rol}`))
</script>

<template>
  <div data-espacio="operativo" class="flex flex-col gap-8">
    <CabeceraEspacio
      composicion="operativo"
      :nombre="nombre"
      :rol="rol"
      :cargando="cargando"
    />

    <BuscadorUnificado enfasis="dominante" />

    <div class="grid gap-8 lg:grid-cols-2">
      <BloqueLista
        bloque="recientes"
        clave-titulo="workspace.recent.title"
        clave-vacio="workspace.recent.empty"
        :elementos="BUSQUEDAS_RECIENTES"
        :cargando="cargando"
      />

      <BloqueLista
        bloque="favoritos"
        clave-titulo="workspace.favorites.title"
        clave-vacio="workspace.favorites.empty"
        :elementos="FAVORITOS"
        :cargando="cargando"
      />

      <BloqueLista
        bloque="alertas"
        clave-titulo="workspace.alerts.title"
        clave-vacio="workspace.alerts.empty"
        :elementos="ALERTAS"
        :cargando="cargando"
      />

      <!--
        The profile block belongs to this composition and to no other: it is
        branch 1.5 of the A3 map and the primary persona is the only one who
        named it as part of her home during the card sorting.

        `min-w-0` on a grid item is not a detail: a track sized `1fr` still
        refuses to go below the min-content width of what it holds, so one long
        sentence inside would widen the column past the viewport.
      -->
      <section
        data-bloque="perfil"
        :data-estado="cargando ? 'cargando' : 'lista'"
        :aria-labelledby="idPerfil"
        class="flex min-w-0 flex-col gap-2"
      >
        <h2 :id="idPerfil" class="text-titulo-3 text-corriente-pleno">
          {{ t('workspace.profile.title') }}
        </h2>

        <dl class="flex flex-col">
          <div class="flex min-h-11 min-w-0 items-center justify-between gap-3 border-b border-grid px-1">
            <dt class="text-etiqueta text-corriente-tenue">
              {{ t('workspace.profile.role') }}
            </dt>
            <dd class="text-cuerpo text-corriente-pleno">
              <span v-if="claveRol === ''" class="inline-block h-3 w-20 bg-ground-alt" aria-hidden="true" />
              <template v-else>{{ t(claveRol) }}</template>
            </dd>
          </div>

          <div
            data-origen="ejemplo"
            class="flex min-h-11 min-w-0 items-center justify-between gap-3 px-1"
          >
            <dt class="text-etiqueta text-corriente-tenue">
              {{ t('workspace.profile.lastAccess') }}
            </dt>
            <dd class="flex items-center gap-2">
              <time :datetime="ULTIMO_ACCESO" class="text-cuerpo tabular-nums text-corriente-pleno">
                {{ ultimoAcceso }}
              </time>
              <span class="border border-grid px-1 text-micro uppercase text-corriente-tenue">
                {{ t('workspace.sample.badge') }}
              </span>
            </dd>
          </div>
        </dl>
      </section>
    </div>

    <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('workspace.sample.hint') }}
    </p>
  </div>
</template>
