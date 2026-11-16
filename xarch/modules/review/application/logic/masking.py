"""What text a question about a file carries: the file's text with what would give the answer away, or name a person,
masked. The module an import of the app's own code names would say the part, and placement would read its answer
there; so each such import has the module it names, as the source writes it, replaced on its line. Then each text the
profile says review hides (`review.mask`): as written, case counting, `*` standing for a run of one or more letters,
digits, `_`, `-` and `.`."""
from __future__ import annotations

import re

from xarch.kernel.source import Import
from xarch.modules.review.application.logic.lines import lines as cut

MASK = "<masked>"
"""What stands in a masked text for the dotted name an import of the app's own code imports from."""
PERSON = "person@example.test"
"""What stands in a masked text for an e-mail address."""
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN = r"[\w.-]+"
"""What `*` stands for in a text the profile says review hides: a run of one or more letters, digits, `_`, `-` and
`.`."""


def own(imported: Import, root: str) -> bool:
    """Whether an import names the app's own code: it is named from the importing file's folder, or its first step is
    root, the app's import name."""
    return imported.relative or imported.module[:1] == (root,)


def _hidden(pattern: str) -> re.Pattern[str]:
    """What a text the profile says review hides matches."""
    return re.compile(RUN.join(re.escape(piece) for piece in pattern.split("*")))


def masked(text: str, imports: tuple[Import, ...], root: str, mask: tuple[str, ...] = ()) -> str:
    """The text with the module each import of the app's own code names replaced by MASK on the import's line, every
    e-mail address by PERSON, then each match of a text of mask by MASK, in mask's order."""
    lines = list(cut(text))
    for imported in imports:
        if own(imported, root) and imported.written and 0 < imported.line <= len(lines):
            lines[imported.line - 1] = lines[imported.line - 1].replace(imported.written, MASK, 1)
    result = EMAIL.sub(PERSON, "".join(lines))
    for pattern in mask:
        result = _hidden(pattern).sub(MASK, result)
    return result
