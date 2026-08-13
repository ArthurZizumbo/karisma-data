<script setup lang="ts">
/**
 * The field dictionary of the governance screen, with its four states.
 *
 * The screen opens on the INITIAL state and not on a spinner: nothing is
 * requested until a term is typed, which is what keeps the endpoint from
 * answering a 422 to a query nobody wrote, and what lets the empty state say
 * what to do instead of spinning.
 *
 * The list is never reordered or filtered when a panel opens. The criterion is
 * that the screen is left exactly as it was found, and the cheapest way to
 * break it is to sort the results by "last opened".
 *
 * The two composables are the whole logic: this component reads their state and
 * draws it. What the box holds is deliberately not what the search ran with
 * -typing is not searching-, so the results never claim to answer a question
 * that was not asked.
 */
import type { CampoCatalogo } from '~/types/linaje'
import { ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import GobiernoAccesoBitacora from '~/components/gobierno/AccesoBitacora.vue'
import GobiernoOverlayLinaje from '~/components/gobierno/OverlayLinaje.vue'
import GobiernoTarjetaCampo from '~/components/gobierno/TarjetaCampo.vue'
import { MINIMO_TERMINO, useBusquedaCatalogo } from '~/composables/useBusquedaCatalogo'
import { useLinajeCampo } from '~/composables/useLinajeCampo'
import { claveDeFaceta } from '~/types/linaje'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()

const busqueda = useBusquedaCatalogo()
const linaje = useLinajeCampo()

const idTitulo = useId()
const idCampo = useId()

/** What the box holds. It becomes the query only when the form is submitted. */
const borrador = ref('')

async function enviar(): Promise<void> {
  await busqueda.buscar(borrador.value)
}

/** Label of a domain chip: its translation when known, its code otherwise. */
function etiquetaDominio(codigo: string): string {
  const clave = claveDeFaceta('domain', codigo)
  return clave === null ? codigo : t(clave)
}

async function abrirLinaje(campo: CampoCatalogo): Promise<void> {
  await linaje.abrir(campo)
}
</script>

<template>
  <section
    data-diccionario
    :aria-labelledby="idTitulo"
    class="flex flex-col gap-6"
  >
    <header class="flex flex-col gap-1">
      <h2 :id="idTitulo" class="flex items-center gap-2 font-display text-titulo-2 text-corriente-pleno">
        <Icon name="lucide:book-open" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('lineage.dictionary.title') }}
      </h2>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('lineage.dictionary.hint') }}
      </p>
    </header>

    <form class="flex flex-col gap-1" @submit.prevent="enviar">
      <label :for="idCampo" class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('lineage.dictionary.searchLabel') }}
      </label>

      <div class="flex flex-wrap items-stretch gap-2">
        <div class="relative flex min-w-64 flex-1 items-center">
          <Icon
            name="lucide:search"
            class="pointer-events-none absolute left-3 size-4 shrink-0 text-corriente-tenue"
            aria-hidden="true"
          />
          <input
            :id="idCampo"
            v-model="borrador"
            data-campo-busqueda
            type="search"
            :placeholder="t('lineage.dictionary.searchPlaceholder')"
            class="min-h-11 w-full border border-corriente-medio bg-ground pl-9 pr-3 text-cuerpo text-corriente-pleno placeholder:text-corriente-tenue"
            :class="ANILLO_FOCO"
          >
        </div>

        <button
          type="submit"
          data-accion-busqueda
          :disabled="borrador.trim().length < MINIMO_TERMINO"
          class="flex min-h-11 items-center border border-corriente-medio px-4 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground disabled:border-grid disabled:text-corriente-apagado"
          :class="ANILLO_FOCO"
        >
          {{ t('lineage.dictionary.searchAction') }}
        </button>
      </div>

      <p class="text-micro text-corriente-tenue">
        {{ t('lineage.dictionary.searchHint') }}
      </p>
    </form>

    <div
      v-if="busqueda.dominios.value.length > 0"
      role="group"
      :aria-label="t('lineage.dictionary.domainsLabel')"
      class="flex flex-wrap gap-2"
    >
      <button
        type="button"
        data-chip-dominio="todos"
        :aria-pressed="busqueda.dominio.value === null"
        class="min-h-11 rounded-sm border px-3 text-micro"
        :class="[
          ANILLO_FOCO,
          busqueda.dominio.value === null
            ? 'border-corriente-pleno text-corriente-pleno'
            : 'border-grid text-corriente-tenue',
        ]"
        @click="busqueda.filtrarPorDominio(null)"
      >
        {{ t('lineage.dictionary.domainAll') }}
      </button>

      <button
        v-for="dominio in busqueda.dominios.value"
        :key="dominio.codigo"
        type="button"
        :data-chip-dominio="dominio.codigo"
        :aria-pressed="busqueda.dominio.value === dominio.codigo"
        class="min-h-11 rounded-sm border px-3 text-micro"
        :class="[
          ANILLO_FOCO,
          busqueda.dominio.value === dominio.codigo
            ? 'border-corriente-pleno text-corriente-pleno'
            : 'border-grid text-corriente-tenue',
        ]"
        @click="busqueda.filtrarPorDominio(dominio.codigo)"
      >
        {{ etiquetaDominio(dominio.codigo) }} · {{ dominio.total }}
      </button>
    </div>

    <div :data-estado="busqueda.estado.value" class="flex flex-col gap-3">
      <template v-if="busqueda.estado.value === 'inicial'">
        <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
          <Icon name="lucide:search" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
          {{ t('lineage.dictionary.state.initial.title') }}
        </h3>
        <p class="text-cuerpo text-corriente-medio">
          {{ t('lineage.dictionary.state.initial.body') }}
        </p>
      </template>

      <!--
        The skeleton reserves the height of three cards, so nothing below it
        moves when the answer lands. A spinner of its own height is what
        produces the jump this criterion forbids.
      -->
      <div
        v-else-if="busqueda.estado.value === 'cargando'"
        role="status"
        aria-busy="true"
        class="flex flex-col gap-3"
      >
        <span class="sr-only">{{ t('lineage.dictionary.state.loading') }}</span>
        <span
          v-for="ficha in 3"
          :key="ficha"
          aria-hidden="true"
          class="h-40 animate-pulse rounded-lg bg-ground-alt"
        />
      </div>

      <template v-else-if="busqueda.estado.value === 'vacio'">
        <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
          <Icon name="lucide:inbox" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
          {{ t('lineage.dictionary.state.empty.title') }}
        </h3>
        <p class="text-cuerpo text-corriente-medio">
          {{ t('lineage.dictionary.state.empty.body') }}
        </p>
      </template>

      <template v-else-if="busqueda.estado.value === 'error'">
        <h3 class="flex items-start gap-2 text-titulo-3 text-corriente-pleno">
          <Icon name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
          {{ t('lineage.dictionary.state.error.title') }}
        </h3>
        <p class="text-cuerpo text-corriente-medio">
          {{ t('lineage.dictionary.state.error.body') }}
        </p>
        <p v-if="busqueda.codigo.value !== null" data-codigo-error class="font-mono text-micro text-corriente-tenue">
          {{ busqueda.codigo.value }}
        </p>
        <button
          type="button"
          data-reintentar-busqueda
          class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
          :class="ANILLO_FOCO"
          @click="busqueda.reintentar()"
        >
          <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
          {{ t('lineage.dictionary.state.error.retry') }}
        </button>
      </template>

      <p v-else data-conteo class="text-micro text-corriente-tenue">
        {{ t('lineage.dictionary.results', { count: busqueda.total.value }) }}
      </p>
    </div>

    <ul v-if="busqueda.estado.value === 'listo'" data-resultados class="flex flex-col gap-3">
      <li v-for="campo in busqueda.resultados.value" :key="campo.fieldId">
        <GobiernoTarjetaCampo :campo="campo" @ver-linaje="abrirLinaje" />
      </li>
    </ul>

    <GobiernoAccesoBitacora />

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
