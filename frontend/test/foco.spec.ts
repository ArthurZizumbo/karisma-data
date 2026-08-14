import { beforeEach, describe, expect, it } from 'vitest'

import { enfocables, siguienteEnfocable } from '~/utils/foco'

/**
 * US-029 — the pure half of the focus trap.
 *
 * The tab cycle is the logic every accessibility criterion of this User Story
 * hangs from, so it is tested as a function and not through a mounted
 * component: the assertions below say what the cycle does, and no assertion
 * needs a dialog, an event or a language to hold.
 */

let contenedor: HTMLElement

/** Builds a container out of HTML and puts it in the document. */
function montar(html: string): HTMLElement {
  const nodo = document.createElement('div')
  nodo.innerHTML = html
  document.body.append(nodo)
  return nodo
}

beforeEach(() => {
  document.body.innerHTML = ''
  return () => {
    document.body.innerHTML = ''
  }
})

describe('enfocables', () => {
  it('devuelve los nodos del contenedor en orden de documento', () => {
    // A selector run over `document` instead of over the container would drag
    // the sidebar into the cycle, and the trap would hand focus to the chrome.
    montar('<button id="fuera">fuera</button>')
    contenedor = montar(`
      <a id="uno" href="/gobierno">uno</a>
      <div><button id="dos">dos</button></div>
      <details><summary id="tres">tres</summary></details>
      <input id="cuatro">
    `)

    expect(enfocables(contenedor).map(nodo => nodo.id)).toEqual(['uno', 'dos', 'tres', 'cuatro'])
  })

  it('descarta deshabilitados, ocultos y tabindex negativo', () => {
    // The heading of the panel carries tabindex="-1" so that focus can land on
    // it when the overlay opens. Including it would trap Tab on the title.
    contenedor = montar(`
      <h2 id="titulo" tabindex="-1">Linaje</h2>
      <button id="apagado" disabled>apagado</button>
      <div hidden><button id="escondido">escondido</button></div>
      <button id="vivo">vivo</button>
      <span id="programatico" tabindex="0">programatico</span>
    `)

    expect(enfocables(contenedor).map(nodo => nodo.id)).toEqual(['vivo', 'programatico'])
  })

  it('no lanza sobre un panel sin ningun control', () => {
    // The error state of the overlay is a heading and a paragraph, and the
    // handler asks for the list on every keystroke.
    contenedor = montar('<p>No se pudo cargar el linaje.</p>')

    expect(enfocables(contenedor)).toEqual([])
  })
})

describe('siguienteEnfocable', () => {
  beforeEach(() => {
    contenedor = montar(`
      <button id="primero">primero</button>
      <button id="medio">medio</button>
      <button id="ultimo">ultimo</button>
    `)
  })

  it('envuelve en los dos extremos', () => {
    // `indexOf + 1` without the modulo breaks exactly at the last node, which
    // is where focus escapes; and a handler written only for the forward
    // direction leaves Shift+Tab walking out through the top.
    const lista = enfocables(contenedor)
    const primero = lista[0]!
    const ultimo = lista[2]!

    expect(siguienteEnfocable(lista, ultimo, false)?.id).toBe('primero')
    expect(siguienteEnfocable(lista, primero, true)?.id).toBe('ultimo')
    expect(siguienteEnfocable(lista, primero, false)?.id).toBe('medio')
    expect(siguienteEnfocable(lista, lista[1]!, true)?.id).toBe('primero')
  })

  it('entra por un extremo cuando el foco no esta en la lista', () => {
    // On open, focus sits on the heading, which is outside the cycle. Without
    // this branch `indexOf` returns -1 and Shift+Tab would index at -1.
    const lista = enfocables(contenedor)
    const titulo = document.createElement('h2')

    expect(siguienteEnfocable(lista, null, false)?.id).toBe('primero')
    expect(siguienteEnfocable(lista, titulo, true)?.id).toBe('ultimo')
  })

  it('con lista vacia devuelve null', () => {
    // The error state has no controls; `lista[0]!` would throw at runtime.
    expect(siguienteEnfocable([], null, false)).toBeNull()
    expect(siguienteEnfocable([], null, true)).toBeNull()
  })
})
