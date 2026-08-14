"""SSE transport of the chat: framing, live registry and real cancellation.

This module is the only place that knows what a frame of the stream looks like
on the wire, and it knows nothing about who produces the events: it receives a
provider through the ``ProveedorDeTokens`` protocol and closes it when it is
done. That separation is the seam the go/no-go of the Gemini provider depends
on, so importing a concrete provider here would cost the seam.

Four invariants are worth stating because the tests measure exactly them:

1. ``done`` is emitted once and last, **including when the client already hung
   up**. The byte is lost, the single exit of the generator is not.
2. ``_STREAMS_ACTIVOS`` is empty once a stream ends, whichever way it ended.
   The registry is the honest measure of "nothing is hanging": it fails when
   somebody removes the ``finally`` or replaces it with an ``except`` that does
   not cover cancellation.
3. The cleanup runs to the end **under a cancellation already in flight**, and
   that needs a shield: see the comment on the ``finally`` of ``transmitir``.
4. That same registry is also the ceiling. ``reservar`` takes a slot before the
   response exists, so the number of streams a process serves at once is
   declared and not merely observed; the router turns a refusal into a 429.

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

import anyio
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
from app.utils.reloj import transcurrido_ms

logger = structlog.get_logger()

_STREAMS_ACTIVOS: Final[dict[str, float]] = {}
"""Live streams by id, with their monotonic start. Empty means nothing is hanging."""

MAXIMO_DE_STREAMS: Final[int] = 32
"""How many chat streams this process serves at once.

There is no leak -the ``finally`` of ``transmitir`` always clears the entry-
but there was no ceiling either, and the two are different properties. With
``DEMO_LOGIN_ENABLED`` on, a token costs no credentials, so anybody could open
streams and read them slowly until the memory and the descriptors of a Cloud
Run instance ran out; scale-to-zero makes that cheap to do and expensive to
absorb. 32 is chosen against the demo and not against a load target: the
capture of A4 opens one stream, a reviewer poking with two browsers opens a
handful, and the number has to be small enough that exhausting it is not the
easy path.
"""

VIDA_MAXIMA_DE_RESERVA_S: Final[float] = 300.0
"""Age past which a slot is assumed abandoned and reclaimed.

The one hole of reserving before the body is iterated: a client that hangs up
between the request and the first byte leaves a response whose generator never
starts, so its ``finally`` never runs and its slot is never returned. Without
this sweep, that hole turns a defence against exhausting the memory into a way
of exhausting the counter, which is a worse trade. A stream older than this has
either finished or is beyond anything the scripted provider -or a model with a
sane timeout- can justify.
"""


#: Names of the two mutually exclusive closing records. They are literals of
#: the contract: the capture of the cancellation greps for the first one, and a
#: stream that wrote both -or the wrong one- would prove the opposite of what
#: the evidence claims.
EVENTO_CANCELADO: Final[str] = "chat.stream.cancelado"
EVENTO_COMPLETADO: Final[str] = "chat.stream.completado"
EVENTO_FALLO: Final[str] = "chat.stream.fallo"

#: Records of the ceiling. Neither is a closing record: they say something
#: about the process and nothing about a turn, which is why they are warnings
#: and carry no ``stream_id``.
EVENTO_LIMITE: Final[str] = "chat.stream.limite"
EVENTO_RECLAMADOS: Final[str] = "chat.stream.reclamados"

#: Failure the transport itself publishes when the provider breaks. The step is
#: ``transporte`` because nothing downstream failed: the answer never got to be
#: produced, and the interface has to be able to tell that apart from a silo
#: that did not answer.
CODIGO_TRANSPORTE: Final[str] = "fallo_de_transporte"
CLAVE_MENSAJE_TRANSPORTE: Final[str] = "chat.error.message.recoverable"


class LimiteDeStreamsError(Exception):
    """Raised when every declared stream slot is already taken.

    It is declared next to the registry and not in the router because the
    ceiling is a property of this transport: the router only translates it to
    the status code the HTTP contract of the endpoint publishes.
    """


def streams_activos() -> Mapping[str, float]:
    """Return a read-only view of the live stream registry.

    Returns:
        The identifier of every open stream with the monotonic instant it
        started, as a snapshot no caller can mutate.
    """
    return MappingProxyType(dict(_STREAMS_ACTIVOS))


def reservar() -> str:
    """Take one of the declared stream slots, or refuse the turn.

    The check and the registration happen in the same synchronous block, and
    that is the whole point: asking "is there room" from the router and
    registering later, when the response starts being iterated, leaves an
    ``await`` in between through which every concurrent request passes the
    check before any of them takes a slot. A ceiling with that window is
    advice, not a limit.

    Returns:
        The identifier of the reserved stream, to be handed to ``transmitir``
        so that the registry entry, the closing record and the ``done`` event
        all name the same stream.

    Raises:
        LimiteDeStreamsError: If the process already serves ``MAXIMO_DE_STREAMS``
            streams, none of them old enough to be assumed abandoned.
    """
    if len(_STREAMS_ACTIVOS) >= MAXIMO_DE_STREAMS:
        _reclamar_abandonados()
    if len(_STREAMS_ACTIVOS) >= MAXIMO_DE_STREAMS:
        logger.warning(
            EVENTO_LIMITE,
            streams_activos=len(_STREAMS_ACTIVOS),
            maximo=MAXIMO_DE_STREAMS,
        )
        message = f"limite de streams simultaneos alcanzado: {MAXIMO_DE_STREAMS}"
        raise LimiteDeStreamsError(message)

    identificador = uuid.uuid4().hex
    _STREAMS_ACTIVOS[identificador] = time.monotonic()
    return identificador


def liberar(identificador: str) -> None:
    """Give a stream slot back, whether or not it was ever used.

    It is public and not a line inside the ``finally`` of ``transmitir``
    because it is the other half of ``reservar``: whoever receives a reserved
    identifier owes this call, and a double built to stand in for the transport
    owes it too. Idempotent on purpose -the same turn can be released by the
    generator that ended and by a sweep that assumed it abandoned.

    Args:
        identificador: Identifier handed out by ``reservar``, or the one
            ``transmitir`` generated for itself.
    """
    _STREAMS_ACTIVOS.pop(identificador, None)


def _reclamar_abandonados() -> None:
    """Drop the slots of streams too old to still be running.

    Called only when the registry is full, so a portal under its ceiling never
    pays for the walk.
    """
    limite = time.monotonic() - VIDA_MAXIMA_DE_RESERVA_S
    caducados = [
        identificador
        for identificador, inicio in _STREAMS_ACTIVOS.items()
        if inicio < limite
    ]
    for identificador in caducados:
        liberar(identificador)
    if caducados:
        logger.warning(EVENTO_RECLAMADOS, reclamados=len(caducados))


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
        stream_id: Identifier to correlate the frames with the log record,
            normally the one ``reservar`` already registered. One is generated
            when the caller does not supply it, and registering the same key
            twice is what makes the two entry points agree on one slot instead
            of counting the turn twice.

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
                        primer_token_ms = transcurrido_ms(inicio)
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

        duracion_ms = transcurrido_ms(inicio)
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
        # The cleanup is shielded because the real cancellation does not arrive
        # once: Starlette runs this body inside an anyio task group and cancels
        # its whole scope when the socket dies, and anyio re-delivers that
        # cancellation at *every* await point while the scope stays cancelled.
        # Unshielded, this block dies at its first await -measured with uvicorn
        # and twenty cuts of the socket-: the provider never runs its own
        # ``finally`` and the cancelled turn never writes its closing record,
        # which is the evidence this User Story exists to produce. Everything
        # here is bounded work over local state, so shielding it cannot delay
        # the shutdown of the response.
        with anyio.CancelScope(shield=True):
            liberar(identificador)
            await _cerrar(eventos)
            if not registrado:
                # The consumer walked away from the generator itself, so the
                # loop above never reached its closing record. The stream still
                # ended, and it ended cancelled.
                _registrar_cierre(
                    MotivoCierre.CANCELADO,
                    stream_id=identificador,
                    tokens_emitidos=tokens_emitidos,
                    duracion_ms=transcurrido_ms(inicio),
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

    What the record carries, stated in full because a privacy review is only as
    good as the claim it checks. The five keyword arguments below describe the
    shape of the stream -identifier, outcome, counts, durations- and to them
    ``structlog`` adds, through ``merge_contextvars``, the context
    ``app.core.auth`` bound when the session was resolved: the login identifier
    and the role of the caller. That attribution is deliberate and it is what
    makes an abandoned stream attributable at all.

    What never reaches it, in any of the two paths: the question, the answer,
    any fragment of either, the access token, and any password. The raw prompt
    does not leave the process, and its hash is not written here either -that
    is ``llm.prompt_hash`` and it belongs to the span of the model call, which
    this transport does not open.

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

    What this cannot do, and whoever writes the next provider needs to know:
    when the cancellation is delivered inside the provider's own ``await``, its
    cleanup dies there, before this function gets to ask for anything. The
    shield of the caller covers the closing driven from here; a provider whose
    cleanup suspends has to shield its own ``finally`` as well.

    Args:
        eventos: Iterator returned by the provider.
    """
    cerrar = getattr(eventos, "aclose", None)
    if cerrar is None:
        return
    await cerrar()
