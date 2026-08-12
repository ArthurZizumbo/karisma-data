"""Contracts of the dashboard series endpoint.

Everything the client is allowed to ask for lives in ``SeriesParams``. The
client never sends an expression: it sends a validated, closed vocabulary, and
the deterministic compiler of the service turns it into Polars. That is the
semantic layer rule of the project applied to the one endpoint that carries half
a million numbers, and it is what makes the query a cache key instead of a
program.

The bodies of the errors carry a stable code and never a sentence. The interface
is bilingual and owns the copy; a sentence written here would exist in one
language only.
"""

import json
from datetime import date
from enum import StrEnum
from typing import Annotated, Final, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# The grid US-006 froze: 5 business units x 5 currencies x 10 maturity buckets,
# with serie_id = unit * 50 + currency * 10 + bucket. Reused here as a bound and
# never recomputed.
SERIES_IN_GRID: Final[int] = 250
MAX_SERIE_ID: Final[int] = SERIES_IN_GRID - 1

# Points per line the reader can ask for. The floor is what still draws a
# recognisable trend; the ceiling is the full grid of US-006, which is the
# evidence load and the only value that means "do not reduce".
MIN_POINTS: Final[int] = 100
MAX_POINTS: Final[int] = 2000
DEFAULT_POINTS: Final[int] = 400

# Ceiling of the human readable variant. It exists so the contract can be read
# with curl; a JSON body of half a million numbers would be 14 MB and nobody
# would audit it either.
MAX_JSON_POINTS: Final[int] = 50_000


class MetricName(StrEnum):
    """Numeric column of the aggregate that a line can carry."""

    BALANCE = "saldo_disponible_mxn"
    LCR = "ratio_lcr"
    POSITIONS = "n_posiciones"


class Grouping(StrEnum):
    """Dimension the 250 keys of the grid are collapsed into.

    ``SERIES`` is the identity: every key of the grid stays its own line, which
    is the 250 line, 500 000 point load the performance evidence needs.
    """

    BUSINESS_UNIT = "unidad_negocio"
    CURRENCY = "divisa"
    MATURITY = "bucket_venc"
    SERIES = "serie"


class ResponseFormat(StrEnum):
    """How the points travel.

    ``BINARY`` is what the interface always uses. ``JSON`` exists for human
    inspection and is capped: a contract nobody can read with curl is a contract
    nobody audits.
    """

    BINARY = "binario"
    JSON = "json"


class ReductionMethod(StrEnum):
    """How 2 000 points per line become ``max_puntos``.

    A closed vocabulary of one today. It is published inside the frame so that
    the screen can name the reduction instead of hiding it, and so that adding a
    second method later is a value the client already knows how to read.
    """

    BLOCK_MEAN = "media_por_bloque"


class SeriesErrorCode(StrEnum):
    """Stable codes this endpoint returns in ``detail.codigo``."""

    PAYLOAD_EXCESIVO = "payload_excesivo"
    DATOS_NO_SEMBRADOS = "datos_no_sembrados"


class ErrorSerie(BaseModel):
    """Body of a typed failure. Code first, context after, prose never.

    Attributes:
        codigo: Stable identifier the interface keys its copy on.
        archivo: File the caller would have to seed, when that is the failure.
        puntos: Points the query would have produced, when it is too large.
        maximo: Ceiling that was exceeded.
    """

    codigo: SeriesErrorCode
    archivo: str | None = None
    puntos: int | None = None
    maximo: int | None = None

    def as_detail(self) -> dict[str, object]:
        """Render the body FastAPI puts under ``detail``.

        Returns:
            The populated fields only, so a caller never has to tell an absent
            value from a meaningful null.
        """
        return self.model_dump(exclude_none=True)


class SeriesParams(BaseModel):
    """Validated query of the dashboard series endpoint.

    Unknown parameters are rejected instead of ignored. A misspelled filter that
    is silently dropped gives the reader a chart that answers a question they did
    not ask, and nothing on the screen says so.

    Attributes:
        metrica: Numeric column the lines carry.
        agrupacion: Dimension the grid collapses into.
        serie_id: Keys of the grid to keep. Only with ``agrupacion=serie``.
        unidad_negocio: Business unit codes to keep.
        divisa: Currency codes to keep.
        bucket_venc: Maturity bucket codes to keep.
        desde: First date, clipped to the window the file holds.
        hasta: Last date, clipped the same way.
        max_puntos: Points per line after the server side reduction.
        formato: Transport of the points.
    """

    model_config = ConfigDict(extra="forbid")

    metrica: MetricName = MetricName.BALANCE
    agrupacion: Grouping = Grouping.BUSINESS_UNIT
    serie_id: tuple[Annotated[int, Field(ge=0, le=MAX_SERIE_ID)], ...] = ()
    unidad_negocio: tuple[str, ...] = ()
    divisa: tuple[str, ...] = ()
    bucket_venc: tuple[str, ...] = ()
    desde: date | None = None
    hasta: date | None = None
    max_puntos: int = Field(default=DEFAULT_POINTS, ge=MIN_POINTS, le=MAX_POINTS)
    formato: ResponseFormat = ResponseFormat.BINARY

    @model_validator(mode="after")
    def check_combination(self) -> Self:
        """Reject the two combinations that would answer a different question.

        Returns:
            The validated query.

        Raises:
            ValueError: When ``serie_id`` is sent without ``agrupacion=serie``,
                or when the window is empty.
        """
        if self.serie_id and self.agrupacion is not Grouping.SERIES:
            message = (
                "serie_id solo se admite con agrupacion=serie; con otra "
                "agrupacion las claves se funden y el filtro no significa nada"
            )
            raise ValueError(message)
        desde, hasta = self.desde, self.hasta
        if desde is not None and hasta is not None and desde > hasta:
            message = "desde no puede ser posterior a hasta"
            raise ValueError(message)
        return self

    def cache_key(self) -> str:
        """Return the canonical, order independent form of the query.

        Two requests that ask the same thing with the filters written in another
        order are the same request. Without this the ETag would change with the
        order of the query string, the browser cache would stop matching, and
        nothing would look broken: it would only be slow, which is the kind of
        defect that survives for months.

        Returns:
            A stable string, safe to hash and to use as a dictionary key.
        """
        canonical: dict[str, object] = {
            "metrica": self.metrica.value,
            "agrupacion": self.agrupacion.value,
            "serie_id": sorted(set(self.serie_id)),
            "unidad_negocio": sorted(set(self.unidad_negocio)),
            "divisa": sorted(set(self.divisa)),
            "bucket_venc": sorted(set(self.bucket_venc)),
            "desde": self.desde.isoformat() if self.desde is not None else None,
            "hasta": self.hasta.isoformat() if self.hasta is not None else None,
            "max_puntos": self.max_puntos,
            "formato": self.formato.value,
        }
        return json.dumps(canonical, sort_keys=True, separators=(",", ":"))


class SerieEtiqueta(BaseModel):
    """One line of the answer, named in both languages.

    The labels travel with the data so the legend does not need a second
    request. That is why US-006 wrote the sidecar in the first place.

    Attributes:
        clave: Code of the line, as the grouping dimension spells it.
        serie_id: Key of the grid, or ``None`` when the line is an aggregate.
        label_es: Human label in Spanish.
        label_en: Human label in English.
    """

    clave: str
    serie_id: int | None
    label_es: str
    label_en: str


class Conteo(BaseModel):
    """Cardinalities of the answer, so the client never counts them itself.

    Attributes:
        puntos: ``series * fechas``, the figure the degradation notice shows.
        fechas: Dates shared by every line.
        series: Number of lines.
    """

    puntos: int
    fechas: int
    series: int


class Reduccion(BaseModel):
    """What the server did to fit the line into ``max_puntos``.

    Attributes:
        metodo: Name of the reduction.
        bloque: Business days averaged into one point; one means untouched.
        puntos_originales: Dates before the reduction.
    """

    metodo: ReductionMethod
    bloque: int
    puntos_originales: int


class OrigenSerie(BaseModel):
    """Provenance of every number on screen. US-029 renders this verbatim.

    ``filas_crudas`` and ``semilla`` come from the manifest of the silos. When
    the manifest is missing they are null and the interface shows nothing: an
    invented provenance is worse than no provenance.

    Attributes:
        silo: Source silo of the aggregate.
        archivo: Path of the file the numbers were read from.
        filas_agregadas: Rows of the aggregate.
        filas_crudas: Rows of the silo behind it, when the manifest says so.
        generado_por: Command that produced the aggregate.
        semilla: Seed of the synthetic generator, when the manifest says so.
        transformaciones: Ordered list of what was applied, in Spanish, because
            it is shown to the reader.
        nota_tipo_cambio_es: Exchange rate caveat, Spanish.
        nota_tipo_cambio_en: Exchange rate caveat, English.
    """

    silo: str
    archivo: str
    filas_agregadas: int
    filas_crudas: int | None
    generado_por: str
    semilla: int | None
    transformaciones: tuple[str, ...]
    nota_tipo_cambio_es: str
    nota_tipo_cambio_en: str


class SeriesJson(BaseModel):
    """Human readable variant. Capped at ``MAX_JSON_POINTS``.

    The values are ``float64`` here and ``float32`` in the frame: this is the
    exact variant, and it is what the table and the tooltip of the screen read.

    Attributes:
        metrica: Metric of every line.
        agrupacion: Dimension the lines were grouped by.
        fechas: Dates shared by every line, ascending.
        series: One entry per line, in the same order as ``valores``.
        valores: One row per line; ``None`` is a gap and never a zero.
        conteo: Cardinalities of the answer.
        reduccion: What the server did to the time axis.
        origen: Provenance of the numbers.
    """

    metrica: MetricName
    agrupacion: Grouping
    fechas: tuple[date, ...]
    series: tuple[SerieEtiqueta, ...]
    valores: tuple[tuple[float | None, ...], ...]
    conteo: Conteo
    reduccion: Reduccion
    origen: OrigenSerie
