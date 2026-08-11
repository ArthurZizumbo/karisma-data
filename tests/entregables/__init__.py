"""Tests for the deliverable generators that live in ``docs/entregables/``.

These suites read versioned text files and never open a database nor a browser.
They run with ``--no-cov`` because the coverage threshold of the project
measures ``backend/app`` and nothing else:

    poetry -P backend run pytest -c backend/pyproject.toml tests/entregables \
        --no-cov -q
"""
