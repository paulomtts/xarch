"""The engine on hand-made rules as data: a rule reads the facts of its kinds in the files of its scope, keeps those
its filters pass, compares them with its targets under its quantifier, drops those its exemptions excuse, and says the
rest by the first saying whose conditions hold, once per file where the saying keeps them once."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import PROFILE, imp, in_tests, source
from xarch.kernel.logic.conditions import condition
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.engine import read, run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.parsed import Class
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import (
    AT_LEAST,
    AT_MOST,
    EXISTING,
    LIST,
    MAY_NOT,
    MAY_ONLY,
    MUST_BE_REACHED,
    MUST_REACH,
    UNIQUE,
    Match,
    Rule,
)
from xarch.profile_values.checks import ALL, ANY, APP, STRUCTURE, TESTS, Condition, Saying, Scope

DOMAIN, KERNEL = "modules/docs/domain/doc.py", "kernel/ids.py"
FILES = [source(DOMAIN, imp(1, "yaml"), imp(2, "json"), imp(3, "yaml", "load", "dump")),
         source(KERNEL, imp(1, "yaml"), imp(4, "", "x", up=0)), source("modules/__init__.py", imp(1, "yaml"))]
TESTS_FILES = [in_tests("modules/docs/domain/test_doc.py", imp(5, "yaml"))]
SAY = Saying("{where} imports {package}", "drop {package}")
YAML = (Match("package", words=("yaml",)),)


def c(*texts: str) -> tuple[Condition, ...]:
    return tuple(condition(text) for text in texts)


def rule(**changes) -> Rule:
    fields = {"id": "libraries", "scope": Scope(), "facts": ("import",), "quantifier": MAY_NOT, "targets": YAML,
              "sayings": (SAY,)} | changes
    return Rule(**fields)


def said(*rules: Rule, tests=()) -> list[str]:
    return [f"{v.file}:{v.line}: {v.message}; {v.fix}" for v in
            run(rules, facts_of(FILES, tests, PROFILE, "app", "tests", rules), PROFILE)]


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
    pytest.param(Scope(TESTS, where=c("not tiered")), [], id="a filter about the file narrows the scope"),
])
def test_a_rule_reads_the_files_of_its_scope(scope, expected):
    sayings = (Saying("imports {package}", "drop {package}"),)
    assert [line.split(": ")[0] for line in said(rule(scope=scope, sayings=sayings), tests=TESTS_FILES)] == expected


def test_every_finding_of_a_file_comes_before_those_of_the_next_and_within_a_file_a_rule_before_the_next():
    first, second = rule(sayings=(Saying("first {package}", "x"),)), rule(sayings=(Saying("second {package}", "x"),))
    assert [line.split(";")[0] for line in said(first, second, rule(scope=Scope(ALL, ANY), sayings=(
        Saying("third {package}", "x"),)), tests=TESTS_FILES)] == [
        "app/modules/docs/domain/doc.py:1: first yaml", "app/modules/docs/domain/doc.py:3: first yaml",
        "app/modules/docs/domain/doc.py:1: second yaml", "app/modules/docs/domain/doc.py:3: second yaml",
        "app/modules/docs/domain/doc.py:1: third yaml", "app/modules/docs/domain/doc.py:3: third yaml",
        "app/kernel/ids.py:1: first yaml", "app/kernel/ids.py:1: second yaml", "app/kernel/ids.py:1: third yaml",
        "app/modules/__init__.py:1: first yaml", "app/modules/__init__.py:1: second yaml",
        "app/modules/__init__.py:1: third yaml", "tests/modules/docs/domain/test_doc.py:5: third yaml"]


def test_under_may_only_a_fact_is_a_finding_when_it_matches_no_target():
    assert said(rule(scope=Scope(APP, "kernel"), quantifier=MAY_ONLY, keep=c("not relative"))) == []
    assert said(rule(scope=Scope(APP, "kernel"), quantifier=MAY_ONLY, keep=c("not relative"),
                     targets=(Match("package", words=("json",)),))) == [
        "app/kernel/ids.py:1: kernel/ imports yaml; drop yaml"]


def test_a_fact_matches_the_first_of_the_targets_it_matches():
    two = (Match("package", words=("json",)), Match("package", words=("yaml",)))
    assert said(rule(scope=Scope(APP, "domain"), targets=two, sayings=(Saying("{hit}", "x"),))) == [
        "app/modules/docs/domain/doc.py:1: yaml; x", "app/modules/docs/domain/doc.py:2: json; x",
        "app/modules/docs/domain/doc.py:3: yaml; x"]


def test_a_fact_a_filter_does_not_keep_is_not_read_and_one_an_exemption_excuses_is_no_finding():
    any_import = rule(scope=Scope(APP, "kernel"), targets=EXISTING, sayings=(Saying("{where} imports {written}", "x"),))
    assert said(any_import) == ["app/kernel/ids.py:1: kernel/ imports yaml; x",
                                "app/kernel/ids.py:4: kernel/ imports .; x"]
    assert said(replace(any_import, keep=c("not relative"))) == ["app/kernel/ids.py:1: kernel/ imports yaml; x"]
    assert said(replace(any_import, exempt=c("not relative"))) == ["app/kernel/ids.py:4: kernel/ imports .; x"]


def test_a_finding_is_said_by_the_first_saying_whose_conditions_all_hold_and_once_per_file_when_it_keeps_it_once():
    sayings = (Saying("{where} imports reserved {package} and takes {name}", "x", c("reserved", "takes-a-name"),
                      ("package",)),
               Saying("{where} imports reserved {package}", "x", c("reserved")), Saying("{where} imports {package}", "y"))
    reserving = replace(PROFILE, reserved={"yaml": "only the store"})
    found = run((rule(scope=Scope(APP, "domain"), facts=("imported-name",), sayings=sayings),),
                facts_of(FILES, [], reserving, "app"), reserving)
    assert [v.message for v in found] == ["domain/ of modules/docs imports reserved yaml",
                                          "domain/ of modules/docs imports reserved yaml and takes load"]


def test_the_findings_of_one_line_a_saying_lists_per_line_are_one_finding_listing_the_values_that_differ():
    listing = (Saying("{where} imports {package} and takes {name}", "drop {name} of {package}", per_line=("name",)),)
    found = run((rule(scope=Scope(APP, "domain"), facts=("imported-name",), targets=EXISTING, sayings=listing,
                      keep=c("takes-a-name")),),
                facts_of(FILES, [], PROFILE, "app"), PROFILE)
    assert [(v.line, v.message, v.fix) for v in found] == [
        (3, "domain/ of modules/docs imports yaml and takes load, dump", "drop load, dump of yaml")]


def test_findings_of_one_line_that_differ_in_another_variable_stay_apart():
    listing = (Saying("{where} imports {package} and takes {name}", "x", per_line=("name",)),)
    files = [source(DOMAIN, imp(3, "yaml", "load", "dump"), imp(3, "json", "loads"))]
    found = run((rule(scope=Scope(APP, "domain"), facts=("imported-name",), targets=EXISTING, sayings=listing,
                      keep=c("takes-a-name")),),
                facts_of(files, [], PROFILE, "app"), PROFILE)
    assert [v.message for v in found] == ["domain/ of modules/docs imports yaml and takes load, dump",
                                          "domain/ of modules/docs imports json and takes loads"]


def test_a_value_said_twice_on_one_line_is_listed_once():
    listing = (Saying("{where} imports {package}", "x", per_line=("package",)),)
    found = run((rule(scope=Scope(APP, "domain"), facts=("imported-name",), targets=EXISTING, sayings=listing),),
                facts_of([source(DOMAIN, imp(3, "yaml", "load", "dump"))], [], PROFILE, "app"), PROFILE)
    assert [v.message for v in found] == ["domain/ of modules/docs imports yaml"]


def test_a_rule_in_list_mode_makes_weak_findings():
    found = run((rule(scope=Scope(APP, "kernel"), mode=LIST),), facts_of(FILES, [], PROFILE, "app"), PROFILE)
    assert found == [Weak("libraries", "app/kernel/ids.py", 1, "kernel/ imports yaml", "drop yaml")]
    assert not any(isinstance(v, Violation) for v in found)


def test_under_must_reach_a_file_reaches_by_its_own_fact_or_through_its_links_however_far():
    files = [source("kernel/a.py", imp(1, "app.kernel", "b")), source("kernel/b.py", imp(1, "app.kernel", "c")),
             source("kernel/c.py", imp(1, "yaml")), source("kernel/d.py", imp(1, "json"))]
    reach = rule(scope=Scope(APP, "kernel"), facts=("import",), quantifier=MUST_REACH, links=("import-into-app",),
                 via=c("target-in-own-part"), sayings=(Saying("{where} reaches no {targets}", "x"),))
    found = run((reach,), facts_of(files, [], PROFILE, "app", rules=(reach,)), PROFILE)
    assert [f"{v.file}: {v.message}" for v in found] == ["app/kernel/d.py: kernel/ reaches no yaml"]


def test_under_must_be_reached_a_declaration_is_reached_from_a_root_or_from_a_declaration_reached_however_far():
    tests = [in_tests("fakes/repo.py", classes=(Class(1, "FakeA", named=frozenset({"FakeB"})), Class(2, "FakeB"),
                                                Class(3, "FakeC", named=frozenset({"FakeC"})))),
             in_tests("modules/docs/domain/test_doc.py", named=frozenset({"FakeA"}))]
    reached = rule(scope=Scope(TESTS, where=c("below fakes")), facts=("class",), quantifier=MUST_BE_REACHED,
                   targets=EXISTING, links=("names-mentioned",), roots=Scope(TESTS, where=c("not below fakes")),
                   spread=("class",), sayings=(Saying("{name} is unnamed", "x"),))
    found = run((reached,), facts_of([], tests, PROFILE, "app", "tests", (reached,)), PROFILE)
    assert [v.message for v in found] == ["FakeC is unnamed"]


def test_a_declaration_reached_only_from_its_own_file_is_unreached_when_the_rule_wants_another_file():
    app = [source("modules/docs/application/ports/repo.py", classes=(Class(1, "Repo"), Class(2, "Clock")),
                  named=frozenset({"Repo", "Clock"})),
           source("modules/docs/application/services/doc.py", named=frozenset({"Clock"}))]
    reached = rule(scope=Scope(APP, "ports"), facts=("class",), quantifier=MUST_BE_REACHED, targets=EXISTING,
                   links=("names-mentioned",), roots=Scope(APP), sayings=(Saying("{name} is unnamed", "x"),))
    facts = facts_of(app, [], PROFILE, "app", rules=(reached,))
    assert [v.message for v in run((reached,), facts, PROFILE)] == []
    assert [v.message for v in run((replace(reached, elsewhere=True),), facts, PROFILE)] == ["Repo is unnamed"]


def test_how_many_facts_a_rule_reads_is_counted_so_that_one_that_reads_none_shows():
    facts = facts_of(FILES, [], PROFILE, "app")
    assert read(rule(scope=Scope(APP, "domain")), facts, PROFILE) == 3
    assert read(rule(scope=Scope(APP, "domain"), keep=c("relative")), facts, PROFILE) == 0
    assert read(rule(scope=Scope(APP, "web")), facts, PROFILE) == 0


def test_a_rule_reads_only_the_facts_of_its_kinds_when_the_facts_are_read_for_it():
    imports = rule(scope=Scope(APP, "domain"))
    facts = facts_of(FILES, [], PROFILE, "app", rules=(imports,))
    assert {kind for file in facts.files for kind in file.facts} == {"import"}


COUNTED_FILES = [source("modules/docs/domain/a.py", imp(1, "yaml"), imp(2, "json")),
                 source("modules/docs/adapters/b.py", imp(1, "csv")), source("modules/mail/domain/c.py", imp(1, "re")),
                 source("modules/mail/domain/d.py"), source("modules/note/domain/e.py"), source("kernel/ids.py")]
"""Four imports in the instance docs (two in its domain, one in its adapters), one in the domain of mail, none in
note, and a file of the kernel, in no instance, importing nothing."""


def counted(quantifier: str, count: int, per: str, scope: Scope = Scope(APP)) -> list[str]:
    counting = rule(scope=scope, quantifier=quantifier, targets=EXISTING, count=count, per=per,
                    sayings=(Saying("{file} keeps {count}", "x"),))
    return [f"{v.file}:{v.line}: {v.message}" for v in
            run((counting,), facts_of(COUNTED_FILES, [], PROFILE, "app", rules=(counting,)), PROFILE)]


@pytest.mark.parametrize("per, scope, found", [
    pytest.param("file", Scope(APP), [], id="file"),
    pytest.param("part", Scope(APP, "domain"), ["app/modules/mail/domain/c.py:1: app/modules/mail/domain/c.py keeps 3"],
                 id="part"),
    pytest.param("instance", Scope(APP),
                 ["app/modules/docs/adapters/b.py:1: app/modules/docs/adapters/b.py keeps 3"], id="instance"),
    pytest.param("all", Scope(APP), ["app/modules/docs/adapters/b.py:1: app/modules/docs/adapters/b.py keeps 4",
                                     "app/modules/mail/domain/c.py:1: app/modules/mail/domain/c.py keeps 4"], id="all"),
])
def test_at_most_counts_the_kept_facts_of_the_files_per_groups_together_each_after_the_count_a_finding(per, scope, found):
    assert counted(AT_MOST, 2, per, scope) == found


@pytest.mark.parametrize("per, found", [
    pytest.param("file", ["app/modules/mail/domain/d.py:0: app/modules/mail/domain/d.py keeps 0",
                          "app/modules/note/domain/e.py:0: app/modules/note/domain/e.py keeps 0",
                          "app/kernel/ids.py:0: app/kernel/ids.py keeps 0"], id="file"),
    pytest.param("instance", ["app/modules/note/domain/e.py:0: app/modules/note/domain/e.py keeps 0",
                              "app/kernel/ids.py:0: app/kernel/ids.py keeps 0"], id="instance"),
    pytest.param("part", ["app/kernel/ids.py:0: app/kernel/ids.py keeps 0"], id="part"),
])
def test_at_least_finds_a_group_that_keeps_fewer_at_line_0_of_its_first_file(per, found):
    assert counted(AT_LEAST, 1, per) == found


NAMED_FILES = [source("modules/docs/domain/a.py", classes=(Class(1, "Title"), Class(2, "Draft"))),
               source("modules/docs/adapters/b.py", classes=(Class(3, "Title"),)),
               source("modules/mail/domain/c.py", classes=(Class(4, "Title"), Class(5, "Draft"))),
               source("kernel/ids.py", classes=(Class(6, "Draft"),))]
"""Title twice in the instance docs (its domain and adapters) and once in mail, Draft once in each and once in the
kernel."""


def unique(per: str, scope: Scope = Scope(APP)) -> list[str]:
    once = rule(scope=scope, facts=("class",), quantifier=UNIQUE, targets=EXISTING, field="name", per=per,
                sayings=(Saying("{name} is declared again, first at {first}", "x"),))
    return [f"{v.file}:{v.line}: {v.message}" for v in
            run((once,), facts_of(NAMED_FILES, [], PROFILE, "app", rules=(once,)), PROFILE)]


@pytest.mark.parametrize("per, found", [
    pytest.param("file", [], id="file"),
    pytest.param("instance", ["app/modules/docs/adapters/b.py:3: Title is declared again, first at "
                              "app/modules/docs/domain/a.py:1"], id="instance"),
    pytest.param("part", ["app/modules/mail/domain/c.py:4: Title is declared again, first at "
                          "app/modules/docs/domain/a.py:1",
                          "app/modules/mail/domain/c.py:5: Draft is declared again, first at "
                          "app/modules/docs/domain/a.py:2"], id="part"),
    pytest.param("all", ["app/modules/docs/adapters/b.py:3: Title is declared again, first at "
                         "app/modules/docs/domain/a.py:1",
                         "app/modules/mail/domain/c.py:4: Title is declared again, first at "
                         "app/modules/docs/domain/a.py:1",
                         "app/modules/mail/domain/c.py:5: Draft is declared again, first at "
                         "app/modules/docs/domain/a.py:2",
                         "app/kernel/ids.py:6: Draft is declared again, first at app/modules/docs/domain/a.py:2"],
                 id="all"),
])
def test_unique_finds_each_kept_fact_whose_field_a_fact_before_it_in_its_group_has_naming_the_first(per, found):
    assert unique(per) == found
