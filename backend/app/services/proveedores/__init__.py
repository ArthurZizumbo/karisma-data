"""Sources of chat events, all of them behind one Protocol.

The transport resolves a provider by name and never imports one: that is the
whole seam. The day the go/no-go says GO, ``gemini.py`` lands next to this file,
adds one entry to the table below and no other line of the portal changes.

The Protocol declares a single method on purpose. A second one -``cerrar``,
``preparar``- would have to be implemented by every future provider and would
leak the lifecycle of the source into the transport, which already closes what
it consumes.
"""

from collections.abc import AsyncIterator, Callable, Mapping
from types import MappingProxyType
from typing import Final, Protocol

from app.models.chat import EventoChat, PeticionChat
from app.services.proveedores.guionizado import ProveedorGuionizado


class ProveedorDeTokens(Protocol):
    """Source of chat events; the transport does not know which one is behind."""

    def generar(self, peticion: PeticionChat) -> AsyncIterator[EventoChat]:
        """Yield the typed events of one answer, in contract-legal order.

        Args:
            peticion: Question of the reader, already validated.

        Returns:
            The asynchronous iterator of events, which the transport closes.
        """
        ...


_FABRICAS: Final[Mapping[str, Callable[[], ProveedorDeTokens]]] = MappingProxyType(
    {
        "guionizado": ProveedorGuionizado,
    }
)


def _fabrica_de(nombre: str) -> Callable[[], ProveedorDeTokens]:
    """Look up the factory of a provider, or refuse the name.

    Args:
        nombre: Value of the ``CHAT_PROVIDER`` setting.

    Returns:
        The factory that builds that provider.

    Raises:
        ValueError: If the name is not declared. Failing here and not silently
            falling back to a default is deliberate: an environment that asks
            for a provider that does not exist must not serve a different one
            without saying so.
    """
    fabrica = _FABRICAS.get(nombre)
    if fabrica is None:
        declarados = ", ".join(sorted(_FABRICAS))
        message = f"proveedor de chat desconocido: {nombre}; declarados: {declarados}"
        raise ValueError(message)
    return fabrica


def verificar_proveedor_declarado(nombre: str) -> None:
    """Fail at startup when the configured provider has no factory.

    The setting declares the vocabulary the environment may write; this table
    declares what can actually answer a question, and the two drift. Checked
    only per request, that drift is an application that boots healthy, answers
    ``/health`` with a 200 and turns **every** ``POST /api/chat`` into a 500
    with no ``detail.codigo`` -the shape of failure the strict settings of this
    project exist to make impossible. The check lives here and not in
    ``core/config.py`` because the truth it reads is ``_FABRICAS``, and the
    settings module must not import from ``services/``: the layering of this
    backend goes ``api``/``main`` -> ``services`` -> ``core``, never back.

    This closes the gap completely, and it is worth recording why rather than
    leaving the reader to re-derive it. ``create_app`` is the only way an
    application object comes into being -``app = create_app()`` runs at import
    of ``app.main``- and this call sits in it before a single router is
    mounted. So there is no process that serves ``/health`` with a
    ``CHAT_PROVIDER`` this table cannot honour: the import fails, the container
    never becomes ready, and the revision never takes traffic. Deriving the
    ``Literal`` of the setting from this table would be the other way to get
    there, and it is deliberately not taken: the setting is the vocabulary a
    deployment may write and this table is what can answer today, and keeping
    the first wider is what lets the Gemini go/no-go land as one new file plus
    one new entry here.

    Args:
        nombre: Value of the ``CHAT_PROVIDER`` setting.

    Raises:
        ValueError: If the name has no factory behind it.
    """
    _fabrica_de(nombre)


def obtener_proveedor(nombre: str) -> ProveedorDeTokens:
    """Resolve the configured provider by name.

    Args:
        nombre: Value of the ``CHAT_PROVIDER`` setting.

    Returns:
        A provider ready to answer one question.

    Raises:
        ValueError: If the name is not declared, with the same message the
            startup check writes. Reaching this is a defect: the application
            refused to start with that name.
    """
    return _fabrica_de(nombre)()
