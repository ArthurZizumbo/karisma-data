<script setup lang="ts">
/**
 * Living design system of Karisma Data.
 *
 * The route is not a prototype and not a branch of the A3 map: it is the system
 * the seven prototypes are built with. Rule of the US: the guide describes
 * nothing that this route does not render.
 *
 * Audience decided on 11-ago-2026: the team that builds, over the evaluator.
 * The measured page opened with four paragraphs of justification and put its
 * first colour 718 pixels down; the specimen leads now and every rationale sits
 * behind a disclosure. Someone who came to copy a token finds it in the first
 * viewport.
 *
 * Numbers come from the store, which resolves them against the mode on screen.
 * The matrix is computed per mode because a ratio measured on a light ground
 * says nothing about the dark one.
 */
import { useI18n } from 'vue-i18n'
import LaminaBotones from '~/components/guia/LaminaBotones.vue'
import LaminaCampos from '~/components/guia/LaminaCampos.vue'
import LaminaIconos from '~/components/guia/LaminaIconos.vue'
import LaminaPaleta from '~/components/guia/LaminaPaleta.vue'
import LaminaTablas from '~/components/guia/LaminaTablas.vue'
import LaminaTarjetas from '~/components/guia/LaminaTarjetas.vue'
import LaminaTipografia from '~/components/guia/LaminaTipografia.vue'
import { ANILLO_FOCO } from '~/utils/foco'
import { RUTA_GUIA } from '~/utils/navegacion'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const sistema = useSistemaDiseno()

/** The eight plates, in the order the capture script walks them. */
const LAMINAS = Object.freeze([
  { id: 'paleta', clave: 'guide.plate.palette' },
  { id: 'tipografia', clave: 'guide.plate.typography' },
  { id: 'botones', clave: 'guide.plate.buttons' },
  { id: 'campos', clave: 'guide.plate.fields' },
  { id: 'tablas', clave: 'guide.plate.tables' },
  { id: 'tarjetas', clave: 'guide.plate.cards' },
  { id: 'iconos', clave: 'guide.plate.icons' },
  { id: 'accesibilidad', clave: 'guide.plate.accessibility' },
])
</script>

<template>
  <section :data-ruta="RUTA_GUIA" class="flex flex-col gap-10">
    <!-- Two lines of chrome, not a page of preamble. -->
    <header class="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
      <h1 class="font-display text-titulo-1 text-corriente-pleno">
        {{ t('guide.title') }}
      </h1>
      <p class="font-mono text-micro text-corriente-tenue">
        {{ t('guide.version', { version: sistema.version, date: sistema.fecha }) }}
        · {{ t(`guide.mode.${sistema.modo}`) }}
      </p>
    </header>

    <nav :aria-label="t('guide.index.aria')">
      <ul class="flex flex-wrap gap-x-4 gap-y-1">
        <li v-for="lamina in LAMINAS" :key="lamina.id">
          <a
            :href="`#lamina-${lamina.id}`"
            :data-indice-lamina="lamina.id"
            class="text-etiqueta text-corriente-tenue underline-offset-4 hover:text-corriente-pleno hover:underline"
            :class="ANILLO_FOCO"
          >
            {{ t(lamina.clave) }}
          </a>
        </li>
      </ul>
    </nav>

    <LaminaPaleta id="lamina-paleta" />
    <LaminaTipografia id="lamina-tipografia" />
    <LaminaBotones id="lamina-botones" />
    <LaminaCampos id="lamina-campos" />
    <LaminaTablas id="lamina-tablas" />
    <LaminaTarjetas id="lamina-tarjetas" />
    <LaminaIconos id="lamina-iconos" />

    <!--
      Eighth plate. It documents the generator itself, so it stays in the page:
      the measured matrix of the active mode, the dichromatic separation of the
      semantic marks, and the ceiling that makes shape and icon mandatory.
    -->
    <section id="lamina-accesibilidad" data-lamina="accesibilidad" class="flex flex-col gap-6">
      <h2 class="text-titulo-2 text-corriente-pleno">
        {{ t('guide.plate.accessibility') }}
      </h2>

      <!-- The headline number first: it is the one that decides a rule. -->
      <div class="flex flex-col gap-1 border-l-2 border-info pl-4">
        <p class="font-mono text-display text-corriente-pleno">
          dE {{ sistema.peorSeparacion }}
        </p>
        <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
          {{ t(`guide.accessibility.ceiling.${sistema.modo}`) }}
        </p>
      </div>

      <h3 class="text-titulo-3 text-corriente-pleno">
        {{ t('guide.accessibility.separations') }}
      </h3>
      <ul class="flex flex-col divide-y divide-grid">
        <li
          v-for="s in sistema.separaciones"
          :key="`${s.uno}-${s.otro}`"
          data-separacion
          class="flex items-baseline justify-between gap-4 py-2"
        >
          <span class="text-cuerpo text-corriente-pleno">{{ s.uno }} · {{ s.otro }}</span>
          <span class="font-mono text-micro text-corriente-tenue">{{ s.dicromacia }}</span>
          <span class="font-mono text-dato tabular-nums text-corriente-pleno">
            {{ s.distancia }}
          </span>
        </li>
      </ul>

      <details data-matriz class="border-t border-grid pt-3">
        <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
          {{ t('guide.accessibility.matrix') }} ·
          {{ t('guide.accessibility.matrixCount', { total: sistema.contrastes.length }) }}
        </summary>
        <div class="mt-2 max-h-96 overflow-auto">
          <table class="w-full border-collapse text-left">
            <caption class="sr-only">{{ t('guide.accessibility.matrix') }}</caption>
            <thead>
              <tr>
                <th
                  v-for="col in ['token', 'ratio', 'verdict']"
                  :key="col"
                  scope="col"
                  class="sticky top-0 bg-ground-alt px-2 py-2 text-etiqueta text-corriente-pleno"
                  :class="col === 'ratio' ? 'text-right' : ''"
                >
                  {{ t(`guide.accessibility.column.${col}`) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="par in sistema.contrastes"
                :key="par.token"
                data-par-contraste
                class="border-b border-grid"
              >
                <td class="px-2 py-1 font-mono text-micro text-corriente-pleno">
                  {{ par.token }}
                </td>
                <td class="px-2 py-1 text-right font-mono text-micro tabular-nums text-corriente-pleno">
                  {{ par.ratio }}:1
                </td>
                <td class="px-2 py-1 text-micro text-corriente-medio">
                  {{ par.veredicto }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>

      <p
        v-if="sistema.incumplimientos.length > 0"
        role="alert"
        class="flex items-center gap-2 text-cuerpo text-error"
      >
        <Icon name="lucide:x-circle" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('guide.accessibility.failures', { total: sistema.incumplimientos.length }, sistema.incumplimientos.length) }}
      </p>
    </section>
  </section>
</template>
