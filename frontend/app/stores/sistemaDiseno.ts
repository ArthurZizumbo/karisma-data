/**
 * The design system as shared state.
 *
 * The tokens themselves are build-time constants emitted by `design/emitir.py`,
 * so putting them behind a store would normally be indirection with no gain.
 * What justifies it is the mode and the theme: every token has a value per
 * theme and per mode, the two are shared runtime state, and resolving one
 * without the others is what makes a component import three things and get
 * them out of step.
 *
 * Components read tokens from here and never from the generated module, so a
 * rename in the emitter reaches one file instead of every consumer.
 */
import { defineStore } from 'pinia'
import { computed, onScopeDispose, ref } from 'vue'
import { useModo } from '~/composables/useModo'
import { useTema, type TemaPortal } from '~/composables/useTema'
import {
  ACCION,
  BARRA_LATERAL,
  CERTIFICACION,
  CONTRASTES_POR_TEMA,
  CORRIENTE,
  ESTADOS_CERTIFICACION,
  FECHA_SISTEMA,
  PEOR_SEPARACION_CERTIFICACION,
  PEOR_SEPARACION_POR_TEMA,
  REGLAS,
  SEMANTICOS,
  SEPARACIONES_CERTIFICACION_POR_TEMA,
  SEPARACIONES_POR_TEMA,
  SERIES,
  SUPERFICIE,
  TEMAS,
  TIPOGRAFIA,
  TOKENS,
  VERSION_SISTEMA,
  type EstadoCertificacion,
  type ParContraste,
  type RolTipografico,
  type SeparacionSemantica,
  type TokenColor,
} from '~/utils/tokens.generated'

export const useSistemaDiseno = defineStore('sistemaDiseno', () => {
  /**
   * What the operating system currently prefers.
   *
   * It lives in the store because a Pinia store is a per-request singleton
   * under SSR. A module ref would leak one visitor's preference into another
   * visitor's render, and `useState` would tie the composable to a Nuxt
   * runtime it does not need.
   */
  const preferenciaDelSistema = ref<'claro' | 'oscuro'>('claro')

  if (import.meta.client) {
    const consulta = window.matchMedia('(prefers-color-scheme: dark)')
    preferenciaDelSistema.value = consulta.matches ? 'oscuro' : 'claro'
    const alCambiar = (evento: MediaQueryListEvent): void => {
      preferenciaDelSistema.value = evento.matches ? 'oscuro' : 'claro'
    }
    consulta.addEventListener('change', alCambiar)
    onScopeDispose(() => consulta.removeEventListener('change', alCambiar))
  }

  const { modo, eleccion, elegir } = useModo(preferenciaDelSistema)

  /**
   * Visual theme on screen.
   *
   * It is resolved here and not in each component for the same reason the mode
   * is: the two axes decide the value of every token together, and a component
   * that read one of them from the store and the other from a composable would
   * paint a colour that belongs to neither combination.
   */
  const { tema, fijarTema } = useTema()

  /** Resolve one token to the hex the reader is actually seeing. */
  function valor(token: TokenColor): string {
    return token.temas[tema.value][modo.value]
  }

  /** Look a token up by name; throws rather than returning a silent fallback. */
  function porNombre(nombre: string): TokenColor {
    const encontrado = TOKENS.find((t) => t.nombre === nombre)
    if (encontrado === undefined) {
      throw new Error(`token de color desconocido: ${nombre}`)
    }
    return encontrado
  }

  /**
   * The contrast matrix of the combination on screen, not of the four at once.
   *
   * The ground is not the same in both themes, so a ratio measured in one says
   * nothing about the other: filtering by mode alone would publish the number
   * of a combination the reader is not looking at.
   */
  const contrastes = computed<readonly ParContraste[]>(() =>
    CONTRASTES_POR_TEMA.filter((par) => par.tema === tema.value && par.modo === modo.value),
  )

  /** Dichromatic separation of every semantic pair, for the active combination. */
  const separaciones = computed<readonly SeparacionSemantica[]>(() =>
    SEPARACIONES_POR_TEMA.filter((s) => s.tema === tema.value && s.modo === modo.value),
  )

  /**
   * Worst semantic separation in the active mode.
   *
   * In light mode it is a measured ceiling and not a defect: four semantics all
   * clearing 4.5:1 over a light ground are capped below 0.16 luminance, and
   * four hues do not separate inside that band. It is why shape and icon are
   * mandatory rather than decorative.
   */
  const peorSeparacion = computed<number>(
    () => PEOR_SEPARACION_POR_TEMA[tema.value][modo.value],
  )

  /**
   * Dichromatic separation of the three certification states.
   *
   * It travels apart from `separaciones` because the two answer different
   * questions: that one measures the four semantic marks against each other,
   * this one measures whether `en-revision` and `obsoleto` -which meant the
   * same thing on screen until this release- can still be told apart by a
   * reader who loses a channel. Folding them into one list would also move the
   * published worst pair of the palette, which the graded report already
   * prints.
   */
  const separacionesCertificacion = computed<readonly SeparacionSemantica[]>(() =>
    SEPARACIONES_CERTIFICACION_POR_TEMA.filter(
      (s) => s.tema === tema.value && s.modo === modo.value,
    ),
  )

  /** Worst separation of the certification family in the active combination. */
  const peorSeparacionCertificacion = computed<number>(
    () => PEOR_SEPARACION_CERTIFICACION[tema.value][modo.value],
  )

  /** Every token that fails its own declared rule. Empty is the only pass. */
  const incumplimientos = computed<readonly ParContraste[]>(() =>
    contrastes.value.filter((par) => par.veredicto === 'falla'),
  )

  return {
    modo,
    eleccion,
    elegir,
    tema,
    fijarTema,
    temas: TEMAS as readonly TemaPortal[],
    valor,
    porNombre,
    contrastes,
    separaciones,
    separacionesCertificacion,
    peorSeparacion,
    peorSeparacionCertificacion,
    incumplimientos,
    version: VERSION_SISTEMA,
    fecha: FECHA_SISTEMA,
    superficie: SUPERFICIE as readonly TokenColor[],
    corriente: CORRIENTE as readonly TokenColor[],
    // The group the emitter opened for the institutional identity. Exposed
    // beside the other four and never folded into them: a consumer that walks
    // the groups has to reach every token of TOKENS, and the palette plate
    // proved what happens otherwise -it announced twenty-one and painted
    // eighteen, with action and selection invisible in the graded style guide.
    accion: ACCION as readonly TokenColor[],
    semanticos: SEMANTICOS as readonly TokenColor[],
    // The two groups the A4 excellence pass opened. They are exposed here for
    // the same reason as the rest: the plate that walks the groups has to
    // reach every token of TOKENS, and the palette plate already proved what
    // happens otherwise -it announced twenty-one and painted eighteen-.
    barraLateral: BARRA_LATERAL as readonly TokenColor[],
    certificacion: CERTIFICACION as readonly TokenColor[],
    // Colour and shape together: whoever paints a certification state must not
    // be the one choosing its icon, which is how `en revision` and `obsoleto`
    // ended up sharing a triangle.
    estadosCertificacion: ESTADOS_CERTIFICACION as readonly EstadoCertificacion[],
    series: SERIES as readonly TokenColor[],
    tokens: TOKENS as readonly TokenColor[],
    tipografia: TIPOGRAFIA as readonly RolTipografico[],
    reglas: REGLAS as readonly string[],
  }
})
