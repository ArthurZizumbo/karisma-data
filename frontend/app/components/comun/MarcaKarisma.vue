<script setup lang="ts">
/**
 * The Karisma Data mark, drawn as inline SVG.
 *
 * The portal used to name itself with `lucide:circuit-board` tinted with the
 * informative colour: a packaged icon standing in for a logotype, and painted
 * in the one channel this system reserves for saying something about the data.
 * The design file has a normative page -"Uso del logotipo"- and it declares a
 * different thing: the K symbol on a rounded tile, in three variants, with a
 * clear space rule and a minimum size.
 *
 * The geometry below was measured on that page, rendered at 600 dpi, and it is
 * expressed as proportions of the tile inside a 100 x 100 viewBox. Pixels were
 * deliberately not carried over: the guide asks for the proportion to survive
 * every size, and a viewBox is the only way to promise that.
 *
 *   tile            931 x 933 px measured, corner radius 56  ->  6.01 % of the side
 *   bar width       131                                      -> 14.06 %
 *   gutter           69                                      ->  7.40 %
 *   top inset       183, bottom inset 183 (symmetric)        -> 19.64 %
 *   stem height     566 · middle 366 · short 216             -> 60.73 / 39.27 / 23.18 %
 *   accent bar      333 x 132 at (366, 617)                  -> spans columns 2-3
 *
 * The file also contradicts itself: the five mock-ups use another mark, a
 * ribbon with an amber diamond. The normative page wins, because it is the one
 * that states the rules. The discrepancy is declared in the deliverable.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

/**
 * The three variants the normative page of the design file declares.
 *
 * The type is local: `<script setup>` compiles to a module with no exports of
 * its own, so publishing it here would not compile.
 */
type VarianteMarca = 'principal' | 'inverso' | 'monocromatico'

const props = withDefaults(defineProps<{
  variante?: VarianteMarca
  conNombre?: boolean
}>(), { variante: 'principal', conNombre: false })

const { t } = useI18n()

/**
 * Brand values, transcribed from the palette of the same design file.
 *
 * They are written here and nowhere else on purpose. A logotype is not themed:
 * the guide forbids recolouring it, so painting the tile with `--color-accion`
 * -which is the teal only under the institutional theme and ink under the
 * default one- would repaint the mark every time the reader changed theme.
 * The design system emits no theme invariant brand token yet.
 */
const TEJA_ACCION = '#086B70'
const TINTA_NAVEGACION = '#102A43'
const ACENTO_ATENCION = '#B97812'
const SUPERFICIE = '#FFFFFF'

/** One rectangle of the symbol, in percentage of the tile side. */
interface BarraMarca {
  readonly id: string
  readonly x: number
  readonly y: number
  readonly ancho: number
  readonly alto: number
}

/** Corner radius of the tile: 56 px measured over a 932 px side. */
const RADIO_TEJA = 6.01

/** Corner radius of every bar: 23 px measured over the same 932 px side. */
const RADIO_BARRA = 2.47

/** The three light bars: the stem of the K and its two descending arms. */
const BARRAS_CLARAS: readonly BarraMarca[] = Object.freeze([
  { id: 'asta', x: 17.81, y: 19.64, ancho: 14.06, alto: 60.73 },
  { id: 'brazo-alto', x: 39.27, y: 19.64, ancho: 14.06, alto: 39.27 },
  { id: 'brazo-corto', x: 60.73, y: 19.64, ancho: 14.06, alto: 23.18 },
])

/** The baseline bar, the only element that carries the attention channel. */
// Its right edge and its baseline are taken from the third column and from
// the stem rather than from their own measurement: the two pairs came out
// two pixels apart at 600 dpi, which is the antialiasing of the render and
// not a decision anyone made.
const BARRA_ACENTO: BarraMarca = Object.freeze({
  id: 'base',
  x: 39.27,
  y: 66.21,
  ancho: 35.52,
  alto: 14.16,
})

/** Fills of each variant, as the three plates of the normative page show them. */
interface PaletaMarca {
  readonly teja: string
  readonly barras: string
  readonly acento: string
  readonly nombre: string
}

const PALETA_POR_VARIANTE: Readonly<Record<VarianteMarca, PaletaMarca>> = Object.freeze({
  // Preferred over light grounds and neutral surfaces.
  principal: {
    teja: TEJA_ACCION,
    barras: SUPERFICIE,
    acento: ACENTO_ATENCION,
    nombre: 'currentColor',
  },
  // Navigation, headers and dark institutional grounds. Measured against the
  // other two plates the drawing is identical, teal tile included: what the
  // inverse variant changes is the wordmark, which the file sets in white so
  // that the lockup survives the navy it is meant to sit on.
  inverso: {
    teja: TEJA_ACCION,
    barras: SUPERFICIE,
    acento: ACENTO_ATENCION,
    nombre: SUPERFICIE,
  },
  // Documents without colour, stamps and single ink applications: the accent
  // bar gives up the amber, because one ink cannot carry two channels.
  monocromatico: {
    teja: TINTA_NAVEGACION,
    barras: SUPERFICIE,
    acento: SUPERFICIE,
    nombre: TINTA_NAVEGACION,
  },
})

const paleta = computed<PaletaMarca>(() => PALETA_POR_VARIANTE[props.variante])

/**
 * The symbol only names the product when no wordmark travels beside it.
 *
 * With the name rendered as text, an accessible name on the drawing would make
 * a screen reader announce "Karisma Data" twice in a row.
 */
const rotuloDelSimbolo = computed<string | undefined>(() =>
  props.conNombre ? undefined : t('brand.name'),
)
</script>

<template>
  <span
    data-marca-karisma
    :data-variante="variante"
    class="inline-flex shrink-0 items-center gap-2.5 pe-4"
    :class="conNombre ? 'min-w-30' : undefined"
  >
    <!--
      `pe-4` above and `size-8` here are the two rules of the guide, applied:
      the symbol never renders below its 32 px digital minimum, and it reserves
      a clear space of half its own side -the "1/2 K" of the plate- towards
      whatever follows it. The leading and vertical clear space is the padding
      of the bar that hosts it.
    -->
    <svg
      data-marca-simbolo
      class="size-8 shrink-0"
      viewBox="0 0 100 100"
      xmlns="http://www.w3.org/2000/svg"
      :role="conNombre ? undefined : 'img'"
      :aria-hidden="conNombre ? 'true' : undefined"
      :aria-label="rotuloDelSimbolo"
      focusable="false"
    >
      <rect
        data-marca-teja
        x="0"
        y="0"
        width="100"
        height="100"
        :rx="RADIO_TEJA"
        :ry="RADIO_TEJA"
        :fill="paleta.teja"
      />
      <rect
        v-for="barra in BARRAS_CLARAS"
        :key="barra.id"
        :data-marca-barra="barra.id"
        :x="barra.x"
        :y="barra.y"
        :width="barra.ancho"
        :height="barra.alto"
        :rx="RADIO_BARRA"
        :ry="RADIO_BARRA"
        :fill="paleta.barras"
      />
      <rect
        :data-marca-barra="BARRA_ACENTO.id"
        data-marca-acento
        :x="BARRA_ACENTO.x"
        :y="BARRA_ACENTO.y"
        :width="BARRA_ACENTO.ancho"
        :height="BARRA_ACENTO.alto"
        :rx="RADIO_BARRA"
        :ry="RADIO_BARRA"
        :fill="paleta.acento"
      />
    </svg>

    <!--
      The wordmark appears from 768 px up, which is where the complete mark
      fits its own 120 px minimum width. Below that the plate rules the symbol
      alone, so the name is not rendered small: it is not rendered.
    -->
    <span
      v-if="conNombre"
      data-marca-nombre
      class="hidden whitespace-nowrap text-titulo-3 sm:inline"
      :style="{ color: paleta.nombre }"
    >
      {{ t('brand.name') }}
    </span>
  </span>
</template>
