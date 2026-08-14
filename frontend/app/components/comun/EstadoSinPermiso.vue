<script setup lang="ts">
/**
 * Fourth unhappy state: the door itself is closed.
 *
 * It is drawn where the screen would have been, without changing the URL, so
 * the address stays shareable and the back button behaves. The sidebar and the
 * scope band stay on screen around it, which is what gives the reader a way out
 * that is not a retry.
 *
 * There is NO retry control here, and that is the point rather than an
 * omission: retrying a refusal does not change anyone's role, and offering the
 * button teaches the reader to insist against a door that will not open. The
 * only actionable element is a link to the workspace the reader does own.
 *
 * The component compares nothing. It receives the required role and the current
 * one and translates them; who may see what is decided by the generated map,
 * upstream.
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { RolUsuario } from '~/types/sesion'
import { ANILLO_FOCO } from '~/utils/foco'
import { destinoPorRol } from '~/utils/sesion'

const props = defineProps<{
  /** Minimum role the route demands, as the generated map resolved it. */
  scopeExigido: RolUsuario
  /** Role of the session that was refused. */
  rolActual: RolUsuario
}>()

const { t } = useI18n()

const titulo = ref<HTMLHeadingElement | null>(null)

/**
 * The heading takes the focus when the state appears.
 *
 * On a client side navigation nothing else moves the caret: without this, a
 * keyboard reader stays on the sidebar link they just used and never learns
 * that the screen changed. `tabindex="-1"` makes the heading focusable by
 * script without adding it to the tab order.
 */
onMounted(() => {
  titulo.value?.focus()
})

/**
 * The two lines of detail, in the order the reader needs them.
 *
 * Which role is missing comes first because it explains the refusal; where to
 * ask for it comes second because it is the only action left. Saying the first
 * and not the second is half a state: it names the wall and hides the door.
 */
const detalles = computed(() => [
  {
    clave: 'authz.noPermission.required',
    texto: t('authz.noPermission.required', {
      required: t(`authz.role.${props.scopeExigido}`),
      current: t(`authz.role.${props.rolActual}`),
    }),
  },
  {
    clave: 'authz.noPermission.requestTo',
    texto: t('authz.noPermission.requestTo'),
  },
])

/**
 * Way out: the workspace this role does own.
 *
 * The table lives in `utils/sesion.ts` and is read, never copied: the landing
 * screen of a role is one decision, and it is the entry screen's.
 */
const destino = computed(() => destinoPorRol(props.rolActual))
</script>

<template>
  <section
    data-estado="sin-permiso"
    role="status"
    class="flex max-w-(--medida-maxima) flex-col gap-4 border-l-2 border-aviso pl-5"
  >
    <h1
      ref="titulo"
      tabindex="-1"
      class="flex items-start gap-2 font-display text-titulo-1 text-corriente-pleno"
    >
      <Icon name="lucide:lock" class="mt-1 size-5 shrink-0 text-aviso" aria-hidden="true" />
      {{ t('authz.noPermission.title') }}
    </h1>

    <p class="text-cuerpo-amplio text-corriente-medio">
      {{ t('authz.noPermission.body') }}
    </p>

    <ul class="ml-1 flex flex-col border-l border-corriente-apagado">
      <li
        v-for="detalle in detalles"
        :key="detalle.clave"
        :data-detalle="detalle.clave"
        class="relative py-1.5 pl-4 text-cuerpo text-corriente-tenue"
      >
        <span class="absolute left-0 top-1/2 h-px w-2.5 bg-corriente-apagado" aria-hidden="true" />
        {{ detalle.texto }}
      </li>
    </ul>

    <NuxtLink
      :to="destino"
      data-salida
      class="inline-flex min-h-11 w-fit items-center gap-2 border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
      :class="ANILLO_FOCO"
    >
      <Icon name="lucide:corner-up-left" class="size-4 shrink-0" aria-hidden="true" />
      {{ t('authz.noPermission.exit') }}
    </NuxtLink>
  </section>
</template>
