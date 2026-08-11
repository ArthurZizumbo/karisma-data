"""Deterministic seeding for every synthetic data generator of the project.

This module holds the only literal seed of the repository. Every producer asks
for its own substream: with a single global generator, changing the row count
of one silo would shift every draw that comes after it and a silo nobody
touched would change its bytes.
"""

from typing import Final

import numpy as np
from faker import Faker

SEED: Final[int] = 20260720

# One independent substream per producer. The identifier is part of the
# contract: it is what makes ``--only derivados`` write the same bytes as the
# complete run.
STREAM_IDS: Final[dict[str, int]] = {
    "clientes": 0,
    "creditos": 1,
    "liquidez": 2,
    "derivados": 3,
    "anomalias": 4,
}


def seeded_rng(stream: str) -> np.random.Generator:
    """Return the reproducible generator of a named substream.

    Args:
        stream: Key of :data:`STREAM_IDS`.

    Returns:
        A generator seeded from ``[SEED, STREAM_IDS[stream]]``.

    Raises:
        KeyError: If the stream is not declared. Declaring it is deliberate:
            an ad hoc name would silently create an undocumented byte stream
            that nobody can reproduce on purpose.
    """
    if stream not in STREAM_IDS:
        known = ", ".join(sorted(STREAM_IDS))
        raise KeyError(f"undeclared substream {stream!r}; declared ones are: {known}")
    return np.random.default_rng([SEED, STREAM_IDS[stream]])


def seeded_faker(locale: str = "es_MX") -> Faker:
    """Return a Faker instance whose stream is fixed by :data:`SEED`.

    The instance is seeded through ``seed_instance`` and not through the class
    level ``Faker.seed``: the second one is process wide shared state, so a
    second consumer created later would advance the stream of this one.

    Args:
        locale: Locale of the generated names.

    Returns:
        A Faker instance that yields the same values on every run.
    """
    fake = Faker(locale)
    fake.seed_instance(SEED)
    return fake
