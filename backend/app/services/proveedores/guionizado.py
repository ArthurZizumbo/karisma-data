"""Deterministic provider of S4: real timing, scripted content, no network.

The four conversations below are the whole material of the prototype. They are
written in typed Python and not in JSON because mypy has to see them and
because the anti-hallucination check is a unit test over these constants: a
figure typed by hand into a sentence, with no card behind it, must turn the
suite red the moment it is written.

Nothing in this module opens a socket. What it reproduces is the *cadence* of a
real answer -a card announced before its data, a tool that takes a moment, text
that arrives in fragments- so that the streaming of the interface is exercised
against something that behaves like the model it will replace.
"""

import asyncio
import re
import time
import unicodedata
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from app.models.chat import (
    EstadoTarjeta,
    EventoChat,
    EventoError,
    EventoToken,
    EventoToolCall,
    PasoDelStream,
    PeticionChat,
    ResultadoTarjeta,
)
from app.utils.reloj import transcurrido_ms

#: Pacing of the replay, in milliseconds.
#:
#: 24 ms per fragment is about forty fragments a second: fast enough to read as
#: a model writing and slow enough to be read. 260 ms per card is what a tool
#: that queries a silo feels like, and it is split into two waits so the card
#: passes through its three states instead of blinking.
#:
#: The pair is also what makes the cancellation evidence of section 1.1
#: reproducible: the card of C1 closes at 260 ms and ``curl --max-time 0.4``
#: cuts around the fifth fragment, which is a real cut -more than zero
#: fragments, far fewer than the thirty of the script- and not a cosmetic one.
RETARDO_TOKEN_MS: Final[int] = 24
RETARDO_HERRAMIENTA_MS: Final[int] = 260

#: Prefix of every readable tool name. The label is a full i18n key and never a
#: sentence, so both locales resolve the same card.
PREFIJO_ETIQUETA: Final[str] = "chat.toolCall.tool."

#: Headers of the mini-tables the script returns, as i18n keys.
#:
#: They used to be Spanish prose in the body of each conversation, and the card
#: printed them verbatim: with the interface in English the whole card was
#: translated except its table headers, which still read "Cierre" and
#: "Coeficiente". Naming them here instead of inline also keeps one header from
#: being spelled two ways across four conversations.
CLAVE_COLUMNA_METRICA: Final[str] = "chat.toolCall.column.metric"
CLAVE_COLUMNA_VALOR: Final[str] = "chat.toolCall.column.value"
CLAVE_COLUMNA_CIERRE: Final[str] = "chat.toolCall.column.close"
CLAVE_COLUMNA_COEFICIENTE: Final[str] = "chat.toolCall.column.coefficient"

#: A numeric literal, as the anti-hallucination check counts them. The sign is
#: part of the literal (``-3.42``), and so are the group separator (``1,240``)
#: and the decimal point (``3.42``). The sign is read because inverting one is
#: the cheapest hallucination anybody can type into a graded deliverable: a
#: pattern blind to it takes ``-3.42`` for the ``3.42`` a card really returned
#: and waves through a sentence that says the opposite of the data.
#:
#: A dash glued to a digit is a separator and not a sign, which is what the
#: lookbehind rules out: a date like ``2026-06`` still yields the two literals
#: ``2026`` and ``06``, both of them carried by the same cell, instead of an
#: invented ``-06`` that no row could ever justify.
PATRON_NUMERO: Final[re.Pattern[str]] = re.compile(r"(?<!\d)[+-]?\d+(?:[.,]\d+)*")

#: One fragment of text: a word with the whitespace that follows it, so that
#: concatenating every fragment of a block returns the block untouched.
PATRON_FRAGMENTO: Final[re.Pattern[str]] = re.compile(r"\S+\s*")

#: A whole word of the question, as the keyword table below compares them.
#: Comparing by substring is what let "desagregada" match "agregada", a word
#: that means the opposite, so the question is cut into words once and the
#: table is read as a set.
PATRON_PALABRA: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class PasoGuion:
    """One scripted step: a tool call card or a block of tokens.

    A step is a card when it names a tool and a block of text when it does not.
    No constant of this module sets both, and the replay reads the tool first.

    ``fallo`` stores the very ``EventoError`` the stream publishes and not a
    copy of its fields. A parallel dataclass used to redeclare the five of them
    and the replay copied them across one by one, so the day the contract grows
    a sixth field the script would have kept publishing five with nothing red:
    the mapping was the only place that had to learn about it, and a mapping
    nobody exercises is not a contract. Holding the event itself makes the two
    impossible to drift apart, and it moves the validation of the script to
    import time -a scripted failure with a code or an i18n key outside its
    pattern now refuses to load the module instead of reaching a reader.

    Attributes:
        herramienta: Technical name of the tool, or ``None`` for a text block.
        id: Identifier of the card, stable across its three states.
        fuente: Catalogue field the card cites. A card that resolves without it
            cannot be quoted by the answer, which is what the anti-hallucination
            check measures.
        resultado: Payload the tool returns when it succeeds.
        fallo: Typed failure event the turn ends with, when the tool does not
            succeed. It is scripted material and therefore read only: the
            transport serializes it and no consumer of this module mutates it.
        texto: Block of prose of a text step, replayed fragment by fragment.
    """

    herramienta: str | None = None
    id: str = ""
    fuente: str | None = None
    resultado: ResultadoTarjeta | None = None
    fallo: EventoError | None = None
    texto: str = ""


def etiqueta_de(herramienta: str) -> str:
    """Return the i18n key of the readable name of a tool.

    Args:
        herramienta: Technical name of the tool.

    Returns:
        The full key the interface resolves, never a sentence.
    """
    return f"{PREFIJO_ETIQUETA}{herramienta}"


def fragmentos_de(texto: str) -> tuple[str, ...]:
    """Split a block of prose into the fragments the stream emits.

    Args:
        texto: Block of prose of a text step.

    Returns:
        One fragment per word, whitespace included, so that joining them back
        returns the block unchanged.
    """
    return tuple(PATRON_FRAGMENTO.findall(texto))


def numeros_de(texto: str) -> frozenset[str]:
    """Collect every numeric literal a piece of text carries.

    Args:
        texto: Any string, a sentence of the answer or a cell of a result.

    Returns:
        The literals found, written as they appear, sign included. The check
        compares strings, so ``-3.42`` and ``3.42`` are two different figures
        and only one of them has a card behind it.
    """
    return frozenset(PATRON_NUMERO.findall(texto))


_C1_MOROSIDAD: Final[tuple[PasoGuion, ...]] = (
    PasoGuion(
        herramienta="consultar_metrica",
        id="tc-1",
        fuente="catalogo.creditos.morosidad_cartera",
        resultado=ResultadoTarjeta(
            columnas=[CLAVE_COLUMNA_METRICA, CLAVE_COLUMNA_VALOR],
            filas=[["Morosidad de la cartera hipotecaria", "3.42 %"]],
            cifra="3.42 %",
        ),
    ),
    PasoGuion(
        texto=(
            "La morosidad de la cartera hipotecaria es de 3.42 % en el cierre "
            "más reciente. La cifra sale del campo "
            "catalogo.creditos.morosidad_cartera del catálogo, no de una "
            "estimación del asistente."
        )
    ),
)

_C2_LIQUIDEZ: Final[tuple[PasoGuion, ...]] = (
    PasoGuion(
        herramienta="consultar_metrica",
        id="tc-1",
        fuente="catalogo.liquidez.coeficiente_cobertura",
        resultado=ResultadoTarjeta(
            columnas=[CLAVE_COLUMNA_METRICA, CLAVE_COLUMNA_VALOR],
            filas=[["Coeficiente de cobertura de liquidez", 1.24]],
            cifra="1.24",
        ),
    ),
    PasoGuion(
        herramienta="agregar_serie",
        id="tc-2",
        fuente="catalogo.liquidez.coeficiente_cobertura",
        resultado=ResultadoTarjeta(
            columnas=[CLAVE_COLUMNA_CIERRE, CLAVE_COLUMNA_COEFICIENTE],
            filas=[["2026-06", 1.28], ["2026-07", 1.31], ["2026-08", 1.24]],
        ),
    ),
    PasoGuion(
        texto=(
            "El coeficiente de cobertura de liquidez cerró en 1.24 en "
            "2026-08, después de 1.31 en 2026-07 y 1.28 en 2026-06. Los "
            "tres cierres vienen de catalogo.liquidez.coeficiente_cobertura."
        )
    ),
)

_C3_DERIVADOS: Final[tuple[PasoGuion, ...]] = (
    PasoGuion(
        herramienta="consultar_metrica",
        id="tc-1",
        fuente="catalogo.derivados.exposicion_nocional",
        resultado=ResultadoTarjeta(
            columnas=[CLAVE_COLUMNA_METRICA, CLAVE_COLUMNA_VALOR],
            filas=[["Exposición nocional vigente", "1,240 MXN M"]],
            cifra="1,240 MXN M",
        ),
    ),
    PasoGuion(
        texto=(
            "La exposición nocional en derivados suma 1,240 MXN M según "
            "catalogo.derivados.exposicion_nocional."
        )
    ),
    PasoGuion(
        herramienta="consultar_catalogo",
        id="tc-2",
        fuente="catalogo.derivados.exposicion_nocional",
        fallo=EventoError(
            paso=PasoDelStream.RECUPERACION_DE_DATOS,
            clase="recuperable",
            codigo="silo_no_disponible",
            mensaje_clave="chat.error.message.recoverable",
            recuperable=True,
        ),
    ),
)

_C4_PERMISO: Final[tuple[PasoGuion, ...]] = (
    PasoGuion(
        herramienta="agregar_serie",
        id="tc-1",
        fallo=EventoError(
            paso=PasoDelStream.VERIFICACION_DE_PERMISO,
            clase="permiso",
            codigo="permisos_insuficientes",
            mensaje_clave="chat.error.message.permission",
            recuperable=False,
        ),
    ),
)

CONVERSACIONES: Final[Mapping[str, tuple[PasoGuion, ...]]] = MappingProxyType(
    {
        "morosidad": _C1_MOROSIDAD,
        "liquidez": _C2_LIQUIDEZ,
        "permiso": _C4_PERMISO,
        "derivados": _C3_DERIVADOS,
    }
)
"""The four deterministic conversations, keyed by their identifier."""

#: Conversation replayed when nothing matches. C1 is the minimum path -one
#: card, one figure, one source- and the one the cancellation capture uses.
CONVERSACION_POR_DEFECTO: Final[str] = "morosidad"

#: Words that pick a conversation when the client sends no key, written as a
#: list of requirements per conversation: a question chooses an entry only
#: when it satisfies every requirement, hitting each one with at least one of
#: its synonyms.
#:
#: The conjunction exists because of C4. Its trigger used to be any one of
#: ``contraparte``, ``agregada`` or ``trimestre``, compared by substring, and
#: the interface sends the question and nothing else -there is no menu of
#: conversations- so those three words were the whole demo. "Como va la
#: morosidad este trimestre", which is what the empty state of the screen
#: invites the reader to type, was answered with a refusal for lack of
#: permission, and "informacion desagregada" matched "agregada" inside a word
#: that means the opposite.
#:
#: The criterion that replaces it: a conversation that ends in a failure of
#: authorization is chosen only when the question really asks for what the
#: reader may not see -an aggregation **and** a counterparty-, and a period of
#: time is nobody's trigger, because every financial question names one. C4
#: stays reachable with the question of section 9.4 of the plan, which is the
#: material US-024 writes its notice against.
PALABRAS_CLAVE: Final[Mapping[str, tuple[frozenset[str], ...]]] = MappingProxyType(
    {
        "permiso": (
            frozenset({"agregada", "agregado", "agregacion", "agregar"}),
            frozenset({"contraparte", "contrapartes"}),
        ),
        "liquidez": (frozenset({"liquidez", "coeficiente", "cobertura"}),),
        "derivados": (frozenset({"derivados", "nocional"}),),
        "morosidad": (frozenset({"morosidad", "cartera", "hipotecaria"}),),
    }
)

#: Conversations in the order they are tried: the most demanding rule first,
#: so a question naming an aggregation by counterparty **and** derivatives is
#: read as the specific case instead of as whichever entry happened to be
#: typed earlier. The order is derived from the table and is no longer a
#: promise about how the table was written, which is what the previous version
#: got wrong. The sort is stable, so entries demanding as much as each other
#: keep the declared order and the choice stays deterministic.
_ORDEN_DE_EVALUACION: Final[tuple[str, ...]] = tuple(
    sorted(PALABRAS_CLAVE, key=lambda clave: -len(PALABRAS_CLAVE[clave]))
)


def seleccionar_conversacion(peticion: PeticionChat) -> str:
    """Choose which conversation answers a question, always the same way.

    Three paths, all deterministic: the key the client sends, the keywords of
    the question, and the minimum path as the fallback. A key that is not
    declared is treated as no key at all instead of as an error, because a
    typo in a query string must not break the turn.

    The keyword path is the one that matters: the interface sends the question
    and nothing else, so it is the only path an evaluator ever walks. It
    compares whole words and demands every requirement of an entry, and both
    rules answer measured behaviour rather than taste -see the table above.

    Args:
        peticion: Question of the reader, already validated.

    Returns:
        The identifier of the conversation to replay.
    """
    clave = peticion.conversacion
    if clave is not None and clave in CONVERSACIONES:
        return clave

    palabras = _palabras_de(peticion.mensaje)
    for candidata in _ORDEN_DE_EVALUACION:
        if all(palabras & requisito for requisito in PALABRAS_CLAVE[candidata]):
            return candidata
    return CONVERSACION_POR_DEFECTO


class ProveedorGuionizado:
    """Deterministic provider: real timing, scripted content, no network."""

    def __init__(
        self,
        retardo_token_ms: int = RETARDO_TOKEN_MS,
        retardo_herramienta_ms: int = RETARDO_HERRAMIENTA_MS,
    ) -> None:
        """Store the pacing used to make the stream legible on screen.

        Args:
            retardo_token_ms: Wait between two fragments of text.
            retardo_herramienta_ms: Time a card takes from announced to
                resolved, split in two so the intermediate state is seen.
        """
        self._retardo_token = retardo_token_ms / 1000
        self._retardo_herramienta = retardo_herramienta_ms / 1000

    async def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
        """Replay the selected conversation, announcing each card before its wait.

        The announcement is yielded before the wait and not after it, which is
        the difference between a screen that shows progress and a screen that
        stays dead for a quarter of a second per card.

        A card that fails ends the conversation: the typed error is the last
        event the provider produces, and the transport closes with ``done``.
        That error is the very object the script declared, yielded as it is
        rather than rebuilt field by field, so no field of the contract can
        exist in the script and be dropped on the way to the wire.

        Args:
            peticion: Question of the reader, already validated.

        Yields:
            The events of the answer, in contract-legal order.
        """
        pasos = CONVERSACIONES[seleccionar_conversacion(peticion)]
        indice = 0

        for paso in pasos:
            herramienta = paso.herramienta
            if herramienta is None:
                for fragmento in fragmentos_de(paso.texto):
                    await asyncio.sleep(self._retardo_token)
                    yield EventoToken(texto=fragmento, indice=indice)
                    indice += 1
                continue

            etiqueta = etiqueta_de(herramienta)
            inicio = time.monotonic()
            yield EventoToolCall(
                id=paso.id,
                estado=EstadoTarjeta.ANUNCIO,
                herramienta=herramienta,
                etiqueta=etiqueta,
                fuente=paso.fuente,
            )

            await asyncio.sleep(self._retardo_herramienta / 2)
            yield EventoToolCall(
                id=paso.id,
                estado=EstadoTarjeta.EJECUCION,
                herramienta=herramienta,
                etiqueta=etiqueta,
                transcurrido_ms=transcurrido_ms(inicio),
                fuente=paso.fuente,
            )

            await asyncio.sleep(self._retardo_herramienta / 2)
            fallo = paso.fallo
            if fallo is None:
                yield EventoToolCall(
                    id=paso.id,
                    estado=EstadoTarjeta.RESULTADO,
                    herramienta=herramienta,
                    etiqueta=etiqueta,
                    transcurrido_ms=transcurrido_ms(inicio),
                    resultado=paso.resultado,
                    fuente=paso.fuente,
                )
                continue

            yield EventoToolCall(
                id=paso.id,
                estado=EstadoTarjeta.ERROR,
                herramienta=herramienta,
                etiqueta=etiqueta,
                transcurrido_ms=transcurrido_ms(inicio),
                fuente=paso.fuente,
                paso=fallo.paso,
            )
            yield fallo
            return


def _palabras_de(texto: str) -> frozenset[str]:
    """Cut a question into the whole words the keyword table compares.

    Args:
        texto: Question as the reader typed it, punctuation and accents
            included.

    Returns:
        The words of the question, lower cased and stripped of diacritics, so
        that the table can be read as a set instead of with substring tests.
    """
    return frozenset(PATRON_PALABRA.findall(_sin_acentos(texto.lower())))


def _sin_acentos(texto: str) -> str:
    """Strip the diacritics of a string, leaving the letters underneath.

    The reader writes "exposicion" with an accent and the keyword table stores
    it without one: without this, the choice of conversation would depend on
    the keyboard.

    Args:
        texto: Text to normalize, already lower cased.

    Returns:
        The same text without combining marks.
    """
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(letra for letra in descompuesto if not unicodedata.combining(letra))
