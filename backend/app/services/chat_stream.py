"""SSE transport of the chat: framing, live registry and real cancellation.

This module is the only place that knows what a frame of the stream looks like
on the wire, and it knows nothing about who produces the events: it receives a
provider through the ``ProveedorDeTokens`` protocol and closes it when it is
done. That separation is the seam the go/no-go of the Gemini provider depends
on, so importing a concrete provider here would cost the seam.

Two invariants are worth stating because the tests measure exactly them:

1. ``done`` is emitted once and last, **including when the client already hung
   up**. The byte is lost, the single exit of the generator is not.
2. ``_STREAMS_ACTIVOS`` is empty once a stream ends, whichever way it ended.
   The registry is the honest measure of "nothing is hanging": it fails when
   somebody removes the ``finally`` or replaces it with an ``except`` that does
   not cover cancellation.

Time to first token is computed and written to the closing log record only. It
is never published in ``done`` nor sent to the interface: with a scripted
provider it measures our own ``sleep``, and a figure that honest belongs in a
log and not in a metric anybody could read as latency of a model.
"""

import time
import uuid
from collections.abc import AsyncGenerator, AsyncIterator, Awaitable, Callable, Mapping
from types import MappingProxyType
from typing import Final

import structlog

from app.models.chat import (
    NOMBRE_DE_EVENTO,
    EventoChat,
    EventoDone,
    EventoError,
    EventoToken,
    MotivoCierre,
    PasoDelStream,
    PeticionChat,
)
from app.services.proveedores import ProveedorDeTokens

logger = structlog.get_logger()

_STREAMS_ACTIVOS: Final[dict[str, float]] = {}
"""Live streams by id, with their monotonic start. Empty means nothing is hanging."""

#: Names of the two mutually exclusive closing records. They are literals of
#: the contract: the capture of the cancellation greps for the first one, and a
#: stream that wrote both -or the wrong one- would prove the opposite of what
#: the evidence claims.
EVENTO_CANCELADO: Final[str] = "chat.stream.cancelado"
EVENTO_COMPLETADO: Final[str] = "chat.stream.completado"
EVENTO_FALLO: Final[str] = "chat.stream.fallo"

#: Failure the transport itself publishes when the provider breaks. The step is
#: ``transporte`` because nothing downstream failed: the answer never got to be
#: produced, and the interface has to be able to tell that apart from a silo
#: that did not answer.
CODIGO_TRANSPORTE: Final[str] = "fallo_de_transporte"
CLAVE_MENSAJE_TRANSPORTE: Final[str] = "chat.error.message.recoverable"


def streams_activos() -> Mapping[str, float]:
    """Return a read-only view of the live stream registry.

    Returns:
        The identifier of every open stream with the monotonic instant it
        started, as a snapshot no caller can mutate.
    """
    return MappingProxyType(dict(_STREAMS_ACTIVOS))


def formatear_evento(evento: EventoChat) -> str:
    r"""Render one typed event as an SSE frame.

    Args:
        evento: Event to send, already validated by its model.

    Returns:
        The frame ``event: <name>\\ndata: <json>\\n\\n``, which is the framing
        the client parser is written against.
    """
    nombre = NOMBRE_DE_EVENTO[type(evento)]
    return f"event: {nombre}\ndata: {evento.model_dump_json()}\n\n"


async def transmitir(
    peticion: PeticionChat,
    proveedor: ProveedorDeTokens,
    esta_desconectado: Callable[[], Awaitable[bool]],
    stream_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream contract-legal SSE frames, cancelling the provider when the client leaves.

    The disconnection detector arrives as a callable and not as a ``Request``
    on purpose: ``request.is_disconnected()`` never fires under the ASGI test
    client, so a signature that took the request would make every cancellation
    test a decoration. The router passes ``request.is_disconnected``.

    Args:
        peticion: Question of the reader, already validated.
        proveedor: Source of the events, closed by this function.
        esta_desconectado: Awaited once per event; ``True`` stops production.
        stream_id: Identifier to correlate the frames with the log record. One
            is generated when the caller does not supply it.

    Returns:
        An asynchronous generator, and the narrower type is the point: what the
        server does when the reader leaves is call ``aclose()`` on this object,
        so declaring the wider ``AsyncIterator`` would hide the one method this
        whole User Story is about. Every caller typed against ``AsyncIterator``
        keeps working, because a generator is one.

    Yields:
        One SSE frame per event, and a final ``done`` frame that closes the
        stream exactly once.
    """
    identificador = stream_id if stream_id is not None else uuid.uuid4().hex
    inicio = time.monotonic()
    eventos = proveedor.generar(peticion)
    tokens_emitidos = 0
    primer_token_ms: int | None = None
    motivo = MotivoCierre.COMPLETADO
    registrado = False

    _STREAMS_ACTIVOS[identificador] = inicio
    try:
        try:
            async for evento in eventos:
                if await esta_desconectado():
                    motivo = MotivoCierre.CANCELADO
                    break
                if isinstance(evento, EventoError):
                    motivo = MotivoCierre.ERROR
                yield formatear_evento(evento)
                if isinstance(evento, EventoToken):
                    tokens_emitidos += 1
                    if primer_token_ms is None:
                        primer_token_ms = _transcurrido_ms(inicio)
        except Exception as error:
            # The provider broke where nobody scripted it. The turn still gets
            # a typed error and its `done`: a stream that dies without closing
            # leaves the interface spinning forever.
            motivo = MotivoCierre.ERROR
            logger.warning(
                EVENTO_FALLO,
                stream_id=identificador,
                excepcion=type(error).__name__,
            )
            yield formatear_evento(_error_de_transporte())

        duracion_ms = _transcurrido_ms(inicio)
        # Written before the last frame and not after it: when the socket is
        # already gone, yielding may never return, and the record of the
        # cancellation is the evidence of this User Story.
        _registrar_cierre(
            motivo,
            stream_id=identificador,
            tokens_emitidos=tokens_emitidos,
            duracion_ms=duracion_ms,
            primer_token_ms=primer_token_ms,
        )
        registrado = True
        yield formatear_evento(
            EventoDone(
                motivo=motivo,
                tokens_emitidos=tokens_emitidos,
                duracion_ms=duracion_ms,
            )
        )
    finally:
        _STREAMS_ACTIVOS.pop(identificador, None)
        await _cerrar(eventos)
        if not registrado:
            # The consumer walked away from the generator itself, so the loop
            # above never reached its closing record. The stream still ended,
            # and it ended cancelled.
            _registrar_cierre(
                MotivoCierre.CANCELADO,
                stream_id=identificador,
                tokens_emitidos=tokens_emitidos,
                duracion_ms=_transcurrido_ms(inicio),
                primer_token_ms=primer_token_ms,
            )


def _error_de_transporte() -> EventoError:
    """Build the typed error the transport publishes when the provider breaks.

    Returns:
        A recoverable failure of the ``transporte`` step, with a stable code
        and an i18n key instead of a sentence.
    """
    return EventoError(
        paso=PasoDelStream.TRANSPORTE,
        clase="recuperable",
        codigo=CODIGO_TRANSPORTE,
        mensaje_clave=CLAVE_MENSAJE_TRANSPORTE,
        recuperable=True,
    )


def _registrar_cierre(
    motivo: MotivoCierre,
    *,
    stream_id: str,
    tokens_emitidos: int,
    duracion_ms: int,
    primer_token_ms: int | None,
) -> None:
    """Write the single closing record of a stream.

    Neither the question nor the answer reaches the record: what is measured is
    the shape of the stream, and the raw prompt never leaves the process.

    Args:
        motivo: Why the stream ended.
        stream_id: Identifier that correlates the record with the ``done``.
        tokens_emitidos: Fragments that actually left the server.
        duracion_ms: Milliseconds the stream stayed open.
        primer_token_ms: Time to first token, ``None`` when no fragment was
            emitted. It lives here and nowhere else.
    """
    nombre = EVENTO_CANCELADO if motivo is MotivoCierre.CANCELADO else EVENTO_COMPLETADO
    logger.info(
        nombre,
        stream_id=stream_id,
        motivo=motivo.value,
        tokens_emitidos=tokens_emitidos,
        duracion_ms=duracion_ms,
        primer_token_ms=primer_token_ms,
    )


async def _cerrar(eventos: AsyncIterator[EventoChat]) -> None:
    """Close the provider iterator, so its own cleanup runs.

    The protocol promises an asynchronous iterator and not a generator, so the
    closing method is asked for instead of assumed. Skipping this call is what
    leaves an outgoing connection open the day the provider talks to a model.

    Args:
        eventos: Iterator returned by the provider.
    """
    cerrar = getattr(eventos, "aclose", None)
    if cerrar is None:
        return
    await cerrar()


def _transcurrido_ms(inicio: float) -> int:
    """Return the milliseconds elapsed since a monotonic instant.

    Args:
        inicio: Reading of ``time.monotonic`` taken when the stream started.

    Returns:
        The elapsed time, rounded down to the millisecond.
    """
    return int((time.monotonic() - inicio) * 1000)
