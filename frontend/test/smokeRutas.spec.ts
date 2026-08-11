import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'

/**
 * US-001 — `scripts/smoke_rutas.sh` as a verifiable contract.
 *
 * The smoke is the closing script of the US, but it only runs with the stack
 * up: during the week nobody executes it and its list of routes can fall behind
 * the contract without any warning. These assertions live inside `pnpm test`
 * and compare the three constants of the script against the TypeScript source
 * of truth, so that drift is caught as it is written and not on gate day.
 *
 * None of this runs the script or opens a connection: the versioned file and
 * the markup rendered by the scope banner are the whole subject under test.
 */

/**
 * Reads a file of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function leerDelRepositorio(relativa: string): string {
  return readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
}

const guion = leerDelRepositorio('../../scripts/smoke_rutas.sh')

/** Routes declared in the `RUTAS=( ... )` array of the shell script. */
function rutasDelGuion(): string[] {
  const bloque = guion.match(/^RUTAS=\(\n([\s\S]*?)^\)$/m)?.[1] ?? ''
  return [...bloque.matchAll(/^\s*"([^"]+)"\s*$/gm)].map(coincidencia => coincidencia[1]!)
}

function constanteDelGuion(nombre: string): string {
  return guion.match(new RegExp(`^${nombre}="?([^"\\n]+)"?$`, 'm'))?.[1] ?? ''
}

describe('el smoke recorre exactamente las rutas del contrato', () => {
  it('declara las nueve rutas: el indice mas las ocho del contrato', () => {
    // The order of the walk is not part of the contract -the script chains no
    // state between routes- but the set is: one route too many or too few and
    // the smoke stops covering what it claims to cover.
    const rutas = rutasDelGuion()

    expect([...rutas].sort()).toEqual([RUTA_INDICE, ...RUTAS_CONTRATO].sort())
    expect(new Set(rutas).size).toBe(rutas.length)
  })

  it('cuadra su total esperado con las rutas que recorre', () => {
    // The script aborts when the two numbers disagree; this test keeps that
    // abort from being discovered with the environment up and the gate looming.
    expect(Number(constanteDelGuion('TOTAL_ESPERADO'))).toBe(rutasDelGuion().length)
    expect(Number(constanteDelGuion('TOTAL_ESPERADO'))).toBe(RUTAS_CONTRATO.length + 1)
  })
})

describe('el smoke busca una marca que la franja realmente imprime', () => {
  it('encuentra el atributo del guion en el HTML de FranjaAlcance', () => {
    // CA-7 is checked in the smoke with grep. If the attribute is renamed in
    // the component, the grep would stop finding it and the failure would show
    // up with the stack running, not here.
    const marca = constanteDelGuion('MARCA_FRANJA')

    expect(marca).not.toBe('')
    expect(mount(FranjaAlcance).html()).toContain(marca)
  })

  it('consulta la sonda del api en la ruta que el backend expone', () => {
    // The backend mounts /health at the root, outside the /api prefix, because
    // it does not go through the frontend proxy: Compose and Cloud Run call it
    // directly.
    expect(guion).toContain('${BASE_API}/health')
  })
})
