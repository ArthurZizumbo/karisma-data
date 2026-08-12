import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'
import type { RolUsuario } from '~/types/sesion'
import { usePermisos } from '~/composables/usePermisos'
import { MODULOS, RUTA_ACCESO, RUTAS_CONTRATO } from '~/utils/navegacion'
import {
  ENDPOINTS_POR_RAMA,
  ROLES_EN_ORDEN,
  SCOPE_POR_RAMA,
  SCOPE_POR_RUTA,
} from '~/utils/permisos.generated'
import { MOTIVO_EXPIRADA, ROLES } from '~/utils/sesion'
import { clavesDe, mensaje } from './i18nDePrueba'

/**
 * US-017 — the barrier that keeps the permission matrix from being duplicated.
 *
 * `docs/security.md` and `app/utils/permisos.generated.ts` are two independent
 * projections of the same source, `SCOPE_REGISTRY`: the first is rendered by
 * `render_permission_matrix()` and the second by `scripts/generar_permisos_ui.py`.
 * Comparing them here is what turns "they cannot drift" into something a run of
 * `pnpm test` proves, without executing a line of Python.
 *
 * Nothing in this file mounts a component. What it measures is a declaration.
 */

/**
 * Reads a file of the repository.
 *
 * The path travels as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function leerDelRepositorio(relativa: string): string {
  const ruta = fileURLToPath(new URL(relativa, import.meta.url))
  try {
    return readFileSync(ruta, 'utf8')
  }
  catch {
    // Explicit and not an `undefined` three assertions later: this suite has a
    // hard dependency on a document US-016 owns, and a check that silently
    // skips when its input is missing is not a barrier.
    throw new Error(
      `falta ${relativa}, que es el insumo de esta prueba. Lo escribe US-016 y `
      + 'se regenera con render_permission_matrix()',
    )
  }
}

const seguridad = leerDelRepositorio('../../docs/security.md')

const MATRIZ_INICIO = '<!-- matriz-permisos:inicio -->'
const MATRIZ_FIN = '<!-- matriz-permisos:fin -->'

/**
 * The permission matrix of `docs/security.md`, as endpoint to declared scopes.
 *
 * Only the generated block is read. The prose around it names endpoints too,
 * and taking those would compare the map against an example instead of against
 * the policy.
 */
function matrizPublicada(): Map<string, RolUsuario[]> {
  const bloque = seguridad.split(MATRIZ_INICIO)[1]?.split(MATRIZ_FIN)[0] ?? ''
  const filas = new Map<string, RolUsuario[]>()

  for (const linea of bloque.split('\n')) {
    const celdas = linea.split('|').map(celda => celda.trim())
    const endpoint = celdas[1]?.match(/^`([A-Z]+ \/\S*)`$/)?.[1]
    if (endpoint === undefined) {
      continue
    }
    const scopes = [...(celdas[2] ?? '').matchAll(/`([a-z]+)`/g)].map(
      coincidencia => coincidencia[1] as RolUsuario,
    )
    filas.set(endpoint, scopes)
  }

  return filas
}

const MATRIZ = matrizPublicada()

/** Highest of several scopes; null means "any valid session" and sits below all. */
function mayor(scopes: (RolUsuario | null)[]): RolUsuario | null {
  const reales = scopes.filter((scope): scope is RolUsuario => scope !== null)
  if (reales.length === 0) {
    return null
  }
  return reales.reduce((uno, otro) => (ROLES.indexOf(uno) >= ROLES.indexOf(otro) ? uno : otro))
}

/** Lowest of several scopes; a single null wins, because null is the floor. */
function menor(scopes: (RolUsuario | null)[]): RolUsuario | null {
  if (scopes.length === 0 || scopes.includes(null)) {
    return null
  }
  return (scopes as RolUsuario[]).reduce((uno, otro) =>
    ROLES.indexOf(uno) <= ROLES.indexOf(otro) ? uno : otro,
  )
}

const RAMAS = MODULOS.flatMap(modulo => modulo.subrutas)
const RUTAS_GUARDADAS = RUTAS_CONTRATO.filter(ruta => ruta !== RUTA_ACCESO)

describe('el mapa generado no puede divergir del documento de seguridad', () => {
  it('nombra solo endpoints que la matriz publicada declara', () => {
    // This is the failure the whole mechanism exists to catch: a User Story
    // renames or adds an endpoint in SCOPE_REGISTRY and nobody regenerates, so
    // the sidebar keeps hiding a module from somebody who may now open it.
    const declarados = Object.values(ENDPOINTS_POR_RAMA).flatMap(lista => [...lista])
    const ausentes = declarados.filter(endpoint => !MATRIZ.has(endpoint))

    expect(declarados.length).toBeGreaterThan(0)
    expect(ausentes).toEqual([])
  })

  it.each(
    Object.entries(ENDPOINTS_POR_RAMA).filter(([, endpoints]) => endpoints.length > 0),
  )('exige en la rama %s el mayor scope de sus endpoints', (rama, endpoints) => {
    const esperado = mayor(
      [...endpoints].map(endpoint => mayor((MATRIZ.get(endpoint) ?? []) as RolUsuario[])),
    )

    // The assistant is cross cutting and has no module, so its exigency travels
    // on its route instead of on a branch of the site map.
    const emitido = rama in SCOPE_POR_RAMA
      ? SCOPE_POR_RAMA[rama]
      : SCOPE_POR_RUTA['/asistente']

    expect(emitido ?? null).toBe(esperado)
  })

  it('usa para el estado sin permiso el mismo texto que publica el 403', () => {
    // The backend answers a stable code and the interface chooses the words. If
    // US-016 rewrites the copy of `permisos_insuficientes` and this screen keeps
    // saying something else, the reader gets two versions of the same refusal.
    const fila = seguridad
      .split('\n')
      .find(linea => linea.includes('`errores.autorizacion.permisos_insuficientes`'))
    const celdas = (fila ?? '').split('|').map(celda => celda.trim())

    expect(fila, 'falta la fila permisos_insuficientes en docs/security.md').toBeDefined()
    expect(mensaje('es', 'authz.noPermission.body')).toBe(celdas[3])
    expect(mensaje('en', 'authz.noPermission.body')).toBe(celdas[4])
  })
})

describe('el mapa generado cubre el mapa de sitio entero', () => {
  it('asigna exigencia a los cuatro modulos y a las dieciseis ramas, sin sobrantes', () => {
    // A branch added to the site map with no entry here would be shown to
    // everybody, which is the silent half of the failure: nothing breaks, the
    // door is simply open.
    const esperadas = [...MODULOS.map(modulo => modulo.id), ...RAMAS.map(rama => rama.id)]

    expect(Object.keys(SCOPE_POR_RAMA).sort()).toEqual(esperadas.sort())
  })

  it('asigna exigencia a toda ruta guardada del contrato, sin sobrantes', () => {
    // '/acceso' must NOT be here: it is public, and an entry for it would mean
    // somebody decided to guard the entry screen.
    expect(Object.keys(SCOPE_POR_RUTA).sort()).toEqual([...RUTAS_GUARDADAS].sort())
    expect(Object.keys(SCOPE_POR_RUTA)).not.toContain(RUTA_ACCESO)
  })

  it.each(MODULOS.map(modulo => modulo.id))(
    'exige en el modulo %s el menor scope de sus ramas',
    (id) => {
      // The minimum and not the maximum. With the maximum, the exploration
      // module would demand `analista` because of its exports panel, and the
      // operations profile would lose the ad hoc query, which is its job.
      const ramas = MODULOS.find(modulo => modulo.id === id)?.subrutas ?? []
      const esperado = menor(ramas.map(rama => SCOPE_POR_RAMA[rama.id] ?? null))

      expect(SCOPE_POR_RAMA[id] ?? null).toBe(esperado)
    },
  )

  it.each(RUTAS_GUARDADAS.filter(ruta => RAMAS.some(rama => rama.ruta === ruta)))(
    'exige en la ruta %s el menor scope de las ramas que pinta',
    (ruta) => {
      const esperado = menor(
        RAMAS.filter(rama => rama.ruta === ruta).map(rama => SCOPE_POR_RAMA[rama.id] ?? null),
      )

      expect(SCOPE_POR_RUTA[ruta] ?? null).toBe(esperado)
    },
  )
})

describe('el vocabulario de roles llega entero desde el backend', () => {
  it('conserva el orden total de ROLE_HIERARCHY, sin repeticiones', () => {
    // Compared against ROLES of utils/sesion.ts, which US-015 owns: comparing
    // the generated map against itself would pass whatever it emitted.
    expect([...ROLES_EN_ORDEN]).toEqual([...ROLES])
    expect(new Set(ROLES_EN_ORDEN).size).toBe(ROLES_EN_ORDEN.length)
    expect(ROLES_EN_ORDEN.at(-1)).toBe('admin')
  })

  it.each(ROLES_EN_ORDEN)('rotula el perfil %s en los dos idiomas', (rol) => {
    // A fifth role arriving without its label would print the raw key at the
    // reader, in the one screen whose job is to explain a refusal.
    for (const idioma of ['es', 'en'] as const) {
      expect(clavesDe(idioma)).toContain(`authz.role.${rol}`)
    }
  })
})

describe('usePermisos proyecta el mapa sobre la sesion', () => {
  it('devuelve la ruta del re-login limpio al expirar', () => {
    // The contract of the query value is shared with the entry screen: two
    // literals would let the guard send a reason that screen does not know.
    expect(usePermisos().expirarSesion()).toBe(`${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`)
  })
})
