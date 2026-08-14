"""Chat endpoint. It receives, delegates and answers: no logic here.

The route demands ``operativo`` and not "any valid session". The assistant is a
point query wearing another skin: it answers with the same figures the query
endpoint serves, so it cannot be cheaper to reach than the data behind it. The
day a read-only profile joins the portal, the catalogue stays open and the
assistant does not.

An authorization failure lands **before** the stream is opened, so it travels
as a normal JSON body with its ``WWW-Authenticate`` challenge and never as an
SSE event: the client has no parser mounted yet. A failure in the middle of the
stream is the opposite case and belongs to the transport, which publishes it as
``event: error``.

Which provider answers is a setting, not a decision of this module: it resolves
the configured name and hands the result to the transport.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import StreamingResponse

from app.core.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.scopes import Scope
from app.models.chat import PeticionChat
from app.models.user import UserOut
from app.services import chat_stream
from app.services.proveedores import obtener_proveedor

router: Final[APIRouter] = APIRouter(prefix="/api/chat", tags=["chat"])

TIPO_DE_MEDIO: Final[str] = "text/event-stream"

#: Headers without which the stream is not a stream. ``X-Accel-Buffering`` is
#: the one that matters in the cloud: an intermediary that buffers the body
#: delivers the whole answer at the end, and the demo of the progressive
#: streaming disappears without a single test noticing.
CABECERAS_DE_STREAM: Final[Mapping[str, str]] = MappingProxyType(
    {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
)


@router.post(
    "",
    response_class=StreamingResponse,
    summary="Abre el stream SSE de una pregunta al asistente",
    responses={
        200: {"description": "Flujo de eventos tool_call, token, error y done"},
        401: {"description": "Sin sesion valida"},
        403: {"description": "La sesion no alcanza el nivel operativo"},
    },
)
async def transmitir_chat(
    request: Request,
    peticion: PeticionChat,
    _caller: Annotated[UserOut, Security(get_current_user, scopes=[Scope.OPERATIVO])],
    settings: Annotated[Settings, Depends(get_settings)],
) -> StreamingResponse:
    """Open the SSE stream for one question; cancellation follows the client socket.

    Args:
        request: Incoming request. Only its disconnection detector is used, and
            it travels to the transport as a callable so that the cancellation
            can be exercised without a socket.
        peticion: Question of the reader, already validated.
        _caller: Identity resolved by the security dependency. The answer does
            not depend on who asks in S4, so the caller is only the guard.
        settings: Application settings, for the name of the provider.

    Returns:
        The streaming response, with the headers that keep the body from being
        cached or buffered on its way to the browser.
    """
    return StreamingResponse(
        chat_stream.transmitir(
            peticion,
            obtener_proveedor(settings.chat_provider),
            request.is_disconnected,
        ),
        media_type=TIPO_DE_MEDIO,
        headers=CABECERAS_DE_STREAM,
    )
