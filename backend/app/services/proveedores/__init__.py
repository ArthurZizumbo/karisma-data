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


def obtener_proveedor(nombre: str) -> ProveedorDeTokens:
    """Resolve the configured provider by name.

    Args:
        nombre: Value of the ``CHAT_PROVIDER`` setting.

    Returns:
        A provider ready to answer one question.

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
    return fabrica()
