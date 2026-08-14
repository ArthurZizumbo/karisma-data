/**
 * Background export jobs: the history, the single global timer and the moment.
 *
 * It lives in Pinia and not in the screen because the acceptance criterion is
 * "job status readable from any screen": a `useFetch` in the page dies the
 * moment the reader navigates, and the extraction takes longer than the visit.
 * The store keeps DECISIONS and the small records the interface renders; the
 * produced file never comes near it, the browser downloads it through a signed
 * link.
 *
 * SSE was considered and refused in the plan: the chat already pays for that
 * transport, and one `SELECT` by primary key every three seconds is cheaper to
 * build, to test and to run than a second stream.
 *
 * The three moments are DERIVED. Nothing in this module can set them, which is
 * the whole point: a screen that could be told it is showing a link would be
 * able to show one that does not exist.
 */
import type { ComputedRef, Ref } from 'vue'
import type {
  CodigoErrorExportacion,
  EstadoHistorial,
  EstadoTrabajo,
  FalloExportacion,
  MomentoExportacion,
  SolicitudExportacion,
  TrabajoDetalle,
  TrabajoResumen,
  TrabajoVigilado,
} from '~/types/exportacion'
import { defineStore } from 'pinia'
import { computed, ref, shallowRef, watch } from 'vue'
import { usePermisos } from '~/composables/usePermisos'
import { estadoDeFallo } from '~/utils/sesion'

/** Path published by the permission registry of US-016. Not invented here. */
export const RUTA_EXPORTACION = '/api/export'

/**
 * Milliseconds between two polls of the same live job.
 *
 * Three thousand, and the number is argued. The target job -a million rows to
 * CSV through `sink_csv`- takes 8 to 15 seconds, so three seconds yields three
 * to five samples of the intermediate state: enough for the progress to move
 * and for the A4 capture of the second moment not to depend on luck. At one
 * second the traffic triples and nothing new is learnt, because below two
 * seconds the eye cannot tell one refresh of an indeterminate bar from the
 * next. At five seconds a short job jumps from `pendiente` to `completado` in a
 * single sample and the intermediate state becomes invisible, which is exactly
 * what the deliverable needs to be able to photograph.
 */
export const INTERVALO_SONDEO_MS = 3000

/**
 * Polls a single job is worth before the interface gives up on it.
 *
 * Two hundred at three seconds is ten minutes. The background task is a
 * `BackgroundTasks` of FastAPI with no queue behind it, so a job is lost if the
 * container scales to zero mid flight; without this ceiling the browser would
 * ask about it until the tab closes.
 */
export const MAXIMO_SONDEOS = 200

/** Rows asked of the history. The endpoint caps at 200. */
export const LIMITE_HISTORIAL = 50

/** The four codes `ExportErrorCode` publishes under `detail.codigo`. */
const CODIGOS_DE_EXPORTACION: readonly CodigoErrorExportacion[] = Object.freeze([
  'trabajo_no_encontrado',
  'enlace_caducado',
  'firma_invalida',
  'trabajos_no_disponibles',
])

/**
 * Whether a job will never change state again.
 *
 * Written once and read everywhere, because it is the predicate that decides
 * when the timer stops. The backend froze it as `EstadoTrabajo.es_terminal`,
 * and a second spelling of it -a list of literals inlined at a call site- is
 * how a polling loop outlives its own job.
 *
 * @param estado - State the job last reported.
 * @returns True for `completado` and `fallido`, false for the other two.
 */
export function esTerminal(estado: EstadoTrabajo): boolean {
  return estado === 'completado' || estado === 'fallido'
}

/**
 * Reads the status and the stable code out of a refused request.
 *
 * There are two shapes of failure body on these four endpoints and telling them
 * apart is the whole job of this function: session and permission failures come
 * from US-015 and carry `detail` as a loose string, while the export failures
 * carry `{"detail": {"codigo": "..."}}`. Reading the first as the second prints
 * an object at the reader; reading the second as the first loses the code.
 *
 * @param error - Value thrown by the request.
 * @returns The status -0 when there is none- and the code when the body has one.
 */
export function falloDeExportacion(error: unknown): FalloExportacion {
  const detalle = (error as { data?: { detail?: unknown } } | null)?.data?.detail
  const codigo
    = detalle !== null && typeof detalle === 'object'
      ? (detalle as { codigo?: unknown }).codigo
      : null

  return {
    estado: estadoDeFallo(error),
    codigo:
      typeof codigo === 'string' && (CODIGOS_DE_EXPORTACION as readonly string[]).includes(codigo)
        ? (codigo as CodigoErrorExportacion)
        : null,
  }
}

/** Newest first, with a deterministic tie break for two jobs of the same ms. */
function porRecencia(uno: TrabajoVigilado, otro: TrabajoVigilado): number {
  const diferencia = Date.parse(otro.solicitado_en) - Date.parse(uno.solicitado_en)
  return diferencia !== 0 ? diferencia : uno.job_id.localeCompare(otro.job_id)
}

/** Everything the export screen -and any future watcher of it- needs. */
export interface EstadoExportaciones {
  /** History, newest first, with the polled detail merged over each row. */
  trabajos: ComputedRef<readonly TrabajoVigilado[]>
  /** Jobs that can still change state. Drives the timer and nothing else. */
  vivos: ComputedRef<readonly TrabajoVigilado[]>
  /** The moment the real state is in. Derived, never assigned. */
  momento: ComputedRef<MomentoExportacion>
  /** Moment pinned by `?momento=`, which also switches the auto advance off. */
  momentoFijado: Ref<MomentoExportacion | null>
  /** What the screen renders: the pinned moment when there is one. */
  momentoVisible: ComputedRef<MomentoExportacion>
  /**
   * Real job the visible moment is about, or null when none is in it.
   *
   * This is state, not presentation: it does not move when the reader closes a
   * card, so it is the only honest source for "this moment has nothing in it".
   */
  trabajoDelMomento: ComputedRef<TrabajoVigilado | null>
  /**
   * Row the reader has expanded right now, or null when none is.
   *
   * A presentation decision and nothing more. One click on an open card empties
   * it while the job keeps running, so no emptiness may be derived from here.
   */
  trabajoDestacado: ComputedRef<TrabajoVigilado | null>
  /** State of the history request, in the vocabulary the screens share. */
  estado: ComputedRef<EstadoHistorial>
  /** Last refused request, or null. */
  fallo: Ref<FalloExportacion | null>
  /** True while a request is on the wire. */
  enviando: Ref<boolean>
  /** True while the timer is armed. */
  sondeando: ComputedRef<boolean>
  cargarHistorial: () => Promise<void>
  /** POST /api/export. Returns the job id, or null when it was refused. */
  solicitar: (payload: SolicitudExportacion) => Promise<string | null>
  iniciarSondeo: () => void
  detenerSondeo: () => void
  /**
   * Drops every trace of the reader who was signed in, and stops the watch.
   *
   * A Pinia store belongs to the application, not to the session: the same tab
   * that an analyst signs out of is the tab the next one signs into, and the
   * rows kept here -dataset, row count, size, instants of every export- would
   * be waiting for them. It is not a cosmetic reset either, because `trabajos`
   * re-injects as rows every detail that the freshly read history does not
   * carry: the previous session's jobs would come back on top of a history that
   * is legitimately someone else's.
   */
  olvidar: () => void
  /** Pauses on a hidden tab. Idempotent; the plugin calls it once at boot. */
  observarVisibilidad: () => void
  olvidarVisibilidad: () => void
  fijarMomento: (valor: MomentoExportacion | null) => void
  /** Expands one row of the history by hand, or clears the choice with null. */
  destacar: (jobId: string | null) => void
}

export const useExportacionesStore = defineStore('exportaciones', (): EstadoExportaciones => {
  const { expirarSesion } = usePermisos()

  // shallowRef: rows are replaced whole and never edited in place, so a deep
  // proxy over the list would buy reactivity that nothing here reads.
  const resumenes = shallowRef<readonly TrabajoResumen[]>([])
  const detalles = ref<Record<string, TrabajoDetalle>>({})
  const caducados = ref<readonly string[]>([])
  const fase = ref<'inicial' | 'cargando' | 'listo' | 'error'>('inicial')
  const fallo = ref<FalloExportacion | null>(null)
  const enviando = ref(false)
  const momentoFijado = ref<MomentoExportacion | null>(null)
  const destacadoId = ref<string | null>(null)
  const armado = ref(false)

  /**
   * True once the reader opened a row by hand.
   *
   * It switches the follow off, and only that: without it, the row the reader
   * just opened would close again on the next poll that moves the state. Not
   * reactive, because nothing renders it.
   */
  let manual = false

  /** Polls spent per job. Not reactive: nothing renders a counter. */
  const sondeos = new Map<string, number>()
  /** Jobs whose detail was already asked for, so the watcher cannot loop. */
  const detallesPedidos = new Set<string>()

  /**
   * Jobs already known to have reached an end, from any source.
   *
   * This is what makes the history be re-read once per TRANSITION and not once
   * per poll: it is seeded by every history read and by every detail, so a job
   * that was already finished the first time the interface heard of it never
   * asks for a refresh that would bring back the same rows.
   */
  const terminales = new Set<string>()

  let temporizador: ReturnType<typeof setInterval> | null = null
  let escuchando = false

  const trabajos = computed<readonly TrabajoVigilado[]>(() => {
    const vistos = new Set<string>()
    const filas: TrabajoVigilado[] = []

    for (const resumen of resumenes.value) {
      vistos.add(resumen.job_id)
      const detalle = detalles.value[resumen.job_id]
      filas.push({
        url_descarga: null,
        caduca_en: null,
        ...resumen,
        ...(detalle ?? {}),
        caducadoEnCliente: caducados.value.includes(resumen.job_id),
      })
    }

    // A job requested a second ago is not in the history yet: the answer of the
    // POST is the only record of it until the next reload, and dropping it here
    // would make the screen forget what the reader just asked for.
    for (const detalle of Object.values(detalles.value)) {
      if (!vistos.has(detalle.job_id)) {
        filas.push({ ...detalle, caducadoEnCliente: caducados.value.includes(detalle.job_id) })
      }
    }

    return filas.sort(porRecencia)
  })

  const vivos = computed<readonly TrabajoVigilado[]>(() =>
    trabajos.value.filter(trabajo => !esTerminal(trabajo.estado) && !trabajo.caducadoEnCliente),
  )

  const momento = computed<MomentoExportacion>(() => {
    if (vivos.value.length > 0) {
      return 'proceso'
    }
    const reciente = trabajos.value[0]
    return reciente !== undefined && reciente.estado === 'completado' ? 'enlace' : 'solicitud'
  })

  const momentoVisible = computed<MomentoExportacion>(() => momentoFijado.value ?? momento.value)

  /**
   * The real job a moment expands.
   *
   * @param valor - Moment being rendered.
   * @returns That job, or null when no real job is in that moment.
   */
  function trabajoDeMomento(valor: MomentoExportacion): TrabajoVigilado | null {
    if (valor === 'proceso') {
      return vivos.value[0] ?? null
    }
    if (valor === 'enlace') {
      return trabajos.value.find(trabajo => trabajo.estado === 'completado') ?? null
    }
    return null
  }

  /**
   * The job of the moment being rendered, as state and not as presentation.
   *
   * Published because the screen has to be able to tell "there is nothing in
   * this moment" from "the reader closed the card". `trabajoDestacado` answers
   * the second question and the reader empties it with one click, so a screen
   * that derived its emptiness from it would announce that no export is running
   * while the export runs, visible, three rows below.
   */
  const trabajoDelMomento = computed<TrabajoVigilado | null>(() =>
    trabajoDeMomento(momentoVisible.value),
  )

  const trabajoDestacado = computed<TrabajoVigilado | null>(
    () => trabajos.value.find(trabajo => trabajo.job_id === destacadoId.value) ?? null,
  )

  const estado = computed<EstadoHistorial>(() => {
    if (fase.value === 'inicial' || fase.value === 'cargando') {
      return 'cargando'
    }
    if (fase.value === 'error') {
      return 'error'
    }
    return trabajos.value.length === 0 ? 'vacio' : 'listo'
  })

  const sondeando = computed<boolean>(() => armado.value)

  function detenerSondeo(): void {
    if (temporizador !== null) {
      clearInterval(temporizador)
      temporizador = null
    }
    armado.value = false
  }

  /**
   * Empties everything the previous reader left behind.
   *
   * Every live structure, not only the visible list: `detalles` alone is enough
   * to repopulate the history -`trabajos` appends every detail the history does
   * not carry, which is what keeps a job requested a second ago on screen- and
   * `terminales`, `sondeos` and `detallesPedidos` are keyed by job id, so a
   * leftover entry would decide, for the next session, that a job it has never
   * seen was already asked about. The timer goes with them: there is nothing
   * left to watch, and the cookie that made those requests possible is gone.
   *
   * `momentoFijado` stays. It is not the reader's data but the query string of
   * the visit -`?momento=`- and the screen re-applies it, or clears it, on the
   * next navigation; dropping it here would leave the address bar naming a pin
   * the store no longer holds.
   */
  function olvidar(): void {
    detenerSondeo()
    resumenes.value = []
    detalles.value = {}
    caducados.value = []
    sondeos.clear()
    terminales.clear()
    detallesPedidos.clear()
    destacadoId.value = null
    fallo.value = null
    enviando.value = false
    // Back to `inicial` and not to `listo`: with the rows gone, a phase that
    // still claimed the history had been read would render the designed empty
    // state -"you have not exported anything yet"- to the next reader before a
    // single request has been made on their behalf.
    fase.value = 'inicial'
    // The row the previous reader opened by hand cannot keep the follow off for
    // the next one.
    manual = false
  }

  /**
   * Ends a session the server no longer recognises.
   *
   * @param error - Value thrown by the request.
   * @returns True when the failure was a 401 and the reader is on their way out.
   */
  async function expiro(error: unknown): Promise<boolean> {
    if (estadoDeFallo(error) !== 401) {
      return false
    }
    // Before the navigation, never after: the entry screen is one route away
    // and this store outlives it. Polling a portal that has stopped recognising
    // the session is the second way this timer leaks, and leaving the rows here
    // is how the next reader of this tab ends up looking at someone else's
    // exports.
    olvidar()
    await navigateTo(expirarSesion())
    return true
  }

  /**
   * Files the detail the server just answered with.
   *
   * @param detalle - Job exactly as the endpoint returned it.
   */
  function guardar(detalle: TrabajoDetalle): void {
    detalles.value = { ...detalles.value, [detalle.job_id]: detalle }
  }

  /**
   * Files the identifiers that already reached an end.
   *
   * @param filas - Rows just read from the wire, of either shape.
   */
  function registrarTerminales(filas: readonly TrabajoResumen[]): void {
    for (const fila of filas) {
      if (esTerminal(fila.estado)) {
        terminales.add(fila.job_id)
      }
    }
  }

  /** GET /api/export: the history of the caller, newest first. */
  async function pedirHistorial(): Promise<TrabajoResumen[]> {
    return await $fetch<TrabajoResumen[]>(RUTA_EXPORTACION, {
      query: { limite: LIMITE_HISTORIAL },
    })
  }

  /**
   * Reads the history again because a job just reached an end.
   *
   * The poll only knows the jobs THIS tab is watching, so an export the same
   * analyst asked for in another tab stays invisible here until the list is
   * read again -which, without this, meant reloading the page. It runs once per
   * transition to a terminal state and never once per poll: at three seconds a
   * refresh per round would double the traffic of the screen to re-read a list
   * that only changes when a job starts or ends.
   *
   * Silent on purpose. The rows on screen are the last thing the server really
   * said, and blanking them into an error banner because a refresh nobody asked
   * for hit a blip would take away what the reader already has. A session that
   * died is the exception: there is nothing left to refresh.
   */
  async function releerHistorial(): Promise<void> {
    try {
      const filas = await pedirHistorial()
      resumenes.value = filas
      registrarTerminales(filas)
      // Same rule as in the poll: the list the reader is looking at came back
      // whole, so whatever failed before is no longer what is happening.
      fallo.value = null
      fase.value = 'listo'
      // The other tab may have left a job still running: from here on it is
      // watched by this one too, which is the point of keeping the watch in the
      // store and not in the screen that started it.
      iniciarSondeo()
    }
    catch (error) {
      await expiro(error)
    }
  }

  /**
   * Takes a job out of the watch list without pretending that it finished.
   *
   * @param jobId - Identifier of the job the portal stops watching.
   */
  function darPorPerdido(jobId: string): void {
    if (!caducados.value.includes(jobId)) {
      caducados.value = [...caducados.value, jobId]
    }
  }

  /** GET /api/export/{job_id}: the state, and the signed link once it exists. */
  async function consultar(jobId: string): Promise<void> {
    try {
      const detalle = await $fetch<TrabajoDetalle>(`${RUTA_EXPORTACION}/${jobId}`)
      const acabaDeTerminar = esTerminal(detalle.estado) && !terminales.has(detalle.job_id)
      // The band describes the state of NOW, not the worst state ever reached.
      // A single blip during a ten minute watch used to leave the red stripe on
      // screen until the reader navigated away, next to a card that meanwhile
      // finished and is offering its link: two readings of the same job, and
      // the loud one is the false one.
      fallo.value = null
      guardar(detalle)
      registrarTerminales([detalle])
      if (acabaDeTerminar) {
        await releerHistorial()
      }
    }
    catch (error) {
      if (await expiro(error)) {
        return
      }
      const detalle = falloDeExportacion(error)
      fallo.value = detalle
      // A job the server no longer recognises will not start recognising it:
      // asking again every three seconds until the tab closes is the leak this
      // branch exists to close.
      if (detalle.estado === 404) {
        darPorPerdido(jobId)
      }
    }
  }

  /** One round: every live job asked once, then the timer re-examined. */
  async function sondear(): Promise<void> {
    const activos = vivos.value
    if (activos.length === 0) {
      detenerSondeo()
      return
    }

    await Promise.all(
      activos.map(async (trabajo) => {
        const cuenta = (sondeos.get(trabajo.job_id) ?? 0) + 1
        sondeos.set(trabajo.job_id, cuenta)
        if (cuenta > MAXIMO_SONDEOS) {
          darPorPerdido(trabajo.job_id)
          return
        }
        await consultar(trabajo.job_id)
      }),
    )

    if (vivos.value.length === 0) {
      detenerSondeo()
    }
  }

  function alCambiarVisibilidad(): void {
    if (document.hidden) {
      detenerSondeo()
      return
    }
    iniciarSondeo()
  }

  function observarVisibilidad(): void {
    if (escuchando || typeof document === 'undefined') {
      return
    }
    document.addEventListener('visibilitychange', alCambiarVisibilidad)
    escuchando = true
  }

  function olvidarVisibilidad(): void {
    if (!escuchando) {
      return
    }
    document.removeEventListener('visibilitychange', alCambiarVisibilidad)
    escuchando = false
  }

  function iniciarSondeo(): void {
    // One timer for the whole application. A second one would double the
    // traffic and turn the declared interval into a lie.
    if (temporizador !== null || vivos.value.length === 0) {
      return
    }
    if (typeof document !== 'undefined' && document.hidden) {
      return
    }
    observarVisibilidad()
    temporizador = setInterval(() => {
      void sondear()
    }, INTERVALO_SONDEO_MS)
    armado.value = true
  }

  async function cargarHistorial(): Promise<void> {
    fase.value = fase.value === 'listo' ? 'listo' : 'cargando'
    fallo.value = null

    try {
      const filas = await pedirHistorial()
      resumenes.value = filas
      registrarTerminales(filas)
      fase.value = 'listo'
      // A job left running when the reader closed the tab is still running now.
      iniciarSondeo()
    }
    catch (error) {
      if (await expiro(error)) {
        return
      }
      fallo.value = falloDeExportacion(error)
      fase.value = 'error'
    }
  }

  async function solicitar(payload: SolicitudExportacion): Promise<string | null> {
    enviando.value = true
    fallo.value = null

    try {
      const trabajo = await $fetch<TrabajoDetalle>(RUTA_EXPORTACION, {
        method: 'POST',
        body: payload,
      })
      guardar(trabajo)
      sondeos.set(trabajo.job_id, 0)
      // The new job is the one the reader is waiting for, so an old row they
      // had expanded stops being the answer to "what is happening".
      manual = false
      iniciarSondeo()
      return trabajo.job_id
    }
    catch (error) {
      if (!(await expiro(error))) {
        fallo.value = falloDeExportacion(error)
      }
      return null
    }
    finally {
      enviando.value = false
    }
  }

  function fijarMomento(valor: MomentoExportacion | null): void {
    momentoFijado.value = valor
    // The pinned moment decides which real job is expanded, so a choice the
    // reader made before pinning cannot survive it.
    manual = false
    destacadoId.value = trabajoDelMomento.value?.job_id ?? null
  }

  function destacar(jobId: string | null): void {
    manual = true
    destacadoId.value = jobId === destacadoId.value ? null : jobId
  }

  // The follow. The expanded row is the job of the moment being rendered, and
  // it moves when that job moves -which is what makes the second and the third
  // moment appear on their own- until the reader opens a row by hand. With a
  // moment pinned, `momentoVisible` no longer advances, so this only fills in
  // the real job of the pinned moment: the state is never fabricated, and with
  // no job in that moment nothing is expanded.
  watch(
    () => trabajoDelMomento.value?.job_id ?? null,
    (jobId) => {
      if (!manual) {
        destacadoId.value = jobId
      }
    },
  )

  // The history only carries the summary, so a job that completed while the tab
  // was closed has no link until it is asked about by id. Asking once per job
  // is what keeps this from looping when the answer carries no link either.
  watch(trabajoDestacado, (trabajo) => {
    if (
      trabajo !== null
      && trabajo.estado === 'completado'
      && trabajo.url_descarga === null
      && !detallesPedidos.has(trabajo.job_id)
    ) {
      detallesPedidos.add(trabajo.job_id)
      void consultar(trabajo.job_id)
    }
  })

  return {
    trabajos,
    vivos,
    momento,
    momentoFijado,
    momentoVisible,
    trabajoDelMomento,
    trabajoDestacado,
    estado,
    fallo,
    enviando,
    sondeando,
    cargarHistorial,
    solicitar,
    iniciarSondeo,
    detenerSondeo,
    olvidar,
    observarVisibilidad,
    olvidarVisibilidad,
    fijarMomento,
    destacar,
  }
})
