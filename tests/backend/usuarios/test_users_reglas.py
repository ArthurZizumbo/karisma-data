"""The business rules: self protection, logical delete, idempotence and 422.

The self protection rule is the reason this module exists, and it is tested from
both ends because it has two doors. ``PATCH`` with a lower role and ``DELETE``
are the obvious one; ``PATCH {"disabled": true}`` is the door that the
re-enabling feature opened, and implementing the guard in only one of them
leaves an administrator able to lock themselves out from the other.

The rule has a third door that no body can show: the caller. Authorization is
granted by the ``scope`` claim of a token that was signed before the row
changed, so the last two cases of this module act with a session whose claim
still says ``admin`` over a row that no longer does, which is the only shape in
which a demotion undoes itself.

Everything here runs over HTTP against the real router, the real service and the
real body model. Only the two repositories are doubled, so no assertion depends
on PostgreSQL being up.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.scopes import ErrorCode, Scope
from app.models.user import UserAdminOut, UserErrorCode, UserOut, UserRoleUpdate
from app.services import user_admin_service

from .conftest import ADMIN, OTRO, FakeAdminUserRepository

if TYPE_CHECKING:
    from app.models.user import AppUser

# The three operations of the service that write. The list is exhaustive on
# purpose: a fourth one added without its own guard is the way this defect comes
# back, and the parametrization turns red as soon as the name is added here.
ESCRITURAS: Final[tuple[str, ...]] = (
    "change_role",
    "set_disabled",
    "apply_partial_update",
)


def ruta(user_id: uuid.UUID) -> str:
    """Return the path of one user.

    Args:
        user_id: Primary key of the user.

    Returns:
        The path of the resource.
    """
    return f"/api/users/{user_id}"


def marca(cuerpo: dict[str, Any]) -> datetime:
    """Return the modification stamp of a response body.

    Args:
        cuerpo: Decoded body of an administration response.

    Returns:
        The parsed ``updated_at``.
    """
    return datetime.fromisoformat(cuerpo["updated_at"])


def test_cambiar_el_rol_de_otro_mueve_la_marca_de_modificacion(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """The role is stored and the only audit trail of the screen moves with it.

    Writing the role and forgetting the stamp would leave the column that
    replaced the access log saying the account was never touched.
    """
    antes = cliente_admin.get("/api/users", headers=cabecera_admin).json()
    original = next(fila for fila in antes["items"] if fila["username"] == OTRO)

    respuesta = cliente_admin.patch(
        ruta(id_de(OTRO)),
        json={"role": Scope.OPERATIVO.value},
        headers=cabecera_admin,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["role"] == Scope.OPERATIVO.value
    assert marca(cuerpo) > marca(original)


def test_reasignar_el_mismo_rol_no_mueve_la_marca(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    repositorio_admin_falso: FakeAdminUserRepository,
) -> None:
    """A request that changes nothing is not recorded as an administrative act.

    Without this, opening the dropdown and choosing the role the row already has
    would stamp the account as modified today and the column would stop meaning
    anything.
    """
    antes = cliente_admin.get("/api/users", headers=cabecera_admin).json()
    original = next(fila for fila in antes["items"] if fila["username"] == OTRO)

    respuesta = cliente_admin.patch(
        ruta(id_de(OTRO)), json={"role": original["role"]}, headers=cabecera_admin
    )

    assert respuesta.status_code == 200
    assert marca(respuesta.json()) == marca(original)
    assert "update_role" not in repositorio_admin_falso.llamadas


def test_degradarse_a_si_mismo_da_409_sin_tocar_el_repositorio(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    repositorio_admin_falso: FakeAdminUserRepository,
) -> None:
    """The guard runs before the write, not after it.

    A guard placed after the update demotes the administrator and only then
    reports the conflict, which is the worst of both outcomes.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(ADMIN)), json={"role": Scope.ANALISTA.value}, headers=cabecera_admin
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (UserErrorCode.ADMIN_NO_PUEDE_DEGRADARSE.value)
    assert repositorio_admin_falso.llamadas == []


def test_reafirmarse_admin_a_si_mismo_es_200(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """Sending your own role back is a no-op and not a conflict.

    A guard written as "any PATCH on yourself is 409" reports a clash where
    nothing changes, and the interface would show an error for an action that
    had no effect.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(ADMIN)), json={"role": Scope.ADMIN.value}, headers=cabecera_admin
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["role"] == Scope.ADMIN.value


def test_un_admin_degradado_no_se_reasciende_con_el_token_que_le_quedaba(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    filas_admin: dict[uuid.UUID, UserAdminOut],
    usuarios_semilla: "dict[str, AppUser]",
    repositorio_admin_falso: FakeAdminUserRepository,
) -> None:
    """A demotion the demoted user can undo is not a demotion at all.

    This is the case above with one fact changed: the row no longer says
    ``admin``, while the token signed minutes earlier still does. Deciding the
    no-op from the body -"asking for ``admin`` cannot possibly take ``admin``
    away"- lets that request through, ``change_role`` sees a role that differs
    from the stored one, writes it, and the account is an administrator again
    for good. The window is not the lifetime of the token: it is permanent,
    because the write restores the very role the token claims.
    """
    propio = id_de(ADMIN)
    # The demotion another administrator applied at 10:05, landing on both sides
    # of the double: the row the session is resolved from and the row the
    # administration endpoints serve.
    usuarios_semilla[ADMIN].role = Scope.OPERATIVO.value
    filas_admin[propio] = filas_admin[propio].model_copy(
        update={"role": Scope.OPERATIVO}
    )

    respuesta = cliente_admin.patch(
        ruta(propio), json={"role": Scope.ADMIN.value}, headers=cabecera_admin
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value
    assert "update_role" not in repositorio_admin_falso.llamadas
    assert filas_admin[propio].role is Scope.OPERATIVO


def test_borrarse_a_si_mismo_da_409_y_deja_la_cuenta_activa(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """The administrator cannot close the door from the inside with DELETE."""
    respuesta = cliente_admin.delete(ruta(id_de(ADMIN)), headers=cabecera_admin)

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        UserErrorCode.ADMIN_NO_PUEDE_DESACTIVARSE.value
    )

    listado = cliente_admin.get("/api/users", headers=cabecera_admin).json()
    propia = next(fila for fila in listado["items"] if fila["username"] == ADMIN)
    assert propia["disabled"] is False


def test_desactivarse_por_patch_da_el_mismo_409(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """The second door of the same rule, opened by the re-enabling feature.

    Implementing the guard only in ``DELETE`` leaves ``PATCH {"disabled": true}``
    as a way around it, and the two paths are indistinguishable to the caller.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(ADMIN)), json={"disabled": True}, headers=cabecera_admin
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        UserErrorCode.ADMIN_NO_PUEDE_DESACTIVARSE.value
    )


def test_mezclar_un_cambio_permitido_con_uno_prohibido_da_409_sin_leer_la_fila(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    repositorio_admin_falso: FakeAdminUserRepository,
) -> None:
    """The two guards are evaluated before the first read, not one per operation.

    This is the only body that can mix a change the portal allows -reasserting
    your own role, which is a no-op- with one it forbids. Answering it by
    chaining ``change_role`` and ``set_disabled``, each checking its own guard,
    is the shape the plan described and it reads the row before refusing it.
    The status code would look identical from outside, and the property the
    self protection rule rests on -a refused request never reaches the
    database- would quietly stop holding for the combined body while every
    other test kept passing.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(ADMIN)),
        json={"role": Scope.ADMIN.value, "disabled": True},
        headers=cabecera_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        UserErrorCode.ADMIN_NO_PUEDE_DESACTIVARSE.value
    )
    assert repositorio_admin_falso.llamadas == []


def test_desactivar_es_baja_logica_y_el_usuario_sigue_en_la_lista(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """A physical delete would destroy the audit trail ``db/AGENTS.md`` protects."""
    respuesta = cliente_admin.delete(ruta(id_de(OTRO)), headers=cabecera_admin)

    assert respuesta.status_code == 200
    assert respuesta.json()["disabled"] is True

    listado = cliente_admin.get("/api/users", headers=cabecera_admin).json()
    assert listado["total"] == 7
    fila = next(item for item in listado["items"] if item["username"] == OTRO)
    assert fila["disabled"] is True


def test_desactivar_dos_veces_devuelve_el_mismo_cuerpo(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """``DELETE`` is idempotent, and the idempotence is real and not apparent.

    Treating the second call as a conflict shows an error where the outcome is
    already the desired one; writing again would move the stamp and make two
    identical requests answer two different bodies.
    """
    destino = ruta(id_de(OTRO))

    primera = cliente_admin.delete(destino, headers=cabecera_admin)
    segunda = cliente_admin.delete(destino, headers=cabecera_admin)

    assert (primera.status_code, segunda.status_code) == (200, 200)
    assert primera.json() == segunda.json()


def test_reactivar_por_patch_devuelve_la_cuenta_al_portal(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """Re-enabling travels on the flag, not on a fourth endpoint."""
    destino = ruta(id_de(OTRO))
    cliente_admin.delete(destino, headers=cabecera_admin)

    respuesta = cliente_admin.patch(
        destino, json={"disabled": False}, headers=cabecera_admin
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["disabled"] is False


def test_rol_y_bandera_en_un_solo_cuerpo_se_aplican_los_dos(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """A body carrying both changes ends on the state the caller asked for.

    Applying only the first field and answering 200 would tell the interface
    that a change it never made had succeeded.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(OTRO)),
        json={"role": Scope.DIRECTIVO.value, "disabled": True},
        headers=cabecera_admin,
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["role"], cuerpo["disabled"]) == (Scope.DIRECTIVO.value, True)


@pytest.mark.parametrize(
    ("metodo", "cuerpo"),
    [("PATCH", {"role": Scope.OPERATIVO.value}), ("DELETE", None)],
    ids=["patch", "delete"],
)
def test_usuario_inexistente_da_404_y_no_un_cuerpo_nulo(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    metodo: str,
    cuerpo: dict[str, Any] | None,
) -> None:
    """An absent row is reported, never serialised as a 200 with ``null``."""
    respuesta = cliente_admin.request(
        metodo,
        ruta(uuid.UUID(int=0)),
        json=cuerpo,
        headers=cabecera_admin,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == UserErrorCode.USUARIO_NO_ENCONTRADO.value


def test_cuerpo_vacio_da_422_con_el_codigo_de_sin_cambios(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """An empty body is refused instead of answering 200 without changing anything."""
    respuesta = cliente_admin.patch(ruta(id_de(OTRO)), json={}, headers=cabecera_admin)

    assert respuesta.status_code == 422
    assert UserErrorCode.SIN_CAMBIOS_SOLICITADOS.value in respuesta.text


def test_campo_ajeno_da_422_por_extra_forbid(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """A client that believes the full edition exists is told, not ignored.

    Without ``extra="forbid"`` the request answers 200, the field is dropped and
    nothing on the screen says the rename never happened.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(OTRO)), json={"username": "otro"}, headers=cabecera_admin
    )

    assert respuesta.status_code == 422


def test_la_grafia_prohibida_del_rol_nombra_el_literal_canonico(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """``administrador`` is answered with a message naming ``admin``.

    The spelling was erased from the interface but survives in old clients and
    in hand written requests; the default enum error would not say which literal
    to use.
    """
    respuesta = cliente_admin.patch(
        ruta(id_de(OTRO)), json={"role": "administrador"}, headers=cabecera_admin
    )

    assert respuesta.status_code == 422
    assert "'admin'" in respuesta.text


class _RepositorioQuePierdeLaFila(FakeAdminUserRepository):
    """Double where the row disappears between the read and the write."""

    async def update_role(self, user_id: uuid.UUID, role: Scope) -> UserAdminOut | None:
        """Report that the update matched no row.

        Args:
            user_id: Primary key of the row.
            role: Role that would have been stored.

        Returns:
            ``None``, always.
        """
        self.llamadas.append("update_role")
        return None


@pytest.mark.asyncio
async def test_si_la_fila_desaparece_entre_lectura_y_escritura_hay_404(
    filas_admin: dict[uuid.UUID, UserAdminOut],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """A write that matches nothing is a 404 and not a 200 with a null body.

    Two administrators acting on the same row at once is the reachable version
    of this, and the defect it guards against is the service trusting the
    optional return of the repository.
    """
    repositorio = _RepositorioQuePierdeLaFila(filas_admin)
    # UserAdminOut is a UserOut, so the seeded row is the actor as it stands.
    actor = filas_admin[id_de(ADMIN)]

    with pytest.raises(HTTPException) as excepcion:
        await user_admin_service.change_role(
            repositorio, user_id=id_de(OTRO), role=Scope.OPERATIVO, actor=actor
        )

    assert excepcion.value.status_code == 404
    assert excepcion.value.detail == UserErrorCode.USUARIO_NO_ENCONTRADO.value


async def escribir(
    operacion: str,
    repositorio: FakeAdminUserRepository,
    *,
    user_id: uuid.UUID,
    actor: UserOut,
) -> UserAdminOut:
    """Run one write operation of the service by name.

    The dispatch is written here and not as three near identical tests so that
    the guard is asserted over the whole write surface with one body of prose:
    what is being claimed is a property of every entry point that writes, not a
    behaviour of one of them.

    Args:
        operacion: Name of the operation, one of ``ESCRITURAS``.
        repositorio: Administration double.
        user_id: Primary key of the row the operation acts upon.
        actor: Caller of the operation.

    Returns:
        The row as the operation leaves it, when it is not refused.
    """
    if operacion == "change_role":
        return await user_admin_service.change_role(
            repositorio, user_id=user_id, role=Scope.OPERATIVO, actor=actor
        )
    if operacion == "set_disabled":
        return await user_admin_service.set_disabled(
            repositorio, user_id=user_id, disabled=True, actor=actor
        )
    return await user_admin_service.apply_partial_update(
        repositorio,
        user_id=user_id,
        change=UserRoleUpdate(role=Scope.OPERATIVO),
        actor=actor,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("operacion", ESCRITURAS, ids=list(ESCRITURAS))
async def test_ninguna_escritura_atiende_a_quien_ya_no_es_admin_en_la_fila(
    filas_admin: dict[uuid.UUID, UserAdminOut],
    id_de: Callable[[str], uuid.UUID],
    operacion: str,
) -> None:
    """The stored role authorises a write; the claim of the token only opens it.

    The scope guard of ``core/auth.py`` never reads the row, so a session opened
    while the caller was an administrator keeps arriving here after the role was
    taken away. This analyst is that arrival, and the target is somebody else's
    row so that no self protection rule can refuse the request for the wrong
    reason: without the check at the entry of each write, the three operations
    reach the repository with a permission the portal already revoked.
    """
    repositorio = FakeAdminUserRepository(filas_admin)
    # UserAdminOut is a UserOut, so the seeded row is the actor as it stands.
    actor = filas_admin[id_de(OTRO)]
    assert actor.role is not Scope.ADMIN, "el caso exige un actor sin admin en la fila"

    with pytest.raises(HTTPException) as excepcion:
        await escribir(operacion, repositorio, user_id=id_de(ADMIN), actor=actor)

    assert excepcion.value.status_code == 403
    assert excepcion.value.detail == ErrorCode.PERMISOS_INSUFICIENTES.value
    assert repositorio.llamadas == []
