"""What a check reads of the source, as facts a language's reader supplies: the vocabulary of those facts, what each
check needs of them, and how well a reader supplies one. A language's data file grades each fact it supplies: exact,
or partial with a note saying what it misses; a fact it does not grade it does not supply. spec refuses a key whose
check needs a fact the language does not supply, and lists one that reads a partial fact as approximate; the rules
module reads the facts.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

EXACT, PARTIAL = "exact", "partial"

FACTS: dict[str, str] = {
    "file": "the source files below the app and the tests, and where each sits",
    "syntax": "a file that does not parse, the line and the message",
    "import": "each import: what it names, the names it takes from it, the line",
    "import.relative": "whether an import is named from the importing file's own folder, and how far it climbs",
    "import.standard": "whether an import names the standard library",
    "comment": "each line comment, its text and line",
    "use": "each name read, as the dotted path the import binding its first name reaches, and how much it bound",
    "call": "each call whose callee an import binds, as that dotted path, with its arguments",
    "method_call": "each call of an attribute no import binds, and whether it is on the object a method is called on",
    "parameter_call": "each call of a method of a function's parameter",
    "callback": "each call of a function's own parameter, whether it is the receiver and whether it is annotated "
                "as a callable",
    "class": "the classes a file defines at the top level: name, bases, line",
    "class.methods": "the methods of a class, each with its return annotation",
    "class.attributes": "the names a class's body and methods assign on it",
    "class.fields": "the names a class's body declares with an annotation, in order",
    "class.exception": "whether a class derives from one of the language's builtin exceptions",
    "class.named": "every name a class's bases and body mention",
    "function": "the functions a file defines, at the top level and in its classes: name, owner, line",
    "function.statements": "how many statements a function's body holds, and how many of them do nothing",
    "function.shape": "a fingerprint of a function's code, the same for two functions that do the same",
    "function.signature": "a function's parameters by kind",
    "function.sole_call": "the one call a function's whole body makes, with its arguments",
    "function.decorated": "whether a function has a decorator",
    "function.returns": "the names a function's return annotation mentions",
    "function.blocks": "each statement of a function's body that opens a block, by its keyword",
    "function.asserts": "whether a function's body asserts",
    "function.mentions": "every name a function's body uses",
    "function.tables": "the tables of cases decorating a test function",
    "union": "a name bound at the top level of a file to names joined as alternatives",
    "module_functions": "the names a file binds at the top level to a function and nothing else",
    "named": "every name a file mentions, annotations included",
}
"""Each fact a check may read, and what it is."""

NEEDS: dict[str, tuple[str, ...]] = {
    "rules": ("import", "import.relative"),
    "libraries": ("import", "import.relative", "import.standard"),
    "forbidden": ("import", "import.relative", "use", "method_call"),
    "tiers": ("import", "import.relative"),
    "types-only": ("call", "use", "module_functions"),
    "cycles": ("import", "import.relative"),
    "package-only": ("import", "import.relative"),
    "scenario-coverage": ("union", "function.tables", "function.blocks", "function.asserts", "function.mentions"),
    "no-comments": ("comment",),
    "stand-ins": ("class", "class.methods", "class.attributes", "call", "parameter_call"),
    "closed-tree": ("file",),
    "must-import": ("import", "import.relative", "import.standard", "function.statements"),
    "no-duplicates": ("function", "function.statements", "function.shape"),
    "no-twins": ("class", "class.fields"),
    "dead-code": ("class", "named", "import", "import.relative", "function.statements", "class.exception"),
    "pass-through": ("function", "function.sole_call", "function.signature", "function.decorated"),
    "holds": ("class", "class.methods", "class.exception", "function", "function.returns"),
    "no-callbacks": ("callback",),
    "names": ("class",),
    "built-by": ("class", "call"),
    "private-imports": ("import", "import.relative"),
    "structure": ("file",),
    "test-tree": ("file",),
    "syntax": ("syntax",),
}
"""The facts each check, by its rule id, reads."""


@dataclass(frozen=True)
class Supply:
    """How a language's reader supplies a fact: its grade (EXACT or PARTIAL) and, for a partial one, what it misses."""
    fact: str
    grade: str
    note: str = ""


@dataclass(frozen=True)
class Shortfall:
    """A key whose check needs a fact the language supplies partly or not at all: its address in the profile, the
    fact, and the reader's note on it (None: the fact is not supplied)."""
    address: str
    fact: str
    note: str | None


def shortfalls(address: str, needs: Iterable[str], supplies: Mapping[str, Supply]) -> list[Shortfall]:
    """The facts a key at address needs that the language does not supply exactly, in the order of the needs."""
    return [Shortfall(address, fact, None if fact not in supplies else supplies[fact].note) for fact in needs
            if fact not in supplies or supplies[fact].grade != EXACT]
