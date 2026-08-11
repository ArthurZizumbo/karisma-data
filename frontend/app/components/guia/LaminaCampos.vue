<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO_CONGELADO } from '~/utils/foco'

/**
 * Field, chip and badge plate of the living design system.
 *
 * The border of every field is the strong neutral and never the light rule.
 * That is finding 4 of the contrast matrix: the light rule reaches 1.42:1 over
 * the surface, so a field drawn with it has, for measuring purposes, no border
 * at all. It is also the reason the matrix was computed in the first place.
 */
defineOptions({ name: 'LaminaCampos' })

/** One of the six states a form field can be captured in. */
interface CeldaCampo {
  /** Slug written into data-campo-estado. */
  readonly estado: string
  readonly claveEstado: string
  readonly claveEtiqueta: string
  /** Value the field is rendered with, empty when the state is the empty one. */
  readonly valor: string
  readonly clases: string
  readonly deshabilitado: boolean
  readonly soloLectura: boolean
  readonly invalido: boolean
}

/** One of the five semantic chips. */
interface ChipEstado {
  readonly id: string
  readonly clave: string
  readonly icono: string
  readonly clases: string
}

const BASE_CAMPO
  = 'min-h-11 w-full rounded-md border bg-surface px-3 text-cuerpo text-ink placeholder:text-muted'

const CAMPOS: readonly CeldaCampo[] = Object.freeze([
  {
    estado: 'reposo',
    claveEstado: 'guide.fields.state.rest',
    claveEtiqueta: 'guide.fields.label.account',
    valor: '',
    clases: 'border-line-strong',
    deshabilitado: false,
    soloLectura: false,
    invalido: false,
  },
  {
    // Focus is frozen with the same ring the browser paints, because a plate
    // has no pointer and no caret to show it with. Same ring as every other
    // control of the portal: the field plate used to freeze its own.
    estado: 'foco',
    claveEstado: 'guide.fields.state.focus',
    claveEtiqueta: 'guide.fields.label.period',
    valor: '',
    clases: `border-primary ${ANILLO_FOCO_CONGELADO}`,
    deshabilitado: false,
    soloLectura: false,
    invalido: false,
  },
  {
    estado: 'relleno',
    claveEstado: 'guide.fields.state.filled',
    claveEtiqueta: 'guide.fields.label.source',
    valor: 'SIC-BANXICO',
    clases: 'border-line-strong',
    deshabilitado: false,
    soloLectura: false,
    invalido: false,
  },
  {
    estado: 'error',
    claveEstado: 'guide.fields.state.error',
    claveEtiqueta: 'guide.fields.label.amount',
    valor: '0',
    clases: 'border-danger',
    deshabilitado: false,
    soloLectura: false,
    invalido: true,
  },
  {
    estado: 'deshabilitado',
    claveEstado: 'guide.fields.state.disabled',
    claveEtiqueta: 'guide.fields.label.note',
    valor: '',
    clases: 'cursor-not-allowed border-line-strong bg-surface-alt text-muted',
    deshabilitado: true,
    soloLectura: false,
    invalido: false,
  },
  {
    estado: 'solo-lectura',
    claveEstado: 'guide.fields.state.readonly',
    claveEtiqueta: 'guide.fields.label.code',
    valor: 'EXP-2026-0731',
    clases: 'border-line-strong bg-surface-alt',
    deshabilitado: false,
    soloLectura: true,
    invalido: false,
  },
])

const CHIPS: readonly ChipEstado[] = Object.freeze([
  {
    id: 'neutro',
    clave: 'guide.fields.chip.neutral',
    icono: 'lucide:circle-dashed',
    clases: 'border-line-strong bg-surface-alt text-ink',
  },
  {
    id: 'informativo',
    clave: 'guide.fields.chip.info',
    icono: 'lucide:info',
    clases: 'border-primary bg-primary-100 text-primary-700',
  },
  {
    id: 'correcto',
    clave: 'guide.fields.chip.success',
    icono: 'lucide:circle-check',
    clases: 'border-success-700 bg-success-100 text-success-900',
  },
  {
    // Finding 2: the warning text is accent 900 over accent 100 (7.58:1). The
    // 700 over the same fill stays at 3.96:1 and fails AA for normal text.
    id: 'aviso',
    clave: 'guide.fields.chip.warning',
    icono: 'lucide:triangle-alert',
    clases: 'border-accent-700 bg-accent-100 text-accent-text',
  },
  {
    // The system has no danger fill token, so the rejected chip is drawn as a
    // bordered chip over the surface: 6.23:1 for the text and 5.9:1 for the
    // border.
    id: 'rechazo',
    clave: 'guide.fields.chip.danger',
    icono: 'lucide:circle-alert',
    clases: 'border-danger bg-surface text-danger',
  },
])

/** The four profiles of the portal, reusing the keys of the prototype index. */
const INSIGNIAS = Object.freeze([
  { rol: 'operativo', clave: 'prototype.profile.operations', clases: 'border-primary text-primary-700' },
  { rol: 'analista', clave: 'prototype.profile.analyst', clases: 'border-secondary-700 text-secondary-700' },
  { rol: 'directivo', clave: 'prototype.profile.executive', clases: 'border-success-700 text-success-900' },
  {
    rol: 'administrador',
    clave: 'prototype.profile.administration',
    clases: 'border-accent-700 text-accent-text',
  },
])

const { t } = useI18n()
</script>

<template>
  <section
    data-lamina="campos"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.fields') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.fields.description') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.fields.borderNote') }}
      </p>
    </header>

    <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2 lg:grid-cols-3">
      <li
        v-for="campo in CAMPOS"
        :key="campo.estado"
        :data-campo-estado="campo.estado"
        class="flex flex-col gap-1"
      >
        <label :for="`campo-${campo.estado}`" class="text-etiqueta text-ink">
          {{ t(campo.claveEtiqueta) }}
        </label>
        <input
          :id="`campo-${campo.estado}`"
          type="text"
          :class="[BASE_CAMPO, campo.clases]"
          :value="campo.valor"
          :placeholder="t('guide.fields.placeholder')"
          :disabled="campo.deshabilitado"
          :readonly="campo.soloLectura"
          :aria-invalid="campo.invalido ? 'true' : undefined"
          :aria-describedby="campo.invalido ? `campo-${campo.estado}-mensaje` : `campo-${campo.estado}-ayuda`"
        >
        <p
          v-if="campo.invalido"
          :id="`campo-${campo.estado}-mensaje`"
          class="flex items-center gap-1 text-etiqueta text-danger"
        >
          <Icon name="lucide:circle-alert" class="size-4 shrink-0" aria-hidden="true" />
          {{ t('guide.fields.error') }}
        </p>
        <p v-else :id="`campo-${campo.estado}-ayuda`" class="text-etiqueta text-muted">
          {{ t('guide.fields.help') }}
        </p>
        <span class="text-micro text-muted">{{ t(campo.claveEstado) }}</span>
      </li>
    </ul>

    <div class="flex flex-col gap-2">
      <h3 class="font-display text-titulo-3 text-ink">
        {{ t('guide.fields.chips') }}
      </h3>
      <ul class="flex flex-wrap gap-2">
        <li v-for="chip in CHIPS" :key="chip.id" :data-chip="chip.id">
          <span
            class="inline-flex items-center gap-1 rounded-sm border px-2 py-1 text-etiqueta"
            :class="chip.clases"
          >
            <Icon :name="chip.icono" class="size-5 shrink-0" aria-hidden="true" />
            {{ t(chip.clave) }}
          </span>
        </li>
      </ul>
    </div>

    <div class="flex flex-col gap-2">
      <h3 class="font-display text-titulo-3 text-ink">
        {{ t('guide.fields.badges') }}
      </h3>
      <ul class="flex flex-wrap gap-2">
        <li v-for="insignia in INSIGNIAS" :key="insignia.rol" :data-badge-rol="insignia.rol">
          <span
            class="inline-flex items-center rounded-full border bg-surface px-3 py-1 text-etiqueta"
            :class="insignia.clases"
          >
            {{ t(insignia.clave) }}
          </span>
        </li>
      </ul>
      <p class="max-w-prose text-micro text-muted">
        {{ t('guide.fields.badgeNote') }}
      </p>
    </div>
  </section>
</template>
