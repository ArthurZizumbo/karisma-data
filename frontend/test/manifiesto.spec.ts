import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

/**
 * US-002 — the frontend manifest as a verifiable contract.
 *
 * `scripts/verificar_pines.sh` checks the same thing, but it only runs when
 * somebody invokes it. These assertions live inside `pnpm test`, so that a
 * `pnpm install` on another machine that breaks a pin fails loudly instead of
 * silently degrading reproducibility.
 */

interface Manifiesto {
  packageManager?: string
  engines?: { node?: string }
  devEngines?: { runtime?: { name?: string, version?: string, onFail?: string } }
  pnpm?: unknown
}

function leer(relativa: string): string {
  return readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
}

const manifiesto = JSON.parse(leer('../package.json')) as Manifiesto
const nvmrc = leer('../.nvmrc').trim()
const dockerfile = leer('../Dockerfile')
const workspace = leer('../pnpm-workspace.yaml')

const MAYOR_ESPERADO = '22'

/**
 * Floor of the Node 22 line, raised on 10-ago-2026 when @nuxtjs/i18n entered.
 *
 * Its toolchain pulls oxc-parser, whose native binding declares
 * `engines: ^20.19.0 || >=22.12.0`. pnpm skips an optional dependency whose
 * engines do not fit the range the project declares, so with `>=22.0.0` the
 * binding was silently omitted and every command that loads the module -
 * `nuxt prepare`, `nuxt typecheck`, `nuxt build` - died with "Cannot find
 * module ./parser.win32-x64-msvc.node". Narrowing the range is what installs
 * it. `.nvmrc` and the Dockerfile keep naming the line, not the patch: both
 * resolve to a current 22.x, which is already above this floor.
 */
const MINIMO_ESPERADO = '22.12.0'

describe('CA-2 · gestor de paquetes fijado y verificable', () => {
  it('declara pnpm con version exacta y hash de integridad', () => {
    // Without the sha512 suffix the field pins the version but not its
    // content: a tampered republication of that same version would run alike.
    expect(manifiesto.packageManager).toMatch(/^pnpm@\d+\.\d+\.\d+\+sha512\.[a-f0-9]{128}$/)
  })
})

describe('CA-2b · la configuracion de pnpm vive en un solo archivo', () => {
  it('no conserva el campo pnpm en package.json', () => {
    // pnpm 11 does not read that field. Leaving it is worse than not having
    // it: the next reader believes it is in force.
    expect(manifiesto.pnpm).toBeUndefined()
  })

  it('no deja marcadores sin resolver en pnpm-workspace.yaml', () => {
    expect(workspace).not.toContain('set this to')
  })

  it('declara pmOnFail y el permiso de compilacion de cada dependencia nativa', () => {
    expect(workspace).toMatch(/^pmOnFail:\s*download$/m)
    expect(workspace).toMatch(/^\s+esbuild:\s*(true|false)$/m)
    expect(workspace).toMatch(/^\s+unrs-resolver:\s*(true|false)$/m)
  })
})

describe('CA-3 · Node 22 fijado en las cuatro puertas', () => {
  it('fija Node 22 en .nvmrc', () => {
    expect(nvmrc).toBe(MAYOR_ESPERADO)
  })

  it('acota engines.node al mayor 22 con un rango, no con una cadena suelta', () => {
    expect(manifiesto.engines?.node).toBe(`>=${MINIMO_ESPERADO} <23.0.0`)
  })

  it('declara devEngines.runtime, que es la unica puerta que descarga y fija', () => {
    const runtime = manifiesto.devEngines?.runtime
    expect(runtime?.name).toBe('node')
    expect(runtime?.version).toBe(`^${MINIMO_ESPERADO}`)
    expect(runtime?.onFail).toBe('download')
  })

  it('no baja el piso por debajo del que exigen los binarios nativos', () => {
    // The two gates that install Node must not drift below the version the
    // oxc-parser binding needs, or pnpm goes back to skipping it and the
    // failure resurfaces as a missing .node file at build time.
    expect(manifiesto.engines?.node).toContain(MINIMO_ESPERADO)
    expect(manifiesto.devEngines?.runtime?.version).toContain(MINIMO_ESPERADO)
  })

  it('usa node:22-slim en las dos etapas del Dockerfile', () => {
    const etapas = [...dockerfile.matchAll(/^FROM\s+node:(\S+)/gm)].map(coincidencia => coincidencia[1])
    expect(etapas).toHaveLength(2)
    for (const etapa of etapas) {
      expect(etapa).toBe(`${MAYOR_ESPERADO}-slim`)
    }
  })

  it('no se contradice entre puertas', () => {
    const declarados = new Set([
      nvmrc,
      manifiesto.engines?.node?.match(/>=(\d+)\./)?.[1],
      manifiesto.devEngines?.runtime?.version?.match(/\^(\d+)\./)?.[1],
      dockerfile.match(/^FROM\s+node:(\d+)-/m)?.[1],
    ])
    expect([...declarados]).toEqual([MAYOR_ESPERADO])
  })
})
