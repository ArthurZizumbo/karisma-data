/**
 * Life cycle of the export watch, started once for the whole application.
 *
 * The acceptance criterion is "job status readable from any screen", and that
 * is a statement about where the watch LIVES. A `useFetch` in the export page
 * dies with the page: the reader asks for a million rows, walks to the
 * dashboard while it runs, and comes back to a screen that never learnt the job
 * had finished. The timer belongs to the Pinia store, and the store is created
 * here, at boot, so nothing that unmounts can take it down.
 *
 * `.client` because there is nothing to watch during server rendering: the
 * timer, the tab visibility and the whole notion of "while the reader is
 * elsewhere" only exist in a browser.
 *
 * This is the first file of `app/plugins/`. It was preferred over an edit to
 * `app/layouts/portal.vue` because that layout is shared with the user stories
 * in flight this week, and adding a directory collides with nobody.
 */
import { watch } from 'vue'

import { useSesion } from '~/composables/useSesion'
import { useExportacionesStore } from '~/stores/exportaciones'

export default defineNuxtPlugin(() => {
  const exportaciones = useExportacionesStore()
  const { sesion } = useSesion()

  // The store outlives every page, and that is exactly what makes it a hazard
  // when the reader changes: two analysts share one tab, the first signs out,
  // and without this watch the second one opens the export screen and reads the
  // first one's history -dataset, row counts, sizes- because those rows are
  // still in memory. `olvidar()` covers the expiry path from inside the store;
  // this covers the deliberate sign out, which is a different door and lives in
  // a composable of another User Story that this one does not edit.
  //
  // The comparison is on the login name and not on the object: the session is
  // reloaded from `/api/auth/me` on every boot, so a fresh object for the same
  // person is the normal case and must not wipe a job that is still running.
  watch(
    () => sesion.value?.usuario ?? null,
    (ahora, antes) => {
      if (antes !== null && ahora !== antes) {
        exportaciones.olvidar()
      }
    },
  )

  // Attached at boot and not when the first job is requested: a reader who
  // leaves the tab while a job runs must stop paying for the poll, and the
  // listener is what makes that true on every screen and not only on the one
  // that started the job.
  //
  // Nothing is torn down here because there is no moment at which to do it: the
  // Nuxt runtime publishes no `app:unmount` hook, and the only event that ends
  // this application is the document going away, which takes the timer and the
  // listener with it. The store still owns the pair -`detenerSondeo` and
  // `olvidarVisibilidad`- for whoever creates it outside a browser tab.
  exportaciones.observarVisibilidad()
})
