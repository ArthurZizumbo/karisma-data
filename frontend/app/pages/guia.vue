<script setup lang="ts">
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
import {
  CONTRASTES,
  FECHA_GUIA,
  HALLAZGOS,
  REGLAS_DERIVADAS,
  VERSION_GUIA,
} from '~/utils/tokens.generated'

/**
 * Living design system of Karisma Data.
 *
 * The route is not a prototype and not a branch of the A3 map: it is the system
 * the seven prototypes are built with, and the surface figures 14 to 16 of the
 * A4 document are captured from. Rule of the US: the guide describes nothing
 * that this route does not render.
 *
 * The plates are imported eagerly instead of through the Lazy prefix. They
 * fetch nothing, so deferring them would buy no payload worth the trade, and
 * the capture script would race a Suspense boundary that resolves after the
 * screenshot.
 */
definePageMeta({ layout: 'portal' })

const { t } = useI18n()

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
  <section :data-ruta="RUTA_GUIA" class="flex flex-col gap-6">
    <header class="flex flex-col gap-2">
      <h1 class="font-display text-titulo-1 text-primary-dark">
        {{ t('guide.title') }}
      </h1>
      <p class="max-w-prose text-cuerpo-amplio text-ink">
        {{ t('guide.subtitle') }}
      </p>
      <p class="text-etiqueta text-muted">
        {{ t('guide.version', { version: VERSION_GUIA, date: FECHA_GUIA }) }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.source') }}
      </p>
      <p class="max-w-prose rounded-sm bg-accent-100 px-2 py-1 text-cuerpo text-accent-text">
        {{ t('guide.generatedProse') }}
      </p>
    </header>

    <!--
      First level of the progressive disclosure: the eight plates as a list, so
      any of them is one click away and none of the detail is more than two.
    -->
    <nav :aria-label="t('guide.index.aria')" class="flex flex-col gap-2">
      <h2 class="font-display text-titulo-3 text-ink">
        {{ t('guide.index.title') }}
      </h2>
      <ol class="flex flex-wrap gap-2">
        <li v-for="(lamina, indice) in LAMINAS" :key="lamina.id">
          <a
            :href="`#lamina-${lamina.id}`"
            :data-indice-lamina="lamina.id"
            class="inline-flex min-h-11 items-center rounded-md border border-line-strong bg-surface-alt px-3 text-cuerpo text-ink hover:border-primary"
            :class="ANILLO_FOCO"
          >
            {{ indice + 1 }}. {{ t(lamina.clave) }}
          </a>
        </li>
      </ol>
    </nav>

    <LaminaPaleta id="lamina-paleta" />
    <LaminaTipografia id="lamina-tipografia" />
    <LaminaBotones id="lamina-botones" />
    <LaminaCampos id="lamina-campos" />
    <LaminaTablas id="lamina-tablas" />
    <LaminaTarjetas id="lamina-tarjetas" />
    <LaminaIconos id="lamina-iconos" />

    <!--
      Eighth plate. It stays in the page instead of becoming a component because
      it documents the generator itself: the four defects the contrast matrix
      found, the rules that replaced them and the full set of measured pairs.
    -->
    <section
      id="lamina-accesibilidad"
      data-lamina="accesibilidad"
      class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
    >
      <header class="flex flex-col gap-1">
        <h2 class="font-display text-titulo-2 text-primary-dark">
          {{ t('guide.plate.accessibility') }}
        </h2>
        <p class="max-w-prose text-cuerpo text-muted">
          {{ t('guide.accessibility.description') }}
        </p>
        <p class="max-w-prose text-cuerpo text-muted">
          {{ t('guide.accessibility.verdictLegend') }}
        </p>
      </header>

      <h3 class="font-display text-titulo-3 text-ink">
        {{ t('guide.accessibility.findings') }}
      </h3>
      <ul class="grid gap-[var(--grid-gap)] lg:grid-cols-2">
        <li
          v-for="hallazgo in HALLAZGOS"
          :key="hallazgo.numero"
          :data-hallazgo="hallazgo.numero"
          class="flex flex-col gap-2 rounded-md border border-line-strong bg-surface-alt p-3"
        >
          <h4 class="font-display text-titulo-3 text-ink">
            {{ t('guide.accessibility.finding', { number: hallazgo.numero }) }}
          </h4>
          <p lang="es" class="text-cuerpo text-ink">
            {{ hallazgo.diagnostico }}
          </p>

          <div class="flex flex-col gap-1">
            <span class="text-etiqueta text-ink">{{ t('guide.accessibility.measured') }}</span>
            <span
              class="inline-flex w-fit rounded-sm border border-line-strong px-2 py-1 text-cuerpo"
              :style="{ color: hallazgo.par.frenteHex, backgroundColor: hallazgo.par.fondoHex }"
            >
              {{ t('guide.accessibility.sample') }}
            </span>
            <span class="text-cuerpo tabular-nums text-ink">
              {{ hallazgo.par.frente }} / {{ hallazgo.par.fondo }} ·
              {{ hallazgo.par.ratio.toFixed(2) }}:1 · {{ hallazgo.par.veredicto }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-etiqueta text-ink">{{ t('guide.accessibility.replacement') }}</span>
            <span
              class="inline-flex w-fit rounded-sm border border-line-strong px-2 py-1 text-cuerpo"
              :style="{
                color: hallazgo.sustituto.frenteHex,
                backgroundColor: hallazgo.sustituto.fondoHex,
              }"
            >
              {{ t('guide.accessibility.sample') }}
            </span>
            <span class="text-cuerpo tabular-nums text-ink">
              {{ hallazgo.sustituto.frente }} / {{ hallazgo.sustituto.fondo }} ·
              {{ hallazgo.sustituto.ratio.toFixed(2) }}:1 · {{ hallazgo.sustituto.veredicto }}
            </span>
            <span lang="es" class="text-micro text-ink">{{ hallazgo.sustituto.regla }}</span>
          </div>
        </li>
      </ul>

      <h3 class="font-display text-titulo-3 text-ink">
        {{ t('guide.accessibility.rules') }}
      </h3>
      <ol lang="es" class="flex list-decimal flex-col gap-1 pl-6">
        <li v-for="regla in REGLAS_DERIVADAS" :key="regla" class="max-w-prose text-cuerpo text-ink">
          {{ regla }}
        </li>
      </ol>

      <!--
        Third level of the disclosure: forty odd measured pairs are reference
        material, not reading material, so they open on demand and stay one
        click from anywhere in the plate.
      -->
      <details data-matriz class="rounded-md border border-line-strong bg-surface-alt">
        <summary
          class="cursor-pointer px-3 py-2 text-cuerpo text-ink"
          :class="ANILLO_FOCO"
        >
          {{ t('guide.accessibility.matrix') }} ·
          {{ t('guide.accessibility.matrixCount', { total: CONTRASTES.length }) }}
        </summary>
        <div class="max-h-96 overflow-auto">
          <table class="w-full border-collapse text-left">
            <caption class="sr-only">
              {{ t('guide.accessibility.matrix') }}
            </caption>
            <thead>
              <tr>
                <th scope="col" class="sticky top-0 bg-primary-700 px-2 py-2 text-etiqueta text-surface">
                  {{ t('guide.accessibility.column.foreground') }}
                </th>
                <th scope="col" class="sticky top-0 bg-primary-700 px-2 py-2 text-etiqueta text-surface">
                  {{ t('guide.accessibility.column.background') }}
                </th>
                <th
                  scope="col"
                  class="sticky top-0 bg-primary-700 px-2 py-2 text-right text-etiqueta text-surface"
                >
                  {{ t('guide.accessibility.column.ratio') }}
                </th>
                <th scope="col" class="sticky top-0 bg-primary-700 px-2 py-2 text-etiqueta text-surface">
                  {{ t('guide.accessibility.column.verdict') }}
                </th>
                <th scope="col" class="sticky top-0 bg-primary-700 px-2 py-2 text-etiqueta text-surface">
                  {{ t('guide.accessibility.column.rule') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="par in CONTRASTES"
                :key="`${par.frente}-${par.fondo}`"
                data-par-contraste
                class="border-b border-line odd:bg-surface even:bg-surface-alt"
              >
                <td class="px-2 py-1 text-cuerpo text-ink">
                  {{ par.frente }} {{ par.frenteHex }}
                </td>
                <td class="px-2 py-1 text-cuerpo text-ink">
                  {{ par.fondo }} {{ par.fondoHex }}
                </td>
                <td class="px-2 py-1 text-right text-cuerpo tabular-nums text-ink">
                  {{ par.ratio.toFixed(2) }}:1
                </td>
                <td class="px-2 py-1 text-cuerpo text-ink">
                  {{ par.veredicto }}
                </td>
                <td lang="es" class="px-2 py-1 text-cuerpo text-ink">
                  {{ par.regla }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </section>
  </section>
</template>
