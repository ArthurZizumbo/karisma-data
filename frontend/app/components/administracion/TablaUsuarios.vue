<script setup lang="ts">
/**
 * The portal accounts, their filter and the three states that are not the list.
 *
 * Presentational on purpose: it receives rows and a state, and it emits what
 * the reader asked for. Nothing here decides whether an action is possible, and
 * nothing here calls the API -that lives in `useUsuarios`, so this component
 * can be mounted against any of its four states without a transport.
 *
 * The skeleton is the table itself with its cells emptied: same header, same
 * number of rows, same cell metrics. A spinner of its own height is what makes
 * the page jump the moment the answer lands, and the criterion forbids it by
 * name.
 */
import type { AccionUsuario, EstadoPanel, UsuarioAdmin } from '~/types/usuarios'
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import AdministracionFilaUsuario from '~/components/administracion/FilaUsuario.vue'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Rows that pass the filter, which are the ones the table draws. */
  usuarios: readonly UsuarioAdmin[]
  /** Accounts the portal holds, filter aside. The empty state names it. */
  total: number
  estado: EstadoPanel
  /** Login name of the administrator running the session, or null. */
  usernamePropio: string | null
}>()

const emit = defineEmits<{
  /** Asks for confirmation. It never executes anything. */
  solicitar: [accion: AccionUsuario]
  reintentar: []
}>()

/**
 * Text filter, owned by the composable and edited here.
 *
 * A model and not a property: the empty state is caused by this field and the
 * screen that reports the cause has to be the one that can undo it.
 */
const filtro = defineModel<string>('filtro', { required: true })

const { t } = useI18n()

const idFiltro = useId()

/** The six columns, in the order the header declares them. */
const COLUMNAS = Object.freeze(['user', 'email', 'role', 'status'] as const)

/**
 * Rows the skeleton draws.
 *
 * On a reload it is exactly what is on screen, so nothing moves. On a cold open
 * there is nothing to count yet and it falls back to the seven accounts the
 * portal ships with, which is the closest honest guess available before the
 * first answer arrives.
 */
const FILAS_EN_FRIO = 7

const filasEsqueleto = computed(() => (props.total > 0 ? props.total : FILAS_EN_FRIO))

const hayTabla = computed(() => props.estado === 'listo' || props.estado === 'cargando')
</script>

<template>
  <section :data-estado-panel="estado" class="flex flex-col gap-3">
    <div class="flex flex-col gap-1">
      <h2 class="text-titulo-2 text-corriente-pleno">
        {{ t('admin.users.title') }}
      </h2>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('admin.users.caption') }}
      </p>
      <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
        {{ t('admin.users.scopeNote') }}
      </p>
    </div>

    <div class="flex flex-col gap-1">
      <label :for="idFiltro" class="text-etiqueta text-corriente-pleno">
        {{ t('admin.users.filter.label') }}
      </label>
      <input
        :id="idFiltro"
        v-model="filtro"
        data-campo-filtro
        type="search"
        autocomplete="off"
        :placeholder="t('admin.users.filter.placeholder')"
        class="min-h-9 w-full max-w-96 rounded-md border border-corriente-medio bg-ground px-3 text-cuerpo text-corriente-pleno"
        :class="ANILLO_FOCO"
      >
    </div>

    <p v-if="estado === 'cargando'" role="status" class="sr-only">
      {{ t('admin.users.state.loading') }}
    </p>

    <div v-if="hayTabla" class="overflow-x-auto border border-grid">
      <table class="w-full border-collapse text-left" :aria-busy="estado === 'cargando'">
        <caption class="sr-only">{{ t('admin.users.caption') }}</caption>
        <thead>
          <tr class="bg-ground-alt">
            <th
              v-for="columna in COLUMNAS"
              :key="columna"
              scope="col"
              class="h-(--table-row-height) px-3 text-etiqueta text-corriente-pleno"
            >
              {{ t(`admin.users.column.${columna}`) }}
            </th>
            <th scope="col" class="h-(--table-row-height) px-3 text-etiqueta text-corriente-pleno">
              {{ t('admin.users.modified') }}
            </th>
            <th
              scope="col"
              class="h-(--table-row-height) border-l border-grid pl-(--grid-gap) pr-3 text-etiqueta text-corriente-pleno"
            >
              {{ t('admin.users.column.actions') }}
            </th>
          </tr>
        </thead>

        <tbody v-if="estado === 'cargando'" aria-hidden="true">
          <tr
            v-for="fila in filasEsqueleto"
            :key="fila"
            data-fila-esqueleto
            class="border-t border-grid even:bg-ground-alt"
          >
            <td class="h-(--table-row-height) px-3 py-2">
              <span class="block h-3 w-40 animate-pulse rounded-sm bg-grid" />
              <span class="mt-1 block h-2 w-24 animate-pulse rounded-sm bg-grid" />
            </td>
            <td v-for="celda in 5" :key="celda" class="h-(--table-row-height) px-3 py-2">
              <span class="block h-3 w-24 animate-pulse rounded-sm bg-grid" />
            </td>
          </tr>
        </tbody>

        <tbody v-else>
          <AdministracionFilaUsuario
            v-for="usuario in usuarios"
            :key="usuario.id"
            :usuario="usuario"
            :propia="usuario.username === usernamePropio"
            @solicitar="emit('solicitar', $event)"
          />
        </tbody>
      </table>
    </div>

    <div
      v-else-if="estado === 'vacio'"
      class="flex flex-col items-start gap-2 border border-dashed border-corriente-apagado p-6"
    >
      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:inbox" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('admin.users.state.empty.title') }}
      </h3>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('admin.users.state.empty.body', { total }) }}
      </p>
      <button
        type="button"
        data-limpiar-filtro
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="filtro = ''"
      >
        <Icon name="lucide:x" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('admin.users.filter.clear') }}
      </button>
    </div>

    <div
      v-else
      role="alert"
      class="flex flex-col items-start gap-2 border border-dashed border-error p-6"
    >
      <h3 class="flex items-start gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
        {{ t('admin.users.state.error.title') }}
      </h3>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('admin.users.state.error.body') }}
      </p>
      <button
        type="button"
        data-reintentar
        class="inline-flex min-h-11 items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="emit('reintentar')"
      >
        <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('admin.users.action.retry') }}
      </button>
    </div>
  </section>
</template>
