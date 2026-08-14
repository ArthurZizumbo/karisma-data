/**
 * Wire contract of the background export, mirrored from the backend.
 *
 * Every field name below is the one the API spells, in Spanish, exactly as
 * `backend/app/models/export.py` froze it: `job_id`, `estado`, `tamano_bytes`,
 * `solicitado_en`. Renaming them here would give the same record two
 * vocabularies -the divergence this project already paid for once with
 * `administrador` against `admin`- and `/api/export` falls through the
 * wildcard Nitro proxy, so there is no route in between where a translation
 * could legitimately live.
 *
 * `object_key` is deliberately absent: the backend never serialises it, and a
 * type that declared it would describe a field the interface can never read.
 */

/**
 * The four states of a job.
 *
 * Terminal is `completado` or `fallido`, and that predicate is written once, in
 * `~/stores/exportaciones`, never as a list of literals at each call site.
 */
export type EstadoTrabajo = 'pendiente' | 'en_proceso' | 'completado' | 'fallido'

/** The two formats the request accepts. `xlsx` is degraded, see the store. */
export type FormatoExportacion = 'csv' | 'xlsx'

/**
 * The three exportable datasets, and only these three.
 *
 * They are the rows of `catalog_source` with a real extract behind them. The
 * backend validator rejects anything else with a 422, so offering a fourth
 * option would build a job that can only end `fallido`.
 */
export type DatasetExportable = 'creditos' | 'liquidez' | 'derivados'

/** Filters as the compiler understands them: `{columna: valor | [valores]}`. */
export type FiltrosExportacion = Readonly<Record<string, string | readonly string[]>>

/** Body of `POST /api/export`. Extra keys are a 422, never an ignored field. */
export interface SolicitudExportacion {
  readonly dataset: DatasetExportable
  readonly formato: FormatoExportacion
  readonly filtros: FiltrosExportacion
}

/** One row of `GET /api/export`, newest first. */
export interface TrabajoResumen {
  readonly job_id: string
  readonly dataset: string
  readonly formato: FormatoExportacion
  readonly estado: EstadoTrabajo
  readonly filas: number | null
  readonly tamano_bytes: number | null
  readonly solicitado_en: string
  readonly iniciado_en: string | null
  readonly terminado_en: string | null
  readonly error: string | null
}

/**
 * Answer of `POST /api/export` and of the polling endpoint.
 *
 * The two extra fields travel together and only when the job completed and the
 * caller owns it: `url_descarga` is a RELATIVE path -
 * `/api/export/<job_id>/download?exp=...&sig=...`- so the Nitro proxy forwards
 * it untouched, and `caduca_en` is the very instant the signed `exp` encodes.
 * Publishing one without the other would describe a deadline belonging to
 * nothing.
 */
export interface TrabajoDetalle extends TrabajoResumen {
  readonly url_descarga: string | null
  readonly caduca_en: string | null
}

/**
 * A job as the interface watches it: the wire record plus what only the client
 * knows, which is that it stopped answering.
 */
export interface TrabajoVigilado extends TrabajoDetalle {
  /** True once the job burned the polling budget without reaching an end. */
  readonly caducadoEnCliente: boolean
}

/** The three moments of the screen. Derived from real state, never set. */
export type MomentoExportacion = 'solicitud' | 'proceso' | 'enlace'

/**
 * Codes that travel in the `error` field of a `fallido` job.
 *
 * They are state of the job and not HTTP: a job that failed answered 200 when
 * it was asked about.
 */
export type CodigoErrorTrabajo
  = | 'origen_ausente'
    | 'columna_desconocida'
    | 'formato_no_disponible'
    | 'fallo_interno'

/**
 * Codes the export endpoints answer with, under `detail.codigo`.
 *
 * This is the second shape of error body and it is not the first: the failures
 * of session and permission come from US-015 and carry `detail` as a loose
 * string. Confusing the two prints an object at the reader.
 */
export type CodigoErrorExportacion
  = | 'trabajo_no_encontrado'
    | 'enlace_caducado'
    | 'firma_invalida'
    | 'trabajos_no_disponibles'

/** A refused request, ready to be rendered. */
export interface FalloExportacion {
  /** HTTP status, or 0 when the failure carried none, as a network error does. */
  readonly estado: number
  /** Stable code under `detail.codigo`, or null when the body carried none. */
  readonly codigo: CodigoErrorExportacion | null
}

/** The four states the history can be in. `listo` is the only happy one. */
export type EstadoHistorial = 'cargando' | 'listo' | 'vacio' | 'error'
