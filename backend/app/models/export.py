"""Persistence mirror and API contracts of the background export jobs.

The table is created by dbmate (``db/migrations/20260813204211_create_export_job.sql``);
``ExportJob`` only reflects it and never creates schema. Two vocabularies live in
this module as ``StrEnum`` -the lifecycle state and the output format- and both
are literal mirrors of a ``CHECK`` constraint of that migration. The database
keeps the last word: a direct write that bypasses Python is still rejected,
which is the whole reason the states are not validated in Python alone.

The wire contracts are in Spanish, like every other contract of the portal
(``SeriesParams``, ``ErrorSerie``), because they are read by the interface and
not by the database. ``object_key`` never appears in any of them: it is the
opaque handle of the storage backend, the column comment says so in SQL, and a
response that carried it would hand the caller a name it could try to guess
against the bucket.
"""

import uuid
from datetime import datetime
from difflib import get_close_matches
from enum import StrEnum
from typing import Annotated, Any, Final

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

# Datasets a request may name. The criterion is "the source has a real extract
# behind it", and the authority for that is the catalog: the three rows of
# ``catalog_source`` whose ``has_extract`` is true in ``db/seeds/catalog.sql``.
# The other nine documented sources are catalog entries without a Parquet file,
# so accepting them would create a job that can only end as ``fallido``.
#
# The same three names are the keys of ``SILOS`` in ``ml/data/schemas.py`` and
# the three files ``make data`` writes into ``data/silos/``: catalog, generator
# and filesystem agree, and the tuple is verified against the seed by
# ``tests/backend/test_export_job_migracion.py``.
#
# It is a frozen constant and not a query on purpose. A ``field_validator`` runs
# while FastAPI is still parsing the body, before any session exists; reaching
# the database there would put a round trip in the path of a malformed request
# and would make body validation depend on the seed being loaded.
#
# ``serie_tablero`` is deliberately absent: it is the preaggregated artifact of
# ``data/aggregates/``, it has no ``catalog_source`` row, and it is already
# served by ``GET /api/metrics/series``.
DATASETS_EXPORTABLES: Final[tuple[str, ...]] = ("creditos", "liquidez", "derivados")

# Similarity floor of the hint. Below this, ``difflib`` starts suggesting a name
# that shares two letters with what was typed, which reads as a bug rather than
# as help.
_UMBRAL_SUGERENCIA: Final[float] = 0.6


class EstadoTrabajo(StrEnum):
    """Lifecycle state of an export job. Mirrors the CHECK constraint in SQL.

    The four values are the exact set of
    ``CHECK (status IN (...))`` in the migration. Adding a value here without
    adding it there produces a model that persists a row the database refuses,
    and the parity is asserted by the migration test suite.
    """

    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"

    @property
    def es_terminal(self) -> bool:
        """Return whether the job will not change state again.

        The polling store stops on this: a job that reached a terminal state
        will never move, so one more request is one request with no information
        in it.

        Returns:
            True for ``completado`` and ``fallido``, False otherwise.
        """
        return self in (EstadoTrabajo.COMPLETADO, EstadoTrabajo.FALLIDO)


class FormatoExportacion(StrEnum):
    """Output format requested by the analyst: csv or xlsx.

    Mirrors ``CHECK (export_format IN ('csv', 'xlsx'))``. The extension of the
    produced file is the value itself, which is why it is a ``StrEnum`` and not
    a mapping.
    """

    CSV = "csv"
    XLSX = "xlsx"


class ExportJob(SQLModel, table=True):
    """Persisted export job. One row per request; never deleted, only expired.

    ``status`` and ``export_format`` are typed as ``str`` and not as their
    enumerations for the same reason ``AppUser.role`` is: with the enumeration
    here SQLAlchemy would map the columns to its native ``Enum`` type, and the
    real columns are ``TEXT`` with a ``CHECK``, which is what lets a state be
    added without an ``ALTER TYPE``. The model mirrors the database; the
    contracts below carry the closed vocabulary.

    No ``index=True`` is declared on any field. The three indexes of the table
    are one composite and two partial, and none of them is expressible in this
    class; claiming a single column index here would describe an object that
    does not exist in ``db/schema.sql``.

    Attributes:
        id: Primary key, ``gen_random_uuid()`` on the database side.
        requested_by: Owner of the job, foreign key to ``app_user``. Every read
            of the history filters by it; a job belongs to who asked for it.
        dataset: Name of the exported source, one of
            ``DATASETS_EXPORTABLES``.
        export_format: Output format code, ``csv`` or ``xlsx``.
        filters: Structured query already validated and bounded by
            ``SolicitudExportacion``, which is what keeps this JSONB column
            from weighing whatever a request decided to send. Never SQL and
            never a Polars expression.
        status: Lifecycle state code, one of the values of ``EstadoTrabajo``.
        row_count: Rows written, known only once the job completed.
        byte_size: Size of the produced file in bytes.
        object_key: Opaque handle in the storage backend. Never serialized.
        error_code: Stable failure code, required when the state is
            ``fallido``.
        created_at: When the job was requested, ``now()`` on the database side.
        started_at: When the background task picked it up.
        finished_at: When it reached a terminal state.
        expires_at: When the signed link stops working, ``created_at`` plus the
            configured lifetime.
    """

    __tablename__ = "export_job"

    id: uuid.UUID | None = Field(default=None, primary_key=True)
    requested_by: uuid.UUID = Field(foreign_key="app_user.id")
    dataset: str
    export_format: str
    filters: dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    status: str = EstadoTrabajo.PENDIENTE.value
    row_count: int | None = None
    byte_size: int | None = None
    object_key: str | None = None
    error_code: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    expires_at: datetime | None = None


# Ceilings of the structured query one request may carry. They are not taste:
# ``filtros`` is written verbatim into a JSONB column by the first statement of
# the job, so until something bounds the contract, what the body declares is
# what the row weighs, and a dictionary of any size and any depth was accepted
# and stored before any part of the pipeline looked at it.
#
# The numbers are read off the silos an export may name. The widest of the three
# has twelve columns, so one predicate per column never approaches
# ``_FILTROS_MAXIMOS``; the largest closed domain of any of those columns holds
# ten values, and ``_VALORES_MAXIMOS`` leaves an order of magnitude on top for
# the case no domain covers -a list of client or counterparty identifiers typed
# by hand-. The longest text a silo carries in a filterable column is a client
# name, far below ``_LONGITUD_MAXIMA_DE_VALOR``. Together they cap a stored
# query at a few hundred kilobytes instead of at whatever fits through a socket.
_FILTROS_MAXIMOS: Final[int] = 32
_VALORES_MAXIMOS: Final[int] = 100
_LONGITUD_MAXIMA_DE_COLUMNA: Final[int] = 64
_LONGITUD_MAXIMA_DE_VALOR: Final[int] = 128

# Name of a column of the silo, which is the only thing a filter may name.
ColumnaDeFiltro = Annotated[str, Field(max_length=_LONGITUD_MAXIMA_DE_COLUMNA)]

# One value of a membership predicate. This used to be ``Any``, which let a body
# nest an object, a null or an array of arrays inside a filter and hand it to
# ``pl.col(...).is_in(...)`` -the one expression of the extraction the caller
# gets to influence at all-. What replaces it is four scalars and no container:
# the string, which is all the interface ever sends (``analizarFiltros`` of
# ``useExportaciones.ts`` reads ``columna=valor`` into a string, or into a list
# of strings when the reader typed commas), plus the number and boolean forms a
# client or the agent may legitimately send for a numeric or boolean column.
ValorDeFiltro = (
    Annotated[str, Field(max_length=_LONGITUD_MAXIMA_DE_VALOR)] | int | float | bool
)

# A scalar or a bounded list of scalars: the whole vocabulary of ``_con_filtros``
# in ``export_service``, which turns each entry into exactly one ``is_in``.
ValoresDeFiltro = Annotated[list[ValorDeFiltro], Field(max_length=_VALORES_MAXIMOS)]


class SolicitudExportacion(BaseModel):
    """Request body of POST /api/export.

    Unknown keys are rejected instead of ignored: a misspelled filter that is
    silently dropped produces a file that answers a question nobody asked, and
    the download says nothing about it.

    Attributes:
        dataset: Source to export. Validated against ``DATASETS_EXPORTABLES``.
        formato: Output format. Defaults to ``csv``, which is the format the
            spreadsheet of the analyst opens without a converter.
        filtros: Structured query the compiler turns into Polars, bounded in
            width, in depth and in size. Empty means the whole dataset.
    """

    model_config = ConfigDict(extra="forbid")

    dataset: str
    formato: FormatoExportacion = FormatoExportacion.CSV
    filtros: Annotated[
        dict[ColumnaDeFiltro, ValorDeFiltro | ValoresDeFiltro],
        Field(max_length=_FILTROS_MAXIMOS),
    ] = Field(default_factory=dict)

    @field_validator("dataset")
    @classmethod
    def dataset_must_be_known(cls, value: str) -> str:
        """Reject datasets outside the published catalog with a fuzzy hint.

        Accepting an unknown name would cost the caller a job that can only end
        as ``fallido`` after the background task looks for a file that is not
        there, and the failure would arrive seconds later through polling
        instead of immediately in the response.

        Args:
            value: Dataset name as it arrived in the body.

        Returns:
            The name, stripped of surrounding whitespace.

        Raises:
            ValueError: When the name is not one of ``DATASETS_EXPORTABLES``.
        """
        nombre = value.strip()
        if nombre in DATASETS_EXPORTABLES:
            return nombre

        cercanos = get_close_matches(
            nombre.lower(),
            DATASETS_EXPORTABLES,
            n=1,
            cutoff=_UMBRAL_SUGERENCIA,
        )
        pista = f"; el mas parecido es '{cercanos[0]}'" if cercanos else ""
        exportables = ", ".join(DATASETS_EXPORTABLES)
        message = (
            f"'{nombre}' no es un conjunto exportable. Los exportables son "
            f"{exportables}{pista}"
        )
        raise ValueError(message)


class TrabajoResumen(BaseModel):
    """Job as listed in the history: no signed URL, no internal object key.

    Neither absent field is an oversight. ``object_key`` is the handle of the
    storage backend and stays inside the server, and the signed URL is minted
    per request with its own expiry, so publishing it in a list would hand out
    as many live links as rows the page carries.

    Attributes:
        job_id: Identifier of the job and path parameter of the detail
            endpoint.
        dataset: Source that was exported.
        formato: Output format that was requested.
        estado: Lifecycle state of the job.
        filas: Rows written, ``None`` until the job completes.
        tamano_bytes: Size of the produced file, ``None`` until it completes.
        solicitado_en: When the job was requested.
        iniciado_en: When the background task picked it up, ``None`` while it
            is still queued.
        terminado_en: When it reached a terminal state, ``None`` while it is
            alive.
        error: Stable failure code, present only when the state is
            ``fallido``.
    """

    job_id: uuid.UUID
    dataset: str
    formato: FormatoExportacion
    estado: EstadoTrabajo
    filas: int | None = None
    tamano_bytes: int | None = None
    solicitado_en: datetime
    iniciado_en: datetime | None = None
    terminado_en: datetime | None = None
    error: str | None = None


class TrabajoDetalle(TrabajoResumen):
    """Job as polled: adds signed URL and expiry when the state is completed.

    The two added fields travel together and only together. The expiry that
    matters to the reader is the expiry of the link they are looking at, not a
    property of the row: the URL is signed with that instant inside the signed
    material, so publishing one without the other would describe a deadline
    that belongs to nothing.

    Attributes:
        url_descarga: Signed URL of the produced file, ``None`` unless the
            state is ``completado``.
        caduca_en: Instant the signed URL stops being accepted, ``None``
            unless the state is ``completado``.
    """

    url_descarga: str | None = None
    caduca_en: datetime | None = None
