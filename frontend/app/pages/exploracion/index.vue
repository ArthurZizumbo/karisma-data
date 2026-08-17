<script setup lang="ts">
/**
 * Branch 2.1 of the A3 map: the thematic catalogue of the portal.
 *
 * The screen composes from `useBusquedaCatalogo`, the same composable the
 * governance dictionary uses, with no second search state and no parallel
 * types: the catalogue is one endpoint and one state machine, and a copy of
 * either would drift the day the wire contract moves.
 *
 * THIS SCREEN IS DISCOVERY, and `/gobierno` is the defence of the datum. The
 * two used to open with the same label, the same placeholder and almost the
 * same empty state, which made the second one read as a duplicate of the first.
 * What is answered here is "which field do I need"; what is answered there is
 * "where does this figure come from and who answers for it". Each row therefore
 * opens the journey of its field, and the result carries the exit towards the
 * record.
 *
 * THE TERM LIVES IN THE ADDRESS. The header search box navigates here with
 * `?q=`, and applying it is the job of this screen: the composable seeds the
 * term from the address on a cold open, writes every search back into it and
 * replaces instead of pushing, so the term survives the round trip through the
 * screens this very page offers.
 *
 * The layout is the one the design file resolved: the box on top, the domain
 * counts down the left, the results in the middle. The counts are a column and
 * not a chip strip because they are the second question the reader asks -"how
 * much of this is risk?"- and a strip pushes the answer off the fold as soon as
 * the catalogue grows past four domains.
 *
 * The page holds no logic of its own: it projects the state of the composable
 * onto the three properties the result table declares, and the four unhappy
 * states are decided there, once. The fifth -no permission- belongs to the
 * continuations, which are the only scoped thing on this screen.
 */
import type { CampoCatalogo } from '~/types/linaje'
import type { PaginaCatalogo } from '~/composables/useBusquedaCatalogo'
import type { SubrutaNav } from '~/types/navegacion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import ExploracionAccionesCatalogo from '~/components/exploracion/AccionesCatalogo.vue'
import ExploracionBuscadorCatalogo from '~/components/exploracion/BuscadorCatalogo.vue'
import ExploracionFiltroDominios from '~/components/exploracion/FiltroDominios.vue'
import ExploracionResultadosCatalogo from '~/components/exploracion/ResultadosCatalogo.vue'
import GobiernoOverlayLinaje from '~/components/gobierno/OverlayLinaje.vue'
import { useBusquedaCatalogo } from '~/composables/useBusquedaCatalogo'
import { useLinajeCampo } from '~/composables/useLinajeCampo'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'
import { moduloActivo } from '~/utils/navegacion'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
const busqueda = useBusquedaCatalogo({ sincronizarUrl: true })

/**
 * The journey of one field, opened from a row.
 *
 * The same composable and the same overlay the governance screen mounts, on
 * purpose: a second panel drawn here would be a second answer to "where does
 * this come from", and the two would drift the first time one of them changed.
 */
const linaje = useLinajeCampo()

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
 * table component never has to guess whether an empty array means "nothing
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

/** Opens the journey of the field a row asked for. */
async function verLinaje(campo: CampoCatalogo): Promise<void> {
  await linaje.abrir(campo)
}
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.explore.description')" />

    <ExploracionBuscadorCatalogo
      :cargando="cargando"
      :termino="busqueda.termino.value"
      @buscar="busqueda.buscar"
    />

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
          @ver-linaje="verLinaje"
        />

        <ExploracionAccionesCatalogo :subrutas="continuaciones" />
      </div>
    </div>

    <GobiernoOverlayLinaje
      :abierto="linaje.abierto.value"
      :campo="linaje.campo.value"
      :linaje="linaje.linaje.value"
      :estado="linaje.estado.value"
      :codigo="linaje.codigo.value"
      @cerrar="linaje.cerrar()"
      @reintentar="linaje.reintentar()"
    />
  </section>
</template>
