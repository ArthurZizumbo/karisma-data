import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EstadoSinPermiso from '~/components/comun/EstadoSinPermiso.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { RUTA_ACCESO, RUTA_GUIA, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { SCOPE_POR_RUTA } from '~/utils/permisos.generated'
import { ROLES } from '~/utils/sesion'
import { crearI18nDePrueba } from './i18nDePrueba'

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

/**
 * Routes declared in the `RUTAS=( ... )` array of the shell script.
 *
 * The line break is matched as `\r?\n` and the closing paren is anchored with
 * `\s*$`: the script is checked out with CRLF on any machine whose git has
 * `core.autocrlf` on, and a pattern that only accepts LF reads an empty array
 * there. Silently: `?.[1] ?? ''` turns the miss into zero routes, so the two
 * assertions below fail with "expected 10 to be +0" and point at the contract
 * instead of at the line ending that actually broke.
 */
function rutasDelGuion(): string[] {
  const bloque = guion.match(/^RUTAS=\(\r?\n([\s\S]*?)^\)\s*$/m)?.[1] ?? ''
  return [...bloque.matchAll(/^\s*"([^"]+)"\s*$/gm)].map(coincidencia => coincidencia[1]!)
}

function constanteDelGuion(nombre: string): string {
  return guion.match(new RegExp(`^${nombre}="?([^"\\n]+)"?$`, 'm'))?.[1] ?? ''
}

/** Same, for a constant whose value carries double quotes of its own. */
function constanteEntrecomillada(nombre: string): string {
  return guion.match(new RegExp(`^${nombre}='([^']+)'$`, 'm'))?.[1] ?? ''
}

describe('el smoke recorre exactamente las rutas publicas del portal', () => {
  it('declara las diez rutas: el indice, la guia y las ocho del contrato', () => {
    // The order of the walk is not part of the contract -the script chains no
    // state between routes- but the set is: one route too many or too few and
    // the smoke stops covering what it claims to cover.
    const rutas = rutasDelGuion()

    expect([...rutas].sort()).toEqual([RUTA_INDICE, RUTA_GUIA, ...RUTAS_CONTRATO].sort())
    expect(new Set(rutas).size).toBe(rutas.length)
  })

  it('cuadra su total esperado con las rutas que recorre', () => {
    // The script aborts when the two numbers disagree; this test keeps that
    // abort from being discovered with the environment up and the gate looming.
    //
    // Two above the contract, not one: the index and the style guide are the
    // two routes that answer 200 without being a branch of the A3 map.
    expect(Number(constanteDelGuion('TOTAL_ESPERADO'))).toBe(rutasDelGuion().length)
    expect(Number(constanteDelGuion('TOTAL_ESPERADO'))).toBe(RUTAS_CONTRATO.length + 2)
  })
})

describe('el smoke busca una marca que la franja realmente imprime', () => {
  it('encuentra el atributo del guion en el HTML de FranjaAlcance', () => {
    // CA-7 is checked in the smoke with grep. If the attribute is renamed in
    // the component, the grep would stop finding it and the failure would show
    // up with the stack running, not here.
    const marca = constanteDelGuion('MARCA_FRANJA')

    expect(marca).not.toBe('')
    expect(
      mount(FranjaAlcance, { global: { plugins: [crearI18nDePrueba()] } }).html(),
    ).toContain(marca)
  })

  it('consulta la sonda del api en la ruta que el backend expone', () => {
    // The backend mounts /health at the root, outside the /api prefix, because
    // it does not go through the frontend proxy: Compose and Cloud Run call it
    // directly.
    expect(guion).toContain('${BASE_API}/health')
  })
})

describe('el smoke entra antes de recorrer y ejercita la guarda', () => {
  it('acuna una sesion y recorre las diez rutas con ella', () => {
    // Since US-017 seven of the ten routes answer 302 without a cookie. A walk
    // that forgot the session would report seven broken routes and read like a
    // broken portal instead of like a guard doing its job.
    expect(guion).toContain('acunar_sesion "$ROL_RECORRIDO" "$GALLETAS_RECORRIDO"')
    expect(guion).toContain('-b "$GALLETAS_RECORRIDO"')
  })

  it('recorre con el unico perfil que alcanza las diez rutas', () => {
    // With any other role /administracion answers 403 and the walk fails on a
    // route that is in fact working exactly as designed.
    const rol = constanteDelGuion('ROL_RECORRIDO')
    const inalcanzables = Object.entries(SCOPE_POR_RUTA).filter(
      ([, scope]) => scope !== null && ROLES.indexOf(rol as never) < ROLES.indexOf(scope),
    )

    expect(ROLES).toContain(rol)
    expect(inalcanzables).toEqual([])
  })

  it('comprueba que una ruta guardada rebota sin sesion', () => {
    const ruta = constanteDelGuion('RUTA_GUARDADA')

    expect(RUTAS_CONTRATO).toContain(ruta)
    expect(Object.keys(SCOPE_POR_RUTA)).toContain(ruta)
    expect(ruta).not.toBe(RUTA_ACCESO)
    expect(guion).toContain('comprobar_guarda_sin_sesion')
  })

  it('elige para el caso negativo una ruta que el perfil de prueba no alcanza', () => {
    // If somebody lowers the exigency of that route, the 403 the script waits
    // for becomes a 200 and the check turns into a green that proves nothing.
    const ruta = constanteDelGuion('RUTA_DE_MAYOR_RANGO')
    const rol = constanteDelGuion('ROL_SIN_PERMISO')
    const exigido = SCOPE_POR_RUTA[ruta] ?? null

    expect(ROLES).toContain(rol)
    expect(exigido).not.toBeNull()
    expect(ROLES.indexOf(rol as never)).toBeLessThan(ROLES.indexOf(exigido as never))
  })

  it('busca en el cuerpo bloqueado una marca que el estado realmente imprime', () => {
    // Same failure mode as the scope band: renamed in the component, the grep
    // stops finding it and the defect shows up with the stack running instead
    // of here.
    const marca = constanteEntrecomillada('MARCA_SIN_PERMISO')
    const html = mount(EstadoSinPermiso, {
      props: { scopeExigido: 'admin' as const, rolActual: 'operativo' as const },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true, NuxtLink: true } },
    }).html()

    expect(marca).not.toBe('')
    expect(html).toContain(marca)
  })
})
