import type { VueWrapper } from '@vue/test-utils'
import type { EstadoTarjeta, ItemHilo, TarjetaToolCall } from '~/types/chat'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h, nextTick, shallowRef } from 'vue'

import HistorialConversacion, { tarjetasEnVuelo } from '~/components/chat/HistorialConversacion.vue'
import ToolCallCard from '~/components/chat/ToolCallCard.vue'
import LaminaTarjetasToolCall from '~/components/guia/LaminaTarjetasToolCall.vue'
import Guia from '~/pages/guia.vue'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-028 - the tool call card, the thread that holds it and the plate of A4.
 *
 * What is measured here is what makes a number believable and what keeps a
 * long conversation usable, never the markup that carries it: not one Tailwind
 * class, not one element count, not one snapshot. That surface moves in US-024
 * and again in the visual pass of A4, and an assertion on it would be debt
 * deleted at the first real change.
 *
 * Every message is compared against the shipped catalogue through `mensaje`.
 * A spec that typed the copy by hand would stay green while the translation
 * was missing, which is the one defect a bilingual interface cannot afford.
 *
 * The parity of `chat.toolCall.*` between `es` and `en` is deliberately absent:
 * `idioma.spec.ts` already compares the whole key set of both catalogues and
 * `contratos.spec.ts` already demands that every literal key resolve in both.
 * A third copy of that guard would rot in a different direction than the two.
 */

/**
 * Instant every fixture is measured against.
 *
 * Frozen rather than `Date.now()`: the elapsed time is a subtraction, and a
 * wall clock would make the same card read differently on two runs.
 */
const AHORA = 1_755_100_000_000

/** Card whose event is applied in the re-render measurement. */
const ID_OBJETIVO = 'tc-0'

/**
 * Normative correspondence between a contract state and its badge key.
 *
 * Spelled out here and not read from the component: taking the map the
 * component uses would make the assertion agree with itself no matter which
 * key it pointed at. This is the table of section 4.4 of the plan.
 */
const CLAVE_DE_ESTADO: Readonly<Record<EstadoTarjeta, string>> = Object.freeze({
  anuncio: 'chat.toolCall.state.announced',
  ejecucion: 'chat.toolCall.state.running',
  resultado: 'chat.toolCall.state.done',
  error: 'chat.toolCall.state.failed',
})

/** The four states of the contract, in the order the plate walks them. */
const ESTADOS: readonly EstadoTarjeta[] = Object.freeze([
  'anuncio',
  'ejecucion',
  'resultado',
  'error',
])

/**
 * Builds a reduced card, defaulting to the shape the announcement arrives in.
 *
 * The announcement is the default on purpose: it is the state with the most
 * null fields, so a fixture that forgets to override one produces the hardest
 * case and not the easiest.
 *
 * @param parcial - Fields that differ from the announcement.
 * @returns The card as the reducer of US-023 hands it over.
 */
function tarjetaDe(parcial: Partial<TarjetaToolCall> = {}): TarjetaToolCall {
  return {
    id: 'tc-1',
    estado: 'anuncio',
    herramienta: 'consultar_metrica',
    etiqueta: 'chat.toolCall.tool.consultar_metrica',
    transcurrido_ms: null,
    resultado: null,
    fuente: null,
    paso: null,
    iniciadaEnMs: AHORA,
    ...parcial,
  }
}

/** Resolved card with a figure, five rows and a catalogue field behind it. */
function tarjetaResuelta(parcial: Partial<TarjetaToolCall> = {}): TarjetaToolCall {
  return tarjetaDe({
    id: 'tc-resuelta',
    estado: 'resultado',
    herramienta: 'agregar_serie',
    etiqueta: 'chat.toolCall.tool.agregar_serie',
    transcurrido_ms: 1240,
    resultado: {
      columnas: ['chat.toolCall.column.close', 'chat.toolCall.column.coefficient'],
      filas: [
        ['2026-04', 1.19],
        ['2026-05', 1.22],
        ['2026-06', 1.28],
        ['2026-07', 1.31],
        ['2026-08', 1.24],
      ],
      cifra: '1.24',
    },
    fuente: 'catalogo.liquidez.coeficiente_cobertura',
    ...parcial,
  })
}

function montarTarjeta(tarjeta: TarjetaToolCall, ahoraMs: number = AHORA, interrumpida = false) {
  return mount(ToolCallCard, {
    props: { tarjeta, ahoraMs, interrumpida },
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true },
    },
  })
}

function montarHistorial(hilo: readonly ItemHilo[], motivoCierre: 'cancelado' | null = null) {
  return mount(HistorialConversacion, {
    props: { hilo, motivoCierre },
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true },
    },
  })
}

/** Renders a catalogue message with its single placeholder filled in. */
function conValor(clave: string, marcador: string, valor: string): string {
  return mensaje('es', clave).replace(`{${marcador}}`, valor)
}

describe('la tarjeta distingue sus cuatro estados sin depender del color', () => {
  it('pinta cada estado del contrato con su propio valor y su propia rama', () => {
    // The defect: a `v-if` that forgets a branch and lets `error` fall into the
    // one that draws a result. The card would show a figure for a query that
    // returned nothing, which is the hallucination this component exists to
    // make impossible.
    for (const estado of ESTADOS) {
      const wrapper = montarTarjeta(tarjetaDe({ estado, paso: 'recuperacion_de_datos' }))

      expect(wrapper.find('[data-prueba="tarjeta-tool-call"]').attributes('data-estado-tool-call'))
        .toBe(estado)
      wrapper.unmount()
    }

    const fallida = montarTarjeta(tarjetaDe({ estado: 'error', paso: 'recuperacion_de_datos' }))
    const resuelta = montarTarjeta(tarjetaResuelta())

    expect(fallida.find('[data-prueba="fallo"]').exists()).toBe(true)
    expect(fallida.find('[data-prueba="cifra"]').exists()).toBe(false)
    expect(resuelta.find('[data-prueba="cifra"]').exists()).toBe(true)
    expect(resuelta.find('[data-prueba="fallo"]').exists()).toBe(false)
  })

  it('acompana cada estado con icono y con texto, nunca solo con color', () => {
    // The defect: telling the states apart by colour alone. Under dichromacy
    // the resolved badge and the failed one are the same hue, and a reader
    // would take a query that failed for one that was audited. Each badge is
    // checked against the normative table, so swapping two of them -running
    // shown as done- fails here and not in a screenshot nobody reads.
    for (const estado of ESTADOS) {
      const wrapper = montarTarjeta(tarjetaDe({ estado }))
      const insignia = wrapper.find('[data-prueba="insignia-estado"]')

      expect(insignia.find('icon-stub').exists()).toBe(true)
      expect(insignia.text()).toBe(mensaje('es', CLAVE_DE_ESTADO[estado]))
      wrapper.unmount()
    }
  })
})

describe('el anuncio se pinta antes de que exista el dato', () => {
  it('monta sin resultado ni tiempo del servidor, y sin region viva propia', () => {
    // The defect: reading `tarjeta.resultado.filas.length` without a guard. The
    // announcement is emitted BEFORE the tool answers, so that access throws on
    // the very first card of every conversation and takes the thread with it.
    //
    // The second defect, and the reason this assertion is written in the
    // negative: a live region declared here. The card lives inside the
    // `role="log"` of `asistente.vue`, which sets `aria-live="off"` on purpose
    // so the history is navigated and not recited. A polite region nested one
    // level below undoes that decision from the inside, and with the budget of
    // five tool calls per turn it is up to fifteen announcements on top of the
    // ones the turn already makes in its own status region. What announces the
    // turn is that region, once per transition; the card is read when the
    // reader goes to it.
    const tarjeta = tarjetaDe({ estado: 'anuncio' })

    expect(tarjeta.resultado).toBeNull()
    expect(tarjeta.transcurrido_ms).toBeNull()

    const wrapper = montarTarjeta(tarjeta)

    expect(wrapper.find('[data-prueba="estado-tarjeta"]').attributes('aria-live')).toBeUndefined()
    expect(wrapper.find('[data-prueba="anuncio"]').text()).toBe(
      mensaje('es', 'chat.toolCall.announce'),
    )
    expect(wrapper.find('[data-prueba="tabla-resultado"]').exists()).toBe(false)
  })

  it('lee 1.2 s cuando lleva 1200 ms corriendo, y no lo recita', () => {
    // The defect: printing the raw milliseconds -"1200 s"- or rounding to the
    // whole second from the first tick, which shows a query that advances as
    // one that is stuck. The elapsed time is the only signal that the assistant
    // is alive, so while it runs it has a progress bar next to it.
    //
    // The second defect, measured in the negative: `role="status"` on this
    // paragraph. The container rewrites it every 250 ms, and `role="status"`
    // carries an implicit `aria-live="polite"`, so a stopwatch becomes four
    // announcements per second. Politeness defers, it does not merge: the queue
    // drains as soon as the reader goes idle, and what drains is a counter. It
    // is the same reasoning `asistente.vue` uses to refuse a polite region for
    // forty fragments per second, applied at four.
    const wrapper = montarTarjeta(
      tarjetaDe({ estado: 'ejecucion', iniciadaEnMs: AHORA - 1200 }),
      AHORA,
    )
    const transcurrido = wrapper.find('[data-prueba="transcurrido"]')

    expect(transcurrido.text()).toBe(conValor('chat.toolCall.elapsed', 'seconds', '1.2'))
    expect(transcurrido.text()).not.toContain('1200')
    expect(transcurrido.attributes('role')).toBeUndefined()
    expect(transcurrido.attributes('aria-live')).toBeUndefined()
    expect(wrapper.find('[data-prueba="progreso"]').exists()).toBe(true)
  })
})

describe('la cifra llega antes que el texto y nunca sin su fuente', () => {
  it('coloca la tarjeta resuelta por delante del primer texto del turno', () => {
    // The defect: ordering the thread by type, or painting the answer in a
    // container above the cards. Either one breaks the criterion the User Story
    // exists for -the evidence is read before the number it justifies- and no
    // other test would notice, because both items would still be on screen.
    const hilo: readonly ItemHilo[] = [
      { tipo: 'tarjeta', id: 'tc-1', tarjeta: tarjetaResuelta({ id: 'tc-1' }) },
      { tipo: 'texto', id: 'tx-1', texto: 'El coeficiente de cobertura cierra en 1.24.' },
    ]
    const wrapper = montarHistorial(hilo)
    const orden = wrapper.findAll('[data-item]').map(nodo => nodo.attributes('data-item'))

    expect(wrapper.find('[data-estado-tool-call="resultado"]').exists()).toBe(true)
    expect(orden.indexOf('tarjeta')).toBeGreaterThanOrEqual(0)
    expect(orden.indexOf('tarjeta')).toBeLessThan(orden.indexOf('texto'))
  })

  it('marca la ausencia de fuente en lugar de callarla', () => {
    // The defect: a figure with no catalogue behind it painted exactly like a
    // cited one. That is the hallucination the card exists to expose, and the
    // two readings have to differ on screen and not only in the props.
    const sinFuente = montarTarjeta(tarjetaResuelta({ fuente: null }))
    const conFuente = montarTarjeta(tarjetaResuelta())

    expect(sinFuente.find('[data-prueba="fuente"]').text()).toBe(
      mensaje('es', 'chat.toolCall.source.missing'),
    )
    expect(conFuente.find('[data-prueba="fuente"]').text()).toBe(
      conValor('chat.toolCall.source.cited', 'source', 'catalogo.liquidez.coeficiente_cobertura'),
    )
    expect(sinFuente.find('[data-prueba="fuente"]').text()).not.toBe(
      conFuente.find('[data-prueba="fuente"]').text(),
    )
  })
})

/** What one event over one card cost the rest of the thread. */
interface Medicion {
  /** `ToolCallCard` instances whose `updated` hook ran for that single event. */
  actualizadas: number
  /** DOM nodes of a sample of untouched cards, before the event. */
  antes: readonly Element[]
  /** The same sample, after it. */
  despues: readonly Element[]
}

/** Positions of the untouched cards whose DOM identity is sampled. */
const MUESTRA: readonly number[] = Object.freeze([1, 2, 3, 100, 150])

/**
 * Builds a thread of `n` cards: the first one running, the rest resolved.
 *
 * That is the real shape of a conversation -one tool answers at a time- and it
 * is what keeps the measurement honest: with every card in flight the shared
 * clock would repaint all of them, and the counter would end up measuring the
 * tick instead of the event.
 *
 * @param n - Length of the thread.
 * @returns The thread items, in arrival order.
 */
function hiloDe(n: number): readonly ItemHilo[] {
  const items: ItemHilo[] = [{
    tipo: 'tarjeta',
    id: ID_OBJETIVO,
    tarjeta: tarjetaDe({ id: ID_OBJETIVO, estado: 'ejecucion' }),
  }]
  for (let indice = 1; indice < n; indice += 1) {
    const id = `tc-${indice}`
    items.push({
      tipo: 'tarjeta',
      id,
      tarjeta: tarjetaDe({
        id,
        estado: 'resultado',
        transcurrido_ms: 900,
        resultado: { columnas: [], filas: [], cifra: '1.24' },
        fuente: 'catalogo.liquidez.coeficiente_cobertura',
      }),
    })
  }
  return items
}

/**
 * Applies one `tool_call` event over a thread of `n` cards and measures it.
 *
 * The event is applied exactly as the reducer of US-023 applies it: a new
 * array, a new object for the affected card and the SAME reference for every
 * other one. Vue compares props with `===`, and that identity is what decides
 * whether one child is patched or eight hundred are.
 *
 * Timers are faked because the running card feeds on the shared clock: a tick
 * landing mid-measurement would add updates that belong to the clock and not to
 * the event, and the count would depend on how long the machine took to mount.
 *
 * @param n - Length of the thread.
 * @returns The update count and the sampled nodes, before and after.
 */
async function medirEvento(n: number): Promise<Medicion> {
  vi.useFakeTimers()
  let actualizadas = 0

  const hilo = shallowRef<readonly ItemHilo[]>(hiloDe(n))
  const anfitrion = defineComponent({
    setup() {
      return () => h(HistorialConversacion, { hilo: hilo.value, motivoCierre: null })
    },
  })

  const wrapper = mount(anfitrion, {
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true },
      mixins: [{
        updated(this: { $: { type: unknown } }) {
          if (this.$.type === ToolCallCard) {
            actualizadas += 1
          }
        },
      }],
    },
  })
  await nextTick()

  const muestrear = (): Element[] => {
    const tarjetas = wrapper.findAll('[data-prueba="tarjeta-tool-call"]')
    return MUESTRA.map(posicion => tarjetas[posicion]!.element)
  }
  const antes = muestrear()

  actualizadas = 0
  hilo.value = hilo.value.map(item =>
    item.tipo === 'tarjeta' && item.id === ID_OBJETIVO
      ? {
          ...item,
          tarjeta: {
            ...item.tarjeta,
            estado: 'resultado',
            transcurrido_ms: 1240,
            resultado: { columnas: [], filas: [], cifra: '1.24' },
            fuente: 'catalogo.liquidez.coeficiente_cobertura',
          },
        }
      : item,
  )
  await nextTick()

  const medicion: Medicion = { actualizadas, antes, despues: muestrear() }

  wrapper.unmount()
  vi.useRealTimers()
  return medicion
}

describe('actualizar una tarjeta no vuelve a renderizar el historial', () => {
  it('con 200 tarjetas, un evento actualiza exactamente una instancia', async () => {
    // The defect: losing the stable `key`, or a reducer that clones the whole
    // array of objects. Either one re-renders the two hundred cards on every
    // event of the single one that is running, which is the cost the acceptance
    // criterion caps at one.
    const medicion = await medirEvento(200)

    expect(medicion.actualizadas).toBe(1)
  })

  it('el mismo evento cuesta lo mismo con 800 tarjetas que con 200', async () => {
    // The defect: a hidden O(N). It looks fine in a demo of four questions and
    // turns the chat into a crawl five minutes into a real conversation. An
    // absolute threshold would not catch it: only comparing two lengths does.
    const doscientas = await medirEvento(200)
    const ochocientas = await medirEvento(800)

    expect(ochocientas.actualizadas).toBe(doscientas.actualizadas)
  })

  it('conserva la identidad de los nodos de las tarjetas no afectadas', async () => {
    // The defect: Vue recreating elements instead of patching them. The update
    // count would still look low -a recreated child is not an updated one-
    // while the reader loses the focus they had inside a card and every
    // animation in flight restarts. Reference identity is what tells them apart.
    const medicion = await medirEvento(200)

    expect(medicion.antes).toHaveLength(MUESTRA.length)
    for (const [posicion, nodo] of medicion.antes.entries()) {
      expect(medicion.despues[posicion]).toBe(nodo)
    }
  })
})

describe('la anatomia de la tarjeta la mantiene auditable', () => {
  it('conserva icono, nombre, tiempo, resultado y cita de la fuente', () => {
    // The defect: a redesign that drops the source citation "because it did not
    // fit". The card keeps looking correct, stops being auditable, and nobody
    // finds out until someone asks where a number came from.
    const wrapper = montarTarjeta(tarjetaResuelta())
    const anclas = ['icono-herramienta', 'nombre-herramienta', 'transcurrido', 'cifra', 'fuente']

    for (const ancla of anclas) {
      expect(wrapper.find(`[data-prueba="${ancla}"]`).exists()).toBe(true)
    }

    expect(wrapper.find('[data-prueba="nombre-herramienta"]').text()).toBe(
      mensaje('es', 'chat.toolCall.tool.agregar_serie'),
    )
    expect(wrapper.find('[data-prueba="fuente"]').text()).toContain(
      'catalogo.liquidez.coeficiente_cobertura',
    )
  })

  it('despliega la tabla desde un boton que dice si esta abierto y que controla', async () => {
    // The defect: a `<div>` with `@click` for the disclosure. It is unreachable
    // by keyboard and mute to a screen reader, so level 2 of the progressive
    // disclosure does not exist for anyone who is not using a mouse. The row
    // count is asserted too: an `aria-expanded` that flips without opening
    // anything is the same lie with better manners.
    const wrapper = montarTarjeta(tarjetaResuelta())
    const plegable = wrapper.find('[data-prueba="plegable"]')

    expect(plegable.element.tagName).toBe('BUTTON')
    expect(plegable.attributes('aria-expanded')).toBe('false')
    expect(plegable.attributes('aria-controls')).toBe(
      wrapper.find('[data-prueba="tabla-resultado"]').attributes('id'),
    )
    expect(wrapper.findAll('[data-fila]')).toHaveLength(3)

    await plegable.trigger('click')

    expect(wrapper.find('[data-prueba="plegable"]').attributes('aria-expanded')).toBe('true')
    expect(wrapper.findAll('[data-fila]')).toHaveLength(5)
    expect(wrapper.emitted('plegado')).toEqual([[true]])
  })
})

/** Resolves a path of the repository, the way `contratos.spec.ts` does. */
function rutaDelRepositorio(relativa: string): string {
  return fileURLToPath(new URL(relativa, import.meta.url))
}

function montarLamina() {
  return mount(LaminaTarjetasToolCall, {
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true },
    },
  })
}

describe('la lamina de la guia documenta los cuatro estados por separado', () => {
  it('monta cuatro tarjetas reales, una por estado del contrato', () => {
    // The defect: a gallery that stops at three states and leaves out the one
    // that matters most. A4 would document a card that never fails, and the
    // reviewer would never see what the interface does when the tool does not
    // answer.
    const wrapper = montarLamina()
    const tarjetas = wrapper.findAll('[data-estado-tool-call]')

    expect(tarjetas).toHaveLength(4)
    expect(tarjetas.map(nodo => nodo.attributes('data-estado-tool-call')).sort()).toEqual(
      [...ESTADOS].sort(),
    )
  })

  it('da un anclaje distinto a cada estado y casa su seccion con el indice', () => {
    // Two mute failures, and neither one shows on screen. If the four states
    // shared an anchor, the capture script would produce the same image four
    // times and A4 would ship four copies of the announcement. And if the tenth
    // entry of `LAMINAS` were registered under an id that does not match the
    // section, the link `NavegacionLaminas` derives -`#lamina-<id>`- would lead
    // nowhere: nothing renders in red, the reader simply never arrives.
    const wrapper = montarLamina()
    const anclajes = wrapper.findAll('[id^="lamina-tool-call--"]')
      .map(nodo => nodo.attributes('id'))

    expect(anclajes).toHaveLength(4)
    expect(new Set(anclajes).size).toBe(4)
    expect([...anclajes].sort()).toEqual(
      ESTADOS.map(estado => `lamina-tool-call--${estado}`).sort(),
    )

    const pagina = readFileSync(rutaDelRepositorio('../app/pages/guia.vue'), 'utf8')
    const entrada = pagina.match(/id:\s*'([\w-]+)',\s*clave:\s*'guide\.plate\.toolCall'/)
    const montaje = pagina.match(/<LaminaTarjetasToolCall\s+id="([\w-]+)"/)
    if (entrada === null || montaje === null) {
      throw new Error('la lamina nueva no esta registrada en guia.vue')
    }

    expect(wrapper.find('[data-lamina]').attributes('data-lamina')).toBe(entrada[1])
    expect(montaje[1]).toBe(`lamina-${entrada[1]}`)
  })
})

/** Id of the tenth entry of `LAMINAS`, and of the section that renders it. */
const LAMINA_TOOL_CALL = 'tarjetas-tool-call'

/**
 * The guide page, framed the way Nuxt frames it.
 *
 * `definePageMeta` is a macro the Nuxt plugin compiles away and that does not
 * exist here, and `ClientOnly` is a Nuxt component the palette plate wraps its
 * copy button in: both are supplied so that a failure to mount is a failure of
 * the page and not of the harness. No router is installed on purpose -the guide
 * navigates itself with fragment links and reads no route- so nothing of the
 * harness can stand in for a plate that did not render.
 */
function montarGuia(): VueWrapper {
  vi.stubGlobal('definePageMeta', () => undefined)

  return mount(Guia, {
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true, ClientOnly: { template: '<div><slot /></div>' } },
    },
  })
}

describe('la guia monta su decima lamina y no solo la declara', () => {
  /**
   * The page mounted by this block, released case by case.
   *
   * `NavegacionLaminas` opens an `IntersectionObserver` and adds a `scrollend`
   * listener on mount, and `guia.vue` is the only page of this suite: a wrapper
   * left behind would keep both alive into the next file.
   */
  let pagina: VueWrapper | null = null

  afterEach(() => {
    pagina?.unmount()
    pagina = null
    vi.unstubAllGlobals()
  })

  it('renderiza la lamina de tarjetas de tool call anclada dentro de la pagina', () => {
    // The defect this catches: the tenth entry of `LAMINAS` written without the
    // block that renders it -or the block deleted and the entry left behind-.
    // The style guide would ship without the plate that is the acceptance
    // criterion CA-8 of A4, and today NOTHING notices: `guia.vue` is at 0 % of
    // coverage, `laminas.spec.ts` counts chips, moments and icons but never
    // plates, and the case above reads `guia.vue` AS TEXT, so it measures that
    // the entry and the mount are written -not that the page mounts them-. A
    // page that threw on mount, or a `v-if` that hid the plate, would leave
    // every suite green.
    //
    // Mounting is also what makes the assertion about the four cards mean
    // something: the plate is checked on its own elsewhere, and what is
    // measured here is that those four reach the page a reader opens.
    pagina = montarGuia()

    const lamina = pagina.get(`#lamina-${LAMINA_TOOL_CALL}`)

    expect(lamina.attributes('data-lamina')).toBe(LAMINA_TOOL_CALL)
    expect(lamina.text()).toContain(mensaje('es', 'guide.plate.toolCall'))

    const tarjetas = lamina.findAll('[data-estado-tool-call]')

    expect(tarjetas).toHaveLength(4)
    expect(tarjetas.map(nodo => nodo.attributes('data-estado-tool-call')).sort()).toEqual(
      [...ESTADOS].sort(),
    )
  })

  it('deja cada entrada del indice sobre un bloque real y en el mismo orden', () => {
    // The defect this catches, in the two directions the tenth plate can break.
    // An entry with no section: the link `NavegacionLaminas` derives,
    // `#lamina-<id>`, leads nowhere -nothing renders in red, the reader simply
    // never arrives-. A section with no entry: the plate exists and no index
    // reaches it, which for a document read by its index is the same as not
    // being there.
    //
    // The order is compared and not only the set, because `LAMINAS` is
    // documented as "the order the capture script walks them": a plate rendered
    // in a position the index does not predict makes the captures of A4 come
    // out under the wrong heading.
    pagina = montarGuia()

    const enElIndice = pagina.findAll('[data-indice-lamina]')
      .map(nodo => nodo.attributes('data-indice-lamina'))
    const renderizadas = pagina.findAll('[data-lamina]')
      .map(nodo => nodo.attributes('data-lamina'))

    expect(enElIndice).toContain(LAMINA_TOOL_CALL)
    expect(renderizadas).toEqual(enElIndice)

    for (const id of enElIndice) {
      expect(pagina!.find(`#lamina-${id}`).exists(), `sin anclaje: lamina-${id}`).toBe(true)
    }
  })
})

describe('una consulta detenida por el lector no se pinta como fallida', () => {
  it('interrumpe solo lo que seguia en vuelo y apaga el progreso', () => {
    // The defect: `tarjetasEnVuelo` returning every card, so a query that had
    // already answered is repainted as interrupted. That turns "you stopped it"
    // into "it failed" over a figure that is perfectly good, which is the
    // interface lie the cancellation rule exists to prevent. The other half is
    // the opposite one: a card left spinning forever after the stream closed.
    const hilo: readonly ItemHilo[] = [
      { tipo: 'tarjeta', id: 'tc-resuelta', tarjeta: tarjetaResuelta({ id: 'tc-resuelta' }) },
      {
        tipo: 'tarjeta',
        id: 'tc-corriendo',
        tarjeta: tarjetaDe({ id: 'tc-corriendo', estado: 'ejecucion' }),
      },
      { tipo: 'texto', id: 'tx-1', texto: 'El coeficiente de cobertura cierra en 1.24.' },
      {
        tipo: 'tarjeta',
        id: 'tc-anunciada',
        tarjeta: tarjetaDe({ id: 'tc-anunciada', estado: 'anuncio' }),
      },
      {
        tipo: 'tarjeta',
        id: 'tc-fallida',
        tarjeta: tarjetaDe({ id: 'tc-fallida', estado: 'error', paso: 'transporte' }),
      },
    ]

    expect(tarjetasEnVuelo(hilo)).toEqual(['tc-corriendo', 'tc-anunciada'])

    const wrapper = montarHistorial(hilo, 'cancelado')
    const corriendo = wrapper.find('[data-estado-tool-call="ejecucion"]')

    expect(wrapper.findAll('[data-interrumpida="true"]')).toHaveLength(2)
    expect(wrapper.findAll('[data-prueba="progreso"]')).toHaveLength(0)
    expect(corriendo.attributes('data-interrumpida')).toBe('true')
    expect(corriendo.find('[data-prueba="insignia-estado"]').text()).toBe(
      mensaje('es', 'chat.toolCall.state.interrupted'),
    )
    expect(wrapper.find('[data-estado-tool-call="resultado"]').attributes('data-interrumpida'))
      .toBeUndefined()
    expect(wrapper.find('[data-estado-tool-call="error"]').attributes('data-interrumpida'))
      .toBeUndefined()
  })
})
