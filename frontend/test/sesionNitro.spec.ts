import { beforeEach, describe, expect, it, vi } from 'vitest'

/**
 * US-015 — the four Nitro routes that keep the JWT out of the browser.
 *
 * The whole security claim of this User Story lives on this side: the token is
 * minted here, stored in an httpOnly cookie here and replayed as a bearer
 * header here, and the browser never holds it. Every assertion below pins one
 * way that claim can quietly stop being true.
 *
 * No test opens a connection and none of them reads a file of `backend/`. The
 * contract of the API is frozen in section 4 of the planning document, and the
 * doubles below implement exactly that contract: the h3 utilities, `$fetch` and
 * the upstream answers.
 */

/** Minimal shape of the h3 event the handlers actually read. */
interface EventoFalso {
  path: string
  method: string
  origen: string
  cabeceras: Record<string, string>
  cookies: Record<string, string>
  cuerpo: unknown
  context: { nitro: Record<string, unknown> }
}

/** A cookie written or dropped by a handler. */
interface CookieEscrita {
  nombre: string
  valor: string
  opciones: Record<string, unknown>
}

/** A call a handler made to the backend. */
interface LlamadaUpstream {
  url: string
  opciones: Record<string, unknown>
}

const API_BASE = 'http://api-de-compose:8000'
const TOKEN = 'jwt.de.prueba.sin-secreto'

const PERFIL = {
  id: '0f6d2a1e-0000-4000-8000-000000000001',
  username: 'lmendez',
  email: 'lmendez@karisma.demo',
  full_name: 'Laura Méndez',
  role: 'operativo',
  disabled: false,
  created_at: '2026-08-11T00:00:00Z',
}

let cookiesEscritas: CookieEscrita[]
let cookiesBorradas: CookieEscrita[]
let llamadas: LlamadaUpstream[]
let sinContenido: number[]

/** Answers the doubled backend gives, keyed by the path being asked for. */
let respuestas: Map<string, () => unknown>

function crearEvento(parcial: Partial<EventoFalso> = {}): EventoFalso {
  return {
    path: '/api/auth/token',
    method: 'POST',
    origen: 'https://karisma-web.example',
    cabeceras: {},
    cookies: {},
    cuerpo: { usuario: 'lmendez', contrasena: 'clave-de-prueba' },
    context: { nitro: {} },
    ...parcial,
  }
}

/**
 * Loads a handler with the Nitro auto-imports already doubled.
 *
 * The module is imported after the stubs are in place because
 * `defineEventHandler` runs at import time.
 */
async function cargar(ruta: string): Promise<(evento: EventoFalso) => Promise<unknown>> {
  vi.resetModules()
  const modulo = await import(/* @vite-ignore */ ruta)
  return modulo.default as unknown as (evento: EventoFalso) => Promise<unknown>
}

const cargarToken = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/auth/token.post')
const cargarDemo = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/auth/demo.post')
const cargarLogout = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/auth/logout.post')
const cargarComodin = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/[...]')

beforeEach(() => {
  cookiesEscritas = []
  cookiesBorradas = []
  llamadas = []
  sinContenido = []
  respuestas = new Map<string, () => unknown>([
    ['/api/auth/token', () => ({ access_token: TOKEN, token_type: 'bearer' })],
    ['/api/auth/demo', () => ({ access_token: TOKEN, token_type: 'bearer', modo: 'demostracion' })],
    ['/api/auth/me', () => PERFIL],
  ])

  vi.stubGlobal('defineEventHandler', (manejador: unknown) => manejador)
  vi.stubGlobal('useRuntimeConfig', () => ({ apiBase: API_BASE }))
  vi.stubGlobal('readBody', (evento: EventoFalso) => Promise.resolve(evento.cuerpo))
  vi.stubGlobal('getRequestURL', (evento: EventoFalso) => new URL(evento.path, evento.origen))
  vi.stubGlobal(
    'getHeader',
    (evento: EventoFalso, nombre: string) => evento.cabeceras[nombre.toLowerCase()],
  )
  vi.stubGlobal('getCookie', (evento: EventoFalso, nombre: string) => evento.cookies[nombre])
  vi.stubGlobal('getRequestIP', () => '203.0.113.7')

  vi.stubGlobal(
    'setCookie',
    (_evento: EventoFalso, nombre: string, valor: string, opciones: Record<string, unknown>) => {
      cookiesEscritas.push({ nombre, valor, opciones })
    },
  )
  vi.stubGlobal(
    'deleteCookie',
    (_evento: EventoFalso, nombre: string, opciones: Record<string, unknown>) => {
      cookiesBorradas.push({ nombre, valor: '', opciones })
    },
  )
  vi.stubGlobal('sendNoContent', (_evento: EventoFalso, codigo: number) => {
    sinContenido.push(codigo)
  })

  vi.stubGlobal(
    'createError',
    (opciones: { statusCode: number, statusMessage?: string, data?: unknown }) =>
      Object.assign(new Error(opciones.statusMessage ?? 'Error'), opciones),
  )

  vi.stubGlobal('$fetch', (url: string, opciones: Record<string, unknown> = {}) => {
    llamadas.push({ url, opciones })
    const respuesta = respuestas.get(new URL(url).pathname)
    if (respuesta === undefined) {
      return Promise.reject(Object.assign(new Error('Not Found'), { status: 404 }))
    }
    return Promise.resolve(respuesta())
  })

  vi.stubGlobal(
    'proxyRequest',
    (evento: EventoFalso, destino: string, opciones?: { headers?: Record<string, string> }) =>
      Promise.resolve({ destino, cabeceras: opciones?.headers, evento }),
  )

  return () => {
    vi.unstubAllGlobals()
  }
})

describe('la cookie de sesion', () => {
  it('sale httpOnly, estricta, de sitio completo y con la vida del token', async () => {
    // Without httpOnly any injected script walks off with the token and the
    // central claim of this User Story stops being true. SameSite=Strict is the
    // browser half of the CSRF defence QA-M2 required, and Max-Age exists so no
    // cookie outlives the token it carries.
    const manejador = await cargarToken()

    await manejador(crearEvento())

    expect(cookiesEscritas).toHaveLength(1)
    expect(cookiesEscritas[0]!.nombre).toBe('karisma_sesion')
    expect(cookiesEscritas[0]!.valor).toBe(TOKEN)
    expect(cookiesEscritas[0]!.opciones).toMatchObject({
      httpOnly: true,
      sameSite: 'strict',
      path: '/',
      maxAge: 1800,
    })
  })

  it.each([
    ['https://karisma.example', true],
    ['http://localhost:3000', false],
  ])('con %s marca secure como %s', async (origen, esperado) => {
    // Under `make dev` the container serves the production build over http, so
    // deriving `secure` from import.meta.dev would emit a Secure cookie the
    // browser discards: the login would do nothing in the one environment where
    // the captures are recorded.
    const manejador = await cargarToken()

    await manejador(crearEvento({ origen }))

    expect(cookiesEscritas[0]!.opciones.secure).toBe(esperado)
  })
})

describe('la respuesta al navegador', () => {
  it('lleva la sesion y ningun token', async () => {
    // The comfortable shortcut is returning the body of the backend as it came.
    // It carries the token, and from there it reaches any script on the page.
    const manejador = await cargarToken()

    const respuesta = await manejador(crearEvento())

    expect(respuesta).toEqual({ usuario: 'lmendez', nombre: 'Laura Méndez', rol: 'operativo' })
    expect(JSON.stringify(respuesta)).not.toContain(TOKEN)
  })

  it('pide el perfil con el token recien emitido', async () => {
    const manejador = await cargarToken()

    await manejador(crearEvento())

    const perfil = llamadas.find(llamada => llamada.url.endsWith('/api/auth/me'))
    expect(perfil?.opciones.headers).toEqual({ authorization: `Bearer ${TOKEN}` })
  })

  it('manda las credenciales como formulario de OAuth2', async () => {
    // FastAPI reads them with OAuth2PasswordRequestForm: a JSON body answers
    // 422 and the login never works, whatever the password is.
    const manejador = await cargarToken()

    await manejador(crearEvento())

    const emision = llamadas[0]!
    expect(emision.url).toBe(`${API_BASE}/api/auth/token`)
    expect(emision.opciones.headers).toEqual({
      'content-type': 'application/x-www-form-urlencoded',
    })
    expect(emision.opciones.body).toBe('username=lmendez&password=clave-de-prueba')
  })

  it('traduce el 401 del backend sin repetir su texto', async () => {
    // The backend answers `Credenciales incorrectas`, in Spanish, fixed by the
    // acceptance criteria. Relaying it would put Spanish inside the English
    // interface; what travels is the status and a code.
    respuestas.set('/api/auth/token', () => {
      throw Object.assign(new Error('Unauthorized'), {
        status: 401,
        data: { detail: 'Credenciales incorrectas', codigo: 'credenciales_invalidas' },
      })
    })
    const manejador = await cargarToken()

    await expect(manejador(crearEvento())).rejects.toMatchObject({
      statusCode: 401,
      data: { codigo: 'credenciales_invalidas' },
    })
    expect(cookiesEscritas).toHaveLength(0)
  })

  it('no guarda la cookie si el perfil no se puede leer', async () => {
    // A token whose profile does not read back is a token the interface could
    // not act on: storing it leaves a session that looks open and answers
    // nothing.
    respuestas.set('/api/auth/me', () => ({ ...PERFIL, role: 'administrador' }))
    const manejador = await cargarToken()

    await expect(manejador(crearEvento())).rejects.toMatchObject({ statusCode: 502 })
    expect(cookiesEscritas).toHaveLength(0)
  })
})

describe('el acceso de demostracion', () => {
  it('abre sesion con el rol pedido y guarda la cookie', async () => {
    const manejador = await cargarDemo()

    const respuesta = await manejador(
      crearEvento({ path: '/api/auth/demo', cuerpo: { rol: 'directivo' } }),
    )

    expect(llamadas[0]!.opciones.body).toEqual({ rol: 'directivo' })
    expect(cookiesEscritas[0]!.nombre).toBe('karisma_sesion')
    expect(JSON.stringify(respuesta)).not.toContain(TOKEN)
  })

  it('traduce el 404 del backend a la puerta apagada', async () => {
    // With DEMO_LOGIN_ENABLED off the route does not exist upstream. Reporting
    // it as a server failure would send the reader looking for a fault that is
    // in fact a deliberate configuration.
    respuestas.delete('/api/auth/demo')
    const manejador = await cargarDemo()

    await expect(
      manejador(crearEvento({ path: '/api/auth/demo', cuerpo: { rol: 'analista' } })),
    ).rejects.toMatchObject({ statusCode: 404, data: { codigo: 'demo_deshabilitado' } })
  })

  it('rechaza un rol inventado sin tocar el backend', async () => {
    // Upstream this is a 422, which the screen would report as a server
    // failure; and a role that is not one of the four has no landing route.
    const manejador = await cargarDemo()

    await expect(
      manejador(crearEvento({ path: '/api/auth/demo', cuerpo: { rol: 'administrador' } })),
    ).rejects.toMatchObject({ statusCode: 400, data: { codigo: 'rol_desconocido' } })
    expect(llamadas).toHaveLength(0)
  })
})

describe('la salida', () => {
  it('borra la cookie y no habla con el backend', async () => {
    // The JWT is stateless and there is no revocation list: inventing a call
    // upstream would add server state to a design that deliberately has none.
    const manejador = await cargarLogout()

    await manejador(crearEvento({ path: '/api/auth/logout', cuerpo: null }))

    expect(cookiesBorradas).toHaveLength(1)
    expect(cookiesBorradas[0]!.nombre).toBe('karisma_sesion')
    expect(cookiesBorradas[0]!.opciones).toMatchObject({ httpOnly: true, path: '/' })
    expect(sinContenido).toEqual([204])
    expect(llamadas).toHaveLength(0)
  })
})

describe('el comodin convierte la cookie en un bearer', () => {
  it('inyecta el token de la sesion en cada solicitud', async () => {
    // Without the injection every /api/** call answers 401 while the reader
    // holds a perfectly valid session.
    const manejador = await cargarComodin()

    const respuesta = (await manejador(
      crearEvento({ path: '/api/catalogo', method: 'GET', cookies: { karisma_sesion: TOKEN } }),
    )) as { cabeceras: Record<string, string> }

    expect(respuesta.cabeceras.authorization).toBe(`Bearer ${TOKEN}`)
  })

  it('deja el authorization vacio cuando no hay sesion', async () => {
    // A visitor with no cookie must reach the API as an anonymous caller, not
    // with a header that happens to be missing: the two new cases of
    // `proxyApi.spec.ts` pin the other half, that the client cannot supply one.
    const manejador = await cargarComodin()

    const respuesta = (await manejador(
      crearEvento({ path: '/api/catalogo', method: 'GET' }),
    )) as { cabeceras: Record<string, string> }

    expect(respuesta.cabeceras.authorization).toBe('')
  })
})

describe('la verificacion de origen cierra la otra mitad de QA-M2', () => {
  it.each([
    ['../server/api/[...]', '/api/exportacion'],
    ['../server/api/auth/token.post', '/api/auth/token'],
    ['../server/api/auth/logout.post', '/api/auth/logout'],
  ])('rechaza en %s un POST declarado cross-site', async (modulo, path) => {
    // The literal scenario of QA-M2: a form hosted anywhere else, posting with
    // the session of the victim. The three routes are covered because the two
    // specific ones never reach the catch-all.
    const manejador = await cargar(modulo)
    // Wrapped because the logout handler is synchronous: it has nothing to wait
    // for, so it throws instead of returning a rejected promise.
    const ejecutar = async (): Promise<unknown> =>
      manejador(crearEvento({ path, cabeceras: { 'sec-fetch-site': 'cross-site' } }))

    await expect(ejecutar()).rejects.toMatchObject({
      statusCode: 403,
      data: { codigo: 'origen_ajeno' },
    })
  })

  it('rechaza un POST con Origin ajeno cuando no hay Sec-Fetch-Site', async () => {
    // An older browser sends no Sec-Fetch-Site and the check has to survive it.
    const manejador = await cargarComodin()

    await expect(
      manejador(crearEvento({
        path: '/api/exportacion',
        cabeceras: { origin: 'https://otro-sitio.example' },
      })),
    ).rejects.toMatchObject({ statusCode: 403 })
  })

  it('deja pasar un POST del propio sitio', async () => {
    const manejador = await cargarComodin()

    const respuesta = (await manejador(
      crearEvento({
        path: '/api/exportacion',
        cabeceras: { 'sec-fetch-site': 'same-origin', 'origin': 'https://karisma-web.example' },
      }),
    )) as { destino: string }

    expect(respuesta.destino).toBe(`${API_BASE}/api/exportacion`)
  })

  it('deja pasar un POST sin Origin ni Sec-Fetch-Site', async () => {
    // curl, `scripts/smoke_rutas.sh` and the agent tools are not browsers and
    // send neither header. A check that rejected them would break the manual
    // verification of every following User Story.
    const manejador = await cargarComodin()

    const respuesta = (await manejador(crearEvento({ path: '/api/exportacion' }))) as {
      destino: string
    }

    expect(respuesta.destino).toBe(`${API_BASE}/api/exportacion`)
  })

  it('no le pide origen propio a una lectura', async () => {
    // A GET changes nothing, and demanding the headers there would break every
    // server side render and every link opened from outside the site.
    const manejador = await cargarComodin()

    const respuesta = (await manejador(
      crearEvento({
        path: '/api/catalogo',
        method: 'GET',
        cabeceras: { 'sec-fetch-site': 'cross-site' },
      }),
    )) as { destino: string }

    expect(respuesta.destino).toBe(`${API_BASE}/api/catalogo`)
  })
})
