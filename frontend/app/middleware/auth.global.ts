import { usePermisos } from '~/composables/usePermisos'
import { useSesion } from '~/composables/useSesion'
import { decidirGuarda, esRutaPublica } from '~/utils/guarda'

/**
 * Global session guard. The only global middleware of the project.
 *
 * `@nuxtjs/i18n` registers none under `strategy: 'no_prefix'` -verified against
 * the installed module, `dist/module.mjs` line 1764 and
 * `dist/runtime/plugins/route-locale-detect.js`- so there is no ordering to
 * negotiate. The language travels in the `karisma_locale` cookie with
 * `path: '/'`, which is why a redirect never loses it.
 *
 * Everything this file does is glue. The decision itself is a pure function in
 * `~/utils/guarda`, and what each route demands comes from the generated map
 * through `usePermisos`.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const { limpiarBloqueo, marcarBloqueo, scopeExigidoPor, expirada, olvidarExpiracion }
    = usePermisos()

  // Every navigation starts without an inherited block: otherwise the "no
  // permission" state sticks and the next allowed screen renders blocked.
  limpiarBloqueo()

  // The three public routes cost no request at all. On Cloud Run with scale to
  // zero that is the difference between opening the prototype index and waking
  // the backend up for nothing.
  if (esRutaPublica(to.path)) {
    return
  }

  const { sesion, cargarSesion } = useSesion()

  // Read before any call: it is what tells an expiry from a first visit. The
  // flag is part of it because whoever detected the 401 already emptied the
  // session state, so without it the two cases are indistinguishable here.
  const habiaSesion = sesion.value !== null || expirada.value

  if (!habiaSesion) {
    try {
      // Not revalidated on every navigation. The cookie and the token die
      // together at 1800 s, so after that the cookie stops travelling and the
      // first data call answers 401.
      await cargarSesion()
    }
    catch {
      // An unhandled rejection here would turn a network hiccup into an error
      // page. The state is cleared explicitly rather than assumed.
      sesion.value = null
    }
  }

  const decision = decidirGuarda({
    ruta: to.path,
    sesion: sesion.value,
    habiaSesion,
    scopeExigido: scopeExigidoPor(to.path),
  })

  switch (decision.tipo) {
    case 'permitir':
      return

    case 'redirigir':
      // The reason is consumed here: it is told once, on the screen that can
      // act on it. Telling it again on the next navigation would accuse the
      // reader of an expiry that already happened and was already explained.
      olvidarExpiracion()

      // On the server this is a real 302, so the browser never receives the
      // HTML of a route it may not open.
      return navigateTo({
        path: decision.destino,
        query: decision.motivo === undefined ? {} : { motivo: decision.motivo },
      })

    case 'sin-permiso': {
      marcarBloqueo({ ruta: to.path, scopeExigido: decision.scopeExigido })

      // The navigation is NOT aborted: it has to complete so the address stays
      // shareable and the back button behaves. What changes is the status of
      // the server response, which is how the smoke tells the state apart from
      // a screen that merely rendered.
      const evento = useRequestEvent()
      if (evento !== undefined) {
        setResponseStatus(evento, 403)
      }
      return
    }

    default: {
      // A new variant of DecisionGuarda breaks the build here instead of
      // falling through to "allow", which is the failure a boolean would have.
      const exhaustivo: never = decision
      return exhaustivo
    }
  }
})
