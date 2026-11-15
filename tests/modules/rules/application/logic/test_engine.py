"""The engine on hand-made rules as data: a rule reads the facts of its kinds in the files of its scope, keeps those
its filters pass, compares them with its targets under its quantifier, drops those its exemptions excuse, and says the
rest by the first saying whose condition holds, once per file where the saying keeps them once."""
import pytest

from tests.modules.rules.builders import PROFILE, imp, in_tests, source
from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.rule import (
    ALL,
    ANY,
    APP,
    LIST,
    MAY_NOT,
    MAY_ONLY,
    MUST_BE_REACHED,
    MUST_REACH,
    STRUCTURE,
    TESTS,
    Rule,
    Saying,
    Scope,
    Targets,
)
from xarch.modules.rules.domain.values import Class

DOMAIN, KERNEL = "modules/docs/domain/doc.py", "kernel/ids.py"
FILES = [source(DOMAIN, imp(1, "yaml"), imp(2, "json"), imp(3, "yaml", "load", "dump")),
         source(KERNEL, imp(1, "yaml"), imp(4, "", "x", up=0)), source("modules/__init__.py", imp(1, "yaml"))]
TESTS_FILES = [in_tests("modules/docs/domain/test_doc.py", imp(5, "yaml"))]
SAY = Saying("{part} imports {top}", "drop {top}")


def rule(**changes) -> Rule:
    fields = {"id": "libraries", "scope": Scope(), "facts": ("import",), "quantifier": MAY_NOT,
              "targets": Targets("packages", words=("yaml",)), "sayings": (SAY,)} | changes
    return Rule(**fields)


def said(*rules: Rule, tests=()) -> list[str]:
    return [f"{v.file}:{v.line}: {v.message}; {v.fix}" for v in
            run(rules, facts_of(FILES, tests, PROFILE, "app", "tests"), PROFILE)]


@pytest.mark.parametrize("scope, expected", [
    pytest.param(Scope(APP, "domain"), ["app/modules/docs/domain/doc.py:1", "app/modules/docs/domain/doc.py:3"],
                 id="a scope of a part reads the files of that part"),
    pytest.param(Scope(APP, STRUCTURE), ["app/modules/__init__.py:1"],
                 id="a scope of the structure reads the files no part claims"),
    pytest.param(Scope(APP), ["app/modules/docs/domain/doc.py:1", "app/modules/docs/domain/doc.py:3",
                              "app/kernel/ids.py:1", "app/modules/__init__.py:1"], id="a scope of any part reads all"),
    pytest.param(Scope(TESTS), ["tests/modules/docs/domain/test_doc.py:5"],
                 id="a scope of the tests reads the test files alone"),
    pytest.param(Scope(TESTS, "domain", "unit"), ["tests/modules/docs/domain/test_doc.py:5"],
                 id="a test is in the scope of the part it mirrors and of its tier"),
    pytest.param(Scope(TESTS, "domain", "integration"), [], id="a test of another tier is not"),
    pytest.param(Scope(TESTS, where=("untiered",)), [], id="a filter of a file narrows the scope"),
])
def test_a_rule_reads_the_files_of_its_scope(scope, expected):
    assert [line.split(": ")[0] for line in said(rule(scope=scope), tests=TESTS_FILES)] == expected


def test_every_finding_of_a_file_comes_before_those_of_the_next_and_within_a_file_a_rule_before_the_next():
    first, second = rule(sayings=(Saying("first {top}", "x"),)), rule(sayings=(Saying("second {top}", "x"),))
    assert [line.split(";")[0] for line in said(first, second, rule(scope=Scope(ALL, ANY), sayings=(
        Saying("third {top}", "x"),)), tests=TESTS_FILES)] == [
        "app/modules/docs/domain/doc.py:1: first yaml", "app/modules/docs/domain/doc.py:3: first yaml",
        "app/modules/docs/domain/doc.py:1: second yaml", "app/modules/docs/domain/doc.py:3: second yaml",
        "app/modules/docs/domain/doc.py:1: third yaml", "app/modules/docs/domain/doc.py:3: third yaml",
        "app/kernel/ids.py:1: first yaml", "app/kernel/ids.py:1: second yaml", "app/kernel/ids.py:1: third yaml",
        "app/modules/__init__.py:1: first yaml", "app/modules/__init__.py:1: second yaml",
        "app/modules/__init__.py:1: third yaml", "tests/modules/docs/domain/test_doc.py:5: third yaml"]


def test_under_may_only_a_fact_is_a_finding_when_it_matches_no_target():
    assert said(rule(scope=Scope(APP, "kernel"), quantifier=MAY_ONLY, keep=("absolute", "has-a-path"))) == []
    assert said(rule(scope=Scope(APP, "kernel"), quantifier=MAY_ONLY, keep=("absolute", "has-a-path"),
                     targets=Targets("packages", words=("json",)))) == ["app/kernel/ids.py:1: kernel/ imports yaml; drop yaml"]


def test_a_fact_a_filter_does_not_keep_is_not_read_and_one_an_exemption_excuses_is_no_finding():
    relative = rule(scope=Scope(APP, "kernel"), targets=Targets("existing"))
    assert said(relative) == ["app/kernel/ids.py:1: kernel/ imports yaml; drop yaml",
                              "app/kernel/ids.py:4: kernel/ imports ; drop "]
    assert said(rule(scope=Scope(APP, "kernel"), targets=Targets("existing"), keep=("absolute",))) == [
        "app/kernel/ids.py:1: kernel/ imports yaml; drop yaml"]
    assert said(rule(scope=Scope(APP, "kernel"), targets=Targets("existing"), exempt=("absolute",))) == [
        "app/kernel/ids.py:4: kernel/ imports ; drop "]


def test_a_finding_is_said_by_the_first_saying_whose_condition_holds_and_once_per_file_when_it_keeps_it_once():
    sayings = (Saying("{part} imports reserved {top}", "x", "reserved", ("top",)), Saying("{part} imports {top}", "y"))
    reserving = PROFILE.__class__(**{**PROFILE.__dict__, "reserved": {"yaml": "only the store"}})
    found = run((rule(scope=Scope(APP, "domain"), facts=("imported",), sayings=sayings),),
                facts_of(FILES, [], reserving, "app"), reserving)
    assert [v.message for v in found] == ["domain/ of modules/docs imports reserved yaml"]


def test_a_rule_in_list_mode_makes_weak_findings():
    found = run((rule(scope=Scope(APP, "kernel"), mode=LIST),), facts_of(FILES, [], PROFILE, "app"), PROFILE)
    assert found == [Weak("libraries", "app/kernel/ids.py", 1, "kernel/ imports yaml", "drop yaml")]
    assert not any(isinstance(v, Violation) for v in found)


@pytest.mark.parametrize("bad", [
    pytest.param(rule(keep=("sunny",)), id="a filter no list holds"),
    pytest.param(rule(targets=Targets("colours")), id="a kind of target no list holds"),
    pytest.param(rule(quantifier="maybe"), id="a quantifier no list holds"),
    pytest.param(rule(sayings=(Saying("{weather}", "x"),)), id="a variable no list holds"),
    pytest.param(rule(scope=Scope(APP, where=("sunny",))), id="a filter of a file no list holds"),
])
def test_a_name_the_engine_does_not_know_is_refused_naming_it(bad):
    with pytest.raises(ValueError, match="named"):
        said(bad)


def test_under_must_reach_a_file_reaches_by_its_own_fact_or_through_its_links_however_far():
    files = [source("kernel/a.py", imp(1, "app.kernel", "b")), source("kernel/b.py", imp(1, "app.kernel", "c")),
             source("kernel/c.py", imp(1, "yaml")), source("kernel/d.py", imp(1, "json"))]
    reach = rule(scope=Scope(APP, "kernel"), facts=("import",), quantifier=MUST_REACH, links=("edge",),
                 via="own-part-instance", sayings=(Saying("{part} reaches no {wanted}", "x"),))
    found = run((reach,), facts_of(files, [], PROFILE, "app"), PROFILE)
    assert [f"{v.file}: {v.message}" for v in found] == ["app/kernel/d.py: kernel/ reaches no yaml"]


def test_under_must_be_reached_a_declaration_is_reached_from_a_root_or_from_a_declaration_reached_however_far():
    tests = [in_tests("fakes/repo.py", classes=(Class(1, "FakeA", named=frozenset({"FakeB"})), Class(2, "FakeB"),
                                                Class(3, "FakeC", named=frozenset({"FakeC"})))),
             in_tests("modules/docs/domain/test_doc.py", named=frozenset({"FakeA"}))]
    reached = rule(scope=Scope(TESTS, where=("in-the-fakes",)), facts=("class",), quantifier=MUST_BE_REACHED,
                   links=("names",), roots=Scope(TESTS, where=("not-in-the-fakes",)), spread=("class",),
                   sayings=(Saying("{name} is unnamed", "x"),))
    found = run((reached,), facts_of([], tests, PROFILE, "app", "tests"), PROFILE)
    assert [v.message for v in found] == ["FakeC is unnamed"]
