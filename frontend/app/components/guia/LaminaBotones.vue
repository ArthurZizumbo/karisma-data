<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO, ANILLO_FOCO_CONGELADO } from '~/utils/foco'

/**
 * Button matrix of the living design system.
 *
 * Seventeen cells: three variants by five states, plus the destructive action
 * and the loading one. The course material shows nine, and the four that are
 * missing there -pressed, disabled, destructive and loading- are exactly the
 * ones two screens end up drawing differently when the guide leaves them out.
 *
 * Hover, focus and pressed are rendered frozen, with the classes each state
 * produces, because a plate cannot capture a pointer. The focus cell paints
 * `ANILLO_FOCO_CONGELADO`, which is the ring of the product with the
 * `focus-visible` variant dropped: the plate used to freeze a primary-700 ring
 * that no control of the portal has ever painted.
 */
defineOptions({ name: 'LaminaBotones' })

/** Slug written into data-boton-celda, and therefore part of the contract. */
type Variante = 'contenido' | 'contorno' | 'texto' | 'destructiva'
type Estado = 'reposo' | 'puntero' | 'foco' | 'activo' | 'deshabilitado' | 'carga'

/** The five states every variant has to declare. */
const ESTADOS_BASE = ['reposo', 'puntero', 'foco', 'activo', 'deshabilitado'] as const

type EstadoBase = (typeof ESTADOS_BASE)[number]

interface VarianteBoton {
  readonly variante: Variante
  readonly claveVariante: string
  readonly claveEtiqueta: string
  readonly clases: Readonly<Record<EstadoBase, string>>
}

interface CeldaBoton {
  /** `<variante>-<estado>`, the value the capture script selects by. */
  readonly id: string
  readonly variante: Variante
  readonly claveVariante: string
  readonly claveEstado: string
  readonly claveEtiqueta: string
  readonly clases: string
  readonly deshabilitado: boolean
  readonly cargando: boolean
  readonly destructiva: boolean
}

/** Shape shared by the seventeen cells. 44 px of height is the touch target. */
const BASE
  = 'inline-flex min-h-11 w-full items-center justify-center gap-2 whitespace-nowrap rounded-md px-4 text-cuerpo transition-colors motion-reduce:transition-none'

const CLAVE_ESTADO: Readonly<Record<Estado, string>> = Object.freeze({
  reposo: 'guide.buttons.state.rest',
  puntero: 'guide.buttons.state.hover',
  foco: 'guide.buttons.state.focus',
  activo: 'guide.buttons.state.active',
  deshabilitado: 'guide.buttons.state.disabled',
  carga: 'guide.buttons.state.loading',
})

const VARIANTES: readonly VarianteBoton[] = Object.freeze([
  {
    variante: 'contenido',
    claveVariante: 'guide.buttons.variant.filled',
    claveEtiqueta: 'guide.buttons.label.filled',
    clases: {
      reposo: 'border border-primary bg-primary text-surface',
      puntero: 'border border-primary-dark bg-primary-dark text-surface',
      foco: `border border-primary bg-primary text-surface ${ANILLO_FOCO_CONGELADO}`,
      activo: 'border border-primary-900 bg-primary-900 text-surface',
      deshabilitado: 'cursor-not-allowed border border-line-strong bg-surface-alt text-muted',
    },
  },
  {
    variante: 'contorno',
    claveVariante: 'guide.buttons.variant.outline',
    claveEtiqueta: 'guide.buttons.label.outline',
    clases: {
      reposo: 'border border-primary bg-surface text-primary',
      puntero: 'border border-primary-dark bg-primary-100 text-primary-700',
      foco: `border border-primary bg-surface text-primary ${ANILLO_FOCO_CONGELADO}`,
      activo: 'border border-primary-900 bg-primary-300 text-primary-900',
      deshabilitado: 'cursor-not-allowed border border-line-strong bg-surface text-muted',
    },
  },
  {
    variante: 'texto',
    claveVariante: 'guide.buttons.variant.text',
    claveEtiqueta: 'guide.buttons.label.text',
    clases: {
      // A transparent border in the resting state, so the tertiary button keeps
      // the same box as the other two and the row never shifts on hover.
      reposo: 'border border-transparent bg-surface text-primary',
      puntero: 'border border-line-strong bg-surface-alt text-primary-700',
      foco: `border border-transparent bg-surface text-primary ${ANILLO_FOCO_CONGELADO}`,
      activo: 'border border-line-strong bg-primary-300 text-primary-900',
      deshabilitado: 'cursor-not-allowed border border-transparent bg-surface text-muted',
    },
  },
])

const CELDAS: readonly CeldaBoton[] = Object.freeze([
  ...VARIANTES.flatMap(variante =>
    ESTADOS_BASE.map(estado => ({
      id: `${variante.variante}-${estado}`,
      variante: variante.variante,
      claveVariante: variante.claveVariante,
      claveEstado: CLAVE_ESTADO[estado],
      claveEtiqueta: variante.claveEtiqueta,
      clases: variante.clases[estado],
      deshabilitado: estado === 'deshabilitado',
      cargando: false,
      destructiva: false,
    })),
  ),
  {
    id: 'destructiva-reposo',
    variante: 'destructiva',
    claveVariante: 'guide.buttons.variant.destructive',
    claveEstado: CLAVE_ESTADO.reposo,
    claveEtiqueta: 'guide.buttons.label.destructive',
    clases: 'border border-danger-strong bg-danger text-surface',
    deshabilitado: false,
    cargando: false,
    destructiva: true,
  },
  {
    id: 'contenido-carga',
    variante: 'contenido',
    claveVariante: 'guide.buttons.variant.filled',
    claveEstado: CLAVE_ESTADO.carga,
    claveEtiqueta: 'guide.buttons.label.loading',
    clases: 'cursor-progress border border-primary bg-primary text-surface',
    deshabilitado: true,
    cargando: true,
    destructiva: false,
  },
])

const { t } = useI18n()
</script>

<template>
  <section
    data-lamina="botones"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.buttons') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.buttons.description') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.buttons.frozenNote') }}
      </p>
      <p class="max-w-prose rounded-sm bg-accent-100 px-2 py-1 text-cuerpo text-accent-text">
        {{ t('guide.buttons.rule') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.buttons.focusRing') }}
      </p>
      <!--
        The literal string, not a description of it: whoever copies a cell of
        this plate into a new control copies this and gets the ring the browser
        really paints.
      -->
      <p
        data-anillo-foco
        class="w-fit rounded-sm border border-line-strong bg-surface px-2 py-1 font-mono text-etiqueta text-ink"
      >
        {{ ANILLO_FOCO }}
      </p>
    </header>

    <!--
      Five columns only from 1440 px up, which is the capture viewport of the
      A4 figures. At 1280 the cell would be narrower than the destructive label
      and the row would overflow: rule 7 of the interface checklist.
    -->
    <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <li
        v-for="celda in CELDAS"
        :key="celda.id"
        :data-boton-celda="celda.id"
        class="flex flex-col gap-1"
      >
        <button
          type="button"
          :class="[BASE, celda.clases]"
          :disabled="celda.deshabilitado"
          :aria-busy="celda.cargando ? 'true' : undefined"
        >
          <Icon
            v-if="celda.cargando"
            name="lucide:loader-circle"
            class="size-5 shrink-0 animate-spin motion-reduce:animate-none"
            aria-hidden="true"
          />
          <Icon
            v-else-if="celda.destructiva"
            name="lucide:trash-2"
            class="size-5 shrink-0"
            aria-hidden="true"
          />
          {{ t(celda.claveEtiqueta) }}
        </button>
        <span class="text-micro text-muted">
          {{ t(celda.claveVariante) }} · {{ t(celda.claveEstado) }}
        </span>
      </li>
    </ul>
  </section>
</template>
