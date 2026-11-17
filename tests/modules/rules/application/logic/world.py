"""A small project whose files say a little of everything the engine reads, so that the tests of each filter, target
and variable can name a fact by its file and line: PROFILE's app (package `app`) and its tests (package `tests`).

    app/modules/docs/domain/doc.py            domain: imports (yaml, the kernel, a relative one, json, a private
                                              name), classes (Doc, DocError an exception, Shown a record, Frozen
                                              and Pair immutable records, Loose a record that is not), a
                                              top-level function and a method that forwards, comments, callbacks,
                                              uses and method calls
    app/modules/docs/application/ports/repo.py ports: Repo, an interface
    app/modules/docs/application/services/publish.py services: builds Doc, calls and passes make on
    app/bootstrap/wiring.py                   bootstrap, which may import everything
    app/modules/__init__.py                   the structure's package file
    app/modules/docs/domain/errors.py         a file of exceptions only
    app/platform/latin.py                     a file that could not be read as text
    app/platform/broken.py                    a file that does not parse
    tests/modules/docs/domain/test_doc.py     a unit test of domain: imports of the app, a helper, a fake, a test
    tests/modules/docs/builders.py            a helper that is no test
    tests/fakes/repo.py                       the fakes: FakeRepo, and Fake itself
    tests/architecture/test_rules.py          a guard test, placed by its tier's folder
"""
from __future__ import annotations

from dataclasses import replace

from tests.modules.rules.builders import PROFILE, RULES, imp, in_tests, source
from xarch.kernel.source import Unparsable
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.parsed import Call, Callback, Class, Comment, Function, Method, MethodCall, SoleCall, Use
from xarch.modules.rules.domain.rule import Fact, Found, Match, Read, Rule
from xarch.profile_values.checks import Saying, Scope
from xarch.profile_values.placement import Target

DOMAIN = "app/modules/docs/domain/doc.py"
PORTS = "app/modules/docs/application/ports/repo.py"
SERVICE = "app/modules/docs/application/services/publish.py"
WIRING = "app/bootstrap/wiring.py"
STRUCTURE = "app/modules/__init__.py"
ERRORS = "app/modules/docs/domain/errors.py"
TEST = "tests/modules/docs/domain/test_doc.py"
HELPER = "tests/modules/docs/builders.py"
FAKE = "tests/fakes/repo.py"
GUARD = "tests/architecture/test_rules.py"
UNREAD = "app/platform/latin.py"
BROKEN = "app/platform/broken.py"
DOC = ("app", "modules", "docs", "domain", "doc", "Doc")
MAKE = ("app", "modules", "docs", "domain", "doc", "make")

APP = [
    source("modules/docs/domain/doc.py", imp(1, "yaml"), imp(2, "app.kernel", "ids"), imp(3, "", "values", up=0),
           imp(4, "json", "loads"), imp(5, "app.kernel.ids", "_secret", "__all__"),
           classes=(Class(6, "Doc", named=frozenset({"Repo"})), Class(7, "DocError", exception=True),
                    Class(8, "Shown", methods=(Method(8, "__repr__", "str"),)),
                    Class(9, "Frozen", immutable=True), Class(9, "Loose"),
                    Class(9, "Pair", bases=(("typing", "NamedTuple"),), immutable=True)),
           functions=(Function(10, "make", returns_named=frozenset({"Shown"}), statements=1),
                      Function(11, "get", owner="Doc", forwards="self.repo.get",
                               sole_call=SoleCall(("self", "repo", "get"), then=("name",))),
                      Function(12, "put", owner="Doc", forwards="self.repo.put", sole_call=SoleCall(("self", "repo", "put")))),
           comments=(Comment(13, "# noqa: E501"), Comment(14, "# a note TODO")),
           callbacks=(Callback(15, "make", "check", annotated=True), Callback(16, "get", "self", receiver=True)),
           uses=(Use(17, ("datetime", "datetime", "now"), 2), Use(18, ("yaml", "load"), 1)),
           method_calls=(MethodCall(19, "resolve", held=True), MethodCall(20, "absolute")),
           module_functions=("make",), named=frozenset({"Doc", "make", "Repo"})),
    source("modules/docs/application/ports/repo.py", imp(1, "typing", "Protocol"),
           classes=(Class(2, "Repo", bases=(("typing", "Protocol"),)),)),
    source("modules/docs/application/services/publish.py", imp(1, "app.modules.docs.domain", "doc"),
           imp(2, "app.modules.docs.domain.doc", "Doc"), imp(3, "app.platform", "db"),
           calls=(Call(4, DOC), Call(5, MAKE), Call(6, ("yaml", "dump"))), uses=(Use(5, MAKE, 2), Use(7, MAKE, 2)),
           named=frozenset({"Doc", "Repo"})),
    source("bootstrap/wiring.py", imp(1, "app.modules.docs.domain.doc", "Doc"), calls=(Call(2, DOC),)),
    source("modules/__init__.py", imp(1, "app.kernel", "ids")),
    source("kernel/ids.py"), source("platform/db.py"),
    source("platform/latin.py", error=Unparsable(0, "not UTF-8 text", unreadable=True)),
    source("platform/broken.py", error=Unparsable(3, "invalid syntax")),
    source("modules/docs/domain/errors.py", classes=(Class(1, "DocMissing", exception=True),))]
TESTS = [
    in_tests("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
             imp(2, "tests.modules.docs", "builders"), imp(3, "tests.fakes", "repo"),
             imp(4, "tests.architecture", "test_rules"), imp(5, "app.platform", "db")),
    in_tests("modules/docs/builders.py"),
    in_tests("fakes/repo.py", classes=(Class(1, "FakeRepo"), Class(2, "Fake"))),
    in_tests("architecture/test_rules.py", imp(1, "app.kernel", "ids"))]

FACTS = facts_of(APP, TESTS, PROFILE, "app", "tests")
RESERVED = replace(PROFILE, reserved={"json": "only io reads files"})
LISTED = replace(PROFILE, libraries={"platform": ("yaml",), "domain": ("yaml",)})
NARROWED = replace(PROFILE, rules={**RULES, "services": (Target("domain", "own", (), "*Id"), Target("kernel"))})
BUILT = replace(PROFILE, built_by={"domain": ("bootstrap",)})
"""PROFILE reserving json, listing yaml in two parts' libraries, narrowing what services may import of domain to the
names a pattern matches, and letting only bootstrap build domain's classes."""
RULE = Rule("mine", Scope(), ("import",), "may_not", (Match("exist"),), (Saying("m", "f"),))


def read(file: str) -> Read:
    return next(r for r in FACTS.files if r.file.name == file)


def facts(file: str, kind: str) -> tuple[Fact, ...]:
    return read(file).facts[kind]


def found(file: str, kind: str, rule: Rule = RULE, hit: tuple[str, ...] | None = None) -> list[Found]:
    return [Found(rule, read(file), fact, hit) for fact in facts(file, kind)]

