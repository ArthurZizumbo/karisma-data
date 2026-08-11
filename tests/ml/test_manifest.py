"""Tests of the two generated documents: the README and the manifest."""

import json
import re
from pathlib import Path

import pytest

from ml.data.generators import SMOKE_SCALE, write_silos
from ml.data.manifest import (
    GenerationReport,
    render_readme,
    write_manifest,
    write_readme,
)
from ml.data.schemas import SILOS


@pytest.fixture
def informe(tmp_path: Path) -> GenerationReport:
    """Return the report of a real reduced scale run, not a fabricated one.

    The reduced scale is the constant the CLI itself uses, so the suite and
    "--scale smoke" can never drift apart.
    """
    return write_silos(tmp_path, scale=SMOKE_SCALE)


def test_readme_render_is_idempotent(informe: GenerationReport) -> None:
    """Two renders of the same report must be the same string.

    A date.today or any other non deterministic value in the template puts
    git diff --exit-code in red on every run and makes the idempotence gate
    inapplicable, which is the whole reason the document is generated.
    """
    primero = render_readme(informe)
    segundo = render_readme(informe)

    assert primero == segundo
    assert re.search(r"\d{4}-\d{2}-\d{2}\s*$", primero.splitlines()[0]) is None
    assert "Generado por `make data`" in primero
    assert primero.endswith("\n")


def test_readme_counts_match_the_report(informe: GenerationReport) -> None:
    """Prose that drifts from the data is the defect the emission prevents.

    Every measured count has to appear in the rendered text; a hand written
    number would survive a regeneration that changed the file behind it.
    """
    texto = render_readme(informe)

    for silo in informe.silos:
        assert f"`{silo.name}`" in texto
        assert f"{silo.rows:,}".replace(",", " ") in texto
        assert silo.sha256[:16] in texto
    assert f"{informe.total_rows:,}".replace(",", " ") in texto
    assert "sintetico" in texto.lower()

    # A reduced scale run is not allowed to rewrite the versioned document.
    with pytest.raises(ValueError, match="complete run"):
        write_readme(informe, Path("data"))


def test_manifest_is_valid_json_with_every_silo(
    informe: GenerationReport, tmp_path: Path
) -> None:
    """A truncated or renamed manifest leaves the quality view without source.

    The lineage and quality screens read this file instead of rereading the
    parquet files, so a missing key is a blank panel there.
    """
    destino = write_manifest(informe, tmp_path)
    contenido = json.loads(destino.read_text(encoding="utf-8"))

    assert destino.name == "manifest.json"
    assert contenido["semilla"] == informe.seed
    assert contenido["filas_totales"] == informe.total_rows
    assert [silo["nombre"] for silo in contenido["silos"]] == list(SILOS)
    for silo in contenido["silos"]:
        assert silo["sha256"]
        assert silo["filas"] > 0
        assert silo["columnas"] == len(SILOS[silo["nombre"]].fields)
        assert silo["anomalias"]
    assert informe.serie is not None
    assert contenido["serie_tablero"]["filas"] == informe.serie.rows
