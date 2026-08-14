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
from typing import Final, Literal

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

#: A numeric literal, as the anti-hallucination check counts them. The group
#: separator is part of the literal (``1,240``) and so is the decimal point
#: (``3.42``); a date like ``2026-06`` yields two literals, which is what makes
#: a sentence that names the month traceable to the row that carries it.
PATRON_NUMERO: Final[re.Pattern[str]] = re.compile(r"\d+(?:[.,]\d+)*")

#: One fragment of text: a word with the whitespace that follows it, so that
#: concatenating every fragment of a block returns the block untouched.
PATRON_FRAGMENTO: Final[re.Pattern[str]] = re.compile(r"\S+\s*")


@dataclass(frozen=True)
class FalloGuion:
    """Typed failure a scripted tool call ends in.

    The five fields are exactly the ones ``EventoError`` publishes, because the
    script is where they are decided and US-024 writes its notice against them.

    Attributes:
        paso: Step of the stream that failed.
        clase: Family of the failure.
        codigo: Stable code, never a sentence.
        mensaje_clave: i18n key of the copy the interface shows.
        recuperable: Whether retrying the same turn can succeed.
    """

    paso: PasoDelStream
    clase: Literal["recuperable", "permiso"]
    codigo: str
    mensaje_clave: str
    recuperable: bool


@dataclass(frozen=True)
class PasoGuion:
    """One scripted step: a tool call card or a block of tokens.

    A step is a card when it names a tool and a block of text when it does not.
    No constant of this module sets both, and the replay reads the tool first.

    Attributes:
        herramienta: Technical name of the tool, or ``None`` for a text block.
        id: Identifier of the card, stable across its three states.
        fuente: Catalogue field the card cites. A card that resolves without it
            cannot be quoted by the answer, which is what the anti-hallucination
            check measures.
        resultado: Payload the tool returns when it succeeds.
        fallo: Typed failure when the tool does not succeed.
        texto: Block of prose of a text step, replayed fragment by fragment.
    """

    herramienta: str | None = None
    id: str = ""
    fuente: str | None = None
    resultado: ResultadoTarjeta | None = None
    fallo: FalloGuion | None = None
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
        The literals found, written as they appear.
    """
    return frozenset(PATRON_NUMERO.findall(texto))


_C1_MOROSIDAD: Final[tuple[PasoGuion, ...]] = (
    PasoGuion(
        herramienta="consultar_metrica",
        id="tc-1",
        fuente="catalogo.creditos.morosidad_cartera",
        resultado=ResultadoTarjeta(
            columnas=["Métrica", "Valor"],
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
            columnas=["Métrica", "Valor"],
            filas=[["Coeficiente de cobertura de liquidez", 1.24]],
            cifra="1.24",
        ),
    ),
    PasoGuion(
        herramienta="agregar_serie",
        id="tc-2",
        fuente="catalogo.liquidez.coeficiente_cobertura",
        resultado=ResultadoTarjeta(
            columnas=["Cierre", "Coeficiente"],
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
            columnas=["Métrica", "Valor"],
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
        fallo=FalloGuion(
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
        fallo=FalloGuion(
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

#: Words that pick a conversation when the client sends no key.
#:
#: The order is part of the contract: the question of C4 also names an
#: exposure, so its own words are looked up first. The sets are disjoint
#: anyway, which is what keeps the choice deterministic however the mapping is
#: iterated.
PALABRAS_CLAVE: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "permiso": ("contraparte", "agregada", "trimestre"),
        "liquidez": ("liquidez", "coeficiente", "cobertura"),
        "derivados": ("derivados", "nocional"),
        "morosidad": ("morosidad", "cartera", "hipotecaria"),
    }
)


def seleccionar_conversacion(peticion: PeticionChat) -> str:
    """Choose which conversation answers a question, always the same way.

    Three paths, all deterministic: the key the client sends, a keyword of the
    question, and the minimum path as the fallback. A key that is not declared
    is treated as no key at all instead of as an error, because the client of
    the demo picks from a menu and a typo must not break the turn.

    Args:
        peticion: Question of the reader, already validated.

    Returns:
        The identifier of the conversation to replay.
    """
    clave = peticion.conversacion
    if clave is not None and clave in CONVERSACIONES:
        return clave

    normalizado = _sin_acentos(peticion.mensaje.lower())
    for candidata, palabras in PALABRAS_CLAVE.items():
        if any(palabra in normalizado for palabra in palabras):
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
                transcurrido_ms=_transcurrido_ms(inicio),
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
                    transcurrido_ms=_transcurrido_ms(inicio),
                    resultado=paso.resultado,
                    fuente=paso.fuente,
                )
                continue

            yield EventoToolCall(
                id=paso.id,
                estado=EstadoTarjeta.ERROR,
                herramienta=herramienta,
                etiqueta=etiqueta,
                transcurrido_ms=_transcurrido_ms(inicio),
                fuente=paso.fuente,
                paso=fallo.paso,
            )
            yield EventoError(
                paso=fallo.paso,
                clase=fallo.clase,
                codigo=fallo.codigo,
                mensaje_clave=fallo.mensaje_clave,
                recuperable=fallo.recuperable,
            )
            return


def _transcurrido_ms(inicio: float) -> int:
    """Return the milliseconds elapsed since a monotonic instant.

    Args:
        inicio: Reading of ``time.monotonic`` taken when the card was announced.

    Returns:
        The elapsed time, rounded down to the millisecond.
    """
    return int((time.monotonic() - inicio) * 1000)


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
