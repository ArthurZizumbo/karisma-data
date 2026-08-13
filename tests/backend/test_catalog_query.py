"""The pure half of the catalog search: the tsquery and the query fingerprint.

No database and no client here. Every case below fixes a decision that has a
concrete way of going wrong in production, and most of them look harmless in a
diff: a whitelist written without accents, an ``AND`` instead of an ``OR``, a
lost prefix operator. All three produce a search that returns nothing while the
SQL keeps looking correct.

The last three cases guard the other half of the module that is pure: the
fingerprint the journal records instead of the typed text.
"""

from hashlib import sha256

import pytest

from app.services.catalog_service import MAX_TERMS, build_tsquery, query_fingerprint


def test_tokens_se_normalizan_a_minusculas() -> None:
    """Uppercase input produces the same query as lowercase input.

    Without the fold, ``SALDO`` reaches ``to_tsquery`` as written; the Spanish
    dictionary lowercases anyway, but the prefix operand does not, and the
    comparison of the two forms is what shows it.
    """
    assert build_tsquery("SALDO Vencido") == build_tsquery("saldo vencido")


@pytest.mark.parametrize(
    "consulta",
    ["saldo & vencido", "saldo | vencido", "!saldo", "(saldo)", "saldo:*", "'saldo'"],
)
def test_operadores_de_tsquery_no_sobreviven(consulta: str) -> None:
    """No tsquery operator typed by the user reaches the engine.

    The whitelist is the defence, not an escape. If ``&``, ``!``, ``(`` or
    ``:`` got through, a user typing a parenthesis would make ``to_tsquery``
    raise a syntax error and the endpoint answer 500.

    Args:
        consulta: Text carrying an operator of the tsquery grammar.
    """
    resultado = build_tsquery(consulta)

    cuerpo = resultado.replace(" | ", " ").removesuffix(":*")
    assert not set(cuerpo) & set("&|!():'\"")


def test_ultimo_termino_lleva_prefijo() -> None:
    """Typing forward keeps matching, which is what the prefix operator buys.

    Losing it means "sald" no longer finds "saldo" and the search box stops
    answering until the word is complete.
    """
    assert build_tsquery("saldo venc") == "saldo | venc:*"


def test_terminos_se_unen_con_or() -> None:
    """The terms are combined with OR and never with AND.

    This is the defect that would not look like one: ``AND`` reads as more
    precise and turns every typed sentence -"cuanto debe un cliente de su
    hipoteca"- into zero results, with nothing in the logs to show for it.
    """
    resultado = build_tsquery("cuanto debe un cliente de su hipoteca")

    assert " | " in resultado
    assert "&" not in resultado


def test_tokens_de_un_caracter_se_descartan() -> None:
    """A single letter never becomes a term.

    With the prefix operator, ``a:*`` matches a good part of the catalog and
    the ranking of the real terms drowns in it.
    """
    assert build_tsquery("a saldo") == "saldo:*"
    assert build_tsquery("saldo a") == "saldo:*"


def test_maximo_doce_terminos() -> None:
    """A pasted paragraph does not become a three hundred term tsquery.

    The cap is on the number of terms and not on the length of the string,
    because the cost is in the query plan, not in the parsing.
    """
    resultado = build_tsquery(" ".join(f"palabra{indice}" for indice in range(40)))

    assert resultado.count(" | ") == MAX_TERMS - 1
    assert resultado.endswith(":*")


def test_consulta_sin_tokens_devuelve_cadena_vacia() -> None:
    """A query with nothing usable yields an empty string, not a lone prefix.

    Returning ``":*"`` would make ``to_tsquery`` raise, turning "the user typed
    punctuation" into a 500.
    """
    assert build_tsquery("... !!! ???") == ""
    assert build_tsquery("") == ""


def test_acentos_se_conservan_en_el_token() -> None:
    """An accented word survives whole, because the stemmer needs it whole.

    Written as ``[0-9a-z_]`` the whitelist would split "credito" with an accent
    into "cr" and "dito", and the entry indexed as ``credit`` would stop being
    found. The stemmer normalises the accent, but only if it receives the word.
    """
    assert build_tsquery("crédito") == "crédito:*"
    assert build_tsquery("días de mora") == "días | de | mora:*"


def test_la_huella_es_estable_dentro_del_proceso() -> None:
    """The same text yields the same fingerprint twice in the same process.

    It is the only property the field is read for: the journal has to tell the
    repeated searches of one reader apart. Drawing the salt per call -the
    obvious way to write this and still pass a privacy review- would make every
    record a fresh value, and the field would keep looking correct while
    meaning nothing.
    """
    assert query_fingerprint("saldo vencido") == query_fingerprint("saldo vencido")


def test_textos_distintos_dan_huellas_distintas() -> None:
    """Two different searches never collapse into the same fingerprint.

    A digest of the salt alone, or of the number of terms, satisfies the case
    above and destroys the field: everything typed that day would correlate
    with everything else.
    """
    assert query_fingerprint("saldo vencido") != query_fingerprint("saldo vigente")


def test_la_huella_no_es_el_sha256_desnudo_del_texto() -> None:
    """The value in the journal cannot be recomputed from outside the process.

    This is the case that goes red on a return to ``sha256(raw_query)``, which
    is what the module recorded until the salt was added. SHA-256 is public and
    a search box holds little entropy, so whoever suspects a card number was
    typed hashes it and greps the journal; with the username bound by
    ``structlog.contextvars``, one match names the person and the minute.

    No case fixes the fingerprint of a given string, and none can: the salt is
    drawn at import, so the expected value would differ on the next run.
    """
    sospecha = "4152313412341234"

    assert query_fingerprint(sospecha) != sha256(sospecha.encode("utf-8")).hexdigest()
