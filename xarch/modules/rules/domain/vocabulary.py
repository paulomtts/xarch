"""The words a check is written in, in one table: the kinds of fact a check reads, with the fields each carries; the
filters, the kinds of target, the quantifiers and the variables of its messages, each with the fields it reads. The
rule reads it to refuse a check that names a word that does not exist or does not apply, the engine to read only what
its checks need, and `xarch profile explain` to say what each word means.

A check reads, in the files of its scope, the facts of its kinds; it keeps those that pass its filters; a kept fact is
a finding when it matches one of its targets (may_not) or none (may_only); a file must reach a target, by a fact of
its own or through the links that lead it to other files (must_reach), and a fact must be reached from a set of root
files (must_be_reached). A finding an exception excuses is dropped; the others are said by the message and fix of the
first case whose filters hold.

A field is what a fact carries: always, or (sometimes) only when the filter named beside it holds of it. A filter, a
kind of target or a variable applies to a kind of fact when the kind carries a field it reads; one that reads no field
applies to every kind. A filter about the file asks of the file a fact is in; a filter about the target asks of what
the fact reaches. Some words apply only to the files of the app (side app) or of the tests (side tests).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from xarch.modules.rules.domain.published import Slot

APP_SIDE, TESTS_SIDE = "app", "tests"
"""The side a word applies to, when it applies to one only: the files of the app, or those of the tests."""

FILE, FACT, TARGET = "file", "fact", "target"
"""What a filter asks about: the file a fact is in, the fact, or what the fact reaches."""

FOLDER, PATTERN, KIND, KEY, NUMBER = "folder", "pattern", "kind", "key", "whole number"
"""What a filter's value is, for a filter that takes one: a folder below the root of the file (a/b), a name pattern
with `*` for any text, the name of a kind of fact, a key of a part, or a whole number."""

NAMES, PACKAGES, PATTERNS, PARTS, PLACES = "dotted names", "package names", "patterns", "parts", "places"
"""What the values of a kind of target are: dotted names (or `.<method>()`), top-level names of packages, patterns with
`*` for any text, names of parts, or places written as an entry of `imports.may` writes a target."""

HIT, KEY_OF_RULE, SCOPE_PART, VALUES, COUNTED, CHAINED = "hit", "key", "scope part", "values", "counted", "chained"
"""What a variable needs of its rule besides fields: a target matched (may_not), the key the rule expands from, a part
its scope names, targets that list values, a quantifier that counts (at_most, at_least), or must_not_reach."""

RENAMED_VARIABLES = {"part": "where"}
"""The variables that were called otherwise: a check that writes the old name is told the new one."""

PART_KEYS = ("built_by",)
"""The keys of a part a filter may name: lists of parts."""



@dataclass(frozen=True)
class Kind:
    """A kind of fact: its name, what one is, the fields it always carries, those it carries only when the filter beside
    each holds, the side whose files have it ("" both), the facts of the source it needs of the language (FACTS of
    capabilities), and those a field needs besides; and what a file does with what it names, as a message says it
    (`{verb}`; "" for a kind that names nothing)."""
    name: str
    meaning: str
    fields: tuple[str, ...]
    sometimes: dict[str, str] = field(default_factory=dict)
    side: str = ""
    needs: tuple[str, ...] = ()
    field_needs: dict[str, tuple[str, ...]] = field(default_factory=dict)
    verb: str = ""

    def carries(self, name: str) -> bool:
        """Whether a fact of the kind can carry the field, always or sometimes."""
        return name in self.fields or name in self.sometimes

    @property
    def links(self) -> bool:
        """Whether a fact of the kind leads somewhere: to the file it reaches, or to the names it mentions."""
        return self.carries("reaches") or self.carries("mentions")


@dataclass(frozen=True)
class Filter:
    """A filter: its name, what is true of what passes it, whether it asks about the file, the fact or what the fact
    reaches, the fields it reads (any one of them carried makes it apply; none: it applies to every kind), the side it
    applies to, what its value is ("" for none), whether it needs a target matched (HIT), and the facts of the source
    (FACTS of capabilities) it needs of the language when written as is: negated, it needs none, since under a
    language without them every fact passes it."""
    name: str
    meaning: str
    about: str
    reads: tuple[str, ...] = ()
    side: str = ""
    value: str = ""
    needs: str = ""
    facts: tuple[str, ...] = ()

    def applies_to(self, kind: Kind) -> bool:
        return not self.reads or any(kind.carries(name) for name in self.reads)


@dataclass(frozen=True)
class TargetKind:
    """A kind of target: its name, when a fact matches it, the fields it compares (any one carried), what its values
    are ("" for a kind that takes none), and the side it applies to."""
    name: str
    meaning: str
    reads: tuple[str, ...] = ()
    values: str = ""
    side: str = ""

    def applies_to(self, kind: Kind) -> bool:
        return not self.reads or any(kind.carries(name) for name in self.reads)


@dataclass(frozen=True)
class Variable:
    """A variable of a message or a fix, written `{name}`: what it prints, the fields of the fact it reads (any one
    carried; none: it reads the file, the profile or the rule), the side it applies to, what it needs of its rule
    besides, and the kinds it applies to when it reads no field but applies to some only."""
    name: str
    meaning: str
    reads: tuple[str, ...] = ()
    side: str = ""
    needs: str = ""
    kinds: tuple[str, ...] = ()

    def applies_to(self, kind: Kind) -> bool:
        if self.kinds:
            return kind.name in self.kinds
        if self.name == "verb":
            return bool(kind.verb)
        return not self.reads or any(kind.carries(name) for name in self.reads)

    def needs_field(self, kind: Kind) -> str:
        """The filter a fact of the kind must pass for the variable to print something, "" for none."""
        if any(name in kind.fields for name in self.reads):
            return ""
        return next((kind.sometimes[name] for name in self.reads if name in kind.sometimes), "")


@dataclass(frozen=True)
class WordFacets:
    """What a word of any category says besides its name and meaning, each "" or empty when its category says none:
    what it asks about (a filter: the file, the fact or what the fact reaches), the side of the files it applies to,
    what its value is, and for a kind its fields (each name, what it is, and the filter under which a fact carries
    it), the facts of the source it needs and its verb."""
    about: str = ""
    side: str = ""
    value: str = ""
    fields: tuple[tuple[str, str, str], ...] = ()
    needs: tuple[str, ...] = ()
    verb: str = ""


@dataclass(frozen=True)
class Quantifier:
    """What a check does with what it keeps: its name, what it means, and whether it reaches through the facts that
    link a file to others (through, through_only, then_through) rather than compare each fact alone."""
    name: str
    meaning: str
    reaches: bool = False


FIELDS: dict[str, str] = {
    "line": "the line it is on, 0 for the file as a whole",
    "path": "the dotted name it names, from the root it starts at: what an import imports, the name a use reads, the "
            "callee of a call",
    "method": "the name of the method called",
    "name": "the name it carries: a name an import takes, a class's or a function's name, a method called, a "
            "parameter",
    "written": "what an import names, as the source writes it",
    "text": "what it says: a comment's text, a syntax error's message",
    "marker": "the marker a comment opens with, as its reader writes it",
    "mentions": "the names it mentions, by their last step",
    "reaches": "the file or package of the app or of the tests it leads to",
    "place": "where what it leads to sits: a part, or a folder of the layout",
    "bound": "how many steps of its path the import that binds it names",
    "function": "the function it is in",
    "forwarded": "the callee a method forwards to",
    "returned": "the attributes it returns of the call's result",
    "relative": "whether an import is named from the importing file's own folder",
    "standard": "whether an import names the standard library",
    "type-only": "whether an import is made only for the type checker, never when the code runs",
    "on-own-object": "whether a method is called on the object itself or on something it holds",
    "top-level": "whether a function is defined at the top level, in no class",
    "forwards": "whether a method only passes its arguments on to one call",
    "exception": "whether a class is an exception",
    "record": "whether a class is a record",
    "immutable": "whether a class is an immutable record",
    "interface": "whether a class is an interface",
    "receiver": "whether a parameter is the object or class a method is called on",
    "annotated-callable": "whether a parameter's annotation says it is a callable",
    "no-statements": "whether no function or method of a file holds a real statement",
    "exceptions-only": "whether a file defines classes, every one an exception, and no top-level function",
    "unreadable": "whether a file could not be read as text at all",
    "doc": "whether a comment is a doc comment",
    "public": "whether the name is for other files to use, as the language decides it",
    "lines": "how many lines a file holds",
    "bases": "the classes a class derives from, however far: each base it names, read through the import that binds "
             "it or as a class of its own file, then the bases of each the project defines, each a dotted name",
}
"""Every field a kind of fact may carry, and what it is."""

_IMPORT = ("import",)
_CLASS_EXCEPTION = ("class", "class.exception")

KINDS: tuple[Kind, ...] = (
    Kind("syntax-error", "a file that does not parse, at the line of its error, or that cannot be read as text at all: "
                         "no other check reads it", ("line", "text", "unreadable"), needs=("syntax",)),
    Kind("file", "the file as a whole, at line 0", ("line", "no-statements", "exceptions-only", "lines"),
         needs=("file",), field_needs={"no-statements": ("function.statements",),
                                       "exceptions-only": (*_CLASS_EXCEPTION, "function"), "lines": ("file.lines",)}),
    Kind("names-mentioned", "every name the file mentions, annotations included, as one fact at line 0", ("line", "mentions"),
         needs=("named",)),
    Kind("import", "each import as written", ("line", "path", "written", "relative", "standard", "type-only"),
         needs=_IMPORT, field_needs={"relative": ("import.relative",), "standard": ("import.standard",),
                                     "type-only": ("import.type_only",)}, verb="import"),
    Kind("imported-name", "each name an import takes, its path what the import names and the name (that alone for "
                          "an import of the whole)",
         ("line", "path", "written", "relative", "standard", "public", "type-only"), {"name": "takes-a-name"},
         needs=_IMPORT, field_needs={"relative": ("import.relative",), "standard": ("import.standard",),
                                     "public": ("public",), "type-only": ("import.type_only",)},
         verb="import"),
    Kind("use", "each name read, called or not, as the dotted path the import binding its first name reaches",
         ("line", "path", "bound"), needs=("use", "import.resolved"), verb="use"),
    Kind("method-call", "each call of a method on something no import names (a variable, a parameter, an attribute)",
         ("line", "method", "name", "on-own-object"), needs=("method_call",), verb="call"),
    Kind("call", "each call whose callee an import binds, as that dotted path", ("line", "path"),
         {"place": "target-placed"}, needs=("call", "import.resolved"), verb="call"),
    Kind("construction", "each call of a class the app defines at the top level of a file, read through the import "
                         "that binds it", ("line", "path", "name", "place", "exception", "record"),
         needs=("call", "class", "import.resolved"),
         field_needs={"exception": _CLASS_EXCEPTION, "record": ("class.record",)}, verb="build"),
    Kind("function-reference", "each name read that is a function the app defines at the top level of a file, other "
                               "than as the callee of a call (passed on, stored)",
         ("line", "path", "reaches", "place"), needs=("use", "call", "module_functions", "import.resolved"),
         verb="reference"),
    Kind("import-into-app", "each import of a file or package of the app, as the file or package it reaches (an "
                            "import that takes a name from a file or package reaches the name's own file when it is "
                            "one, else the file or package it takes the name from)",
         ("line", "reaches"), {"name": "takes-a-name", "place": "target-placed"}, needs=("import", "import.relative"),
         verb="import"),
    Kind("import-into-tests", "each import of a test file of a file of the tests, as the file or package it reaches",
         ("line", "reaches"), side=TESTS_SIDE, needs=("import", "import.relative"), verb="import"),
    Kind("comment", "each comment, its text as written", ("line", "text", "marker", "doc"), needs=("comment",),
         field_needs={"doc": ("comment.doc",)}),
    Kind("class", "each class defined at the top level of a file", ("line", "name", "mentions", "exception", "record",
                                                                    "interface", "immutable", "public", "bases"),
         needs=("class",), field_needs={"mentions": ("class.named",), "exception": _CLASS_EXCEPTION,
                                        "record": ("class.record",),
                                        "interface": ("class.interface",), "immutable": ("class.immutable",),
                                        "public": ("public",), "bases": ("class.bases",)}),
    Kind("function", "each function defined at the top level, or as a method of a class of the top level",
         ("line", "name", "top-level", "forwards", "public"),
         {"forwarded": "forwards", "returned": "returns-an-attribute"}, needs=("function",),
         field_needs={"top-level": ("function.top_level",), "forwards": ("function.forwards",),
                      "forwarded": ("function.forwards",), "returned": ("function.forwards",), "public": ("public",)}),
    Kind("callback", "each call of a function's own parameter by its bare name",
         ("line", "function", "name", "receiver", "annotated-callable"), needs=("callback",), verb="call"),
)
"""Every kind of fact a check reads, in the order a file's facts are worked out."""

FILTERS: tuple[Filter, ...] = (
    Filter("test", "the file is a test: a file below the tests folder whose name `testing.files` matches", FILE,
           side=TESTS_SIDE),
    Filter("tiered", "the file has a tier: a test's own, or for a file of the app the tier whose tests cover its part",
           FILE),
    Filter("placed", "the file lies in a part or in a folder of the layout", FILE, side=APP_SIDE),
    Filter("package-file", "the file is the language's package file, which stands for its folder", FILE,
           facts=("file.package",)),
    Filter("mirrors-a-part", "the test's folder mirrors a part of the app, rather than lying in its tier's `folder`",
           FILE, side=TESTS_SIDE),
    Filter("may-import-everything", "the file's part may import everything (`imports: {may: everything}`)", FILE,
           side=APP_SIDE),
    Filter("below", "the file lies below the folder, a path from the root its side starts at (the app folder, or the "
                    "tests folder for a test)", FILE, value=FOLDER),
    Filter("beside", "the test sits beside the code it tests, below the app folder (testing.beside), and lies below "
                     "no folder of the tests", FILE, side=TESTS_SIDE),
    Filter("relative", "the import is named from the importing file's own folder", FACT, ("relative",)),
    Filter("standard", "the import names the language's standard library", FACT,
           ("standard",)),
    Filter("type-only", "the import is made only for the type checker, never when the code runs, as the "
                        "language's reader says", FACT, ("type-only",)),
    Filter("reserved", "the top-level package the import names is one `reserved` lists", FACT, ("path",)),
    Filter("listed-by-another-part", "the top-level package the import names is in the `imports.libraries` of a part other "
                                     "than the file's", FACT, ("path",), side=APP_SIDE),
    Filter("app-package", "the import names the app's own package by its root (an import written from the top)", FACT,
           ("path",)),
    Filter("own-code", "the import is of the project's own code: relative, or naming the app's or the tests' package",
           FACT, ("path", "relative")),
    Filter("takes-a-name", "the import takes a name from what it imports, rather than the whole of it", FACT,
           ("name",)),
    Filter("on-own-object", "the method is called on the object itself or on something it holds; `not on-own-object` is "
                            "a call on anything else", FACT, ("on-own-object",)),
    Filter("public", "the name the fact carries is public: the language's reader says it is for other files to use",
           FACT, ("public",)),
    Filter("special", "the name the fact carries is one the language reserves for itself", FACT, ("name",)),
    Filter("named", "the name the fact carries matches the pattern, `*` standing for any text", FACT, ("name",),
           value=PATTERN),
    Filter("fake-named", "the name the fact carries is a fake's: one of the starts `fakes.prefix` gives, followed by "
                         "more", FACT, ("name",)),
    Filter("top-level", "the function is defined at the top level of its file, in no class", FACT, ("top-level",)),
    Filter("forwards", "the method only passes its arguments on to one call on what its object holds", FACT,
           ("forwards",)),
    Filter("returns-an-attribute", "the method that forwards returns an attribute of what the call answers", FACT,
           ("returned",)),
    Filter("exception", "the class is an exception: it derives from one of the language's exceptions, or from a class "
                        "of the app that is one, however far", FACT, ("exception",)),
    Filter("extends", "the class derives from a class whose name matches the pattern, `*` standing for any text: one of "
                      "its bases, or a base of a class the project defines that it derives from, however far, each "
                      "read through the import that binds it", FACT, ("bases",), value=PATTERN),
    Filter("record", "the class is a record, as the language's reader decides", FACT, ("record",)),
    Filter("interface", "the class is an interface: the language marks it as one", FACT, ("interface",)),
    Filter("immutable", "the class is an immutable record: one of its bases, or one of its decorators called with the "
                        "keywords written beside it, is a name the language marks immutable records with", FACT,
           ("immutable",)),
    Filter("receiver", "the parameter called is the object or class its method is called on", FACT, ("receiver",)),
    Filter("annotated-callable", "the parameter called is annotated as a callable", FACT, ("annotated-callable",)),
    Filter("unreadable", "the file could not be read as text at all, so it was never parsed", FACT, ("unreadable",)),
    Filter("directive", "the comment is one the language's tools read: a directive after the marker of the comment, "
                        "a shebang on line 1, an encoding declaration on line 1 or 2", FACT, ("text", "marker")),
    Filter("doc", "the comment is a doc comment: one the language keeps its documentation in", FACT, ("doc",)),
    Filter("no-statements", "no function or method of the file holds a real statement: types, constants, interface "
                            "stubs", FACT, ("no-statements",)),
    Filter("exceptions-only", "the file defines classes, every one an exception, and no top-level function", FACT,
           ("exceptions-only",)),
    Filter("longer-than", "the file holds more lines than the number", FACT, ("lines",), value=NUMBER),
    Filter("reported-at-import", "the use is excused because its import line already carries the finding: the import "
                                 "names in full the target the use matched", FACT, ("bound",), needs=HIT),
    Filter("names-restricted", "the file's part may import what the import reaches only for certain names, those a "
                               "pattern of its `imports.may` allows", FACT, ("place",), side=APP_SIDE),
    Filter("of-kind", "the fact is of that kind", FACT, value=KIND),
    Filter("target-placed", "what the fact reaches lies in a part or in a folder of the layout", TARGET, ("place",)),
    Filter("target-inside-part", "what the fact reaches lies below its part's own folder: one of its files, not the "
                                 "part as a whole", TARGET, ("place",), facts=("file.package",)),
    Filter("target-in-own-part", "what the fact reaches lies in the file's own part, in the file's own instance of a "
                                 "repeating folder", TARGET, ("place",), side=APP_SIDE),
    Filter("target-in-own-tier", "what the fact reaches is a file of the app the file's own tier tests", TARGET,
           ("reaches",)),
    Filter("target-test", "what the fact reaches is a test file", TARGET, ("reaches",)),
    Filter("target-below", "what the fact reaches lies below the folder, a path from the root it starts at", TARGET,
           ("reaches",), value=FOLDER),
    Filter("target-allows-under", "the part what the fact reaches lies in allows the file's part under that key "
                                "(built_by)", TARGET, ("place",), side=APP_SIDE, value=KEY),
    Filter("target-accepted", "the file's part accepts the import of what the fact reaches, by an entry of its "
                              "`imports.accepted` naming the file, what it imports and why", TARGET, ("reaches",),
           side=APP_SIDE),
)
"""Every filter, about the file first, then about the fact, then about what it reaches."""

TARGETS: tuple[TargetKind, ...] = (
    TargetKind("exist", "every fact matches: under may_not, each kept fact is a finding by being there"),
    TargetKind("path", "the dotted name the fact names is one of the values or lies below it; a value written "
                       "`.<method>()` matches a method of that name called on anything", ("path", "method"), NAMES),
    TargetKind("package", "the top-level package the fact names is one of the values", ("path",), PACKAGES),
    TargetKind("name", "the name the fact carries matches one of the values", ("name",), PATTERNS),
    TargetKind("text", "what the fact says matches one of the values", ("text",), PATTERNS),
    TargetKind("part", "what the fact reaches lies in one of the parts the values name, in any instance", ("place",),
               PARTS),
    TargetKind("place", "what the fact reaches is reached from the file's place by one of the values, written as "
                        "an entry of `imports.may` writes a target, with no name pattern and no mode", ("place",), PLACES, APP_SIDE),
    TargetKind("permitted", "the profile lets the file import what the fact reaches: for a file of the app what its "
                            "part may import (a name pattern narrowing it to the names it allows); for a test, of the "
                            "app, what the part its folder mirrors may import, and of the test code, a file of its "
                            "own folder that is no test, or the fakes when its tier tests a part they stand in for",
               ("place", "reaches")),
    TargetKind("outside", "the import names a package outside the project: it is not relative, names neither the "
                          "app's own package nor the standard library", ("path", "relative", "standard")),
)
"""Every kind of target."""

QUANTIFIERS: tuple[Quantifier, ...] = (
    Quantifier("may_not", "a kept fact that matches one of the targets is a finding; the target it matches is its hit"),
    Quantifier("may_only", "a kept fact that matches none of the targets is a finding"),
    Quantifier("must_reach", "a file of the scope is a finding unless it reaches a target: one of its kept facts "
                             "matches, or a link of the kinds `through` names leads from it to a file that does, "
                             "however far", True),
    Quantifier("must_not_reach", "a file of the scope that reaches a target is a finding, at the line of its first step: "
                                 "one of its kept facts matches, or a link of the kinds `through` names leads from it "
                                 "to a file that does, however far; `{chain}` says the way", True),
    Quantifier("must_be_reached", "a kept fact of the scope is a finding unless it is reached: a root file links to it "
                                  "(by a name it mentions, for a declaration; by an import, for a file), or a link "
                                  "of the kinds `then_through` names leads to it from something already reached, "
                                  "however far", True),
    Quantifier("at_most", "a file of the scope may keep at most the number of facts: each kept fact after that many, "
                          "in the order the file says them, is a finding, counted in that file alone"),
    Quantifier("at_least", "a file of the scope that keeps fewer facts than the number is a finding, its file fact the "
                           "fact said, counted in that file alone"),
)
"""What a check does with what it keeps."""

VARIABLES: tuple[Variable, ...] = (
    Variable("key", "the key of the profile the check comes from: parts.store.uses.never, checks.<id>",
             needs=KEY_OF_RULE),
    Variable("scope_part", "the part the check's scope names, bare: store", needs=SCOPE_PART),
    Variable("targets", "the values of the check's targets, joined by `or`: a part or a place as `<part>/`",
             needs=VALUES),
    Variable("hit", "the target the fact matched, as a dotted name", needs=HIT),
    Variable("file", "the file, as a finding shows it: its path from the folder holding the app"),
    Variable("line", "the line of the fact", ("line",)),
    Variable("where", "where the file sits, as a finding names a place: its part (store/ of units/docs), or the words "
                      "for code in no part", side=APP_SIDE),
    Variable("tier", "the file's tier: a test's own, or for a file of the app the tier whose tests cover its part"),
    Variable("mirrored_parts", "the parts a test's folder mirrors, each as `<part>/`, joined by `and`",
             side=TESTS_SIDE),
    Variable("mirrored_may_import", "the keys of what the parts a test mirrors may import, then, after `; `, the key "
                                    "of what its tier's tests may also import when the tier sets it: "
                                    "parts.store.imports.may; tiers.unit.imports.also", side=TESTS_SIDE),
    Variable("own_folder", "the folder a test may import test code from, from the tests folder: tests/units/docs",
             side=TESTS_SIDE),
    Variable("tests_folder", "the folder of the tests where a file of the app is tested: tests/units/docs/store",
             side=APP_SIDE),
    Variable("language", "how a message names the language of the app (`source` when it has no name)"),
    Variable("importable_parts", "the parts the file's part may import, each as `<part>/`", side=APP_SIDE),
    Variable("faked_parts", "the parts the fakes stand in for (`fakes.for`)"),
    Variable("parts_holding_functions", "a part that holds functions, naming the first of those whose `holds` "
                                        "lists functions"),
    Variable("parts_holding_classes", "a part that holds classes, naming the first of those whose `holds` lists "
                                      "classes"),
    Variable("name", "the name the fact carries", ("name",)),
    Variable("path", "the dotted name the fact names: what it imports, reads or calls", ("path",)),
    Variable("qualified_name", "a function's name after its class's and a dot when it is a method (Store.get); a "
                               "class's name", kinds=("function", "class")),
    Variable("package", "the top-level package the fact names: yaml for yaml.safe_load", ("path",)),
    Variable("reserved_reason", "why `reserved` reserves the top-level package the fact names", ("path",)),
    Variable("library_owners", "the other parts whose `imports.libraries` list the top-level package, each as `<part>/`",
             ("path",), side=APP_SIDE),
    Variable("first_library_owner", "the first of those parts, bare", ("path",), side=APP_SIDE),
    Variable("written", "what an import names, as the source writes it", ("written",)),
    Variable("text", "what the fact says: a comment's text, a syntax error's message", ("text",)),
    Variable("target", "what the fact reaches, as a dotted name from the root package of its side", ("reaches",)),
    Variable("target_name", "the same, then the name the import takes when that is no file", ("reaches",)),
    Variable("target_part", "where what the fact reaches sits, as a finding names a place", ("place",)),
    Variable("target_part_name", "the part what the fact reaches lies in, bare", ("place",)),
    Variable("target_package", "the package of the part what the fact reaches lies in, as a dotted name from the "
                               "root package", ("place",)),
    Variable("built_by", "the parts that may build what the part of what the fact reaches defines (its `built_by`), "
                         "each as `<part>/`, joined by `or`", ("place",)),
    Variable("allowed_names", "the names the file's part may import from what the import reaches, as the patterns of "
                              "its `imports.may`, joined by `or`", ("place",), side=APP_SIDE),
    Variable("disallowed_name", "the name an import took that is not allowed: `not <name>`, or `not the file as a "
                                "whole`", kinds=("import-into-app", "imported-name")),
    Variable("move_fix", "where the code that makes the import could go: a part that may import what it reaches",
             ("place",), side=APP_SIDE),
    Variable("type_only_fix", "what to do about a use of a part as more than a type: use it as a type, and leave the "
                              "call to a part that may make it", ("place",), needs=SCOPE_PART),
    Variable("tier_type_only_fix", "the same for a test: drive the tier's subject, with what the tier's tests may "
                                   "touch", ("place",), side=TESTS_SIDE),
    Variable("forwarded", "the callee a method forwards to", ("forwarded",)),
    Variable("returned", "the attributes a forwarding method returns of the call's result, dotted", ("returned",)),
    Variable("verb", "what the file does with what the fact names: import, use, call, build or reference"),
    Variable("function", "the function a parameter called is a parameter of", ("function",)),
    Variable("count", "how many facts the file keeps, for a check that counts them (at_most, at_least)", needs=COUNTED),
    Variable("lines", "how many lines the file holds", ("lines",)),
    Variable("chain", "the way a file reaches a target under must_not_reach: each file its links lead through, as a "
                      "dotted name, then what the fact that matched names, joined by ` -> `", needs=CHAINED),
)
"""Every variable of a message or a fix."""


SLOTS: tuple[Slot, ...] = (
    Slot("read", "the kinds of fact the check reads", "<kind> or [<kind>, ...]", "kinds"),
    Slot("in", "the files the check reads",
         "{files: app | tests | all, part: <part> | structure, tier: <tier>, where: [<filter about the file>, ...]}, "
         "each left out for any; files are app's when left out; a test belongs to the part its folder mirrors",
         "filters"),
    Slot("keep", "the filters a fact must pass, all of them, to be read", "[<filter>, ...]", "filters"),
    Slot("may_not", "a kept fact that matches one of the targets is a finding", "<target> or [<target>, ...]",
         "targets"),
    Slot("may_only", "a kept fact that matches none of the targets is a finding", "<target> or [<target>, ...]",
         "targets"),
    Slot("must_reach", "a file of the scope that reaches no target is a finding. A file reaches one when a kept fact "
                       "of its own matches, or when a link leads it to a file that does, and so on however far: "
                       "`through` names the kinds of fact that are links, `through_only` keeps only the links that "
                       "pass its filters. Example: `read: import-into-app`, `must_reach: {targets: {part: [<part>]}, "
                       "through: import-into-app}` finds each file that imports <part>/ neither itself nor through "
                       "the files it imports",
         "{targets: <target> or [<target>, ...], through: <kind> or [<kind>, ...], through_only: [<filter>, ...]}",
         "targets"),
    Slot("must_not_reach", "a file that reaches a target is a finding", "as must_reach writes it", "targets"),
    Slot("must_be_reached", "a kept fact that is not reached is a finding. It is reached when a root file (`from`) "
                            "links to it, by a link of the kinds `through` names (`through_only` keeps only those that "
                            "pass its filters), or when something already reached links to it, by a link of the kinds "
                            "`then_through` names, however far. Example: `read: class`, `must_be_reached: {from: "
                            "{files: tests}, through: names-mentioned, then_through: class}` finds each class that no "
                            "test names, directly or by way of a class a test names",
         "{from: <files, as `in` writes them>, through: <kind> or [...], through_only: [<filter>, ...], then_through: <kind> "
         "or [...], by_another_file: true}", "kinds"),
    Slot("at_most", "each kept fact of a file after this many is a finding", "<number>"),
    Slot("at_least", "a file that keeps fewer kept facts is a finding", "<number>"),
    Slot("except", "the filters of which any one excuses a finding", "[<filter>, ...]", "filters"),
    Slot("mode", "what a finding is", "fail (it fails the check), or list (it is listed as weak in the enforcement "
                                      "section and fails only `check --strict`); fail when left out"),
    Slot("message", "what was found, said of each finding", "a sentence with {<variable>}s", "variables"),
    Slot("fix", "what to do about it", "an imperative sentence with {<variable>}s", "variables"),
    Slot("once_per", "say a file's first finding per value of these variables", "[<variable>, ...]", "variables"),
    Slot("per_line", "say the findings of a file on one line that differ only in these variables as one, the first, "
                     "each of them written as its values in the order found, joined by `, `", "[<variable>, ...]",
         "variables"),
    Slot("cases", "a message and a fix for the findings of which the filters hold, the first that holds said in place "
                  "of the check's own", "[{when: [<filter>, ...], message, fix, once_per, per_line}, ...]",
         "filters"),
    Slot("examples", "code the check must find something in (flagged) and nothing in (clean), each a small project "
                     "`xarch profile check` runs, failing when one does not behave so",
         "{flagged: {<path>: <code>, ...}, clean: {<path>: <code>, ...}}, a path below the app, or tests/<path> for a "
         "test; required for a check of your own"),
)
"""Every slot of a check, in the order a check is written (the format's SLOTS), with what it means."""

READING = ("each fact of the kinds it reads, in the files of its scope, that passes the filters it keeps, may not "
           "match (may_not) or may only match (may_only) its targets; under must_reach a file must reach a target, "
           "by a fact of its own or by following links from file to file; under must_be_reached a fact must be "
           "reached by following links from the root files, and then from what they reach; of those links, `through` "
           "names the kinds of fact that count, `through_only` keeps the ones that pass its filters, and "
           "`then_through` names the kinds to follow after the first step; a finding an exception excuses is "
           "dropped, and each other is said by the first case whose filters hold, else by the check's message and "
           "fix")
"""How a check reads, in one sentence."""
