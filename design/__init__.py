"""Design system source of truth for the Karisma Data portal.

This package is the origin of the chain, not a consumer of it. The direction was
inverted on 11-ago-2026: the product's design system decides, and the emitters
export it to the Tailwind ``@theme``, to the typed palette the interface reads,
and to the LaTeX plates the A4 report prints.

``docs/entregables/estilo/uxdoc.sty`` is NOT part of this chain. It styles the
course report and is frozen: A1, A2 and A3 are already graded and compile
against it. A colour swatch of the portal printed inside the report is content,
not style.
"""
