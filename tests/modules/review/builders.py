"""Files and parts for the review module's tests: a small profile of two parts, and files of every kind found."""
from __future__ import annotations

from xarch.kernel.source import Import, Unparsable
from xarch.modules.review.domain.values import CodeFile, PartText

PARTS = (PartText("domain", "domain/", "Is it an invariant of one of this module's values?", "values"),
         PartText("main", "__main__.py", "", "starts the app"))
BODY = "class Document:\n" + "    title: str = ''\n" * 60
"""A text long enough to be judged."""
OWN = Import(1, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids")
OTHER = Import(2, ("dataclasses",), ("dataclass",), standard=True, written="dataclasses")
HEAD = "from app.kernel.ids import DocumentId\nfrom dataclasses import dataclass\n"


def found(file: str = "app/modules/documents/domain/document.py", text: str = HEAD + BODY, part: str = "domain",
          error: Unparsable | None = None) -> CodeFile:
    """A file of the app in a part, read."""
    return CodeFile(file, part, text, (OWN, OTHER), error)


BROKEN = found("app/modules/documents/domain/broken.py", error=Unparsable(2, "invalid syntax"))
