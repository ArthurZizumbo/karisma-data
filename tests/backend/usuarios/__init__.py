"""User administration suite of US-018/US-019: permissions, listing and rules.

The package marker is the same one ``tests/backend/permisos/`` carries and for
the same reason: without it pytest names this directory's ``conftest.py`` after
its basename, that module collides with ``tests/backend/conftest.py`` and every
module that does ``from conftest import ...`` ends up importing this one
instead. The uniqueness of the five test module names is true and beside the
point; the file that collides is the ``conftest.py``.
"""
