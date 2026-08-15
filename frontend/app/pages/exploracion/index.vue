<script setup lang="ts">
/**
 * Branch 2.1 of the A3 map: the thematic catalogue of the portal.
 *
 * The screen stopped being scaffolding on 14-ago-2026. It composes from
 * `useBusquedaCatalogo`, the same composable the governance dictionary uses,
 * with no second search state and no parallel types: the catalogue is one
 * endpoint and one state machine, and a copy of either would drift the day the
 * wire contract moves.
 *
 * The layout is the one the design file resolved: the box on top, the domain
 * counts down the left, the results in the middle. The counts are a column and
 * not a chip strip because they are the second question the reader asks -"how
 * much of this is risk?"- and a strip pushes the answer off the fold as soon as
 * the catalogue grows past four domains.
 *
 * The page holds no logic of its own: it projects the state of the composable
 * onto the three properties the result list declares, and the three unhappy
 * states are decided there, once. The fourth -no permission- belongs to the
 * continuations, which are the only scoped thing on this screen.
 */
import type { PaginaCatalogo } from '~/composables/useBusquedaCatalogo'
import type { SubrutaNav } from '~/types/navegacion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import ExploracionAccionesCatalogo from '~/components/exploracion/AccionesCatalogo.vue'
import ExploracionBuscadorCatalogo from '~/components/exploracion/BuscadorCatalogo.vue'
import ExploracionFiltroDominios from '~/components/exploracion/FiltroDominios.vue'
import ExploracionResultadosCatalogo from '~/components/exploracion/ResultadosCatalogo.vue'
import { useBusquedaCatalogo } from '~/composables/useBusquedaCatalogo'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'
import { moduloActivo } from '~/utils/navegacion'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
const busqueda = useBusquedaCatalogo()

const cargando = computed(() => busqueda.estado.value === 'cargando')

/**
 * Typed backend code of the failure, the empty string when the failure carried
 * none, and null when the search did not fail.
 *
 * The empty string is not a placeholder: `codigoDelFallo` returns null for a
 * transport error that never reached the API, and the reader still needs the
 * designed error. Collapsing both into null would hide the whole state.
 */
const error = computed<string | null>(() =>
  busqueda.estado.value === 'error' ? busqueda.codigo.value ?? '' : null,
)

/**
 * The result page, or null while there is nothing to draw.
 *
 * Null covers the initial state, the request in flight and the failure, so the
 * list component never has to guess whether an empty array means "nothing
 * matched" or "nothing was asked for": with a page in hand, zero fields always
 * means zero matches.
 */
const pagina = computed<PaginaCatalogo | null>(() => {
  if (busqueda.estado.value === 'inicial' || cargando.value || error.value !== null) {
    return null
  }
  return {
    total: busqueda.total.value,
    campos: busqueda.resultados.value,
    dominios: busqueda.dominios.value,
  }
})

/**
 * Sibling branches of module 2 that live on a screen of their own.
 *
 * Derived from the navigation contract instead of written as paths: no route
 * literal belongs in a Vue file, and the branches that still render inside this
 * landing screen point at this same route, which is what the filter drops.
 */
const continuaciones = computed<readonly SubrutaNav[]>(() => {
  const modulo = moduloActivo(ruta.value)
  if (modulo === undefined) {
    return []
  }
  return modulo.subrutas.filter(subruta => subruta.ruta !== modulo.ruta)
})
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.explore.description')" />

    <ExploracionBuscadorCatalogo :cargando="cargando" @buscar="busqueda.buscar" />

    <div class="grid gap-8 lg:grid-cols-4">
      <ExploracionFiltroDominios
        class="lg:col-span-1"
        :conteos="busqueda.dominios.value"
        :activo="busqueda.dominio.value"
        @filtrar="busqueda.filtrarPorDominio"
      />

      <div class="flex min-w-0 flex-col gap-8 lg:col-span-3">
        <ExploracionResultadosCatalogo
          :pagina="pagina"
          :cargando="cargando"
          :error="error"
          @reintentar="busqueda.reintentar"
        />

        <ExploracionAccionesCatalogo :subrutas="continuaciones" />
      </div>
    </div>
  </section>
</template>
