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
from typing import Final, Literal

from pydantic import BaseModel, Field, field_validator

#: Bounds of the question. The lower one rejects an empty turn before any work
#: is scheduled; the upper one keeps a pasted document out of the prompt.
MENSAJE_MINIMO: Final[int] = 1
MENSAJE_MAXIMO: Final[int] = 2000


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
        columnas: Header of the mini-table, one entry per column.
        filas: Rows of the mini-table, aligned with ``columnas``.
        cifra: Scalar the card highlights, already formatted for reading, when
            the tool answers with one number instead of with a table.
    """

    columnas: list[str]
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
    etiqueta: str
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
        codigo: Stable code of the failure, never a sentence.
        mensaje_clave: i18n key of the copy the interface shows.
        recuperable: Whether retrying the same turn can succeed.
    """

    paso: PasoDelStream
    clase: Literal["recuperable", "permiso"]
    codigo: str
    mensaje_clave: str
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

    Attributes:
        mensaje: Question typed by the reader.
        conversacion: Key of the scripted conversation to replay, when the
            client picks one. ``None`` leaves the choice to the provider.
    """

    mensaje: str = Field(min_length=MENSAJE_MINIMO, max_length=MENSAJE_MAXIMO)
    conversacion: str | None = None

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
