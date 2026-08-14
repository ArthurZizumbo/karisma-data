<script setup lang="ts">
/**
 * One account of the portal, with the controls that account allows.
 *
 * The row of the administrator running the session renders no role selector and
 * no destructive zone. That is not the rule -the rule lives in the backend,
 * which answers 409- but the interface is what decides whether the reader is
 * offered a button that would be refused. In its place the row says whose
 * account it is and why nothing can be done to it from here.
 *
 * The role badge and the role selector are not redundant. The badge is the
 * confirmed role, the one the server last returned; the selector only asks for
 * a change, and it is reset to the confirmed value the instant it is used, so
 * that a change still waiting for confirmation -or refused with a 409- never
 * shows up as if it had already happened.
 */
import type { RolUsuario } from '~/types/sesion'
import type { AccionUsuario, UsuarioAdmin } from '~/types/usuarios'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatearFecha } from '~/utils/fechas'
import { ANILLO_FOCO } from '~/utils/foco'
import { ROLES } from '~/utils/sesion'

const props = defineProps<{
  usuario: UsuarioAdmin
  /** True when this is the row of the administrator running the session. */
  propia: boolean
}>()

const emit = defineEmits<{ solicitar: [accion: AccionUsuario] }>()

const { t, locale } = useI18n()

/** Anchors the controls of the row to the name they act upon. */
const idNombre = computed(() => `usuario-${props.usuario.username}`)

/**
 * The status chip: its marker, its wording, its colour and its shape.
 *
 * The marker is Spanish because it is the value the acceptance criterion pins
 * in the DOM; the translation key is English because that is the vocabulary of
 * the catalogues. Keeping the two in one place is what stops them from drifting.
 */
const chip = computed(() =>
  props.usuario.disabled
    ? {
        marcador: 'desactivado',
        clave: 'disabled',
        clases: 'text-corriente-tenue border-corriente-apagado',
        icono: 'lucide:circle-dashed',
      }
    : {
        marcador: 'activo',
        clave: 'active',
        clases: 'text-ok border-ok',
        icono: 'lucide:check',
      },
)

/**
 * Asks for a role change and puts the control back where it was.
 *
 * @param evento - Change event of the role selector.
 */
function alElegirRol(evento: Event): void {
  const control = evento.target as HTMLSelectElement
  const rolNuevo = control.value as RolUsuario
  // Back to the confirmed role before anything else: nothing has changed yet,
  // and a selector showing the requested value would be the optimistic update
  // this User Story refuses to make.
  control.value = props.usuario.role
  if (rolNuevo !== props.usuario.role) {
    emit('solicitar', { tipo: 'cambiar-rol', usuario: props.usuario, rolNuevo })
  }
}
</script>

<template>
  <tr
    :data-fila-usuario="usuario.username"
    :data-propia="propia ? 'true' : undefined"
    class="border-t border-grid even:bg-ground-alt"
  >
    <th
      :id="idNombre"
      scope="row"
      class="h-(--table-row-height) px-3 py-2 text-left font-normal"
    >
      <span class="block text-cuerpo text-corriente-pleno">{{ usuario.full_name }}</span>
      <span class="block font-mono text-micro text-corriente-tenue">{{ usuario.username }}</span>
    </th>

    <td class="h-(--table-row-height) px-3 py-2 text-cuerpo text-corriente-medio">
      {{ usuario.email }}
    </td>

    <td class="h-(--table-row-height) px-3 py-2">
      <div class="flex flex-wrap items-center gap-2">
        <span
          :data-insignia-rol="usuario.role"
          class="inline-flex items-center rounded-full border border-corriente-medio px-2.5 py-0.5 font-mono text-micro text-corriente-pleno"
        >
          {{ t(`authz.role.${usuario.role}`) }}
        </span>

        <select
          v-if="!propia"
          data-selector-rol
          :value="usuario.role"
          :aria-label="t('admin.users.action.changeRole')"
          :aria-describedby="idNombre"
          class="min-h-9 rounded-md border border-corriente-medio bg-ground px-2 text-etiqueta text-corriente-pleno"
          :class="ANILLO_FOCO"
          @change="alElegirRol"
        >
          <option v-for="rol in ROLES" :key="rol" :value="rol">
            {{ t(`authz.role.${rol}`) }}
          </option>
        </select>
      </div>
    </td>

    <td class="h-(--table-row-height) px-3 py-2">
      <span
        :data-chip-estado="chip.marcador"
        class="inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 text-etiqueta"
        :class="chip.clases"
      >
        <!-- Colour plus shape: the two states are two colours the same reader
             may not tell apart, and the icon is how the state is read. -->
        <Icon :name="chip.icono" class="size-3 shrink-0" aria-hidden="true" />
        {{ t(`admin.users.status.${chip.clave}`) }}
      </span>
    </td>

    <td class="h-(--table-row-height) px-3 py-2 font-mono text-micro text-corriente-tenue">
      <time :datetime="usuario.updated_at">{{ formatearFecha(usuario.updated_at, locale) }}</time>
    </td>

    <!--
      Last column, separated by a rule and by the grid channel. When it holds
      the destructive action it is marked as such and it holds nothing else:
      that single actionable element is what the separation criterion means, and
      it is why the role selector lives two columns earlier.
    -->
    <td
      v-if="propia"
      class="h-(--table-row-height) border-l border-grid py-2 pl-(--grid-gap) pr-3"
    >
      <span
        data-insignia-propia
        class="inline-flex items-center gap-1 rounded-sm border border-info px-2 py-0.5 text-etiqueta text-info"
      >
        <Icon name="lucide:user-check" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('admin.users.self.badge') }}
      </span>
      <span class="mt-1 block max-w-(--medida-maxima) text-micro text-corriente-tenue">
        {{ t('admin.users.self.note') }}
      </span>
    </td>

    <td
      v-else-if="usuario.disabled"
      class="h-(--table-row-height) border-l border-grid py-2 pl-(--grid-gap) pr-3"
    >
      <button
        type="button"
        data-accion-fila="reactivar"
        :aria-describedby="idNombre"
        class="inline-flex min-h-9 items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="emit('solicitar', { tipo: 'reactivar', usuario })"
      >
        <Icon name="lucide:rotate-ccw" class="size-3.5 shrink-0" aria-hidden="true" />
        {{ t('admin.users.action.reactivate') }}
      </button>
    </td>

    <td
      v-else
      data-zona="destructiva"
      class="h-(--table-row-height) border-l border-grid py-2 pl-(--grid-gap) pr-3"
    >
      <button
        type="button"
        data-accion-fila="desactivar"
        :aria-describedby="idNombre"
        class="inline-flex min-h-9 items-center gap-2 rounded-md border border-error px-3 text-etiqueta text-error hover:bg-error hover:text-ground"
        :class="ANILLO_FOCO"
        @click="emit('solicitar', { tipo: 'desactivar', usuario })"
      >
        <Icon name="lucide:trash-2" class="size-3.5 shrink-0" aria-hidden="true" />
        {{ t('admin.users.action.deactivate') }}
      </button>
    </td>
  </tr>
</template>
