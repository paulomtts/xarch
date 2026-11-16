"""The project docs beside the app: the files the architecture declares, each filled from its template.

The architecture file names every doc (`docs: {<path>: {from, note}}`, see profile_v2), so the set of docs,
their order and their text come from it; a template is filled as docs_template says. The docs are not part of the
app's structure: `check` does not require them.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping

from xarch.modules.spec.application.logic.docs_template import FileTypes, fill
from xarch.modules.spec.domain.published import DocFile
from xarch.modules.spec.domain.values import Architecture

DOCS_ROOT = ("docs", "project")
"""Where the project docs go, below the folder holding the app."""


def doc_files(architecture: Architecture, templates: Mapping[str, str], examples: Mapping[str, str] | None = None,
              tier_examples: Mapping[str, str] | None = None, *, file_types: FileTypes) -> Iterator[DocFile]:
    """Every file the architecture declares, in its order, its text filled from its template.

    templates is the text of each template file, by the name the architecture gives it; examples is the text of each
    example's file, by name, and tier_examples the text of each tier's example test, by tier name; file_types what the
    docs say of a quoted file that is not of the language of the app (see docs_template). Raises InvalidTemplate.
    """
    for doc in architecture.docs:
        if doc.source is not None:
            yield DocFile(doc.path, fill(templates[doc.source], architecture, doc.source, examples, tier_examples,
                                         file_types=file_types))
