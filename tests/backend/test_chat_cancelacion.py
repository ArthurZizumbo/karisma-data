"""Real cancellation of the chat stream, measured without a socket.

The disconnection detector reaches ``chat_stream.transmitir`` as a callable and
not as a ``Request``, and this module is the reason. ``request.is_disconnected``
never fires under the ASGI test client: written against the request, every
assertion below would be a decoration that passes whatever the transport does.
With the seam, each case injects exactly the moment the reader walks away.

Two things are being defended, and they are not the same thing. That the server
stops producing -with a model behind it, a stream nobody is reading is money
being spent- and that nothing survives the stream: no entry in the registry, no
task, no open generator inside the provider. The second one is what the manual
capture of section 1.1 cannot show, and it is where the defects hide.

The frames are parsed with ``json`` and ``str.split`` instead of with the
function that wrote them: checking an output with the module that produced it
only proves the module agrees with itself.
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator, Iterator
from typing import Any, Final

import anyio
import pytest
import structlog
from structlog.testing import capture_logs

from app.models.chat import (
    EstadoTarjeta,
    EventoChat,
    EventoToken,
    EventoToolCall,
    MotivoCierre,
    PeticionChat,
)
from app.services import chat_stream
from app.services.proveedores import ProveedorDeTokens
from app.services.proveedores.guionizado import (
    CONVERSACIONES,
    ProveedorGuionizado,
    fragmentos_de,
)

#: Conversation every case replays. C1 is the minimum path -one card, one
#: figure, one source- and the one the evidence of section 1.1 is taken over,
#: so cancelling the same script here keeps the test and the capture talking
#: about the same stream.
CLAVE: Final[str] = "morosidad"

#: Fragments the script of C1 emits when nobody interrupts it. Derived from the
#: script and never retyped: a hardcoded number would keep passing after
#: somebody rewrote the sentence, and the whole point of the assertions below
#: is the comparison against the total.
TOTAL_DE_TOKENS: Final[int] = sum(
    len(fragmentos_de(paso.texto))
    for paso in CONVERSACIONES[CLAVE]
    if paso.herramienta is None
)

#: Seconds a parked turn would wait if nothing cancelled it. It is never spent:
#: the cancellation is fired the instant the turn parks. It is a number and not
#: an event that never fires so that a broken cancellation fails the case in
#: seconds instead of hanging the suite.
ESPERA_QUE_LA_CANCELACION_INTERRUMPE: Final[float] = 5.0


class DetectorTrasNLlamadas:
    """Disconnection detector that reports the client gone on the Nth ask.

    Attributes:
        llamadas: How many times the transport asked. It is read by the tests
            that need to prove the question is asked at all.
    """

    def __init__(self, corte: int) -> None:
        """Store the call on which the client is reported gone.

        Args:
            corte: Ordinal of the call that starts answering ``True``.
        """
        self._corte = corte
        self.llamadas = 0

    async def __call__(self) -> bool:
        """Answer whether the client has hung up.

        Returns:
            ``True`` from the configured call onwards.
        """
        self.llamadas += 1
        return self.llamadas >= self._corte


class ProveedorEspia:
    """Provider that records whether the transport closed its iterator.

    A provider that is not closed keeps its own ``finally`` unrun. Today that
    leaks nothing; the day the provider talks to a model it leaks the outgoing
    connection of every cancelled turn, which is exactly the failure nobody
    notices until the bill arrives.

    Attributes:
        cerrado: Whether the iterator ran its cleanup.
    """

    def __init__(self, eventos: tuple[EventoChat, ...]) -> None:
        """Store the events this provider replays.

        Args:
            eventos: Events to yield, in order.
        """
        self._eventos = eventos
        self.cerrado = False

    def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
        """Return the iterator of this answer.

        Args:
            peticion: Question of the reader, ignored by the spy.

        Returns:
            The asynchronous iterator the transport consumes and closes.
        """
        return self._reproducir()

    async def _reproducir(self) -> AsyncIterator[EventoChat]:
        """Yield the stored events, marking the cleanup when it runs.

        Yields:
            Each stored event, in order.
        """
        try:
            for evento in self._eventos:
                yield evento
        finally:
            self.cerrado = True


class ProveedorQueLimpiaEsperando:
    """Provider whose cleanup suspends, the way closing a connection does.

    ``ProveedorEspia`` marks its flag with a plain assignment, and an
    assignment survives any cancellation because it never suspends. A provider
    that talks to a model closes a socket, and that awaits: this double is
    therefore the only one in the module able to tell a cleanup that was
    allowed to finish from one that died at its first await.

    Attributes:
        limpiezas: Cleanups that ran to the end, not merely started.
    """

    def __init__(self, eventos: int) -> None:
        """Store how many fragments this provider is willing to produce.

        Args:
            eventos: Upper bound of fragments. It is bounded and not infinite
                so that a transport which stops cancelling fails the case
                instead of hanging the suite.
        """
        self._eventos = eventos
        self.limpiezas = 0

    def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
        """Return the iterator of this answer.

        Args:
            peticion: Question of the reader, ignored by the double.

        Returns:
            The asynchronous iterator the transport consumes and closes.
        """
        return self._reproducir()

    async def _reproducir(self) -> AsyncIterator[EventoChat]:
        """Yield fragments, running an awaiting cleanup on the way out.

        Yields:
            One text fragment per turn of the loop.
        """
        try:
            for indice in range(self._eventos):
                yield EventoToken(texto=f"t{indice} ", indice=indice)
        finally:
            await asyncio.sleep(0)
            self.limpiezas += 1


class DetectorQueSeQueda:
    """Detector that parks the turn on its Nth ask, to fix where the cut lands.

    Where the cancellation is delivered decides what can still be saved, and
    this double exists to make that place deterministic. ``is_disconnected()``
    is a poll and not a wait -it awaits the receive channel inside a scope it
    cancels itself- but it *is* an await, and an await inside the transport is
    where an in-flight cancellation finds the turn with the provider still
    suspended and therefore still closable. Parking here reproduces that
    instant without racing the clock. Measured against uvicorn with real RST
    cuts: with the cleanup unshielded, none of five turns finished it; with
    the shield, all five did.

    Attributes:
        parado: Set once the turn is parked, so the test can cancel exactly
            then instead of sleeping and hoping.
    """

    def __init__(self, parada: int) -> None:
        """Store the ask on which the turn is parked.

        Args:
            parada: Ordinal of the call that no longer answers.
        """
        self._parada = parada
        self._llamadas = 0
        self.parado = asyncio.Event()

    async def __call__(self) -> bool:
        """Answer whether the client hung up, or stop answering altogether.

        Returns:
            ``False`` while the turn advances. From the configured call on it
            never returns: the cancellation of the response arrives first.
        """
        self._llamadas += 1
        if self._llamadas < self._parada:
            return False
        self.parado.set()
        await asyncio.sleep(ESPERA_QUE_LA_CANCELACION_INTERRUMPE)
        return False


class ProveedorSinCierre:
    """Provider whose iterator is a class, so it has no ``aclose`` at all.

    The Protocol promises an ``AsyncIterator`` and not a generator, and this is
    what one written that way looks like: the shape a wrapper around the
    streaming response of a model takes, and the one the seam has to accept the
    day ``gemini.py`` lands.
    """

    def __init__(self, eventos: tuple[EventoChat, ...]) -> None:
        """Store the events this provider replays.

        Args:
            eventos: Events to yield, in order.
        """
        self._pendientes = iter(eventos)

    def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
        """Return the iterator of this answer.

        Args:
            peticion: Question of the reader, ignored by the double.

        Returns:
            The provider itself, which is its own asynchronous iterator.
        """
        return self

    def __aiter__(self) -> AsyncIterator[EventoChat]:
        """Return the iterator, as the asynchronous protocol asks.

        Returns:
            The provider itself.
        """
        return self

    async def __anext__(self) -> EventoChat:
        """Hand over the next stored event.

        Returns:
            The next event of the answer.

        Raises:
            StopAsyncIteration: When there are no events left.
        """
        try:
            return next(self._pendientes)
        except StopIteration:
            raise StopAsyncIteration from None


async def _nunca_desconectado() -> bool:
    """Report a client that stays on the line for the whole stream.

    Returns:
        Always ``False``.
    """
    return False


def _peticion() -> PeticionChat:
    """Build the request every case of this module sends.

    Returns:
        The question that replays C1.
    """
    return PeticionChat(mensaje="morosidad de la cartera", conversacion=CLAVE)


def _proveedor() -> ProveedorGuionizado:
    """Build the scripted provider with the pacing removed.

    Returns:
        A provider that replays C1 with no waits, so the suite measures order
        and cleanup instead of sleeping through a demo.
    """
    return ProveedorGuionizado(retardo_token_ms=0, retardo_herramienta_ms=0)


def _leer(marcos: list[str]) -> list[tuple[str, dict[str, Any]]]:
    """Decode SSE frames into ``(event name, payload)`` pairs.

    Args:
        marcos: Frames as the transport yielded them.

    Returns:
        One pair per frame, in order.
    """
    leidos: list[tuple[str, dict[str, Any]]] = []
    for marco in marcos:
        linea_evento, linea_datos = marco.rstrip("\n").split("\n", 1)
        nombre = linea_evento.removeprefix("event: ")
        leidos.append((nombre, json.loads(linea_datos.removeprefix("data: "))))
    return leidos


async def _transmitir(
    detector: DetectorTrasNLlamadas | None = None,
    proveedor: ProveedorDeTokens | None = None,
) -> list[str]:
    """Consume a whole stream and return its frames.

    Args:
        detector: Disconnection detector. ``None`` keeps the client connected.
        proveedor: Provider to consume. ``None`` uses the scripted one.

    Returns:
        Every frame the transport produced.
    """
    return [
        marco
        async for marco in chat_stream.transmitir(
            _peticion(),
            proveedor if proveedor is not None else _proveedor(),
            detector if detector is not None else _nunca_desconectado,
        )
    ]


async def _medir_cierre(espia: ProveedorEspia) -> bool:
    """Consume a cancelled stream and read the cleanup **without leaving the loop**.

    Where the reading is taken decides whether the two cases about ``aclose()``
    measure anything at all. ``asyncio.run()`` calls
    ``loop.shutdown_asyncgens()`` before closing the loop, and that finalizes
    every asynchronous generator left suspended: a flag read after it comes
    back ``True`` whether or not the transport ever closed the provider. Under
    uvicorn the loop outlives the turn by the whole life of the process, so
    that finalization does **not** happen when an answer ends -which is
    precisely the moment these cases are about. Read from inside, the flag
    reports the transport; read from outside, it reports the garbage
    collector.

    Args:
        espia: Provider whose cleanup is being measured.

    Returns:
        Whether the provider ran its own cleanup by the time the stream ended.
    """
    await _transmitir(DetectorTrasNLlamadas(corte=2), espia)
    return espia.cerrado


@pytest.fixture(autouse=True)
def registro_visible(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make the closing record reachable by ``capture_logs`` in this module.

    Two process-wide facts collide here, and neither is a defect of the code
    under test. ``configure_logging`` installs a filtering bound logger at
    ``LOG_LEVEL``, and the shared environment of the suite pins that to
    ``WARNING``; ``capture_logs`` only swaps the processor chain, so an
    ``info`` record is discarded by the wrapper before any processor sees it.
    On top of that the application caches the bound logger on first use, so a
    module logger that was already used keeps the filtering wrapper it was
    built with.

    The consequence is not confined to the suite and is worth writing down
    where somebody will read it: **a deployment that raises LOG_LEVEL above
    INFO has no cancellation record at all**, and the evidence of section 1.1
    of the plan cannot be captured. ``scripts/captura-cancelacion.sh`` pins the
    level for exactly this reason.

    Args:
        monkeypatch: Used to hand the transport a logger that is not cached.

    Yields:
        None. The fixture only manipulates process-wide state, and restores it.
    """
    configuracion = structlog.get_config()
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        cache_logger_on_first_use=False,
    )
    monkeypatch.setattr(chat_stream, "logger", structlog.get_logger())
    try:
        yield
    finally:
        structlog.configure(**configuracion)


@pytest.fixture(autouse=True)
def registro_limpio() -> Iterator[None]:
    """Fail loudly if a case leaves an entry behind, instead of poisoning the next.

    The registry is module state. Without this the first defect would make
    every later assertion about it meaningless, and the suite would report the
    wrong test as broken.

    Yields:
        None. The fixture only guards process-wide state.
    """
    assert chat_stream.streams_activos() == {}
    yield
    assert chat_stream.streams_activos() == {}


# ---------------------------------------------------------------------------
# B-10: the server stops producing when the reader leaves
# ---------------------------------------------------------------------------


def test_desconexion_corta_el_stream() -> None:
    """A client that hangs up stops the production, it does not just stop reading.

    Defect this catches: dropping the ``esta_desconectado()`` call from inside
    the loop. Every frame would still be well formed and the interface would
    still look right, while the server kept generating the whole answer for
    nobody -and, with Gemini behind the seam, kept paying for it.

    Args:
        None.
    """
    detector = DetectorTrasNLlamadas(corte=3)

    marcos = asyncio.run(_transmitir(detector))
    leidos = _leer(marcos)
    tokens = [nombre for nombre, _ in leidos if nombre == "token"]

    assert detector.llamadas >= 3
    assert len(tokens) < TOTAL_DE_TOKENS / 2
    assert leidos[-1][0] == "done"
    assert leidos[-1][1]["motivo"] == MotivoCierre.CANCELADO.value


def test_el_stream_completo_llega_entero() -> None:
    """With nobody hanging up, the whole script reaches the client.

    Defect this catches: a detector consulted with inverted logic, or a break
    that fires on the first ask. The cancellation cases above would still pass
    -they only require the stream to stop- while every answer of the demo would
    be truncated. Two assertions in opposite directions are what make the first
    one mean something.
    """
    leidos = _leer(asyncio.run(_transmitir()))
    tokens = [nombre for nombre, _ in leidos if nombre == "token"]

    assert len(tokens) == TOTAL_DE_TOKENS
    assert leidos[-1][0] == "done"
    assert leidos[-1][1]["motivo"] == MotivoCierre.COMPLETADO.value
    assert leidos[-1][1]["tokens_emitidos"] == TOTAL_DE_TOKENS


def test_done_cierra_el_stream_exactamente_una_vez() -> None:
    """``done`` appears once and last, whether the stream was cut or not.

    Defect this catches: a second closing event on the cancellation path. The
    client stops listening at the first ``done``, so a duplicate would leave
    the interface in the state of whichever arrived first, and the reader would
    see a cancelled turn reported as completed or the other way round.
    """
    for detector in (None, DetectorTrasNLlamadas(corte=6)):
        leidos = _leer(asyncio.run(_transmitir(detector)))
        cierres = [nombre for nombre, _ in leidos if nombre == "done"]

        assert cierres == ["done"]
        assert leidos[-1][0] == "done"


def test_el_done_del_cancelado_se_emite_aunque_nadie_lo_lea() -> None:
    """The stream closes itself even when the socket is already gone.

    The byte is lost and that is fine; what cannot be lost is the single exit
    of the generator, because it is where the registry is emptied and where the
    closing record is written.

    Defect this catches: a ``break`` that returns without closing. The
    cancellation would look right from outside and the stream would end with no
    ``done`` at all, so a client that reconnected mid-answer -or a test
    consuming without a socket, which is every test here- would have nothing to
    assert on.
    """
    leidos = _leer(asyncio.run(_transmitir(DetectorTrasNLlamadas(corte=1))))

    assert [nombre for nombre, _ in leidos] == ["done"]
    assert leidos[0][1]["motivo"] == MotivoCierre.CANCELADO.value
    assert leidos[0][1]["tokens_emitidos"] == 0


# ---------------------------------------------------------------------------
# B-11, B-12: nothing survives the stream
# ---------------------------------------------------------------------------


def test_registro_queda_vacio_tras_cancelar_y_tras_completar() -> None:
    """The live stream registry is empty once the stream ends, either way.

    This is the honest measure of "no hanging tasks", and it is a registry and
    not a count of tasks because a count is noisy: the event loop of pytest has
    tasks of its own and an assertion over their number passes almost always.

    Defect this catches: removing the ``finally``, or replacing it with an
    ``except Exception`` -which does not catch ``CancelledError``, because that
    one inherits from ``BaseException``. Either way the entry stays, and with
    it the generator and the provider it holds.
    """
    for detector in (None, DetectorTrasNLlamadas(corte=4)):
        asyncio.run(_transmitir(detector))

        assert chat_stream.streams_activos() == {}


def test_el_registro_da_de_alta_mientras_el_stream_vive() -> None:
    """The registry holds the stream while it is open, not only after it closes.

    Defect this catches: a registry that is written and erased in the same
    breath, or never written at all. Both would leave the assertions above
    green -an empty mapping compares equal to an empty mapping- while the
    registry stopped being able to report anything, which is the only thing it
    exists for.
    """
    vistos: list[int] = []

    async def _correr() -> None:
        generador = chat_stream.transmitir(
            _peticion(), _proveedor(), _nunca_desconectado
        )
        try:
            await anext(generador)
            vistos.append(len(chat_stream.streams_activos()))
        finally:
            await generador.aclose()

    asyncio.run(_correr())

    assert vistos == [1]


def test_cancelacion_no_deja_tareas() -> None:
    """Cancelling leaves no task of the transport behind.

    Secondary to the registry and written as a relative delta on purpose: the
    absolute number of tasks alive in a pytest event loop is not ours to
    predict, and an assertion over it would fail for reasons that have nothing
    to do with this module.

    Defect this catches: a provider spawned as a background task and never
    awaited. The registry would come out empty -the transport did finish- while
    the work kept running.
    """

    async def _correr() -> tuple[int, int]:
        antes = len(asyncio.all_tasks())
        await _transmitir(DetectorTrasNLlamadas(corte=5))
        await asyncio.sleep(0)
        return antes, len(asyncio.all_tasks())

    antes, despues = asyncio.run(_correr())

    assert despues <= antes


def test_el_generador_del_proveedor_se_cierra() -> None:
    """The transport closes the provider it consumed, on the cancelled path too.

    Defect this catches: forgetting ``aclose()``. The ``finally`` of the
    provider never runs, so today nothing visible happens and the day
    ``gemini.py`` lands the outgoing connection of every cancelled turn stays
    open until the garbage collector decides otherwise. Verified by deleting
    ``await _cerrar(eventos)`` from the transport; measured from outside the
    loop, as this case was until the reading moved into ``_medir_cierre``, the
    deletion left it green.
    """
    espia = ProveedorEspia(
        (
            EventoToolCall(
                id="tc-1",
                estado=EstadoTarjeta.ANUNCIO,
                herramienta="consultar_metrica",
                etiqueta="chat.toolCall.tool.consultar_metrica",
            ),
            EventoToken(texto="hola ", indice=0),
            EventoToken(texto="mundo", indice=1),
        )
    )

    cerrado = asyncio.run(_medir_cierre(espia))

    assert cerrado is True


def test_abandonar_el_generador_tambien_lo_cierra() -> None:
    """A consumer that walks away mid-stream still empties the registry.

    This is the path the real server takes: when the socket dies, Starlette
    closes the body iterator instead of asking it for another frame, so the
    loop never reaches its own closing branch.

    Defect this catches: doing the cleanup after the loop instead of in a
    ``finally``. Every case above would stay green, because they all consume
    the generator to exhaustion, and the one path production actually uses
    would leak the entry of every interrupted answer. Both readings are taken
    before the loop closes, for the reason written down in ``_medir_cierre``:
    outside it, ``shutdown_asyncgens()`` closes the provider itself and the
    assertion passes with the transport doing nothing.
    """
    espia = ProveedorEspia((EventoToken(texto="hola", indice=0),))

    async def _correr() -> tuple[bool, bool]:
        generador = chat_stream.transmitir(_peticion(), espia, _nunca_desconectado)
        await anext(generador)
        await generador.aclose()
        return espia.cerrado, chat_stream.streams_activos() == {}

    cerrado, registro_vacio = asyncio.run(_correr())

    assert cerrado is True
    assert registro_vacio is True


def test_un_proveedor_sin_aclose_no_rompe_el_cierre() -> None:
    """A provider that is an iterator and not a generator still closes cleanly.

    Defect this catches: simplifying the closing helper into a plain
    ``await eventos.aclose()``. The Protocol promises an ``AsyncIterator``, so a
    provider written as a class has no such method and the ``AttributeError``
    would be raised inside the ``finally`` -after the whole body was already on
    its way-, which reaches the reader as a stream that ends mid answer and the
    server as a 500 on a turn that had answered. It is the shape the Gemini
    provider is most likely to have, and today nothing else in the suite uses
    anything but a generator.
    """
    proveedor = ProveedorSinCierre((EventoToken(texto="hola", indice=0),))

    leidos = _leer(asyncio.run(_transmitir(proveedor=proveedor)))

    assert [nombre for nombre, _ in leidos] == ["token", "done"]
    assert leidos[-1][1]["motivo"] == MotivoCierre.COMPLETADO.value
    assert chat_stream.streams_activos() == {}


def test_el_cancel_scope_de_la_respuesta_cierra_el_turno_entero() -> None:
    """The branch production takes: the cancel scope, not the disconnection probe.

    Twenty real cancellations measured against uvicorn left through here and
    zero through ``esta_desconectado``. Starlette runs the body of a
    ``StreamingResponse`` inside an anyio task group and cancels its whole
    scope when the socket dies, while the turn is parked asking the connection
    whether the reader is still there; every other case of this module injects
    the answer of that probe instead, which is the branch a deployed portal
    almost never takes.

    Defect this catches: a cleanup that is not shielded. anyio re-delivers the
    cancellation at **every** await point while the scope stays cancelled, so
    an unshielded ``finally`` dies at its first one. Two things are lost with
    it and neither is visible from any other case: the provider never finishes
    its own cleanup -one outgoing connection per cancelled turn the day
    ``gemini.py`` lands behind the same Protocol- and the
    ``chat.stream.cancelado`` record, which is the evidence this User Story
    delivers, is never written at all.

    Two measurements decided how this case is written. Removing the shield
    turns it red on the cleanup and would turn it red again on the record; the
    registry is the one assertion that survives, because the entry is dropped
    before the first await. And cancelling with a plain ``task.cancel()``
    instead of the cancel scope of the response leaves the unshielded
    transport **green**: asyncio delivers its cancellation once, so a case
    written that way would be one more decoration.
    """
    proveedor = ProveedorQueLimpiaEsperando(eventos=5)
    detector = DetectorQueSeQueda(parada=3)

    async def _consumir() -> None:
        async for _ in chat_stream.transmitir(_peticion(), proveedor, detector):
            pass

    async def _correr() -> tuple[bool, int]:
        async with anyio.create_task_group() as grupo:
            grupo.start_soon(_consumir)
            await detector.parado.wait()
            grupo.cancel_scope.cancel()
        # Both readings stay inside the loop, for the reason ``_medir_cierre``
        # spells out: after ``asyncio.run`` the count would include the cleanup
        # that ``shutdown_asyncgens`` forces on the abandoned provider.
        return chat_stream.streams_activos() == {}, proveedor.limpiezas

    with capture_logs() as registros:
        registro_vacio, limpiezas = asyncio.run(_correr())

    assert registro_vacio is True
    assert limpiezas == 1

    (cierre,) = [r for r in registros if r["event"] == chat_stream.EVENTO_CANCELADO]

    assert cierre["motivo"] == MotivoCierre.CANCELADO.value
    assert 0 < cierre["tokens_emitidos"] < TOTAL_DE_TOKENS


# ---------------------------------------------------------------------------
# B-13: the record that becomes the evidence of A4
# ---------------------------------------------------------------------------


def test_log_de_cancelacion_es_inequivoco() -> None:
    """A cancelled stream writes one ``chat.stream.cancelado`` and no completion.

    This record is the evidence of this User Story: the deliverable quotes the
    line, not a screenshot of the browser, because a screenshot proves the
    interface changed and not that the server found out. Its three fields are
    what make it readable, and ``tokens_emitidos`` is the one that makes it
    conclusive: strictly between zero and the total means the script was cut
    while it was still producing. Equal to the total would mean the server had
    already finished and the cut was cosmetic.

    Defect this catches: writing ``chat.stream.completado`` on the cancelled
    path. The capture pasted into the deliverable would then be evidence of the
    opposite of what its caption claims.
    """
    corte = 8

    with capture_logs() as registros:
        asyncio.run(_transmitir(DetectorTrasNLlamadas(corte=corte)))

    cancelados = [r for r in registros if r["event"] == chat_stream.EVENTO_CANCELADO]
    completados = [r for r in registros if r["event"] == chat_stream.EVENTO_COMPLETADO]

    assert len(cancelados) == 1
    assert not completados

    (registro,) = cancelados
    assert registro["stream_id"]
    assert registro["duracion_ms"] >= 0
    assert 0 < registro["tokens_emitidos"] < TOTAL_DE_TOKENS


def test_el_log_de_cierre_no_lleva_la_pregunta() -> None:
    """No closing record carries the prompt, in either direction.

    Defect this catches: adding ``mensaje`` to the record while debugging and
    leaving it there. The privacy rule of the project forbids the raw prompt in
    logs and traces, and this is the one place in the chat where a record is
    written per turn, so it is where that rule would break first.
    """
    pregunta = _peticion().mensaje

    with capture_logs() as registros:
        asyncio.run(_transmitir())
        asyncio.run(_transmitir(DetectorTrasNLlamadas(corte=4)))

    for registro in registros:
        assert pregunta not in json.dumps(registro, default=str)


def test_el_stream_id_del_log_es_el_del_done() -> None:
    """The record and the closing event name the same stream.

    Defect this catches: generating a second identifier for the record. The
    capture of the evidence would then be impossible to tie to the stream it
    describes, and correlating a report with its trace would stop working the
    day there is more than one reader.
    """
    with capture_logs() as registros:
        marcos = asyncio.run(_transmitir(DetectorTrasNLlamadas(corte=6)))

    (registro,) = [r for r in registros if r["event"] == chat_stream.EVENTO_CANCELADO]
    nombre, cierre = _leer(marcos)[-1]

    assert nombre == "done"
    assert cierre["motivo"] == MotivoCierre.CANCELADO.value
    assert cierre["tokens_emitidos"] == registro["tokens_emitidos"]


def test_el_tiempo_al_primer_token_no_sale_del_log() -> None:
    """Time to first token is written to the record and to nothing else.

    With a scripted provider that figure measures our own ``sleep``, so
    publishing it as latency would be an honest number about a system that does
    not exist yet -which is the anti-hallucination rule pointed at ourselves.
    It is computed anyway, so that the day Gemini lands it becomes a span
    attribute without touching the contract of the client.

    Defect this catches: adding ``primer_token_ms`` to ``done``. US-028 and
    US-024 read that event, and a field there is a field the interface can
    render.
    """
    with capture_logs() as registros:
        marcos = asyncio.run(_transmitir())

    (registro,) = [r for r in registros if r["event"] == chat_stream.EVENTO_COMPLETADO]
    _, cierre = _leer(marcos)[-1]

    assert registro["primer_token_ms"] is not None
    assert "primer_token_ms" not in cierre
    assert set(cierre) == {"motivo", "tokens_emitidos", "duracion_ms"}


def test_un_turno_fallido_no_se_registra_como_cancelado() -> None:
    """A turn that ends in a typed error writes the completion record, not the other.

    The evidence of section 1.1 is a grep for ``chat.stream.cancelado``, so that
    name has to mean exactly one thing: the reader walked away. The two records
    still tell a failure from an answer, by the ``motivo`` they carry.

    Defect this catches: naming the record by what it is not -completion when
    the motive is completion, cancellation otherwise-. Every silo that did not
    answer would then land in the capture as a reader pressing Stop, and the
    line pasted into the deliverable would be evidence of a cancellation that
    never happened.
    """

    async def _correr() -> list[str]:
        return [
            marco
            async for marco in chat_stream.transmitir(
                PeticionChat(
                    mensaje="exposicion por contraparte", conversacion="permiso"
                ),
                _proveedor(),
                _nunca_desconectado,
            )
        ]

    with capture_logs() as registros:
        marcos = asyncio.run(_correr())

    _, cierre = _leer(marcos)[-1]

    assert cierre["motivo"] == MotivoCierre.ERROR.value
    assert not [r for r in registros if r["event"] == chat_stream.EVENTO_CANCELADO]

    (registro,) = [r for r in registros if r["event"] == chat_stream.EVENTO_COMPLETADO]

    assert registro["motivo"] == MotivoCierre.ERROR.value


# ---------------------------------------------------------------------------
# The transport survives a provider that breaks
# ---------------------------------------------------------------------------


def test_un_proveedor_que_revienta_cierra_el_turno() -> None:
    """A provider that raises still produces a typed error and its ``done``.

    Defect this catches: letting the exception escape the generator. Starlette
    would abort the response mid body, the client would see a stream that
    simply stops, and the interface would spin forever on a turn that already
    failed -the one state the reader cannot get out of.
    """

    class ProveedorRoto:
        """Provider that fails after its first event."""

        def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
            """Return the iterator that breaks.

            Args:
                peticion: Question of the reader, ignored.

            Returns:
                The iterator the transport consumes.
            """
            return self._reproducir()

        async def _reproducir(self) -> AsyncIterator[EventoChat]:
            """Yield one event and then fail.

            Yields:
                A single text fragment.

            Raises:
                RuntimeError: Always, right after the first event.
            """
            yield EventoToken(texto="hola", indice=0)
            message = "el proveedor se cayo"
            raise RuntimeError(message)

    leidos = _leer(asyncio.run(_transmitir(proveedor=ProveedorRoto())))
    nombres = [nombre for nombre, _ in leidos]

    assert nombres == ["token", "error", "done"]
    assert leidos[1][1]["paso"] == "transporte"
    assert leidos[1][1]["recuperable"] is True
    assert leidos[2][1]["motivo"] == MotivoCierre.ERROR.value
    assert chat_stream.streams_activos() == {}
