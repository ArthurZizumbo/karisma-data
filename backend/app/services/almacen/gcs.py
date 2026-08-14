"""Cloud Storage implementation of the export facade. Written, not executed.

S4 has no GCP project, so this module is complete and dormant: the day the
bucket exists the change is ``EXPORT_STORAGE_BACKEND=gcs`` plus
``poetry install --extras gcs``, not a refactor. That is the entire reason the
facade exists.

``google-cloud-storage`` is deliberately **not** installed during S4, so the
import of ``google.cloud.storage`` happens inside the method that needs a real
client and nowhere else. At module level it would raise ``ModuleNotFoundError``
while ``create_app`` is still importing routers, and the whole API -health probe
included- would stop starting for everybody, exporters or not.

The two collaborators are typed structurally instead of by importing the real
classes under ``TYPE_CHECKING``. The reason is the same absence: mypy resolves
imports in that block too, so naming ``google.cloud.storage`` there would fail
the type gate of a package nobody installed. The protocols below are exactly the
three members this facade uses, which is also what the test double has to
provide.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final, Protocol
from uuid import UUID

import structlog

from app.services.almacen import Reloj, RelojDelSistema

logger = structlog.get_logger()

# Bucket the exports are written to. It is a constant and not a fifth setting on
# purpose: the plan froze four settings for this User Story and none of them may
# make the start up of somebody who never exports fail. The day the Terraform of
# the project creates the bucket, this constant becomes a setting with the same
# safe default, and the handoff records it as the open item it is.
_BUCKET_POR_DEFECTO: Final[str] = "karisma-data-exports"

# Prefix of every object key. It keeps the exports of the portal in one place of
# the bucket, which is what a lifecycle rule will later be attached to -that
# rule is cut number three of the plan and out of scope here-.
_PREFIJO: Final[str] = "exports"

# Version of the signing scheme. V4 is the one that takes a duration and signs
# it, which is what makes the deadline part of the URL instead of a promise.
_VERSION_DE_FIRMA: Final[str] = "v4"


class _Blob(Protocol):
    """The two members of a Cloud Storage blob this facade calls."""

    def upload_from_filename(self, filename: str) -> None:
        """Upload a local file into this blob.

        Args:
            filename: Path of the file to upload.
        """
        ...

    def generate_signed_url(self, *, version: str, expiration: timedelta) -> str:
        """Mint a signed URL for this blob.

        Args:
            version: Signing scheme, ``v4`` for this facade.
            expiration: Lifetime of the URL, counted from the signing.

        Returns:
            The signed URL.
        """
        ...


class _Bucket(Protocol):
    """The single member of a Cloud Storage bucket this facade calls."""

    def blob(self, blob_name: str) -> _Blob:
        """Return a handle of one object of the bucket.

        Args:
            blob_name: Object key inside the bucket.

        Returns:
            The blob handle.
        """
        ...


class _Cliente(Protocol):
    """The single member of a Cloud Storage client this facade calls."""

    def bucket(self, bucket_name: str) -> _Bucket:
        """Return a handle of one bucket.

        Args:
            bucket_name: Name of the bucket.

        Returns:
            The bucket handle.
        """
        ...


class AlmacenGCS:
    """Cloud Storage storage with V4 signed URLs. Not exercised during S4."""

    def __init__(
        self,
        *,
        ttl_horas: int,
        bucket: str = _BUCKET_POR_DEFECTO,
        prefijo: str = _PREFIJO,
        cliente: _Cliente | None = None,
    ) -> None:
        """Bind the storage to its bucket and to the lifetime of its links.

        Args:
            ttl_horas: Lifetime of a minted link, in hours.
            bucket: Name of the bucket the exports are written to.
            prefijo: Prefix of every object key.
            cliente: Already built client. It exists so the construction of the
                signing arguments can be asserted without a project and without
                network; left as ``None``, the real client is built lazily.
        """
        self._ttl = timedelta(hours=ttl_horas)
        self._bucket = bucket
        self._prefijo = prefijo
        self._cliente = cliente
        self._reloj: Reloj = RelojDelSistema()

    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str:
        """Persist the produced file and return its opaque object key.

        Args:
            job_id: Identifier of the job that produced the file.
            origen: Path of the file the background task just wrote.
            formato: Output format code, used as the extension of the key.

        Returns:
            The object key, of the form ``exports/<job_id>.<formato>``.
        """
        object_key = f"{self._prefijo}/{job_id}.{formato}"
        blob = self._blob(object_key)
        await asyncio.to_thread(blob.upload_from_filename, str(origen))
        logger.info("export.almacen.subido", backend="gcs", bucket=self._bucket)
        return object_key

    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]:
        """Return a time limited download URL and the instant it stops working.

        The V4 scheme signs a duration counted from the signing, so the deadline
        of a Cloud Storage link starts when the link is minted and not when the
        job ended. The instant returned here says exactly that instead of
        repeating the one the row keeps, because the value the interface shows
        has to be the one the storage will actually enforce.

        Args:
            object_key: Key returned by ``guardar``.
            emitido: Instant the job finished. Recorded by the caller and not
                used here, for the reason above.

        Returns:
            The signed URL and its expiry.
        """
        url = self._blob(object_key).generate_signed_url(
            version=_VERSION_DE_FIRMA, expiration=self._ttl
        )
        return url, self._reloj.ahora() + self._ttl

    def _blob(self, object_key: str) -> _Blob:
        """Return the handle of one object of the bucket.

        Args:
            object_key: Key inside the bucket.

        Returns:
            The blob handle.
        """
        return self._construir_cliente().bucket(self._bucket).blob(object_key)

    def _construir_cliente(self) -> _Cliente:
        """Return the client, importing the SDK the first time it is needed.

        Returns:
            The injected client, or the default one built from the ambient
            credentials of the runtime.
        """
        if self._cliente is None:
            # The package is absent during S4 by design, so mypy cannot resolve
            # it either; the silencer is scoped to this line and disappears the
            # day the optional extra is installed.
            from google.cloud import storage  # type: ignore[import-not-found]

            self._cliente = storage.Client()
        return self._cliente
