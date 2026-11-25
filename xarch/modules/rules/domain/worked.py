"""Checks of a profile's own, written for the explanation: the example of how a check is written, and of the words no
check xarch has is written with. Their code names the language only by the tokens its data file gives (`%comment%`,
the marker of a line comment, `%extension%`, the ending of a source file, and `%import <dotted> <name>%`, a line that
imports a name from a file of the app, as its `importing` says, and `%subclass <name> <base>%`, a class that derives
from a base, as its `worked` says), so that they hold for any language;
their parts and tiers are those of the smallest profile with a test tier: a part `documents`, a tier `unit` testing
it, and test files named check_* (the one beside the code, in a profile that says testing.beside)."""
from __future__ import annotations

from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, Match, OwnCheck, Rule
from xarch.profile_values.checks import APP, TESTS, Condition, Saying, Scope

TODO = (Match("text", words=("*TODO*",)),)
SCREENS = ("documents/screens%extension%", "%subclass Screen Reactive%\n")
"""A file whose class derives from a base its file does not define."""

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
    OwnCheck(Rule("no-todo-beside", Scope(TESTS, where=(Condition("beside"),)), ("comment",), MAY_NOT, TODO,
                  (Saying("a test beside the code leaves a note for later: {text}",
                          "write the case now, or drop the note"),), key="checks.no-todo-beside"),
             (("documents/check_notes%extension%", "%comment% TODO: a case for an empty title\n"),),
             (("documents/check_notes%extension%", "%comment% one case per title\n"),)),
    OwnCheck(Rule("types-stay-types", Scope(APP, "documents", where=(Condition("below", "documents/types"),)),
                  ("import-into-app",), MAY_NOT, (Match("part", words=("documents",)),),
                  (Saying("{file} holds the types of documents, yet imports {target} at line {line}",
                          "{type_only_fix}"),),
                  keep=(Condition("target-placed"), Condition("target-below", "documents/types", negated=True)),
                  key="checks.types-stay-types"),
             (("documents/types/title%extension%", "%import app.documents.rules trim%\n"),),
             (("documents/types/title%extension%", "%import app.documents.types.text Text%\n"),
              ("documents/rules%extension%", "%import app.documents.types.title Title%\n"))),
    OwnCheck(Rule("rules-for-the-type-checker", Scope(APP, "documents", where=(Condition("below", "documents/types"),)),
                  ("imported-name",), MAY_NOT, (Match("name", words=("trim",)),),
                  (Saying("{file} imports {name} at line {line} when its code runs: the types of documents name the "
                          "rules only for the type checker",
                          "import {name} only for the type checker, or move what calls it out of documents/types"),),
                  keep=(Condition("takes-a-name"), Condition("type-only", negated=True)),
                  key="checks.rules-for-the-type-checker"),
             (("documents/types/title%extension%", "%import app.documents.rules trim%\n"),),
             (("documents/types/title%extension%", "%import app.documents.types.text Text%\n"),)),
    OwnCheck(Rule("types-stay-types-unless-accepted",
                  Scope(APP, "documents", where=(Condition("below", "documents/types"),)), ("import-into-app",),
                  MAY_NOT, (Match("part", words=("documents",)),),
                  (Saying("{file} holds the types of documents, yet imports {target} at line {line}",
                          "{type_only_fix}"),),
                  keep=(Condition("target-placed"), Condition("target-below", "documents/types", negated=True)),
                  exempt=(Condition("target-accepted"),), key="checks.types-stay-types-unless-accepted"),
             (("documents/types/title%extension%", "%import app.documents.rules trim%\n"),),
             (("documents/types/title%extension%", "%import app.documents.types.text Text%\n"),)),
    OwnCheck(Rule("tests-take-only-fakes", Scope(TESTS, where=(Condition("tiered"),)), ("imported-name",), MAY_NOT,
                  (Match("exist"),),
                  (Saying("a test of the {tier} tier takes {name} from the app at line {line}, and no fake",
                          "build what it needs from a fake"),),
                  keep=(Condition("takes-a-name"),), exempt=(Condition("fake-named"),),
                  key="checks.tests-take-only-fakes"),
             (("tests/documents/check_notes%extension%", "%import app.documents.store Store%\n"),),
             (("tests/documents/check_notes%extension%", "%comment% one case per title\n"),)),
    OwnCheck(Rule("pages-never-reactive", Scope(APP, where=(Condition("placed"),)), ("class",), MAY_NOT, EXISTING,
                  (Saying("{name} in {file} derives from Reactive at line {line}", "build {name} from plain parts"),),
                  keep=(Condition("named", "*Page"), Condition("extends", "Reactive")),
                  key="checks.pages-never-reactive"),
             (SCREENS, ("documents/pages%extension%", "%import app.documents.screens Screen%\n%subclass HomePage Screen%\n")),
             (SCREENS, ("documents/pages%extension%", "%subclass HomePage Plain%\n"))),
)
"""The worked checks, the first the example of how a check is written."""
