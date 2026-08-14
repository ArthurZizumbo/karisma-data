"""Filesystem storage with HMAC signed links: the facade S4 actually runs.

The acceptance criterion of the User Story is a download link that expires in
twenty four hours, and in S4 there is no bucket, no credentials and no budget to
spend on a demo. The temptation is to mint a plain path and call it a link, and
then the expiry is never exercised by anything. This class is the alternative:
the deadline travels *inside* the signed material, so a link whose deadline was
edited stops verifying, and a link whose deadline simply passed stops being
served. Those are the two failures the criterion is about, and both are
observable without a network.

The comparison is ``hmac.compare_digest`` and never ``==``. Python compares
strings left to right and returns on the first difference, which leaks how much
of a forged signature was right through the time the answer took; the whole
point of a keyed digest is lost if the check gives that away.

The signature is checked before the deadline on purpose. A link nobody signed
carries an attacker controlled deadline, so reporting that it expired would be
answering a question about a value this portal never issued.
"""

import asyncio
import hashlib
import hmac
import shutil
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final
from uuid import UUID

import structlog

from app.services.almacen import EnlaceCaducado, FirmaInvalida, Reloj

logger = structlog.get_logger()

# Path template of the endpoint that redeems these links. It mirrors the route
# api/export.py mounts, and the suite proves the two agree by requesting a
# minted URL against the real application instead of comparing two literals.
_PLANTILLA_DE_DESCARGA: Final[str] = "/api/export/{job_id}/download?exp={exp}&sig={sig}"

# Directory the produced files are kept in when no other root is given. The
# system temporary directory is not a shortcut: on Cloud Run it is the only
# writable path of the container, and the data directory is mounted read only
# by the compose file, so nothing else would work in both places.
_SUBDIRECTORIO: Final[str] = "karisma-exports"


class AlmacenLocalFirmado:
    """Filesystem storage with HMAC-SHA256 links; the facade used during S4."""

    def __init__(
        self,
        *,
        clave: str,
        ttl_horas: int,
        reloj: Reloj,
        raiz: Path | None = None,
    ) -> None:
        """Bind the storage to its key, its lifetime and its root directory.

        Args:
            clave: HMAC key. It arrives already resolved by ``crear_almacen``,
                which is also where an empty setting is derived from the token
                signing key; this class never reads settings.
            ttl_horas: Lifetime of a minted link, in hours.
            reloj: Clock consulted when a link is redeemed.
            raiz: Directory the files are kept in. Defaults to a folder of the
                system temporary directory.
        """
        self._clave = clave.encode("utf-8")
        self._ttl = timedelta(hours=ttl_horas)
        self._reloj = reloj
        self._raiz = raiz or Path(tempfile.gettempdir()) / _SUBDIRECTORIO

    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str:
        """Persist the produced file and return its opaque object key.

        The move runs in a worker thread. It is filesystem work and the caller
        is the background task of an asynchronous application: doing it inline
        would hold the event loop for as long as the copy takes whenever source
        and destination sit on different devices.

        Args:
            job_id: Identifier of the job that produced the file.
            origen: Path of the file the background task just wrote.
            formato: Output format code, used as the extension of the key.

        Returns:
            The object key, of the form ``<job_id>.<formato>``.
        """
        object_key = f"{job_id}.{formato}"
        await asyncio.to_thread(self._mover, origen, self.ruta_de(object_key))
        return object_key

    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]:
        """Return a time limited download URL and the instant it stops working.

        The returned instant is truncated to the second, because that is the
        precision the signed material carries: promising a microsecond the
        signature cannot express would describe a deadline nothing enforces.

        Args:
            object_key: Key returned by ``guardar``.
            emitido: Instant the lifetime is counted from.

        Returns:
            The relative URL of the download endpoint and its expiry.
        """
        expira = emitido + self._ttl
        marca = int(expira.timestamp())
        url = _PLANTILLA_DE_DESCARGA.format(
            job_id=Path(object_key).stem,
            exp=marca,
            sig=self._digerir(object_key, marca),
        )
        return url, datetime.fromtimestamp(marca, tz=UTC)

    def firmar(self, object_key: str, expira_en: datetime) -> str:
        """Return the hex HMAC over the key and the epoch, which is what expires.

        Args:
            object_key: Key returned by ``guardar``.
            expira_en: Deadline of the link.

        Returns:
            The hex digest carried by the signature parameter of the URL.
        """
        return self._digerir(object_key, int(expira_en.timestamp()))

    def verificar(self, object_key: str, expira_en: int, firma: str) -> None:
        """Raise EnlaceCaducado or FirmaInvalida; constant-time comparison.

        Args:
            object_key: Key the link claims to point at.
            expira_en: Deadline carried by the link, as a Unix timestamp.
            firma: Signature carried by the link.

        Raises:
            FirmaInvalida: If the signature does not match the material.
            EnlaceCaducado: If the signature matches and the deadline passed.
        """
        if not hmac.compare_digest(self._digerir(object_key, expira_en), firma):
            # Neither digest is logged: the expected one is the secret and the
            # received one is what the caller already knows.
            logger.warning("export.enlace.firma_invalida")
            message = "la firma no corresponde al material del enlace"
            raise FirmaInvalida(message)

        if self._reloj.ahora() > datetime.fromtimestamp(expira_en, tz=UTC):
            logger.info("export.enlace.caducado", expira_en=expira_en)
            message = "el enlace firmado ya vencio"
            raise EnlaceCaducado(message)

    def ruta_de(self, object_key: str) -> Path:
        """Return the path of the stored file.

        Args:
            object_key: Key returned by ``guardar``.

        Returns:
            The path inside the root of this storage.
        """
        return self._raiz / object_key

    def _mover(self, origen: Path, destino: Path) -> None:
        """Move the produced file into the root of this storage.

        Args:
            origen: File written by the background task.
            destino: Final path of the file.
        """
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(destino))

    def _digerir(self, object_key: str, exp: int) -> str:
        """Compute the keyed digest of one link.

        Args:
            object_key: Key the link points at.
            exp: Deadline of the link, as a Unix timestamp.

        Returns:
            The hex digest of the key and the deadline joined by a colon.
        """
        material = f"{object_key}:{exp}".encode()
        return hmac.new(self._clave, material, hashlib.sha256).hexdigest()
