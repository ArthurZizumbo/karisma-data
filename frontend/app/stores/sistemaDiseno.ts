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
  CONTRASTES_POR_TEMA,
  CORRIENTE,
  FECHA_SISTEMA,
  PEOR_SEPARACION_POR_TEMA,
  REGLAS,
  SEMANTICOS,
  SEPARACIONES_POR_TEMA,
  SERIES,
  SUPERFICIE,
  TEMAS,
  TIPOGRAFIA,
  TOKENS,
  VERSION_SISTEMA,
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
    peorSeparacion,
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
    series: SERIES as readonly TokenColor[],
    tokens: TOKENS as readonly TokenColor[],
    tipografia: TIPOGRAFIA as readonly RolTipografico[],
    reglas: REGLAS as readonly string[],
  }
})
