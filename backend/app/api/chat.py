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

The one thing this router decides on its own is whether there is room. The
transport declares how many streams a process serves at once and hands out the
slots; the router asks for one before building the response and turns a refusal
into a 429 with a stable code. The check has to live here because a stream that
has already started can no longer answer with a status code, and it has to be a
reservation and not a question because a question leaves an ``await`` between
"there is room" and "the room is mine".
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.responses import StreamingResponse

from app.core.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.scopes import Scope
from app.models.chat import ChatErrorCode, ErrorChat, PeticionChat
from app.models.user import UserOut
from app.services import chat_stream
from app.services.proveedores import obtener_proveedor

router: Final[APIRouter] = APIRouter(prefix="/api/chat", tags=["chat"])

TIPO_DE_MEDIO: Final[str] = "text/event-stream"

#: Headers without which the stream is not a stream.
#:
#: ``X-Accel-Buffering`` is the one that matters in the cloud: an intermediary
#: that buffers the body delivers the whole answer at the end, and the demo of
#: the progressive streaming disappears without a single test noticing.
#:
#: ``no-store`` and not ``no-cache``: the second only forces revalidation, and
#: a store that revalidates has already written the body to disk. This body is
#: authorized by role, so a shared cache holding it is a copy of one reader's
#: answer sitting where another reader's request could be served from.
#:
#: There is no ``Connection`` header here, and its absence is the decision.
#: ``Connection: keep-alive`` is hop-by-hop: HTTP/1.1 already defaults to
#: persistent connections, ASGI owns the transport, and a hop-by-hop header
#: emitted by the application and forwarded by a proxy that should have
#: consumed it is standard material for request smuggling. It bought nothing
#: and it is gone.
CABECERAS_DE_STREAM: Final[Mapping[str, str]] = MappingProxyType(
    {
        "Cache-Control": "no-store",
        "X-Accel-Buffering": "no",
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
        429: {"description": "El portal ya sirve todos los streams que declara"},
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

    Raises:
        HTTPException: 429 when the transport has no free slot. The refusal is
            an ordinary JSON body and not an SSE event for the same reason the
            401 is: the stream has not been opened, so the client has no parser
            mounted yet.
    """
    proveedor = obtener_proveedor(settings.chat_provider)

    # The slot is taken last, once nothing between here and the response can
    # still fail: a reservation dropped on the way out is a slot nobody ever
    # returns.
    try:
        identificador = chat_stream.reservar()
    except chat_stream.LimiteDeStreamsError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=ErrorChat(
                codigo=ChatErrorCode.LIMITE_DE_STREAMS,
                maximo=chat_stream.MAXIMO_DE_STREAMS,
            ).as_detail(),
        ) from error

    return StreamingResponse(
        chat_stream.transmitir(
            peticion,
            proveedor,
            request.is_disconnected,
            identificador,
        ),
        media_type=TIPO_DE_MEDIO,
        headers=CABECERAS_DE_STREAM,
    )
