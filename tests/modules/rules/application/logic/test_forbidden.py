"""The forbidden check on a hand-built profile: a file of a part neither imports a module its list names nor uses a
name it lists, and a test of a tier that says so is held to the list of the part it mirrors."""
import pytest

from xarch.kernel.logic.placement import Target
from xarch.modules.rules.application.logic.forbidden import violations
from xarch.modules.rules.domain.values import Fakes, Framework, Import, Profile, SourceFile, Use
from xarch.modules.rules.domain.values import TestTier as Tier

NOW = ("datetime", "datetime", "now")
PROFILE = Profile(parts={"domain": ("modules", "*", "domain"), "adapters": ("modules", "*", "adapters")},
                  rules={"domain": (Target("domain", "own"),)},
                  folders=((), ("modules",), ("modules", "*")),
                  tiers=(Tier("unit", (Target("domain", "own"),), forbidden=True),
                         Tier("loose", (Target("adapters", "own"),))),
                  forbidden={"domain": (NOW, ("builtins", "open"), ("socket",), ("urllib",))},
                  framework=Framework(("test_*.py",), "test_*"))
DOMAIN = ("modules", "docs", "domain", "doc.py")


def file(path=DOMAIN, imports=(), uses=()) -> SourceFile:
    return SourceFile("/".join(("app", *path)), path, tuple(imports), uses=tuple(uses))


@pytest.mark.parametrize("imports, uses, problems", [
    pytest.param([], [Use(4, NOW, 2)], ["4: domain/ of modules/docs may not use datetime.datetime.now (forbidden.domain)"],
                 id="a listed name used through the import that binds its first steps is reported where it is used"),
    pytest.param([], [Use(4, ("datetime", "datetime", "now", "date"), 1)],
                 ["4: domain/ of modules/docs may not use datetime.datetime.now (forbidden.domain)"],
                 id="a use reaching below a listed name is a use of it"),
    pytest.param([], [Use(4, ("datetime", "datetime", "fromisoformat"), 2), Use(5, ("datetime", "datetime"), 2)], [],
                 id="a name beside or above a listed one is no use of it"),
    pytest.param([], [Use(2, ("builtins", "open"), 0)],
                 ["2: domain/ of modules/docs may not use builtins.open (forbidden.domain)"],
                 id="a builtin used by its bare name is reported"),
    pytest.param([Import(1, ("socket",))], [Use(3, ("socket", "create_connection"), 1)],
                 ["1: domain/ of modules/docs may not import socket (forbidden.domain)"],
                 id="a listed module is reported where it is imported and not again where it is used"),
    pytest.param([Import(1, ("urllib", "request"))], [],
                 ["1: domain/ of modules/docs may not import urllib (forbidden.domain)"],
                 id="a module below a listed one is the listed one"),
    pytest.param([Import(1, ("datetime",), names=("datetime", "date"))], [], [],
                 id="importing what holds a listed name is fine"),
    pytest.param([Import(1, ("datetime", "datetime"), names=("now",))], [Use(2, NOW, 3)],
                 ["1: domain/ of modules/docs may not import datetime.datetime.now (forbidden.domain)"],
                 id="importing a listed name itself is reported at the import"),
    pytest.param([Import(1, ("socket",), level=1)], [], [], id="a relative import is the app's own"),
    pytest.param([Import(1, ("socket",), names=("socket", "create_connection"))], [],
                 ["1: domain/ of modules/docs may not import socket (forbidden.domain)"],
                 id="two names of one listed module on one line are reported once"),
    pytest.param([Import(1, ("time",), names=("time",))], [Use(2, ("time", "time"), 2)], [],
                 id="a name the list does not hold is not reported, even beside a listed one"),
    pytest.param([], [Use(4, ("datetime", "datetime", "now"), 3)], [],
                 id="a use whose import bound the whole listed name was reported at the import"),
])
def test_forbidden(imports, uses, problems):
    assert [str(v).removeprefix("app/modules/docs/domain/doc.py:") for v in
            violations([file(imports=imports, uses=uses)], [], PROFILE)] == problems


def test_a_violation_names_its_rule_and_how_to_fix_it():
    found = violations([file(uses=[Use(4, NOW, 2)])], [], PROFILE)[0]
    assert (found.rule, found.fix) == ("forbidden", "do what needs datetime.datetime.now outside domain/, and hand "
                                                    "domain/ the result")


def test_a_part_with_no_list_and_a_file_in_no_part_are_not_checked():
    adapter = file(("modules", "docs", "adapters", "db.py"), uses=[Use(1, NOW, 2)])
    stray = file(("scripts", "run.py"), uses=[Use(1, NOW, 2)])
    assert violations([adapter, stray], [], PROFILE) == []


def test_a_test_of_a_tier_held_to_the_list_is_checked_as_the_part_it_mirrors():
    held = SourceFile("tests/modules/docs/domain/test_doc.py", ("modules", "docs", "domain", "test_doc.py"), (),
                      uses=(Use(3, ("builtins", "open"), 0),))
    loose = SourceFile("tests/modules/docs/adapters/test_db.py", ("modules", "docs", "adapters", "test_db.py"), (),
                       uses=(Use(3, ("builtins", "open"), 0),))
    assert [str(v) for v in violations([], [held, loose], PROFILE)] == [
        "tests/modules/docs/domain/test_doc.py:3: a test of domain/ (unit tier) may not use builtins.open "
        "(forbidden.domain; tiers.unit.forbidden)"]


def test_without_a_forbidden_list_nothing_is_checked():
    assert violations([file(uses=[Use(4, NOW, 2)])], [], Profile(PROFILE.parts, PROFILE.rules, PROFILE.folders)) == []


@pytest.mark.parametrize("path", [
    pytest.param(("fakes", "clock.py"), id="a fake"),
    pytest.param(("architecture", "test_rules.py"), id="a test placed by its tier's folder mirrors no part"),
    pytest.param(("stray", "test_x.py"), id="a test in no tier"),
])
def test_a_test_that_mirrors_no_listed_part_is_not_checked(path):
    checked = Profile(**{**vars(PROFILE), "fakes": Fakes(("fakes",), ("ports",), "Fake"),
                         "tiers": (*PROFILE.tiers, Tier("guard", (), ("architecture",), forbidden=True))})
    test = SourceFile("tests/" + "/".join(path), path, (), uses=(Use(3, ("builtins", "open"), 0),))
    assert violations([], [test], checked) == []


def test_a_test_of_a_listed_part_in_a_tier_not_held_to_the_list_is_not_checked():
    loose = Profile(**{**vars(PROFILE), "tiers": (Tier("unit", (Target("domain", "own"),)),)})
    test = SourceFile("tests/modules/docs/domain/test_doc.py", ("modules", "docs", "domain", "test_doc.py"), (),
                      uses=(Use(3, ("builtins", "open"), 0),))
    assert violations([], [test], loose) == []
