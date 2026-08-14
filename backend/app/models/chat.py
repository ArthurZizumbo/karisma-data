"""Typed events of the chat stream, frozen as SSE contract v1.

Four names travel on the wire -``tool_call``, ``token``, ``error`` and
``done``- and this module is the only place where their fields are declared.
US-024 (error notice) and US-028 (tool call card) are written against these
names, so a field added here without going through the contract silently
changes two other User Stories.

Nothing here knows how an event is produced or transported: the provider fills
it in and ``app.services.chat_stream`` frames it. The closed vocabularies are
enumerations and not free strings on purpose: the interface switches on them,
and a fifth value nobody declared would reach the browser as an unhandled case.
"""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Annotated, Final, Literal

from pydantic import BaseModel, Field, field_validator

#: Bounds of the question. The lower one rejects an empty turn before any work
#: is scheduled; the upper one keeps a pasted document out of the prompt.
MENSAJE_MINIMO: Final[int] = 1
MENSAJE_MAXIMO: Final[int] = 2000

#: Bound of the conversation key. It is not cosmetic: FastAPI reads the whole
#: body **before** it resolves the security dependency, so an anonymous
#: ``POST /api/chat`` carrying a 200 MB string here materializes those 200 MB
#: in the heap of the process and only then answers 401. Capping ``mensaje``
#: alone left the pasted document a second door, wider than the first.
#:
#: 64 characters and not a ``Literal`` of the four declared keys: the resolver
#: treats an undeclared key as no key at all -a typo in a query string must not
#: break the turn- and that tolerant branch is pinned by its own test. A
#: ``Literal`` would answer 422 there instead, which is a different contract.
CONVERSACION_MAXIMA: Final[int] = 64

#: Shape of the FULL i18n key of a readable tool name.
#:
#: The three patterns below exist for one reason, and it is not tidiness: the
#: day a model answers behind the seam, any of these three fields can carry a
#: value the model influenced, and all three are printed by the browser. A key
#: that exists resolves to another piece of the bundle; one that does not is
#: printed verbatim by ``vue-i18n``, which is exactly the channel through which
#: an internal detail -the one the ``error`` event promises not to carry- would
#: reach the reader. A closed shape is what keeps the promise checkable.
PATRON_ETIQUETA: Final[str] = r"^chat\.toolCall\.tool\.[a-z_]+$"

#: Shape of the i18n key of the copy shown for a failure.
#:
#: Two namespaces and no more, because those are the two that exist: the
#: backend emits ``chat.error.message.*`` -both scripted failures and the
#: transport failure of ``chat_stream``- and the client mints
#: ``chat.stream.transportError`` on its own when the request never reached the
#: server. The second one is accepted here so that this model stays an honest
#: description of every event of this shape the interface handles, and not only
#: of the ones Python builds.
PATRON_CLAVE_DE_MENSAJE: Final[str] = r"^chat\.(error\.message|stream)\.[a-zA-Z]+$"

#: Shape of a stable failure code: lower case, digits and underscores.
#: Anything else is prose, and prose in this field is untranslatable.
PATRON_CODIGO: Final[str] = r"^[a-z0-9_]+$"

#: Shape of the i18n key of one mini-table column header.
#:
#: The header of a column is chrome, not data: it names what the column holds,
#: the same way ``etiqueta`` names the tool. It used to travel as Spanish prose
#: -"Metrica", "Cierre"- and the browser printed it verbatim, so /guia with the
#: interface in English rendered a card that was English everywhere except its
#: two table headers. Measured on 14-ago-2026 against the running container.
#:
#: Making it a key rather than prose is not a new rule: ``etiqueta`` and
#: ``mensaje_clave`` of this same contract are already i18n keys, and prose in
#: ``columnas`` was the anomaly. What stays data is the CONTENT of the rows,
#: which comes from the silo and is not the interface talking.
PATRON_COLUMNA: Final[str] = r"^chat\.toolCall\.column\.[a-zA-Z]+$"


class EstadoTarjeta(StrEnum):
    """Life stage of a tool call card, per SSE contract v1."""

    ANUNCIO = "anuncio"
    EJECUCION = "ejecucion"
    RESULTADO = "resultado"
    ERROR = "error"


class MotivoCierre(StrEnum):
    """Why the stream ended."""

    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    ERROR = "error"


class PasoDelStream(StrEnum):
    """Closed vocabulary of the stream step that can fail (SSE contract v1)."""

    RECUPERACION_DE_DATOS = "recuperacion_de_datos"
    VERIFICACION_DE_PERMISO = "verificacion_de_permiso"
    GENERACION_DE_TEXTO = "generacion_de_texto"
    TRANSPORTE = "transporte"


class ResultadoTarjeta(BaseModel):
    """Mini-table or single figure returned by a tool call.

    Attributes:
        columnas: Header of the mini-table, one i18n key per column. Keys and
            not prose: a header names what the column holds and is therefore
            interface, so it is translated like every other visible string.
            See ``PATRON_COLUMNA``.
        filas: Rows of the mini-table, aligned with ``columnas``. These stay
            data and are NOT translated: they come from the silo, and the day a
            real provider answers, translating them would be inventing.
        cifra: Scalar the card highlights, already formatted for reading, when
            the tool answers with one number instead of with a table.
    """

    columnas: list[Annotated[str, Field(pattern=PATRON_COLUMNA)]]
    filas: list[list[str | float]]
    cifra: str | None = None


class EventoToolCall(BaseModel):
    """SSE event ``tool_call``: one card, four possible states, stable id.

    ``herramienta`` is the technical name (``consultar_metrica``);
    ``etiqueta`` is the FULL i18n key of the readable name, always shaped
    ``chat.toolCall.tool.<herramienta>``, never a sentence: the interface is
    bilingual and resolves the copy, so a sentence here would reach both
    locales untranslated.

    Attributes:
        id: Identifier of the card, stable across its states. The client
            updates by id instead of appending, which is what lets two cards
            live at once without a re-render.
        estado: Life stage of the card.
        herramienta: Technical name of the tool behind the card.
        etiqueta: i18n key of the readable name of the tool.
        transcurrido_ms: Milliseconds since the card was announced. ``None`` in
            the announcement, where nothing has elapsed yet.
        resultado: Payload of the tool, only in the resolving event.
        fuente: Catalogue field the figure comes from. It is what makes a
            number citable, so a card that resolves without it cannot be
            quoted by the answer.
        paso: Step of the stream that failed, only when the card ends in error.
    """

    id: str
    estado: EstadoTarjeta
    herramienta: str
    etiqueta: str = Field(pattern=PATRON_ETIQUETA)
    transcurrido_ms: int | None = None
    resultado: ResultadoTarjeta | None = None
    fuente: str | None = None
    paso: PasoDelStream | None = None


class EventoToken(BaseModel):
    """SSE event ``token``: one incremental text fragment with its index.

    Attributes:
        texto: Fragment of the answer, ready to be appended as it arrives.
        indice: Monotonic position of the fragment in the answer, so a client
            that drops one can tell.
    """

    texto: str
    indice: int


class EventoError(BaseModel):
    """SSE event ``error``: typed failure; the message is an i18n key.

    Exactly FIVE frozen fields, and ``paso`` is a closed vocabulary instead of
    free text. The contract deliberately does not carry the level a permission
    failure demanded: the client derives it, and the backend never publishes
    what a caller would have needed to see the data.

    Attributes:
        paso: Step of the stream that failed.
        clase: Family of the failure. ``recuperable`` invites retrying the same
            turn; ``permiso`` never does.
        codigo: Stable code of the failure, never a sentence. The pattern is
            what makes "never a sentence" enforceable instead of aspirational.
        mensaje_clave: i18n key of the copy the interface shows, constrained to
            the two namespaces that really exist on this wire.
        recuperable: Whether retrying the same turn can succeed.
    """

    paso: PasoDelStream
    clase: Literal["recuperable", "permiso"]
    codigo: str = Field(pattern=PATRON_CODIGO)
    mensaje_clave: str = Field(pattern=PATRON_CLAVE_DE_MENSAJE)
    recuperable: bool


class EventoDone(BaseModel):
    """SSE event ``done``: closes the stream exactly once.

    Attributes:
        motivo: Why the stream ended.
        tokens_emitidos: Fragments that actually left the server. Compared with
            the length of the answer it is what tells a real cancellation from
            a cosmetic one.
        duracion_ms: Milliseconds the stream was open.
    """

    motivo: MotivoCierre
    tokens_emitidos: int
    duracion_ms: int


class PeticionChat(BaseModel):
    """Client request body for ``POST /api/chat``.

    Both fields are bounded, and the second bound is the one that carries the
    promise: the body is read into memory **before** the security dependency
    runs, so an anonymous request is enough to make the process allocate
    whatever this model allows. A cap on ``mensaje`` alone kept a pasted
    document out of the prompt and let it into the heap through the other
    field.

    Attributes:
        mensaje: Question typed by the reader.
        conversacion: Key of the scripted conversation to replay, when the
            client picks one. ``None`` leaves the choice to the provider, and
            so does any key the provider does not declare.
    """

    mensaje: str = Field(min_length=MENSAJE_MINIMO, max_length=MENSAJE_MAXIMO)
    conversacion: str | None = Field(default=None, max_length=CONVERSACION_MAXIMA)

    @field_validator("mensaje")
    @classmethod
    def sin_espacios_vacios(cls, valor: str) -> str:
        """Reject a message that is only whitespace.

        ``min_length`` counts characters, so a turn made of three spaces gets
        past it and opens a stream that answers nothing.

        Args:
            valor: Raw message as the client sent it.

        Returns:
            The message without its surrounding whitespace.

        Raises:
            ValueError: If the message carries no visible character.
        """
        limpio = valor.strip()
        if not limpio:
            message = "el mensaje no puede ser solo espacios en blanco"
            raise ValueError(message)
        return limpio


class ChatErrorCode(StrEnum):
    """Stable codes ``POST /api/chat`` returns in ``detail.codigo``.

    Deliberately not a member of ``core.scopes.ErrorCode``: that enumeration is
    the vocabulary of authentication and authorization -who you are and what
    you may see- and a refusal for lack of capacity is neither. The endpoint
    follows the shape the rest of the API already uses for its own failures
    (``SeriesErrorCode``, ``LineageErrorCode``): a code per feature, never a
    sentence, so the bilingual interface keys its copy on the code.
    """

    LIMITE_DE_STREAMS = "limite_de_streams"


class ErrorChat(BaseModel):
    """Body of a typed failure of the endpoint. Code first, context after.

    Attributes:
        codigo: Stable identifier the interface keys its copy on.
        maximo: Streams the portal serves at once, published so a client can
            tell a refusal it caused from one somebody else caused.
    """

    codigo: ChatErrorCode
    maximo: int | None = None

    def as_detail(self) -> dict[str, object]:
        """Render the body FastAPI puts under ``detail``.

        Returns:
            The populated fields only, so a caller never has to tell an absent
            value from a meaningful null.
        """
        return self.model_dump(exclude_none=True)


EventoChat = EventoToolCall | EventoToken | EventoError | EventoDone
"""Any event the stream can carry. The union is closed: there is no fifth."""

NOMBRE_DE_EVENTO: Final[Mapping[type[BaseModel], str]] = MappingProxyType(
    {
        EventoToolCall: "tool_call",
        EventoToken: "token",
        EventoError: "error",
        EventoDone: "done",
    }
)
"""Wire name of each event type, as it is written in the ``event:`` line."""
