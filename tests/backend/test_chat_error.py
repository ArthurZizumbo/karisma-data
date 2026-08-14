"""The i18n keys the typed error travels with, checked against the catalogues.

What is measured here is the one seam nothing else watches: the backend decides
``mensaje_clave`` and the browser resolves it, and the two halves live in
different languages, in different directories and in different User Stories.
``contratos.spec.ts`` scans the templates of the frontend and finds keys written
as literals inside a ``t('...')`` call; none of these is one. ``idioma.spec.ts``
compares the two catalogues against each other, so a key missing from both is
missing symmetrically and it stays green. A key emitted from Python and absent
from the JSON therefore reaches the reader as its own path -``chat.error.
message.permission`` printed on screen, in Spanish and in English alike- with
the whole suite green on both sides.

Nothing here opens a socket, reads PostgreSQL or builds an application: the
subject is two constants and a mapping, and the catalogues are read from disk as
the text they are.

The second seam is narrower and it is the vocabulary of the refusal itself:
the code that travels in the event is the same one the API publishes in the
``detail`` of its 403, and each end is pinned to its own literal in a different
suite, so nothing compares them to each other.

Why this file carries only these cases: the typed vocabulary of ``paso``,
the ``error``-then-``done`` order and the fields of the two scripted failures
are already pinned by US-023 in ``test_chat_sse.py``
(``test_modelos_rechazan_paso_desconocido``,
``test_un_fallo_del_guion_cierra_el_turno_con_motivo_error`` and
``test_el_material_de_us_024_esta_completo``). Repeating them here would add
assertions that cannot fail on their own, which is the one thing the testing
rule of this repository forbids outright.
"""

import json
import re
from pathlib import Path
from typing import Final

import pytest

from app.core.scopes import ErrorCode
from app.services.chat_stream import CLAVE_MENSAJE_TRANSPORTE
from app.services.proveedores.guionizado import CONVERSACIONES, etiqueta_de

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: The two catalogues the interface ships, by their language code.
CATALOGOS: Final[tuple[str, ...]] = ("es", "en")

#: Shape of a dotted i18n key: at least one dot and no whitespace.
#:
#: The dot is required rather than optional. A pattern that accepted a bare
#: word would take ``error`` -a real top level node of the catalogue- and would
#: not have detected the defect this test declares.
#:
#: The underscore is admitted only after the first segment, because the leaf of
#: a tool label is the technical name of the tool -``chat.toolCall.tool.
#: consultar_metrica``- and that name is snake_case by the contract of the
#: provider. What the pattern still refuses is what it exists to refuse: a
#: sentence, which carries whitespace, and a bare word with no path.
PATRON_CLAVE: Final[re.Pattern[str]] = re.compile(r"^[a-z][A-Za-z]*(\.[A-Za-z_]+)+$")


def _claves_emitibles() -> tuple[str, ...]:
    """Collect every i18n key this backend can put on the wire.

    Four sources and no more: the typed failures of the deterministic script,
    the failure the transport publishes on its own when a provider breaks where
    nobody scripted it, the label of every announced card, and the header of
    every mini-table column.

    The labels and the headers belong here and not in tests of their own. They
    travel the same wire, they are resolved by the same ``t()`` and they fail
    the same way -the reader is shown the route of the key instead of the name
    of the tool or of the column- so leaving them out would have been an
    exemption written into the one check that exists to deny exemptions.

    The headers were the last to arrive, and they arrived because they were the
    one field of this contract that still travelled as prose: with the interface
    in English the card was translated everywhere except its table headers,
    which kept reading "Cierre" and "Coeficiente".

    Returns:
        The keys, sorted, so a parametrised case keeps a stable name.
    """
    claves = {CLAVE_MENSAJE_TRANSPORTE}
    for pasos in CONVERSACIONES.values():
        for paso in pasos:
            if paso.fallo is not None:
                claves.add(paso.fallo.mensaje_clave)
            if paso.herramienta is not None:
                claves.add(etiqueta_de(paso.herramienta))
            if paso.resultado is not None:
                claves.update(paso.resultado.columnas)
    return tuple(sorted(claves))


def _catalogo(idioma: str) -> object:
    """Read one shipped catalogue exactly as the interface bundles it.

    Args:
        idioma: Language code of the catalogue.

    Returns:
        The parsed catalogue, typed as widely as JSON allows: the walk below
        checks every node it descends into, so narrowing it here would only be
        a claim about a file that lives in another directory.
    """
    ruta = REPO_ROOT / "frontend" / "i18n" / "locales" / f"{idioma}.json"
    catalogo: object = json.loads(ruta.read_text(encoding="utf-8"))
    return catalogo


def _resolver(catalogo: object, clave: str) -> object:
    """Walk a dotted key down a catalogue, the way the template does.

    Args:
        catalogo: Parsed catalogue.
        clave: Dotted key.

    Returns:
        The value the key points at, or ``None`` when the path breaks.
    """
    nodo: object = catalogo
    for tramo in clave.split("."):
        if not isinstance(nodo, dict):
            return None
        nodo = nodo.get(tramo)
    return nodo


CLAVES_EMITIBLES: Final[tuple[str, ...]] = _claves_emitibles()


def test_hay_claves_emitibles_que_revisar() -> None:
    """The collection above is not empty, so the two cases below mean something.

    Defect this catches: a refactor that renames ``fallo`` or empties the
    script. Both parametrised tests would then run over nothing and report
    success, which is how a check like this rots without a sound.
    """
    assert len(CLAVES_EMITIBLES) >= 2


@pytest.mark.parametrize("clave", CLAVES_EMITIBLES)
def test_la_clave_del_mensaje_nunca_es_texto_literal(clave: str) -> None:
    """Every emitted message key is a dotted key and not a sentence.

    Defect this catches: somebody writes the Spanish copy straight into
    ``mensaje_clave`` -"No se pudo consultar el silo"- because it is quicker
    than adding two leaves to two catalogues. The interface is bilingual and
    prints this value through ``t()``, so the sentence would reach both
    languages untranslated, and the contract that says the message is a key
    would be broken by the one field it is about.

    Args:
        clave: Key the backend can emit.
    """
    assert PATRON_CLAVE.match(clave) is not None, clave


@pytest.mark.parametrize("idioma", CATALOGOS)
@pytest.mark.parametrize("clave", CLAVES_EMITIBLES)
def test_la_clave_del_mensaje_resuelve_en_los_dos_catalogos(
    clave: str, idioma: str
) -> None:
    """Every emitted message key resolves to real copy in Spanish and English.

    Defect this catches: the backend emits a key that the catalogue does not
    declare, or somebody renames a leaf under ``chat.error.*`` and leaves the
    Python constant pointing at the old path. ``vue-i18n`` then prints the path
    itself, so the reader whose turn just failed is shown
    ``chat.error.message.permission`` where the explanation should have been.
    No frontend test can see it: the key is never written as a literal in a
    template, it arrives over the wire.

    Args:
        clave: Key the backend can emit.
        idioma: Catalogue the key has to resolve in.
    """
    valor = _resolver(_catalogo(idioma), clave)

    assert isinstance(valor, str), f"{idioma}: {clave} no resuelve a una cadena"
    assert valor.strip() != "", f"{idioma}: {clave} resuelve a una cadena vacia"


def test_el_rechazo_del_guion_usa_el_codigo_de_autorizacion_del_portal() -> None:
    """The refusal on the wire carries the code the API already publishes.

    Defect this catches: two vocabularies for the same refusal. Each end is
    pinned to its own literal and nothing compares them -``test_scopes.py``
    writes the five values of ``ErrorCode`` out by hand, and
    ``test_chat_sse.py`` writes the code of the script out by hand-. The day
    authorization renames its code, both of those files are edited together and
    both stay green while the stream keeps emitting the old name: the same
    refusal is ``permisos_insuficientes`` inside the SSE frame and something
    else in the 403 of the endpoint that produced it, and an interface that
    keys copy and screenshots on the code has to learn two spellings of one
    event.

    Comparing sets and not membership also fails on a script emptied of its
    permission failure, which is the way a check over a collection rots without
    a sound.
    """
    codigos: set[str] = set()
    for pasos in CONVERSACIONES.values():
        for paso in pasos:
            if paso.fallo is not None and paso.fallo.clase == "permiso":
                codigos.add(paso.fallo.codigo)

    assert codigos == {ErrorCode.PERMISOS_INSUFICIENTES.value}
