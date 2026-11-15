"""The project docs beside the app: the files the architecture declares, each filled from its template.

The architecture file names every doc (`docs: {<path>: {from, note}}`, see architecture_file.py), so the set of docs,
their order and their text come from it; a template is filled as docs_template.py says. The docs are not part of the
app's structure: `check` does not require them.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping

from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.values import Architecture

DOCS_ROOT = ("docs", "project")
"""Where the project docs go, below the folder holding the app."""


def doc_files(architecture: Architecture, templates: Mapping[str, str], examples: Mapping[str, str] | None = None,
              tier_examples: Mapping[str, str] | None = None) -> Iterator[tuple[tuple[str, ...], str]]:
    """Yield (path, text) for every file the architecture declares, in its order.

    templates is the text of each template file, by the name the architecture gives it; examples is the text of each
    example's file, by name, and tier_examples the text of each tier's example test, by tier name. Raises
    InvalidTemplate.
    """
    for doc in architecture.docs:
        if doc.source is not None:
            yield doc.path, fill(templates[doc.source], architecture, doc.source, examples, tier_examples)
