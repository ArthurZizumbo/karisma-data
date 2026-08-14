<script setup lang="ts">
/**
 * Icon plate, rebuilt in the diagram world.
 *
 * The inventory is named by function and never by shape, which is what makes it
 * usable: someone looking for "lineage" finds it, someone looking for "the one
 * with the branches" does not need to.
 *
 * The grid is dense on purpose. The measured version spent 84 glyphs of equal
 * weight with the function label in the smallest type of the cell, so the plate
 * read as decoration; the name leads now and the glyph is the specimen beside
 * it.
 *
 * The names are literals from a shared module, the very array `nuxt.config.ts`
 * feeds to the bundler. A name assembled at run time renders an empty box in a
 * production build while looking correct under the dev server, which is the
 * kind of defect that only shows up in the captured plate.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'
import { GRUPOS_DE_ICONOS, TAMANOS_DE_ICONO } from '~/components/guia/inventarioIconos'

const { t } = useI18n()
</script>

<template>
  <section data-lamina="iconos" class="flex flex-col gap-8">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.icons') }}
    </h2>

    <div v-for="grupo in GRUPOS_DE_ICONOS" :key="grupo.clave" class="flex flex-col gap-2">
      <h3 class="text-etiqueta uppercase text-corriente-tenue">
        {{ t(grupo.clave) }}
      </h3>
      <ul class="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-x-6">
        <li
          v-for="entrada in grupo.entradas"
          :key="entrada.nombre"
          data-icono
          class="flex items-center gap-3 border-t border-grid py-2"
        >
          <Icon
            :name="entrada.nombre"
            class="size-5 shrink-0 text-corriente-pleno"
            :aria-label="t(entrada.clave)"
          />
          <span class="min-w-0 flex-1 truncate text-cuerpo text-corriente-pleno">
            {{ t(entrada.clave) }}
          </span>
          <code class="shrink-0 font-mono text-micro text-corriente-tenue">
            {{ entrada.nombre.replace('lucide:', '') }}
          </code>
        </li>
      </ul>
    </div>

    <div class="flex flex-col gap-2">
      <h3 class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('guide.icons.sizes') }}
      </h3>
      <ul class="flex items-end gap-6">
        <li
          v-for="tamano in TAMANOS_DE_ICONO"
          :key="tamano.px"
          data-tamano-icono
          class="flex flex-col items-center gap-1"
        >
          <Icon
            name="lucide:database"
            :class="[tamano.clase, 'text-corriente-pleno']"
            :aria-label="t('guide.icons.label', { name: t('guide.icons.item.source'), size: tamano.px })"
          />
          <code class="font-mono text-micro text-corriente-tenue">{{ tamano.px }}</code>
        </li>
      </ul>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.icons.family') }}
      </p>
    </details>
  </section>
</template>
