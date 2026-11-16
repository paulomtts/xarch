"""What text a question about a file carries: the file's text with what would give the answer away, or name a person,
masked. The module an import of the app's own code names would say the part, and placement would read its answer
there; so each such import has the module it names replaced on the lines the import spans, written as the source
writes it, with any blanks or continued lines between its steps and dots. Then each text the
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
BETWEEN = r"(?:[ \t\x0c]|\\(?:\r\n|\r|\n))*"
"""What the source may write between two steps or dots of a dotted name: blanks, and a line continued."""
RUN = r"[\w.-]+"
"""What `*` stands for in a text the profile says review hides: a run of one or more letters, digits, `_`, `-` and
`.`."""


def own(imported: Import, root: str, also: tuple[str, ...] = ()) -> bool:
    """Whether an import names the app's own code: it is named from the importing file's folder, or its first step is
    root, the app's import name, or one of also, the import names of other apps the text may be written for."""
    return imported.relative or imported.module[:1] in ((root,), *((name,) for name in also))


def _hidden(pattern: str) -> re.Pattern[str]:
    """What a text the profile says review hides matches."""
    return re.compile(RUN.join(re.escape(piece) for piece in pattern.split("*")))


def _dotted(written: str) -> re.Pattern[str]:
    """What the dotted name an import imports from matches as the source may write it: its steps and dots, with
    blanks or a continued line between any two, and no name running on before or after it."""
    tokens = re.findall(r"\.|[^.]+", written)
    return re.compile(r"(?<![\w.])" + BETWEEN.join(re.escape(token) for token in tokens) + r"(?!\w)")


def _hidden_name(found: re.Match[str]) -> str:
    """MASK in place of a dotted name as written, followed by each line break it spans, so that no line moves."""
    return MASK + "".join(re.findall(r"\\(?:\r\n|\r|\n)", found.group()))


def masked(text: str, imports: tuple[Import, ...], root: str, mask: tuple[str, ...] = (), also: tuple[str, ...] = ()) -> str:
    """The text with the module each import of the app's own code names (root, or one of also, being its import name)
    replaced by MASK on the lines the import spans, every e-mail address by PERSON, then each match of a text of mask
    by MASK, in mask's order."""
    lines = list(cut(text))
    for imported in imports:
        last = max(imported.last, imported.line)
        if own(imported, root, also) and imported.written and 0 < imported.line and last <= len(lines):
            span = "".join(lines[imported.line - 1:last])
            lines[imported.line - 1:last] = [_dotted(imported.written).sub(_hidden_name, span, count=1)] + [
                "" for _ in range(last - imported.line)]
    result = EMAIL.sub(PERSON, "".join(lines))
    for pattern in mask:
        result = _hidden(pattern).sub(MASK, result)
    return result
