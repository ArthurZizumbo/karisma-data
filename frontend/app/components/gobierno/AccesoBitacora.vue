<script setup lang="ts">
/**
 * Cross access from governance to the audit log, absorbed from US-018/019.
 *
 * The functionality of the log is a later User Story; what this delivers is the
 * link and, for whoever cannot follow it, the reason. The link is NOT rendered
 * disabled: offering a door that answers with a closed door is the defect
 * US-027 identified, and it is not reintroduced here. Whoever lacks the scope
 * reads the copy US-017 already wrote for exactly this situation, so no second
 * wording of the same sentence enters the catalogues.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePermisos } from '~/composables/usePermisos'
import { ANILLO_FOCO } from '~/utils/foco'
import { MODULOS } from '~/utils/navegacion'

const { t } = useI18n()
const { alcanza } = usePermisos()

/** Destination taken from the A3 map, never from a literal path. */
const RUTA_ADMINISTRACION = MODULOS.find(modulo => modulo.id === '4')?.ruta ?? '/administracion'

const puedeEntrar = computed(() => alcanza('admin'))
</script>

<template>
  <section class="flex flex-col gap-2 border-l-2 border-grid pl-5">
    <h2 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:shield-check" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
      {{ t('lineage.crossAccess.title') }}
    </h2>

    <p class="text-cuerpo text-corriente-medio">
      {{ t('lineage.crossAccess.hint') }}
    </p>

    <NuxtLink
      v-if="puedeEntrar"
      data-acceso-bitacora
      :to="RUTA_ADMINISTRACION"
      class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
      :class="ANILLO_FOCO"
    >
      {{ t('lineage.crossAccess.link') }}
    </NuxtLink>

    <p v-else data-sin-bitacora class="text-micro text-corriente-tenue">
      {{ t('authz.noPermission.requestTo') }}
    </p>
  </section>
</template>
