"""Data and model layer of the Portal Centralizado de Datos Financieros.

Explicit package and not an implicit namespace: mypy and ruff resolve
``ml.data.schemas`` without extra configuration. The test suite reaches it
through ``pythonpath = [".", ".."]`` of ``backend/pyproject.toml``, whose
paths resolve against the rootdir that ``-c backend/pyproject.toml`` sets.
A bootstrap inside ``tests/ml/conftest.py`` would look like the obvious
alternative and is not one: two conftest files in directories that are not
packages resolve to the same module name and break the whole suite.
"""
