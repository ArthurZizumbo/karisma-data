"""Storage facade of the export artifacts, and its single point of choice.

Nothing above this package knows whether a finished export lives on a local
filesystem or in a Cloud Storage bucket. The service asks for two things -keep
this file and mint a time limited link to it- and ``crear_almacen`` is the only
function of the backend that reads the storage setting to decide who answers. A
second branch on that setting anywhere else is how this kind of facade rots: the
day the bucket exists, the deployment flips one environment variable, and if the
choice is spread over three modules the flip becomes a refactor. The rule is
checked literally, by counting how many lines of ``backend/app`` name that
setting, so even this paragraph writes around it.

The clock is a protocol for the same reason. The whole value of a link that
expires is that it stops working, and a test that proves it by sleeping for
twenty four hours proves nothing anybody will ever run. With the clock injected
the expiry is exercised by moving the clock: milliseconds, no network, no luck.

Both implementations are imported lazily inside the factory. ``gcs`` needs a
package that is deliberately not installed during S4, and ``local`` needs the
exceptions declared here, so a module level import would either break the
application at start up or close an import cycle.
"""

import hashlib
import hmac
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Protocol, runtime_checkable
from uuid import UUID

from app.core.config import Settings

# Label mixed into the derivation of the signing key. It is domain separation:
# the value derived for export links must be unusable as a token signing key
# even for somebody who holds it, and vice versa.
_ETIQUETA_DE_DERIVACION: Final[bytes] = b"karisma:export:signing-key:v1"


# The two names below are contract, frozen by the plan and consumed by the
# router: renaming them to satisfy the Error suffix convention would rename
# a symbol three modules and the handoff already spell out.
class EnlaceCaducado(Exception):  # noqa: N818
    """The link was signed by this portal, and its deadline already passed."""


class FirmaInvalida(Exception):  # noqa: N818
    """The link does not carry a signature this portal produced."""


class Reloj(Protocol):
    """Source of the current instant, injected so expiry can be tested."""

    def ahora(self) -> datetime:
        """Return the current UTC instant.

        Returns:
            An aware datetime in UTC.
        """
        ...


class RelojDelSistema:
    """The real clock. The only implementation that reaches production."""

    def ahora(self) -> datetime:
        """Return the current UTC instant.

        Returns:
            An aware datetime in UTC, taken from the operating system.
        """
        return datetime.now(UTC)


class AlmacenDeExportaciones(Protocol):
    """Where a finished export is kept and how it is handed to its owner."""

    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str:
        """Persist the produced file and return its opaque object key.

        Args:
            job_id: Identifier of the job that produced the file.
            origen: Path of the file just written by the background task.
            formato: Output format code, used as the extension of the key.

        Returns:
            The object key, which never leaves the server inside a response.
        """
        ...

    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]:
        """Return a time limited download URL and the instant it stops working.

        Args:
            object_key: Key returned by ``guardar``.
            emitido: Instant the lifetime is counted from. It is the moment the
                job finished and not the moment of the poll, so a client that
                keeps polling does not keep renewing a link that should die.

        Returns:
            The URL and the instant it expires.
        """
        ...


@runtime_checkable
class AlmacenServidoPorLaApi(Protocol):
    """Storage whose links are redeemed by this API instead of by a bucket.

    ``AlmacenLocalFirmado`` satisfies it and ``AlmacenGCS`` does not, and that
    is the whole point: the download endpoint exists only for the first kind.
    The service asks for the capability instead of asking which backend is
    configured, so the single point of choice stays single.
    """

    def verificar(self, object_key: str, expira_en: int, firma: str) -> None:
        """Accept the link, or reject it with a typed failure.

        Args:
            object_key: Key the link claims to point at.
            expira_en: Deadline carried by the link, as a Unix timestamp.
            firma: Signature carried by the link.

        Raises:
            FirmaInvalida: If the signature does not match the material.
            EnlaceCaducado: If the signature matches and the deadline passed.
        """
        ...

    def ruta_de(self, object_key: str) -> Path:
        """Return the path of the stored file.

        Args:
            object_key: Key returned by ``guardar``.

        Returns:
            The absolute path the response streams from.
        """
        ...


def derivar_clave_de_firma(jwt_secret_key: str) -> str:
    """Derive the export signing key from the token signing key.

    ``EXPORT_SIGNING_KEY`` has an empty default so that an environment which
    never exports still starts, which is the rule the four settings of this
    User Story obey. Empty cannot mean "sign with nothing": that would make
    every link forgeable by anybody who read the source. It means "derive one",
    and the derivation is a one way HMAC with its own label, so a leaked export
    key does not hand anybody the key that mints access tokens.

    Args:
        jwt_secret_key: HS256 signing key of the access tokens.

    Returns:
        The hex digest used as the HMAC key of the local signed links.
    """
    return hmac.new(
        jwt_secret_key.encode("utf-8"), _ETIQUETA_DE_DERIVACION, hashlib.sha256
    ).hexdigest()


def crear_almacen(
    settings: Settings, reloj: Reloj | None = None
) -> AlmacenDeExportaciones:
    """Single place where the storage setting decides the implementation.

    Args:
        settings: Application settings.
        reloj: Clock used to check expiry. Defaults to the system clock; the
            tests pass their own so the twenty four hours are verified without
            waiting for them.

    Returns:
        The storage the rest of the backend talks to.
    """
    if settings.export_storage_backend == "gcs":
        from app.services.almacen.gcs import AlmacenGCS

        return AlmacenGCS(ttl_horas=settings.export_link_ttl_hours)

    from app.services.almacen.local import AlmacenLocalFirmado

    declarada = settings.export_signing_key.get_secret_value()
    return AlmacenLocalFirmado(
        clave=declarada or derivar_clave_de_firma(settings.jwt_secret_key),
        ttl_horas=settings.export_link_ttl_hours,
        reloj=reloj or RelojDelSistema(),
    )
