<script setup lang="ts">
/**
 * Branch 4.1 of the A3 map: the accounts of the portal and what can be done to
 * them.
 *
 * The screen orchestrates and does not decide. It asks the composable to load,
 * it turns a request coming from a row into a question in a dialog, and it
 * applies the answer only when the reader confirms it. Whether the action is
 * allowed is settled by the backend, and a refusal is rendered where it
 * happened instead of being predicted here.
 *
 * The other three branches of module 4 -requests, the access log and
 * integrations- are not here and are not announced as buttons that do nothing:
 * the description of the screen says where they stand.
 */
import type { AccionUsuario, CodigoConflicto } from '~/types/usuarios'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdministracionDialogoConfirmacion from '~/components/administracion/DialogoConfirmacion.vue'
import AdministracionTablaUsuarios from '~/components/administracion/TablaUsuarios.vue'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'
import { useUsuarios } from '~/composables/useUsuarios'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()

const {
  usuarios,
  usuariosVisibles,
  estado,
  filtro,
  conflicto,
  usernamePropio,
  cargar,
  aplicar,
  limpiarConflicto,
} = useUsuarios()

/** What the reader asked for and has not confirmed yet. */
const pendiente = ref<AccionUsuario | null>(null)

/** The panel, which is where the node that takes focus back is looked up. */
const panel = ref<HTMLElement | null>(null)

/**
 * Control that opened the dialog, noted while the click is still being handled.
 *
 * A plain variable and not a `ref`: nothing renders it, and a reactive proxy
 * over a DOM node would buy this screen a dependency it never reads.
 */
let invocador: HTMLElement | null = null

/** Conflict code of the backend to the sentence that explains it. */
const CLAVE_DE_CONFLICTO: Readonly<Record<CodigoConflicto, string>> = Object.freeze({
  admin_no_puede_degradarse: 'demoteSelf',
  admin_no_puede_desactivarse: 'disableSelf',
  usuario_no_encontrado: 'notFound',
})

/**
 * Copy and tone of the dialog for the pending action.
 *
 * Exhaustive over the union: a fourth action would fail to compile here rather
 * than opening a dialog with the wording of another one.
 */
const dialogo = computed(() => {
  const accion = pendiente.value
  if (accion === null) {
    return { titulo: '', cuerpo: '', confirmar: '', tono: 'normal' as const }
  }

  const nombre = accion.usuario.full_name
  if (accion.tipo === 'cambiar-rol') {
    return {
      titulo: t('admin.users.confirm.role.title'),
      cuerpo: t('admin.users.confirm.role.body', {
        name: nombre,
        role: t(`authz.role.${accion.rolNuevo}`),
      }),
      confirmar: t('admin.users.confirm.role.confirm'),
      tono: 'normal' as const,
    }
  }
  if (accion.tipo === 'desactivar') {
    return {
      titulo: t('admin.users.confirm.deactivate.title'),
      cuerpo: t('admin.users.confirm.deactivate.body', { name: nombre }),
      confirmar: t('admin.users.confirm.deactivate.confirm'),
      tono: 'destructivo' as const,
    }
  }
  return {
    titulo: t('admin.users.confirm.reactivate.title'),
    cuerpo: t('admin.users.confirm.reactivate.body', { name: nombre }),
    confirmar: t('admin.users.confirm.reactivate.confirm'),
    tono: 'normal' as const,
  }
})

/**
 * Takes note of what the reader wants and asks. Nothing leaves for the API.
 *
 * @param accion - Action requested from a row.
 */
function solicitar(accion: AccionUsuario): void {
  limpiarConflicto()
  // Where the reader was standing. It has to be read now, because by the time
  // the action resolves this node may no longer be in the document. The body is
  // what `activeElement` reports when nothing holds focus at all, and it is not
  // somewhere anyone can be sent back to.
  const activo = document.activeElement
  invocador = activo instanceof HTMLElement && activo !== document.body ? activo : null
  pendiente.value = accion
}

function cancelar(): void {
  pendiente.value = null
  // Nothing repaints on a cancellation, so the browser puts focus back on the
  // invoking control by itself when the dialog closes. The reference is dropped
  // instead of used, so this screen never holds a node it has no use for.
  invocador = null
}

/**
 * Puts focus back where the reader was, when nobody else can.
 *
 * Closing the dialog already returns focus to the control that opened it, and
 * when that control is still there the platform does it better than this screen
 * could: the role selector is where a reader who changed a role was standing,
 * and the action cell of that row holds an irreversible button that nobody
 * should be handed by surprise. So a surviving invoker is left alone.
 *
 * What the platform cannot do is the case this exists for: disabling an account
 * replaces the invoking button with the one that re-enables it, so focus is
 * restored onto a node that has already left the document and lands on the body
 * -at the top of the page, and for the reader who can least afford to start
 * over. The anchor is then the action cell of the same row, whatever button
 * occupies it now, found through the two markers the table already publishes;
 * and if the whole table went with it, which is what a generic failure does,
 * the retry is the only thing left to offer.
 *
 * @param username - Account the confirmed action acted upon.
 * @param origen - Control that opened the dialog, possibly already detached.
 */
function devolverFoco(username: string, origen: HTMLElement | null): void {
  if (origen?.isConnected === true) {
    return
  }
  const contenedor = panel.value
  const filas = [...(contenedor?.querySelectorAll<HTMLElement>('[data-fila-usuario]') ?? [])]
  const fila = filas.find(candidata => candidata.dataset.filaUsuario === username)
  const enLaFila = fila?.querySelector<HTMLElement>('[data-accion-fila]') ?? null
  const reintentar = contenedor?.querySelector<HTMLElement>('[data-reintentar]') ?? null
  const destino = enLaFila ?? reintentar
  destino?.focus()
}

async function confirmar(): Promise<void> {
  const accion = pendiente.value
  const origen = invocador
  pendiente.value = null
  invocador = null
  if (accion === null) {
    return
  }
  await aplicar(accion)
  // After the repaint and not before: the anchor being looked for is a button
  // that does not exist until the row is drawn again from the server's answer.
  await nextTick()
  devolverFoco(accion.usuario.username, origen)
}

onMounted(() => {
  void cargar()
})
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.administration.description')" />

    <section id="4.1" ref="panel" data-rama="4.1" class="flex flex-col gap-4">
      <p
        v-if="conflicto !== null"
        role="alert"
        :data-conflicto="conflicto.codigo"
        class="flex items-start gap-2 border-l-2 border-error bg-ground-alt px-4 py-3 text-cuerpo text-corriente-pleno"
      >
        <Icon name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
        {{ t(`admin.users.conflict.${CLAVE_DE_CONFLICTO[conflicto.codigo]}`, { name: conflicto.username }) }}
      </p>

      <AdministracionTablaUsuarios
        v-model:filtro="filtro"
        :usuarios="usuariosVisibles"
        :total="usuarios.length"
        :estado="estado"
        :username-propio="usernamePropio"
        @solicitar="solicitar"
        @reintentar="cargar"
      />
    </section>

    <AdministracionDialogoConfirmacion
      :abierto="pendiente !== null"
      :titulo="dialogo.titulo"
      :cuerpo="dialogo.cuerpo"
      :etiqueta-confirmar="dialogo.confirmar"
      :tono="dialogo.tono"
      @confirmar="confirmar"
      @cancelar="cancelar"
    />
  </section>
</template>
