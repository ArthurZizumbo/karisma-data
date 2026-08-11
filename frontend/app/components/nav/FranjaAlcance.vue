<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { CLAVE_AVISO_ALCANCE } from '~/utils/navegacion'

const { t } = useI18n()
</script>

<template>
  <p
    data-franja-alcance
    role="note"
    :aria-label="t('scope.ariaLabel')"
    class="sticky top-0 z-10 shrink-0 border-b border-grid bg-ground-alt px-4 py-2 text-etiqueta text-corriente-medio md:px-8"
  >
    {{ t(CLAVE_AVISO_ALCANCE) }}
  </p>
</template>
