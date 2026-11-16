"""Checks of a profile's own, written for the explanation: the example of how a check is written, and of the words no
check xarch has is written with. Their code names the language only by the tokens its data file gives (`%comment%`,
the marker of a line comment, `%extension%`, the ending of a source file, and `%import <dotted> <name>%`, a line that
imports a name from a file of the app, as its `importing` says), so that they hold for any language;
their parts and tiers are those of the smallest profile with a test tier: a part `documents`, a tier `unit` testing
it, and test files named check_*."""
from __future__ import annotations

from xarch.modules.rules.domain.rule import APP, MAY_NOT, TESTS, Condition, Match, OwnCheck, Rule, Saying, Scope

TODO = (Match("text", words=("*TODO*",)),)

WORKED: tuple[OwnCheck, ...] = (
    OwnCheck(Rule("no-todo", Scope(APP, where=(Condition("placed"),)), ("comment",), MAY_NOT, TODO,
                  (Saying("{file} leaves a note for later at line {line}: {text}",
                          "do it now, or write it where the team tracks its work"),), key="checks.no-todo"),
             (("documents/notes%extension%", "%comment% TODO: split this file\n"),),
             (("documents/notes%extension%", "%comment% split by kind\n"),)),
    OwnCheck(Rule("no-todo-in-tests", Scope(TESTS, where=(Condition("tiered"),)), ("comment",), MAY_NOT, TODO,
                  (Saying("a test of the {tier} tier leaves a note for later: {text}",
                          "write the case now, or drop the note"),), key="checks.no-todo-in-tests"),
             (("tests/documents/check_notes%extension%", "%comment% TODO: a case for an empty title\n"),),
             (("tests/documents/check_notes%extension%", "%comment% one case per title\n"),)),
    OwnCheck(Rule("types-stay-types", Scope(APP, "documents", where=(Condition("below", "documents/types"),)),
                  ("import-into-app",), MAY_NOT, (Match("part", words=("documents",)),),
                  (Saying("{file} holds the types of documents, yet imports {target} at line {line}",
                          "{type_only_fix}"),),
                  keep=(Condition("target-placed"), Condition("target-below", "documents/types", negated=True)),
                  key="checks.types-stay-types"),
             (("documents/types/title%extension%", "%import app.documents.rules trim%\n"),),
             (("documents/types/title%extension%", "%import app.documents.types.text Text%\n"),
              ("documents/rules%extension%", "%import app.documents.types.title Title%\n"))),
)
"""The worked checks, the first the example of how a check is written."""
PROFILE = ("xarch: 2\nname: worked\ntesting:\n  files: [check_*%extension%]\n  functions: check_*\ntiers:\n  unit: {}\n"
           "parts:\n  documents:\n    path: documents\n    role: the documents\n    tier: unit\n")
"""The profile the worked checks are written for, without its checks."""
