"""What a check reads of the source, as facts a language's reader supplies: the vocabulary of those facts, and how well
a reader supplies one. These are values of the language a profile names, which spec reads from its data file and
rules checks the code with. What each check needs of them is said twice: for a key, in spec's table of keys, which
spec reads when it loads a profile, since it cannot ask rules; and for a rule, by the vocabulary of rules (a kind of
fact and the fields its words read). For a key the engine expands, the two are the same facts, and the wired tests
hold them so. A language's data file
grades each fact it supplies: exact, or partial with a note saying what it misses; a fact it does not grade it does not
supply. A key or a rule that needs a fact the language does not supply is refused, and one that reads a partial fact
is listed as approximate.
"""
from __future__ import annotations

from dataclasses import dataclass

EXACT = "exact"
"""The grade of a fact a reader supplies in full; any other grade supplies it partly."""

PACKAGE_FACT = "file.package"
"""The fact a language supplies, exactly, when its data file gives package_files, and only then; never written under
`supplies`."""

FACTS: dict[str, str] = {
    "file": "the source files below the app and the tests, and where each sits",
    "syntax": "a file that does not parse, the line and the message",
    "import": "each import: what it names, the names it takes from it, the line",
    "import.relative": "whether an import is named from the importing file's own folder, and how far it climbs",
    "import.standard": "whether an import names the standard library",
    "import.resolved": "every import of the app is followed to the place it names, however written",
    "import.mentioned": "whether a file mentions a name an import takes anywhere else, in code or an annotation",
    "comment": "each line comment, its text, its line and where on it it starts and ends, which review cuts before it "
               "sends a text",
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
    "class.types": "the annotation of each field a class declares, as written",
    "class.exception": "whether a class derives from one of the language's builtin exceptions",
    "class.named": "every name a class's bases and body mention",
    "class.immutable": "whether a class is an immutable record, by the marks of the language's data file",
    "class.interface": "whether a class is an interface, by the marks of the language's data file",
    "file.package": "a file stands for the folder that holds it",
    "function": "the functions a file defines, at the top level and in its classes: name, owner, line",
    "function.statements": "how many statements a function's body holds, and how many of them do nothing",
    "function.shape": "a fingerprint of a function's code, the same for two functions that do the same",
    "function.signature": "a function's parameters by kind",
    "function.sole_call": "the one call a function's whole body makes, with its arguments",
    "function.decorated": "whether a function has a decorator",
    "function.forwards": "whether a method only passes its arguments on to one call on what its object holds, and "
                         "that call's callee",
    "function.returns": "the names a function's return annotation mentions",
    "function.blocks": "each statement of a function's body that opens a block, by its keyword",
    "function.expressions": "each expression of a function's body that chooses between values, by its keyword",
    "function.asserts": "whether a function's body asserts",
    "function.mentions": "every name a function's body uses",
    "function.named": "every name a function's definition mentions, its decorators and signature included",
    "function.tables": "the tables of cases decorating a test function",
    "union": "a name bound at the top level of a file to names joined as alternatives",
    "module_functions": "the names a file binds at the top level to a function and nothing else",
    "constant": "the names a file binds at the top level by an assignment, each with the names its statement mentions",
    "named": "every name a file mentions, annotations included",
    "piece": "the functions and classes at the top level of a file and the methods of those classes, each with the "
             "lines it spans",
}
"""Each fact a check, or a review of the code, may read, and what it is."""


@dataclass(frozen=True)
class Supply:
    """How a language's reader supplies a fact: its grade (EXACT, else partly) and, for a partial one, what it misses."""
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
