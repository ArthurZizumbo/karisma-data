<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import GobiernoDiccionarioCampos from '~/components/gobierno/DiccionarioCampos.vue'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.governance.description')" />
    <GobiernoDiccionarioCampos />
  </section>
</template>
