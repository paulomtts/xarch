"""How a name is written in a case: split into its words where the case of its letters changes, then joined in one of
the cases a profile may ask for, and filled into a text in place of the placeholder that asks for it ({name:snake},
...). Nothing else splits a name into words, joins words in a case or lists the cases."""
from __future__ import annotations

import re

CASES = ("snake", "kebab", "camel", "pascal")
"""The cases a profile may ask a name to be written in, in the order the format lists them."""
CASED = tuple(f"{{name:{case}}}" for case in CASES)
"""How a profile asks for a name in each of CASES, in the same order: {name:snake}, {name:kebab}, ..."""
_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def _words(name: str) -> tuple[str, ...]:
    """The words of a name, lowercased: a word ends before a capital that follows a lowercase letter or a digit, and
    before the last capital of a run of capitals followed by a lowercase letter (HTTPCheck is http, check); no other
    character ends one."""
    return tuple(word.lower() for word in _BOUNDARY.split(name))


def written(name: str, case: str) -> str:
    """The name written in one of CASES: snake joins its words with an underscore, kebab with a hyphen; camel
    capitalises each word but the first and pascal every word, both joining them with nothing between."""
    found = _words(name)
    if case == "snake":
        return "_".join(found)
    if case == "kebab":
        return "-".join(found)
    capitalised = [word[:1].upper() + word[1:] for word in found]
    return found[0] + "".join(capitalised[1:]) if case == "camel" else "".join(capitalised)


def filled(text: str, name: str) -> str:
    """The text with each placeholder of CASED in it replaced by the name written in that placeholder's case
    (PublishDocument in test_{name:snake}: test_publish_document); anything else in it stays as written."""
    for case, cased in zip(CASES, CASED):
        text = text.replace(cased, written(name, case))
    return text
