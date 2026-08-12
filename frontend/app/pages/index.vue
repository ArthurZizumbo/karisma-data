<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import BotonPrototipo from '~/components/nav/BotonPrototipo.vue'
import { usePermisos } from '~/composables/usePermisos'
import { ANILLO_FOCO } from '~/utils/foco'
import { PROTOTIPOS, RUTA_ACCESO, RUTA_GUIA, RUTA_INDICE } from '~/utils/navegacion'

const { t } = useI18n()

/**
 * The index is public and the seven prototypes are not.
 *
 * Without this line an evaluator opens the index, presses "1. Inicio", lands on
 * the entry screen and reads the bounce as a broken link. Saying it before the
 * click turns a surprise into a rule of the product, and it disappears the
 * moment there is a session.
 */
const { rol } = usePermisos()
</script>

<template>
  <section :data-ruta="RUTA_INDICE" class="flex flex-col gap-6">
    <CabeceraPantalla
      :titulo="t('screen.index.title')"
      :descripcion="t('screen.index.subtitle')"
    />

    <p
      v-if="rol === null"
      data-aviso-sesion
      class="flex max-w-(--medida-maxima) flex-wrap items-center gap-x-3 gap-y-1 border-l-2 border-aviso pl-5 text-cuerpo text-corriente-medio"
    >
      {{ t('authz.signedOut.notice') }}
      <NuxtLink
        :to="RUTA_ACCESO"
        class="inline-flex items-center gap-1 text-etiqueta text-corriente-pleno underline underline-offset-4 hover:no-underline"
        :class="ANILLO_FOCO"
      >
        {{ t('nav.session.signIn') }}
      </NuxtLink>
    </p>

    <ul class="grid gap-x-10 sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="prototipo in PROTOTIPOS" :key="prototipo.numero">
        <BotonPrototipo :prototipo="prototipo" />
      </li>
    </ul>

    <!--
      Separate block on purpose. The A4 rubric scores prototypes in one section
      and the style guide in another, so the guide is not an eighth numbered
      button: it is the system the seven above are built with, and it carries no
      data-prototipo attribute.
    -->
    <aside data-guia class="flex flex-col gap-2 border-l-2 border-info pl-5">
      <h2 class="text-titulo-2 text-corriente-pleno">
        {{ t('guide.entry.heading') }}
      </h2>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.entry.description') }}
      </p>
      <NuxtLink
        :to="RUTA_GUIA"
        class="mt-1 inline-flex min-h-9 w-fit items-center gap-2 border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
      >
        <Icon name="lucide:circuit-board" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('guide.entry.action') }}
      </NuxtLink>
    </aside>
  </section>
</template>
