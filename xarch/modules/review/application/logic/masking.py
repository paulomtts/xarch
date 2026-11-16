"""What text a question about a file carries: the file's text with what would give the answer away, or name a person,
masked. The module an import of the app's own code names would say the part, and placement would read its answer
there; so each such import has the module it names, as the source writes it, replaced on its line."""
from __future__ import annotations

import re

from xarch.kernel.source import Import

MASK = "<masked>"
"""What stands in a masked text for the dotted name an import of the app's own code imports from."""
PERSON = "person@example.test"
"""What stands in a masked text for an e-mail address."""
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def own(imported: Import, root: str) -> bool:
    """Whether an import names the app's own code: it is named from the importing file's folder, or its first step is
    root, the app's import name."""
    return imported.relative or imported.module[:1] == (root,)


def masked(text: str, imports: tuple[Import, ...], root: str) -> str:
    """The text with the module each import of the app's own code names replaced by MASK on the import's line, and
    every e-mail address by PERSON."""
    lines = text.splitlines(keepends=True)
    for imported in imports:
        if own(imported, root) and imported.written and 0 < imported.line <= len(lines):
            lines[imported.line - 1] = lines[imported.line - 1].replace(imported.written, MASK, 1)
    return EMAIL.sub(PERSON, "".join(lines))
