"""Permission suite of US-016: vocabulary, coverage guard and 401/403 matrix.

The package marker is not decoration. Without it pytest names this directory's
``conftest.py`` after its basename, the module collides with
``tests/backend/conftest.py`` and the four modules of US-015 that do
``from conftest import MINIMAL_ENV`` end up importing this one instead. The
planning document of US-016 ruled the marker out on the grounds that the four
test module names are unique, which is true and beside the point: the file that
collides is the ``conftest.py``. Verified on 2026-08-12 against pytest 9.1.
"""
