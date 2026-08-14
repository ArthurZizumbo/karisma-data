"""The SSE contract of ``POST /api/chat``: framing, order and traceability.

Nothing here opens a socket to a model, and nothing reads PostgreSQL: the
provider of S4 is deterministic by construction and the user lookup enters
through the repository double of the shared conftest. What is measured is the
part three User Stories depend on -the names and types of the four events, the
order they may legally arrive in, and the rule that no figure is spoken before
the card that justifies it- plus the permission rule of the endpoint.

The transport is exercised through the provider and through the client. Neither
alone is enough: the provider decides the order, the client decides whether the
answer is really delivered in pieces, and a stream that arrives in one block is
SSE only by its content type.
"""

import asyncio
import json
import re
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api import chat as api_chat
from app.core.scopes import ErrorCode, Scope
from app.models.chat import (
    MENSAJE_MAXIMO,
    ChatErrorCode,
    EstadoTarjeta,
    EventoChat,
    EventoError,
    EventoToken,
    EventoToolCall,
    MotivoCierre,
    PasoDelStream,
    PeticionChat,
    ResultadoTarjeta,
)
from app.services import chat_stream
from app.services.proveedores import ProveedorDeTokens, obtener_proveedor
from app.services.proveedores.guionizado import (
    CLAVE_COLUMNA_METRICA,
    CLAVE_COLUMNA_VALOR,
    CONVERSACIONES,
    PATRON_NUMERO,
    ProveedorGuionizado,
    fragmentos_de,
    numeros_de,
)

if TYPE_CHECKING:
    from app.models.user import AppUser

RUTA: Final[str] = "/api/chat"

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: Shape every readable tool name must have. A sentence here would reach both
#: locales untranslated, and no other test would notice.
PATRON_ETIQUETA: Final[re.Pattern[str]] = re.compile(r"^chat\.toolCall\.tool\.[a-z_]+$")

#: Spelling of the fourth role in ``frontend/app/types/navegacion.ts``,
#: recorded as debt 2 of US-015. It is the name a token would realistically
#: carry by mistake, which is why the unreadable scope below is that one and
#: not an invented string.
ROL_FUERA_DEL_VOCABULARIO: Final[str] = "administrador"

#: Keys of the four scripted conversations, used to parametrize the invariants
#: that have to hold for every one of them and not only for the happy path.
CLAVES: Final[tuple[str, ...]] = tuple(CONVERSACIONES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _nunca_desconectado() -> bool:
    """Report a client that stays on the line for the whole stream.

    Returns:
        Always ``False``: the cancellation cases live in their own module.
    """
    return False


async def _recolectar(clave: str) -> list[EventoChat]:
    """Replay one conversation with no pacing and return its events in order.

    The delays are set to zero instead of being patched: what these tests
    measure is the order of the events, and a script that takes a quarter of a
    second per card would only make the suite slower.

    Args:
        clave: Identifier of the conversation to replay.

    Returns:
        Every event the provider produced, in the order it produced them.
    """
    proveedor = ProveedorGuionizado(retardo_token_ms=0, retardo_herramienta_ms=0)
    peticion = PeticionChat(mensaje="pregunta de prueba", conversacion=clave)
    return [evento async for evento in proveedor.generar(peticion)]


def _eventos_de(clave: str) -> list[EventoChat]:
    """Return the events of one conversation, from a synchronous test.

    Args:
        clave: Identifier of the conversation to replay.

    Returns:
        Every event the provider produced, in order.
    """
    return asyncio.run(_recolectar(clave))


def _transmitidos(clave: str) -> list[tuple[str, dict[str, Any]]]:
    """Replay one conversation through the transport and decode its frames.

    The frames are split with ``str`` and read with ``json`` and never with the
    function that wrote them: checking an output with the module that produced
    it only proves the module agrees with itself.

    Args:
        clave: Identifier of the conversation to replay.

    Returns:
        One ``(event name, payload)`` pair per frame, in the order the
        transport produced them.
    """

    async def _correr() -> list[str]:
        return [
            marco
            async for marco in chat_stream.transmitir(
                PeticionChat(mensaje="pregunta de prueba", conversacion=clave),
                ProveedorGuionizado(retardo_token_ms=0, retardo_herramienta_ms=0),
                _nunca_desconectado,
            )
        ]

    leidos: list[tuple[str, dict[str, Any]]] = []
    for marco in asyncio.run(_correr()):
        linea_evento, linea_datos = marco.rstrip("\n").split("\n", 1)
        leidos.append(
            (
                linea_evento.removeprefix("event: "),
                json.loads(linea_datos.removeprefix("data: ")),
            )
        )
    return leidos


def _pasos_con_herramienta() -> list[tuple[str, str]]:
    """Return every scripted tool call as ``(conversation, tool)``.

    Returns:
        One pair per card of the script, so a case identifies itself in the
        output of pytest.
    """
    return [
        (clave, paso.herramienta)
        for clave, pasos in CONVERSACIONES.items()
        for paso in pasos
        if paso.herramienta is not None
    ]


def _cabecera(token: str) -> dict[str, str]:
    """Build the authorization header of a request.

    Args:
        token: Encoded access token.

    Returns:
        The header mapping the client sends.
    """
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operativo(usuarios_semilla: dict[str, "AppUser"]) -> str:
    """Return the login identifier of a seeded user carrying ``operativo``.

    Args:
        usuarios_semilla: Rows served by the repository double.

    Returns:
        The login identifier of the first ``operativo`` of the seed.
    """
    for usuario in usuarios_semilla.values():
        if usuario.role == Scope.OPERATIVO.value:
            return usuario.username
    message = "la semilla no trae ningun usuario operativo"
    raise AssertionError(message)


# ---------------------------------------------------------------------------
# B-1, B-9: the response is a stream, and it is delivered as one
# ---------------------------------------------------------------------------


def test_cabeceras_de_stream(
    cliente: TestClient, token_de: Callable[..., str], operativo: str
) -> None:
    """The answer declares itself a stream and forbids every buffer on the way.

    Defect this catches: somebody answers with a ``JSONResponse``, or drops
    ``X-Accel-Buffering``. The second one is invisible in local development and
    fatal in Cloud Run, where the intermediary holds the body until the
    generator ends and the progressive answer of the demo disappears.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
    """
    with cliente.stream(
        "POST",
        RUTA,
        json={"mensaje": "morosidad de la cartera", "conversacion": "morosidad"},
        headers=_cabecera(token_de(operativo, Scope.OPERATIVO.value)),
    ) as respuesta:
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"].startswith("text/event-stream")
        # `no-store` and not `no-cache`: the second one forces revalidation but
        # still allows the body to be written to disk, and this body is the
        # answer one role was allowed to see. The third assertion is written in
        # the negative because `Connection` is hop-by-hop -ASGI already manages
        # persistence- and an application that emits it hands a proxy a header
        # it was supposed to consume, which is the shape of request smuggling.
        assert respuesta.headers["cache-control"] == "no-store"
        assert respuesta.headers["x-accel-buffering"] == "no"
        assert "connection" not in {nombre.lower() for nombre in respuesta.headers}
        respuesta.read()


def test_entrega_incremental() -> None:
    """The transport hands over one frame at a time, never the whole answer.

    Defect this catches: somebody accumulates every event in a list and yields
    once. The content type would still say ``text/event-stream``, every other
    assertion of this file would still pass, and the interface would paint the
    finished answer in a single repaint -SSE by name and a blocking call in
    fact.

    Measured on the generator and not on the client, and the reason is a
    limitation worth writing down rather than working around: the ASGI test
    client buffers the whole body before handing it over, so ``iter_raw`` there
    returns one chunk however the server produced it. What the socket really
    does is the subject of the manual capture of section 1.1, taken against
    uvicorn with ``curl -sN``.
    """
    proveedor = ProveedorGuionizado(retardo_token_ms=0, retardo_herramienta_ms=0)
    peticion = PeticionChat(mensaje="morosidad", conversacion="morosidad")

    async def _correr() -> list[str]:
        return [
            marco
            async for marco in chat_stream.transmitir(
                peticion, proveedor, _nunca_desconectado
            )
        ]

    marcos = asyncio.run(_correr())

    assert len(marcos) >= 2
    for marco in marcos:
        assert marco.startswith("event: ")
        assert marco.endswith("\n\n")
        assert marco.count("event: ") == 1


def test_el_marco_sse_lleva_nombre_y_json(
    cliente: TestClient, token_de: Callable[..., str], operativo: str
) -> None:
    """Every frame is ``event:`` plus ``data:`` and closes with a blank line.

    Defect this catches: somebody sends the payload without its ``event:``
    line, or separates frames with a single newline. The browser parser would
    then deliver every event as the default ``message`` type, and the client of
    US-023 -which switches on the name- would render nothing at all.

    The frames are split with ``str`` and decoded with ``json``: verifying the
    output with the module that produced it would only prove it agrees with
    itself.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
    """
    import json

    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "permiso", "conversacion": "permiso"},
        headers=_cabecera(token_de(operativo, Scope.OPERATIVO.value)),
    )
    marcos = [marco for marco in respuesta.text.split("\n\n") if marco.strip()]

    assert marcos
    for marco in marcos:
        nombre, datos = marco.split("\n", 1)
        assert nombre.startswith("event: ")
        assert datos.startswith("data: ")
        json.loads(datos.removeprefix("data: "))


# ---------------------------------------------------------------------------
# B-2, B-2b, B-2c: the closed vocabularies are closed
# ---------------------------------------------------------------------------


def test_modelos_rechazan_estado_desconocido() -> None:
    """A fifth card state cannot be built.

    Defect this catches: somebody adds a state to the card without going
    through the contract. US-028 switches on these four values, so a fifth one
    would reach the browser as an unhandled case and paint nothing.
    """
    for estado in EstadoTarjeta:
        EventoToolCall(
            id="tc-1",
            estado=estado,
            herramienta="consultar_metrica",
            etiqueta="chat.toolCall.tool.consultar_metrica",
        )

    with pytest.raises(ValidationError):
        EventoToolCall(
            id="tc-1",
            estado="pendiente",  # type: ignore[arg-type]
            herramienta="consultar_metrica",
            etiqueta="chat.toolCall.tool.consultar_metrica",
        )


def test_modelos_rechazan_paso_desconocido() -> None:
    """A fifth step of the stream cannot be built.

    Defect this catches: somebody types ``paso`` as a free ``str``. US-024
    writes its notice against these four values, and with a free string its own
    rejection test could never fail: the frontend would end up comparing
    sentences.
    """
    for paso in PasoDelStream:
        EventoError(
            paso=paso,
            clase="recuperable",
            codigo="silo_no_disponible",
            mensaje_clave="chat.error.message.recoverable",
            recuperable=True,
        )

    with pytest.raises(ValidationError):
        EventoError(
            paso="otro",  # type: ignore[arg-type]
            clase="recuperable",
            codigo="silo_no_disponible",
            mensaje_clave="chat.error.message.recoverable",
            recuperable=True,
        )


def test_modelos_rechazan_clase_de_error_desconocida() -> None:
    """The family of a failure is one of two values and nothing else.

    Defect this catches: somebody publishes a third family -"tecnico",
    "desconocido"- and the notice of US-024, which decides whether to offer a
    retry from this field alone, stops knowing what to do with it.
    """
    with pytest.raises(ValidationError):
        EventoError(
            paso=PasoDelStream.TRANSPORTE,
            clase="tecnico",  # type: ignore[arg-type]
            codigo="fallo",
            mensaje_clave="chat.error.message.recoverable",
            recuperable=True,
        )


@pytest.mark.parametrize(("clave", "herramienta"), _pasos_con_herramienta())
def test_etiqueta_es_clave_i18n(clave: str, herramienta: str) -> None:
    """Every readable tool name is a full i18n key, never a sentence.

    Defect this catches: the script writes "Consultando morosidad" in
    ``etiqueta``. ``t(tarjeta.etiqueta)`` would return that sentence verbatim
    in both locales, so the interface would silently stop being bilingual on
    the one screen where the reader watches the work happen.

    Args:
        clave: Conversation the card belongs to.
        herramienta: Technical name of the tool behind the card.
    """
    tarjetas = [
        evento
        for evento in _eventos_de(clave)
        if isinstance(evento, EventoToolCall) and evento.herramienta == herramienta
    ]

    assert tarjetas
    for tarjeta in tarjetas:
        assert PATRON_ETIQUETA.match(tarjeta.etiqueta), tarjeta.etiqueta


def test_el_mensaje_no_puede_ser_solo_espacios() -> None:
    """A turn made of whitespace never opens a stream.

    Defect this catches: relying on ``min_length`` alone. It counts characters,
    so three spaces get past it and the reader watches a card announce a query
    for a question nobody asked.
    """
    with pytest.raises(ValidationError):
        PeticionChat(mensaje="   ")

    assert PeticionChat(mensaje="  hola  ").mensaje == "hola"


def test_el_mensaje_tiene_un_tope_y_es_el_que_declara_el_contrato() -> None:
    """The question is capped at 2000 characters, and exactly 2000 still fits.

    Defect this catches: widening the bound -or deleting it- the day a real
    model lands behind the seam. The cap is the only thing between a pasted
    document and the prompt, which is a cost per turn with Gemini and an
    injection surface with any model, and the literal is asserted here because
    a test written against the constant alone would keep passing after somebody
    moved it to a hundred thousand. The other direction is checked too: an
    off-by-one would refuse a legitimate question of exactly the declared
    length, and nothing else in the suite sends one that long.
    """
    assert MENSAJE_MAXIMO == 2000

    al_limite = PeticionChat(mensaje="a" * MENSAJE_MAXIMO)

    assert len(al_limite.mensaje) == MENSAJE_MAXIMO

    with pytest.raises(ValidationError):
        PeticionChat(mensaje="a" * (MENSAJE_MAXIMO + 1))


# ---------------------------------------------------------------------------
# B-3, B-4: the order of the stream is legal, and the card comes first
# ---------------------------------------------------------------------------


def _assert_orden_legal(eventos: Iterable[EventoChat]) -> None:
    """Assert that a sequence of events respects the SSE contract v1.

    Three rules in one place, because they are read together: no fragment of
    text may precede the first card that resolved, every card walks
    ``anuncio -> ejecucion* -> (resultado|error)`` under a stable id, and the
    provider never closes the stream itself.

    Args:
        eventos: Events of one conversation, in the order they were produced.

    Raises:
        AssertionError: If any of the three rules is broken.
    """
    materiales = list(eventos)
    por_tarjeta: dict[str, list[EstadoTarjeta]] = {}
    resuelta = False

    for evento in materiales:
        if isinstance(evento, EventoToolCall):
            por_tarjeta.setdefault(evento.id, []).append(evento.estado)
            if evento.estado is EstadoTarjeta.RESULTADO:
                resuelta = True
        if isinstance(evento, EventoToken):
            assert resuelta, "un token llego antes de que ninguna tarjeta resolviera"

    assert por_tarjeta, "la conversacion no anuncio ninguna tarjeta"
    for estados in por_tarjeta.values():
        assert estados[0] is EstadoTarjeta.ANUNCIO
        assert estados[-1] in {EstadoTarjeta.RESULTADO, EstadoTarjeta.ERROR}
        assert all(estado is EstadoTarjeta.EJECUCION for estado in estados[1:-1]), (
            estados
        )


@pytest.mark.parametrize("clave", CLAVES)
def test_orden_legal(clave: str) -> None:
    """Every scripted conversation arrives in an order the contract allows.

    Defect this catches: somebody emits the first fragment of text before the
    card resolves, so the reader sees a figure quoted before its source exists;
    or a card that jumps straight from announced to resolved, which is the
    state US-028 paints while the tool is running.

    ``permiso`` is in the list on purpose: it is the only conversation with no
    text at all, and an assertion written for the happy path alone would treat
    its zero fragments as a pass without ever looking at its card.

    Args:
        clave: Identifier of the conversation replayed.
    """
    _assert_orden_legal(_eventos_de(clave))


@pytest.mark.parametrize("clave", CLAVES)
def test_el_proveedor_no_cierra_el_stream(clave: str) -> None:
    """The provider never emits ``done``: closing belongs to the transport.

    Defect this catches: a provider that closes the stream itself would produce
    two ``done`` once the transport adds its own, and the client -which stops
    listening at the first one- would drop the tail of every answer.

    Args:
        clave: Identifier of the conversation replayed.
    """
    from app.models.chat import EventoDone

    assert not [
        evento for evento in _eventos_de(clave) if isinstance(evento, EventoDone)
    ]


@pytest.mark.parametrize("clave", ["derivados", "permiso"])
def test_un_fallo_del_guion_cierra_el_turno_con_motivo_error(clave: str) -> None:
    """A conversation that ends in a typed error closes with ``done(motivo=error)``.

    Defect this catches: dropping the line of the transport that turns a typed
    error into the closing motive. Every frame would still be legal and the
    notice of US-024 would still be painted, while ``done`` reported the turn
    as completed: the client maps that motive to ``inactivo``, so the screen
    would go back to waiting for the next question as if nothing had failed,
    and US-028 -which derives ``interrumpida`` from exactly this field- would
    never mark the turn the reader watched break.

    Args:
        clave: Identifier of the conversation whose script fails.
    """
    leidos = _transmitidos(clave)
    nombres = [nombre for nombre, _ in leidos]

    assert nombres[-2:] == ["error", "done"]
    assert leidos[-1][1]["motivo"] == MotivoCierre.ERROR.value


def test_anuncio_precede_a_la_espera() -> None:
    """The card is announced before the tool is waited for, not after.

    Defect this catches: somebody moves the announcing ``yield`` behind the
    ``await`` of the tool. Every assertion about order would still pass -the
    announcement still comes first in the sequence- while the screen would sit
    dead for the whole wait, which is precisely the perception of progress this
    User Story exists to demonstrate.

    The clock is replaced instead of measured: a timeline that records both the
    events and the waits is deterministic, and a threshold in milliseconds
    would only be a slow way of flaking.
    """
    linea: list[str] = []
    dormir_real = asyncio.sleep

    async def _dormir(segundos: float) -> None:
        linea.append("espera")
        await dormir_real(0)

    async def _correr() -> None:
        proveedor = ProveedorGuionizado()
        peticion = PeticionChat(mensaje="morosidad", conversacion="morosidad")
        async for evento in proveedor.generar(peticion):
            if isinstance(evento, EventoToolCall):
                linea.append(evento.estado.value)

    with pytest.MonkeyPatch.context() as parche:
        parche.setattr(asyncio, "sleep", _dormir)
        asyncio.run(_correr())

    assert linea[0] == EstadoTarjeta.ANUNCIO.value
    assert linea[1] == "espera"
    assert linea.index(EstadoTarjeta.ANUNCIO.value) < linea.index("espera")
    assert linea.index("espera") < linea.index(EstadoTarjeta.RESULTADO.value)


def test_el_anuncio_no_finge_tiempo_transcurrido() -> None:
    """The announcing event carries no elapsed time, because none has passed.

    Defect this catches: filling ``transcurrido_ms`` with zero instead of
    leaving it empty. US-028 tells "the tool has not started" from "it took no
    time" by exactly this field, and a zero would make the card show a duration
    for work that had not begun.
    """
    anuncios = [
        evento
        for evento in _eventos_de("liquidez")
        if isinstance(evento, EventoToolCall) and evento.estado is EstadoTarjeta.ANUNCIO
    ]

    assert anuncios
    assert all(evento.transcurrido_ms is None for evento in anuncios)


# ---------------------------------------------------------------------------
# B-5: anti-hallucination, as an automatic check and not as an intention
# ---------------------------------------------------------------------------


def _assert_trazabilidad(eventos: Iterable[EventoChat]) -> None:
    """Assert that every figure spoken was returned by an earlier card.

    The rule is walked over the emitted stream and not over the constants of
    the script, so it also fails when the figure exists somewhere in the turn
    but arrives after the sentence that quotes it.

    Args:
        eventos: Events of one conversation, in the order they were produced.

    Raises:
        AssertionError: If a card returns figures without citing its source, or
            if a fragment of text names a literal no earlier card returned.
    """
    permitidas: set[str] = set()

    for evento in eventos:
        if isinstance(evento, EventoToolCall):
            resultado = evento.resultado
            if resultado is None:
                continue
            assert evento.fuente is not None, (
                f"la tarjeta {evento.id} devolvio cifras sin citar su fuente"
            )
            celdas = [str(celda) for fila in resultado.filas for celda in fila]
            for texto in [resultado.cifra or "", *celdas]:
                permitidas |= numeros_de(texto)
        if isinstance(evento, EventoToken):
            huerfanas = numeros_de(evento.texto) - permitidas
            assert not huerfanas, f"cifras sin tarjeta previa: {sorted(huerfanas)}"


def _guion_sintetico(cifra: str, frase: str) -> list[EventoChat]:
    """Build the smallest legal answer: one card with a figure, one sentence.

    A synthetic script and not one of the four real ones, because what is
    exercised here is the guard: a forgery has to be written somewhere, and
    writing it into the script the demo replays would be the defect itself.

    Args:
        cifra: Figure the card returns, written as the script writes them.
        frase: Sentence the answer speaks once the card has resolved.

    Returns:
        The two events, card first, as a provider would have produced them.
    """
    return [
        EventoToolCall(
            id="tc-1",
            estado=EstadoTarjeta.RESULTADO,
            herramienta="consultar_metrica",
            etiqueta="chat.toolCall.tool.consultar_metrica",
            fuente="catalogo.creditos.morosidad_cartera",
            resultado=ResultadoTarjeta(
                columnas=[CLAVE_COLUMNA_METRICA, CLAVE_COLUMNA_VALOR],
                filas=[["Morosidad de la cartera hipotecaria", cifra]],
                cifra=cifra,
            ),
        ),
        EventoToken(texto=frase, indice=0),
    ]


@pytest.mark.parametrize("clave", CLAVES)
def test_trazabilidad_de_cifras(clave: str) -> None:
    """No figure is spoken before a card that returned it and cited a source.

    Defect this catches, and it is the easiest one to introduce by hand:
    somebody writes a sentence of the script with a number no tool ever
    returned. That is the anti-hallucination rule of the project broken at the
    exact place where nothing else would see it, and it would ship inside a
    graded deliverable.

    Args:
        clave: Identifier of the conversation replayed.
    """
    _assert_trazabilidad(_eventos_de(clave))


@pytest.mark.parametrize(
    "frase",
    [
        "La morosidad es de 7.15 % este mes.",
        "La morosidad cayo -3.42 % este mes.",
    ],
)
def test_la_trazabilidad_rechaza_una_cifra_que_ninguna_tarjeta_devolvio(
    frase: str,
) -> None:
    """The check turns red on a forged figure and stays green on the honest one.

    Defect this catches: a guard that approves everything. The case above walks
    four scripts that are correct by construction, so on its own it would stay
    green even if the comparison had quietly become empty; the guard is
    therefore run against synthetic answers, one per class of forgery.

    Two forgeries. The invented figure is the obvious one. The inverted sign is
    the cheap one -every digit still matches the card, and the sentence says
    the opposite of the data- and it was not caught: the numeric pattern did
    not read the sign, so ``-3.42`` and ``3.42`` were the same literal to it.

    The honest answer is asserted first, in the same case, so the test cannot
    pass by failing at everything.

    Args:
        frase: Sentence of the answer, forged in one of the two ways.
    """
    _assert_trazabilidad(_guion_sintetico("3.42 %", "La morosidad es de 3.42 %."))

    with pytest.raises(AssertionError):
        _assert_trazabilidad(_guion_sintetico("3.42 %", frase))


def test_la_trazabilidad_rechaza_una_cifra_citada_antes_de_su_tarjeta() -> None:
    """A figure quoted before its card resolves is not traceable either.

    Defect this catches: a provider that speaks first and resolves its card
    afterwards. Every literal of the answer would exist somewhere in the turn,
    so a check written over the constants of the script would pass it, while
    the reader would have read the figure before its source existed -which is
    the difference between citing and claiming.
    """
    guion = _guion_sintetico("3.42 %", "La morosidad es de 3.42 % este mes.")

    with pytest.raises(AssertionError):
        _assert_trazabilidad(reversed(guion))


def test_el_patron_numerico_lee_el_signo_y_el_separador_de_miles() -> None:
    """A literal keeps its sign, its group separator and its decimal point.

    Defect this catches: a pattern that reads ``1,240`` as two numbers, or one
    blind to the sign. Neither would move the traceability of the four
    conversations -both sides of that comparison call this same function, so a
    pattern that splits a figure splits it in the card and in the sentence
    alike- and the second one shipped: a sentence could invert the meaning of a
    figure and still look sourced.

    The dash of a date is not a sign, and that direction is asserted too: it is
    what keeps ``2026-06`` traceable to the row that carries it instead of
    demanding a ``-06`` no card ever returned.
    """
    assert numeros_de("la morosidad es de 3.42 %") == {"3.42"}
    assert numeros_de("la morosidad cayo -3.42 %") == {"-3.42"}
    assert PATRON_NUMERO.findall("1,240 MXN M") == ["1,240"]
    assert PATRON_NUMERO.findall("cierre de 2026-06") == ["2026", "06"]
    assert numeros_de("sin cifras") == frozenset()


# ---------------------------------------------------------------------------
# B-6, and the seam the go/no-go depends on
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "modulo",
    ["backend/app/services/chat_stream.py", "backend/app/api/chat.py"],
)
def test_el_transporte_no_conoce_al_guion(modulo: str) -> None:
    """Neither the transport nor the router names the scripted provider.

    Defect this catches: an ``import`` of ``ProveedorGuionizado`` taken as a
    shortcut. The whole point of the seam is that the Gemini provider costs an
    hour and zero lines of contract; a transport that knows which provider is
    behind it turns that hour into a refactor of three modules.

    Args:
        modulo: Path of the module, relative to the repository root.
    """
    fuente = (REPO_ROOT / modulo).read_text(encoding="utf-8")

    assert "guionizado" not in fuente.lower()


def test_un_proveedor_desconocido_no_se_sustituye_en_silencio() -> None:
    """Asking for a provider that does not exist fails instead of falling back.

    Defect this catches: a resolver that returns the default when the name is
    unknown. A deployment with ``CHAT_PROVIDER=gemini`` and no Gemini provider
    would then serve the scripted answers, and the honesty banner of the demo
    would be showing the wrong text with nobody the wiser.
    """
    assert isinstance(obtener_proveedor("guionizado"), ProveedorGuionizado)

    with pytest.raises(ValueError, match="desconocido"):
        obtener_proveedor("inventado")


def test_la_aplicacion_no_arranca_si_el_proveedor_configurado_no_tiene_fabrica(
    minimal_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A ``CHAT_PROVIDER`` the table cannot serve stops the startup, not a turn.

    Defect this catches: settings that accept a name the factory table does not
    declare. Before the guard, ``CHAT_PROVIDER=gemini`` built a healthy looking
    application -``/health`` answered 200 and a Cloud Run revision passed its
    health check- while every ``POST /api/chat`` died as a 500 with an opaque
    body. A misconfiguration has to fail where the deployment sees it, once,
    and not once per reader.

    Args:
        minimal_env: Environment the settings need, and the cache reset.
        monkeypatch: Fixture used to name a provider that has no factory.
    """
    from app.core.config import get_settings
    from app.main import create_app

    monkeypatch.setenv("CHAT_PROVIDER", "gemini")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="desconocido"):
        create_app()


def test_no_hay_dependencia_de_gemini_antes_del_go_no_go() -> None:
    """No provider reaches the network, and no SDK of the model is imported.

    Defect this catches: connecting Gemini on the Friday. It would consume the
    Saturday reserved for the go/no-go and put the graded deliverable at risk,
    and the seam exists precisely so that the decision can be taken late.
    """
    carpeta = REPO_ROOT / "backend" / "app" / "services" / "proveedores"
    prohibidos = re.compile(r"google[-_](genai|adk)|httpx|aiohttp|requests\.")

    for archivo in carpeta.glob("*.py"):
        assert not prohibidos.search(archivo.read_text(encoding="utf-8")), archivo.name


# ---------------------------------------------------------------------------
# The seam between the router and the transport
# ---------------------------------------------------------------------------


def test_el_router_entrega_el_detector_de_desconexion_de_esta_peticion(
    cliente: TestClient,
    token_de: Callable[..., str],
    operativo: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The transport receives the disconnection detector of the live request.

    Defect this catches, and it was measured: replacing
    ``request.is_disconnected`` in the router with a callable that always
    answers ``False`` leaves the whole backend suite green. The cancellation is
    proved inside the transport -with an injected detector, because the ASGI
    client never disconnects- and against uvicorn in the manual capture, so the
    one link nothing asserted was the router handing over the real thing. A
    stream carrying a detector that can never report a disconnection is a Stop
    button that stops the browser and not the server, which is the opposite of
    what this User Story claims.

    Identity is asserted and not shape: the callable has to be the bound
    ``Request.is_disconnected`` itself, and the request it is bound to has to
    be the one that carried this header, so neither a stand-in coroutine nor a
    detector belonging to another request would pass.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
        monkeypatch: Used to put a spy in place of the transport.
    """
    testigo = "us-023-costura"
    capturado: dict[str, Any] = {}

    async def _espia(
        peticion: PeticionChat,
        proveedor: ProveedorDeTokens,
        esta_desconectado: Callable[[], Awaitable[bool]],
        stream_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        # The spy owes the release the real transport owes. The router reserves
        # the slot and hands the identifier down, so standing in for
        # `transmitir` means standing in for its `finally` too; without this the
        # reservation outlives the case and the guard of the cancellation suite
        # reports the next test as the one that leaked.
        try:
            capturado["detector"] = esta_desconectado
            capturado["stream_id"] = stream_id
            yield "event: done\ndata: {}\n\n"
        finally:
            if stream_id is not None:
                chat_stream.liberar(stream_id)

    monkeypatch.setattr(chat_stream, "transmitir", _espia)

    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "morosidad de la cartera"},
        headers={
            **_cabecera(token_de(operativo, Scope.OPERATIVO.value)),
            "X-Testigo": testigo,
        },
    )

    assert respuesta.status_code == 200
    detector: Any = capturado["detector"]
    assert detector.__func__ is Request.is_disconnected
    assert detector.__self__.headers["x-testigo"] == testigo
    # The router reserves a slot before answering and hands the identifier down,
    # so that the registry entry, the closing record and the `done` event all
    # name the same stream. Defect this catches: a router that reserves and then
    # lets `transmitir` mint its own identifier, which leaks the reserved slot
    # -nothing ever releases it- and silently lowers the ceiling by one on every
    # turn until the endpoint answers 429 to everybody.
    assert isinstance(capturado["stream_id"], str)
    assert capturado["stream_id"] != ""


def test_el_router_entrega_el_proveedor_que_nombra_la_configuracion(
    cliente: TestClient,
    token_de: Callable[..., str],
    operativo: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The transport answers with the provider the setting resolved, by identity.

    Defect this catches: a router that builds a provider itself or resolves a
    name of its own. ``CHAT_PROVIDER`` would be a setting the deployment writes
    and nobody reads, and the go/no-go of Gemini -whose whole promise is that
    changing provider costs one variable- would fail at the only link the seam
    cannot cover from the inside. Nothing else asserts it: the neighbouring
    case proves the resolver refuses an unknown name, which says nothing about
    who calls it.

    The configured value is ``gemini`` on purpose. It is legal in the
    vocabulary of ``Settings`` and has no factory behind it, so the assertion
    cannot pass by coinciding with the default the environment already carries;
    the resolver is replaced by a spy, which is also what lets the request
    answer while the configured name is one nothing could build.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
        monkeypatch: Used to put spies in place of the resolver and the
            transport, and to write the setting.
    """
    from app.core.config import get_settings

    centinela = ProveedorGuionizado(retardo_token_ms=0, retardo_herramienta_ms=0)
    nombres: list[str] = []
    capturado: dict[str, Any] = {}

    def _resolver(nombre: str) -> ProveedorDeTokens:
        nombres.append(nombre)
        return centinela

    async def _espia(
        peticion: PeticionChat,
        proveedor: ProveedorDeTokens,
        esta_desconectado: Callable[[], Awaitable[bool]],
        stream_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        # Same debt as the spy above: whoever receives a reserved identifier
        # gives it back.
        try:
            capturado["proveedor"] = proveedor
            yield "event: done\ndata: {}\n\n"
        finally:
            if stream_id is not None:
                chat_stream.liberar(stream_id)

    monkeypatch.setenv("CHAT_PROVIDER", "gemini")
    get_settings.cache_clear()
    monkeypatch.setattr(api_chat, "obtener_proveedor", _resolver)
    monkeypatch.setattr(chat_stream, "transmitir", _espia)

    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "morosidad de la cartera"},
        headers=_cabecera(token_de(operativo, Scope.OPERATIVO.value)),
    )

    assert respuesta.status_code == 200
    assert nombres == ["gemini"]
    assert capturado["proveedor"] is centinela


# ---------------------------------------------------------------------------
# B-7, B-8: the assistant is not open to the internet
# ---------------------------------------------------------------------------


def test_chat_sin_token_devuelve_401(cliente: TestClient) -> None:
    """The anonymous request is refused with the challenge of RFC 6750.

    Defect this catches: mounting the router without its ``Security``
    dependency. The assistant would answer anybody who found the path, and the
    scope guard would be the only thing left standing between the prototype and
    the internet.

    Args:
        cliente: Client bound to the repository double.
    """
    respuesta = cliente.post(RUTA, json={"mensaje": "hola"})

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"].startswith("Bearer")
    assert respuesta.json()["detail"] == ErrorCode.CREDENCIALES_AUSENTES.value


def test_chat_con_scope_fuera_del_vocabulario_devuelve_403(
    cliente: TestClient, token_de: Callable[..., str], operativo: str
) -> None:
    """A session whose role the portal cannot read never reaches the assistant.

    This is the only 403 the endpoint can produce today, and the reason is
    written down rather than assumed. The four roles all reach ``operativo``
    through ``ROLE_HIERARCHY``, so parametrizing over "roles below operativo"
    would parametrize over the empty set and the test could never fail; and a
    token with no ``scope`` claim at all is a 401 and not a 403, which is the
    case below. What is left is a claim carrying a name outside the vocabulary:
    ``parse_scope_claim`` drops it, the granted set comes out empty and the
    comparison fails closed.

    ``administrador`` is that name because it is the misspelling of the fourth
    role recorded as debt 2 of US-015, so it is what a token would realistically
    carry by mistake rather than an invented string.

    Defect this catches: declaring the route with ``scopes=[]``. Every role
    would still pass, so no other assertion of this file would move, and this
    request -a session the portal cannot read- would be served the assistant.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
    """
    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "hola"},
        headers=_cabecera(token_de(operativo, ROL_FUERA_DEL_VOCABULARIO)),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value


def test_chat_sin_reclamacion_de_scope_devuelve_401(
    cliente: TestClient, token_de: Callable[..., str], operativo: str
) -> None:
    """A token with no ``scope`` claim is not a session with no permissions.

    The planning of this User Story asserted a 403 here. It is wrong, and the
    correction is recorded as a test rather than as prose: US-015 decided that
    a token without the claim is malformed, not unprivileged, and
    ``test_auth_dependencias.py::test_token_sin_scope_es_401`` fixes that
    behaviour for every endpoint of the portal.

    Defect this catches: someone "fixing" the assistant to answer 403 here, to
    match the plan. That would make a forged token without the claim look like
    an ordinary permission problem, and the interface would offer the reader a
    role escalation instead of asking them to sign in again.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of signed tokens.
        operativo: Login identifier of a seeded ``operativo``.
    """
    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "hola"},
        headers=_cabecera(token_de(operativo, con_scope=False)),
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == ErrorCode.CREDENCIALES_INVALIDAS.value


def test_el_registro_de_scopes_gobierna_el_chat_como_operativo(
    minimal_env: None,
) -> None:
    """The row that governs ``POST /api/chat`` demands ``operativo`` and is current.

    Defect this catches: relaxing the row -to no scope, or to a level every
    session already reaches- while the router keeps its ``Security``
    dependency. The map the interface generates is derived from this table, so
    the assistant would be advertised to roles the endpoint refuses; and a row
    left as ``planificado`` would publish a route that does answer.

    What this case deliberately does **not** assert is that the coverage guard
    approves the application. ``create_app`` calls ``assert_scope_coverage``
    and raises, so comparing its audit against the empty tuple is a comparison
    that can never be false. The guard is exercised against synthetic
    applications in ``permisos/test_scope_coverage.py``, and a route mounted
    without its row shows up here as every client fixture failing to build.

    Args:
        minimal_env: Declared so the environment is in place before ``app`` is
            imported.
    """
    from app.core.permissions import SCOPE_REGISTRY, PermissionRule, RouteKey

    regla: PermissionRule = SCOPE_REGISTRY[RouteKey("POST", "/api/chat")]

    assert regla.scopes == (Scope.OPERATIVO,)
    assert regla.status == "vigente"


# ---------------------------------------------------------------------------
# The script picks its conversation the same way every time
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mensaje", "esperada"),
    [
        ("Cual es la morosidad de la cartera hipotecaria este mes", "morosidad"),
        ("Compara el coeficiente de liquidez de los ultimos tres cierres", "liquidez"),
        ("Resumen de exposicion en derivados y su variacion", "derivados"),
        ("Dame la exposicion agregada por contraparte del ultimo trimestre", "permiso"),
        ("una pregunta que no se parece a ninguna", "morosidad"),
        ("¿Cuál es la morosidad de la cartera hipotecaria?", "morosidad"),
    ],
)
def test_seleccion_de_conversacion_es_determinista(mensaje: str, esperada: str) -> None:
    """The same question always replays the same conversation.

    Defect this catches: a choice that depends on the order a mapping happens
    to be iterated in, or one that breaks when the reader types the accent.
    Both would make the two invariants above -legal order and traceability-
    measure a different conversation on every run, which is worse than a red
    test because it is a green one that means nothing.

    Args:
        mensaje: Question as the reader typed it.
        esperada: Conversation the provider must choose.
    """
    from app.services.proveedores.guionizado import seleccionar_conversacion

    peticion = PeticionChat(mensaje=mensaje)

    assert seleccionar_conversacion(peticion) == esperada
    assert seleccionar_conversacion(peticion) == esperada


@pytest.mark.parametrize(
    ("mensaje", "esperada"),
    [
        ("Como va la morosidad este trimestre", "morosidad"),
        ("Cual es el coeficiente de liquidez del trimestre", "liquidez"),
        ("Dame la exposicion en derivados del trimestre", "derivados"),
        ("Quiero informacion desagregada de derivados", "derivados"),
        ("Que riesgo de contraparte tenemos en derivados", "derivados"),
        ("Dame la exposicion agregada por contraparte del ultimo trimestre", "permiso"),
        ("Muestrame la exposicion agregada por contrapartes", "permiso"),
    ],
)
def test_el_fallo_de_permiso_solo_responde_a_una_agregacion_por_contraparte(
    mensaje: str, esperada: str
) -> None:
    """Only a question that really asks for an aggregation by counterparty fails.

    Defect this catches, and it was measured on the shipped script: the words
    of C4 were ``contraparte``, ``agregada`` and ``trimestre``, any one of them
    sufficed, they were compared as substrings and they were read first. So
    "como va la morosidad este trimestre" -the kind of question the empty state
    of the screen invites- was answered with a refusal for lack of permission,
    and "desagregada" matched "agregada" inside a word that means the opposite.
    The client sends the question and nothing else: there is no menu of
    conversations, so those three words governed the whole demo.

    The other direction is in the list because the fix has to keep C4
    reachable. It is the only material US-024 has for its permission notice,
    and a table tuned only to stop hijacking ordinary questions could leave the
    conversation unreachable without a single assertion moving.

    Args:
        mensaje: Question as the reader typed it.
        esperada: Conversation the provider must choose.
    """
    from app.services.proveedores.guionizado import seleccionar_conversacion

    assert seleccionar_conversacion(PeticionChat(mensaje=mensaje)) == esperada


def test_una_clave_desconocida_no_rompe_el_turno() -> None:
    """An undeclared conversation key falls back instead of failing.

    Defect this catches: raising on a key the client made up. The demo picks
    from a menu, and a typo in a query string must not turn the assistant into
    a 500 in front of an evaluator.
    """
    from app.services.proveedores.guionizado import seleccionar_conversacion

    peticion = PeticionChat(mensaje="morosidad", conversacion="no-existe")

    assert seleccionar_conversacion(peticion) == "morosidad"


def test_el_material_de_us_024_esta_completo() -> None:
    """The two typed failures US-024 writes its notice against are in the script.

    Defect this catches: somebody simplifies the script down to the happy path.
    US-024 is forbidden from writing under ``backend/app``, so without these
    two cases its implementer would have to invent a failure or edit a file
    that is not theirs, and the error states of the deliverable would be
    mock-ups instead of captures.
    """
    fallos = {
        clave: [
            evento for evento in _eventos_de(clave) if isinstance(evento, EventoError)
        ]
        for clave in ("derivados", "permiso")
    }

    (recuperable,) = fallos["derivados"]
    assert recuperable.clase == "recuperable"
    assert recuperable.codigo == "silo_no_disponible"
    assert recuperable.paso is PasoDelStream.RECUPERACION_DE_DATOS
    assert recuperable.recuperable is True

    (permiso,) = fallos["permiso"]
    assert permiso.clase == "permiso"
    assert permiso.codigo == "permisos_insuficientes"
    assert permiso.paso is PasoDelStream.VERIFICACION_DE_PERMISO
    assert permiso.recuperable is False


def test_la_conversacion_de_permiso_no_emite_texto() -> None:
    """A turn refused by authorization answers with no prose at all.

    Defect this catches: a script that writes an apology as ``token`` events.
    The interface owns the copy of a refusal -it is bilingual and the code is
    stable- so a sentence produced here would arrive untranslated and would
    also contradict ``done(tokens_emitidos=0)``.
    """
    assert not [
        evento for evento in _eventos_de("permiso") if isinstance(evento, EventoToken)
    ]


def test_los_fragmentos_reconstruyen_el_texto() -> None:
    """Joining every fragment of a block returns the block unchanged.

    Defect this catches: splitting on whitespace and losing it. The interface
    concatenates fragments as they arrive, so a split that drops the spaces
    would render the answer as one long word, and no assertion about order
    would notice.
    """
    texto = "La morosidad es de 3.42 % en el cierre mas reciente."

    assert "".join(fragmentos_de(texto)) == texto


def test_reservar_rechaza_cuando_el_registro_esta_lleno() -> None:
    """The ceiling refuses a turn once every declared slot is taken.

    Defect this catches: a ceiling that is written but never enforced -a
    ``MAXIMO_DE_STREAMS`` read into a log line and nothing else-. Nothing else
    exercises the refusal: the neighbouring cases all run under the ceiling, so
    they would stay green with the ``raise`` deleted, and the endpoint would go
    on accepting streams until the process ran out of descriptors. With
    ``DEMO_LOGIN_ENABLED`` handing out tokens without credentials, that is one
    loop away from anybody.

    The reservations are made through ``reservar`` and not written into the
    registry by hand, so the case also fails if reserving stops registering.
    """
    reservados = [chat_stream.reservar() for _ in range(chat_stream.MAXIMO_DE_STREAMS)]
    try:
        assert len(chat_stream.streams_activos()) == chat_stream.MAXIMO_DE_STREAMS

        with pytest.raises(chat_stream.LimiteDeStreamsError):
            chat_stream.reservar()

        # The refusal must not have taken a slot on its way out: a ceiling that
        # leaks one reservation per refusal lowers itself with every rejected
        # request until it refuses everything forever.
        assert len(chat_stream.streams_activos()) == chat_stream.MAXIMO_DE_STREAMS
    finally:
        for identificador in reservados:
            chat_stream.liberar(identificador)

    assert chat_stream.streams_activos() == {}


def test_una_reserva_abandonada_no_baja_el_techo_para_siempre(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A slot older than its maximum life is reclaimed instead of held forever.

    Defect this catches: a registry that only ever grows because the one path
    that releases a slot is the ``finally`` of a generator somebody has to
    iterate. A reader who opens a stream and drops the socket before the first
    read leaves an entry nothing returns, and after
    ``MAXIMO_DE_STREAMS`` of those the portal answers 429 to everybody with no
    stream actually running.

    The clock is moved and not slept through: the maximum life is five minutes
    and a test that waited for it would be a test nobody runs.
    """
    # The clock is patched by its dotted path and not by reaching into
    # `chat_stream.time`: `time` is an import of that module and not part of its
    # public surface, so mypy strict refuses the attribute. The string form
    # still replaces the very object the registry stamps its entries with, which
    # is the whole point -patching a second import of `time` would freeze a
    # clock nobody reads.
    reloj = "app.services.chat_stream.time.monotonic"
    ahora = time.monotonic()
    monkeypatch.setattr(
        reloj, lambda: ahora - chat_stream.VIDA_MAXIMA_DE_RESERVA_S - 1.0
    )
    viejos = [chat_stream.reservar() for _ in range(chat_stream.MAXIMO_DE_STREAMS)]

    monkeypatch.setattr(reloj, lambda: ahora)
    try:
        # The registry is full of reservations that are all too old to still be
        # running, so the next turn is served instead of refused.
        nuevo = chat_stream.reservar()

        assert nuevo not in viejos
        assert set(chat_stream.streams_activos()) == {nuevo}
    finally:
        for identificador in [*viejos, *chat_stream.streams_activos()]:
            chat_stream.liberar(identificador)

    assert chat_stream.streams_activos() == {}


def test_el_endpoint_responde_429_con_codigo_estable(
    cliente: TestClient,
    token_de: Callable[..., str],
    operativo: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refused turn answers 429 with a code, never with a sentence.

    Defect this catches: a ceiling enforced in the service and swallowed in the
    router -a 500 with a stack, or a 200 with an empty stream-. The bilingual
    interface keys its copy on ``detail.codigo``; a Spanish sentence there is
    untranslatable, and a 500 tells a client that the portal broke when what
    happened is that it is busy.

    ``reservar`` is replaced rather than the registry filled, so the case
    measures what the router does with a refusal and stays independent of the
    number the ceiling happens to carry.
    """

    def negar() -> str:
        message = "lleno"
        raise chat_stream.LimiteDeStreamsError(message)

    monkeypatch.setattr(chat_stream, "reservar", negar)

    respuesta = cliente.post(
        RUTA,
        json={"mensaje": "como va la morosidad"},
        headers=_cabecera(token_de(operativo, Scope.OPERATIVO.value)),
    )

    assert respuesta.status_code == 429
    detalle = respuesta.json()["detail"]
    assert detalle["codigo"] == ChatErrorCode.LIMITE_DE_STREAMS.value
    assert detalle["maximo"] == chat_stream.MAXIMO_DE_STREAMS
    # The refusal names the ceiling and nothing else: no path, no identifier of
    # somebody else's stream, no sentence in one language.
    assert set(detalle) == {"codigo", "maximo"}
