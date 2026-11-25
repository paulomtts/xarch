"""The tier-imports check on hand-made source files: a test imports, of the app, only the part its folder mirrors and
what that part may import; of the test code, the fakes only when its tier tests a part they stand in for, and other
files only from its own folder."""
from dataclasses import replace

import pytest

from tests.modules.rules.application.logic.checks import tiers as violations
from tests.modules.rules.builders import GUARD, INTEGRATION, PROFILE, UNIT, imp, in_tests, profile, source
from xarch.modules.rules.application.logic import tier_of
from xarch.modules.rules.application.logic.tier_of import allowance, may_use_fakes
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Fakes
from xarch.profile_values.tiers import CheckedTier as Tier

APP = [source(p) for p in ["kernel/ids.py", "modules/docs/domain/doc.py", "modules/docs/domain/values.py",
                           "modules/docs/application/controller.py", "modules/docs/application/ports/repo.py",
                           "modules/docs/contract/__init__.py", "modules/docs/adapters/db.py",
                           "modules/other/domain/doc.py", "platform/sql.py", "web/routes.py", "scripts/seed.py"]]
HELPERS = [in_tests(p) for p in ["modules/docs/builders.py", "modules/other/builders.py", "web/conftest.py",
                                 "fakes/repo.py", "helpers.py", "conftest.py", "support/__init__.py",
                                 "support/clock.py"]]
NO_TIER = "lies in no tier: no part's folder and no tier's `folder` is mirrored here"
DOMAIN_TEST = "modules/docs/domain/test_doc.py"


def problems(path: str, *imports, checked=PROFILE) -> list[str]:
    return [str(v).removeprefix(f"tests/{path}:").lstrip() for v in
            violations([in_tests(path, *imports), *HELPERS], APP, checked, "app", "tests")]


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param(DOMAIN_TEST, [imp(1, "app.modules.docs.domain", "doc"), imp(2, "app.kernel", "ids")], [],
                 id="a test imports its part and what that part may"),
    pytest.param(DOMAIN_TEST, [imp(3, "app.modules.docs.application", "controller")],
                 ["3: a test of domain/ (unit tier) may not import controller/ of modules/docs "
                  "(app.modules.docs.application.controller): it imports only what domain/ may (parts.domain.imports.may)"],
                 id="a test may not import what its part may not"),
    pytest.param(DOMAIN_TEST, [imp(3, "app.modules.other.domain", "doc")],
                 ["3: a test of domain/ (unit tier) may not import domain/ of modules/other "
                  "(app.modules.other.domain.doc): it imports only what domain/ may (parts.domain.imports.may)"],
                 id="@own reaches the instance the test mirrors, not another"),
    pytest.param(DOMAIN_TEST, [imp(3, "app.modules.docs.domain.doc")],
                 [], id="a plain import is read too, and allowed here"),
    pytest.param(DOMAIN_TEST, [imp(3, "app.platform.sql")],
                 ["3: a test of domain/ (unit tier) may not import platform/ (app.platform.sql): it imports only "
                  "what domain/ may (parts.domain.imports.may)"],
                 id="a plain import that is not allowed is reported"),
    pytest.param(DOMAIN_TEST, [imp(1, "pytest"), imp(2, "pathlib", "Path"), imp(3, "app.scripts", "seed")], [],
                 id="the standard library, outside packages and ungoverned places of the app are not its business"),
    pytest.param(DOMAIN_TEST, [imp(3, "", "doc", up=0)], [],
                 id="a relative import is test code, never the app's"),
    pytest.param("modules/docs/application/test_publish.py",
                 [imp(1, "app.modules.docs.application", "controller"), imp(2, "app.modules.docs.domain", "doc"),
                  imp(3, "app.modules.docs.adapters", "db")],
                 ["3: a test of controller/ (integration tier) may not import adapters/ of modules/docs "
                  "(app.modules.docs.adapters.db): it imports only what controller/ may (parts.controller.imports.may)"],
                 id="a test in the folder of a file part imports what that part may"),
    pytest.param("architecture/test_rules.py", [imp(1, "app.kernel", "ids")],
                 ["1: a guard test may not import kernel/ (app.kernel.ids)"],
                 id="a test placed by its tier's folder imports what its tier's subject may, here nothing"),
    pytest.param("kernel/test_ids.py", [imp(1, "app.kernel", "ids"), imp(2, "app.modules.docs.domain", "doc")],
                 ["2: a test of kernel/ (unit tier) may not import domain/ of modules/docs "
                  "(app.modules.docs.domain.doc): it imports only what kernel/ may (parts.kernel.imports.may)"],
                 id="a test of a part outside the instances imports what that part may"),
    pytest.param("platform/test_sql.py", [imp(1, "app.platform", "sql")], [NO_TIER],
                 id="a test of a part no tier tests lies in no tier, and its imports are not checked"),
    pytest.param("scripts/test_seed.py", [],
                 [NO_TIER], id="a test file in no tier is reported, at no line"),
    pytest.param("scripts/helpers.py", [imp(1, "app.platform", "sql")], [],
                 id="a file in no tier that is no test is not checked"),
    pytest.param("fakes/repo.py", [imp(1, "app.platform", "sql"), imp(2, "tests.web", "conftest")], [],
                 id="a fake is not checked"),
    pytest.param("fakes/test_repo.py", [imp(1, "app.platform", "sql")], [],
                 id="a fake named like a test is still a fake, in no tier and not reported"),
])
def test_app_imports(path, imports, expected):
    assert problems(path, *imports) == expected


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("modules/docs/application/test_publish.py", [imp(1, "tests.fakes", "repo")], [],
                 id="a tier testing a part the fakes stand in for may import them"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.fakes.repo", "FakeRepo")],
                 ["1: a unit test may not import the fakes (tests.fakes.repo): only a tier that tests ports may"],
                 id="any other tier may not"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.modules.docs", "builders"), imp(2, "tests.modules.docs.builders", "x")],
                 [], id="a test imports test code from its own instance's folder"),
    pytest.param(DOMAIN_TEST, [imp(1, "", "builders", up=1)], [],
                 id="a relative import of its own folder's test code is fine"),
    pytest.param("modules/docs/domain/__init__.py", [imp(1, "", "builders", up=1)], [],
                 id="a package file's relative import climbs from its own package"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.modules.other", "builders")],
                 ["1: a test may import test code only from its own folder tests/modules/docs/ "
                  "(tests.modules.other.builders)"],
                 id="test code of another instance is reported"),
    pytest.param(DOMAIN_TEST, [imp(1, "", "conftest", up=3), imp(2, "web", "conftest", up=2)],
                 ["1: a test may import test code only from its own folder tests/modules/docs/ (tests.conftest)",
                  "2: a test may import test code only from its own folder tests/modules/docs/ (tests.modules.web)"],
                 id="a relative import that leaves its own folder is reported"),
    pytest.param("web/test_routes.py", [imp(1, "tests.web", "conftest"), imp(2, "tests", "helpers")],
                 ["2: a test may import test code only from its own folder tests/web/ (tests.helpers)"],
                 id="a test outside the instances has its top folder as its own"),
])
def test_test_imports(path, imports, expected):
    assert problems(path, *imports) == expected


SHARED = profile(framework=replace(PROFILE.framework, shared=(("support",), ("helpers.py",))))
"""PROFILE with the folder support/ and the file helpers.py below the tests root shared by every tier."""
SHARED_ELSEWHERE = ("a test may import test code only from its own folder {own}/ or the shared support/, helpers.py "
                    "(testing.shared) ({target})")


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param(DOMAIN_TEST, [imp(1, "tests", "helpers"), imp(2, "tests.support", "clock"),
                               imp(3, "tests.support.clock", "Frozen"), imp(4, "tests", "support")], [],
                 id="a test of any tier imports the shared folder and the shared file"),
    pytest.param("architecture/test_rules.py", [imp(1, "tests.helpers", "x"), imp(2, "tests.support", "clock")], [],
                 id="so does a test placed by its tier's folder"),
    pytest.param(DOMAIN_TEST, [imp(1, "", "helpers", up=3)], [],
                 id="a relative import reaching the shared file is fine too"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.modules.other", "builders"), imp(2, "tests", "conftest")],
                 [f"1: {SHARED_ELSEWHERE.format(own='tests/modules/docs', target='tests.modules.other.builders')}",
                  f"2: {SHARED_ELSEWHERE.format(own='tests/modules/docs', target='tests.conftest')}"],
                 id="test code outside its own folder and the shared ones is still reported, naming the shared ones"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.fakes.repo", "FakeRepo")],
                 ["1: a unit test may not import the fakes (tests.fakes.repo): only a tier that tests ports may"],
                 id="the fakes stay the fakes' rule"),
])
def test_shared_test_code_is_open_to_every_tier(path, imports, expected):
    assert problems(path, *imports, checked=SHARED) == expected


def test_without_shared_the_same_imports_are_reported_as_before():
    assert problems(DOMAIN_TEST, imp(1, "tests", "helpers"), imp(2, "tests.support", "clock")) == [
        "1: a test may import test code only from its own folder tests/modules/docs/ (tests.helpers)",
        "2: a test may import test code only from its own folder tests/modules/docs/ (tests.support.clock)"]


@pytest.mark.parametrize("checked", [
    pytest.param(profile(tiers=(Tier("all", (), ()),)), id="a tier with an empty folder places no test"),
    pytest.param(profile(tiers=(Tier("all", (), None),)), id="a tier with no folder places no test"),
])
def test_a_test_at_the_tests_root_lies_in_no_tier(checked):
    assert problems("test_all.py", imp(1, "tests", "helpers"), checked=checked) == [NO_TIER]


SELFLESS = profile(rules={"kernel": (), "domain": (Target("kernel"),)},
                   tiers=(Tier("unit", (Target("kernel"), Target("domain", "own"))),))


@pytest.mark.parametrize("path, imports", [
    pytest.param("kernel/test_ids.py", [imp(1, "app.kernel", "ids")],
                 id="a part outside the instances whose rules do not list it"),
    pytest.param(DOMAIN_TEST, [imp(1, "app.modules.docs.domain", "doc")],
                 id="a part of an instance whose rules do not list it, in its own instance"),
])
def test_a_test_imports_its_subject_even_when_the_subject_may_not_import_itself(path, imports):
    assert problems(path, *imports, checked=SELFLESS) == []


def test_without_tiers_nothing_is_checked():
    assert problems("scripts/test_seed.py", checked=profile(tiers=())) == []


@pytest.mark.parametrize("path, expected", [
    pytest.param(DOMAIN_TEST, (Target("domain", "own"), Target("domain", "own"), Target("kernel")),
                 id="a test's subject part and what it may import"),
    pytest.param("kernel/test_ids.py", (Target("kernel"), Target("kernel")),
                 id="a part outside the instances is reached in no instance"),
    pytest.param("architecture/test_rules.py", (), id="a tier with no subject allows nothing"),
    pytest.param("modules/docs/application/test_publish.py", (Target("controller", "own"), Target("controller", "own"),
                                                    *PROFILE.rules["controller"]),
                 id="the file part of its folder"),
])
def test_allowance(path, expected):
    assert allowance(PROFILE, tier_of.tested(PROFILE, tuple(path.split("/")), False)) == expected


ALSO = profile(tiers=(UNIT, replace(INTEGRATION, imports_also=(Target("adapters", "own"),)), GUARD))
"""PROFILE, whose integration tests may also import adapters/ of the instance they mirror."""


def test_what_a_tiers_tests_may_also_import_follows_what_the_part_they_mirror_may():
    assert allowance(ALSO, tier_of.tested(ALSO, ("modules", "docs", "application", "test_publish.py"), False)) == (
        Target("controller", "own"), Target("controller", "own"), *PROFILE.rules["controller"], Target("adapters", "own"))


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("modules/docs/application/test_publish.py", [imp(1, "app.modules.docs.adapters", "db")], [],
                 id="a test of the tier may import what its tier's tests may also import"),
    pytest.param("modules/docs/application/test_publish.py", [imp(1, "app.platform", "sql")],
                 ["1: a test of controller/ (integration tier) may not import platform/ (app.platform.sql): it imports "
                  "only what controller/ may (parts.controller.imports.may; tiers.integration.imports.also)"],
                 id="what it still may not import is said with the key of the tier too"),
    pytest.param(DOMAIN_TEST, [imp(1, "app.modules.docs.adapters", "db")],
                 ["1: a test of domain/ (unit tier) may not import adapters/ of modules/docs "
                  "(app.modules.docs.adapters.db): it imports only what domain/ may (parts.domain.imports.may)"],
                 id="a test of another tier may not"),
])
def test_a_tiers_tests_may_also_import_what_it_says_in_the_instance_they_mirror(path, imports, expected):
    assert problems(path, *imports, checked=ALSO) == expected


def in_folder(tier: Tier) -> tier_of.Tested:
    """Where a test in the tier's own folder stands, mirroring no part."""
    return tier_of.Tested(tier, None, (), True, False)


def test_a_tiers_allowance_is_its_subject_and_what_each_part_may_import():
    assert allowance(PROFILE, in_folder(Tier("pair", (Target("kernel"), Target("platform"))))) == (
        Target("kernel"), Target("kernel"), Target("platform"), Target("platform"), Target("kernel"))


def test_a_tiers_own_allowance_replaces_what_its_subject_would_give():
    guard = Tier("guard", (Target("kernel"),), ("architecture",), imports_may=(Target("platform"),))
    assert allowance(PROFILE, in_folder(guard)) == (Target("platform"),)


@pytest.mark.parametrize("tier, expected", [
    pytest.param(Tier("pair", (Target("kernel"),), imports_also=(Target("web"),)),
                 (Target("kernel"), Target("kernel"), Target("web")), id="after its subject and what it may import"),
    pytest.param(Tier("guard", (), ("architecture",), imports_may=(Target("platform"),), imports_also=(Target("web"),)),
                 (Target("platform"), Target("web")), id="after the tier's own allowance"),
])
def test_what_a_tiers_tests_may_also_import_is_added_to_its_allowance(tier, expected):
    assert allowance(PROFILE, in_folder(tier)) == expected


def test_a_test_in_a_tiers_folder_imports_only_what_the_tier_allows():
    guard = Tier("guard", (), ("architecture",), imports_may=(Target("kernel"),))
    checked = profile(tiers=(guard,))
    assert problems("architecture/test_rules.py", imp(1, "app.kernel", "ids"), imp(2, "app.platform", "sql"),
                    checked=checked) == [
        "2: a guard test may not import platform/ (app.platform.sql)"]


@pytest.mark.parametrize("checked, tier, expected", [
    pytest.param(PROFILE, INTEGRATION, True, id="a tier testing ports may use the fakes"),
    pytest.param(PROFILE, UNIT, False, id="one testing none of their parts may not"),
    pytest.param(PROFILE, GUARD, False, id="nor one with no subject"),
    pytest.param(profile(fakes=None), INTEGRATION, False, id="without fakes no tier may"),
    pytest.param(profile(fakes=Fakes(("fakes",), ("ports",), "Fake", ("unit", "guard"))), UNIT, True,
                 id="a tier fakes.tiers lists may, though it tests none of their parts"),
    pytest.param(profile(fakes=Fakes(("fakes",), ("ports",), "Fake", ("unit", "guard"))), GUARD, True,
                 id="so may one with no subject"),
    pytest.param(profile(fakes=Fakes(("fakes",), ("ports",), "Fake", ("unit",))), INTEGRATION, True,
                 id="a tier testing their parts still may when fakes.tiers leaves it out"),
    pytest.param(profile(fakes=Fakes(("fakes",), ("ports",), "Fake", ("unit",))), GUARD, False,
                 id="one neither listed nor testing their parts still may not"),
])
def test_may_use_fakes(checked, tier, expected):
    assert may_use_fakes(checked, tier) == expected


LISTED = profile(fakes=Fakes(("fakes",), ("ports",), "Fake", ("guard",)))
"""PROFILE with the guard tier allowed the fakes by fakes.tiers."""


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("architecture/test_rules.py", [imp(1, "tests.fakes", "repo")], [],
                 id="a test of a tier fakes.tiers lists imports the fakes"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.fakes.repo", "FakeRepo")],
                 ["1: a unit test may not import the fakes (tests.fakes.repo): only a tier that tests ports, or the "
                  "guard tier (fakes.tiers), may"],
                 id="a tier it does not list is told which may"),
])
def test_fakes_tiers_open_the_fakes_to_the_tiers_they_list(path, imports, expected):
    assert problems(path, *imports, checked=LISTED) == expected


@pytest.mark.parametrize("path, imports, fix", [
    pytest.param(DOMAIN_TEST, [imp(3, "app.modules.docs.application", "controller")],
                 "import here only what domain/ may; test controller/ of modules/docs from the folder that mirrors it",
                 id="an app import a test of a part may not make"),
    pytest.param("architecture/test_rules.py", [imp(1, "app.kernel", "ids")],
                 "import here only what the subject of the guard tier may; test kernel/ from the folder that mirrors "
                 "it", id="an app import a test with no subject part may not make"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.fakes.repo", "FakeRepo")],
                 "drop the import of tests.fakes.repo, or move the test to a tier that tests ports",
                 id="the fakes in a tier that may not use them"),
    pytest.param(DOMAIN_TEST, [imp(1, "tests.modules.other", "builders")],
                 "move what tests.modules.other.builders holds into tests/modules/docs/, or drop the import",
                 id="test code of another folder"),
    pytest.param("scripts/test_seed.py", [],
                 "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`",
                 id="a test in no tier"),
])
def test_a_violation_says_what_to_do(path, imports, fix):
    found = violations([in_tests(path, *imports), *HELPERS], APP, PROFILE, "app", "tests")
    assert [(v.rule, v.fix) for v in found] == [("tiers", fix)]


OTHER_TEST = in_tests("modules/docs/domain/test_values.py")


@pytest.mark.parametrize("imports, expected", [
    pytest.param([imp(1, "tests.modules.docs.domain.test_values", "BASE")],
                 ["1: a test may not import another test file (tests.modules.docs.domain.test_values): what tests "
                  "share lives in test code that is no test file"], id="an absolute import of a test file"),
    pytest.param([imp(1, "", "test_values", up=0)],
                 ["1: a test may not import another test file (tests.modules.docs.domain.test_values): what tests "
                  "share lives in test code that is no test file"], id="a relative import of a test file"),
    pytest.param([imp(1, "tests.modules.docs", "builders")], [], id="test code that is no test file"),
])
def test_a_test_imports_no_test_file(imports, expected):
    found = violations([in_tests(DOMAIN_TEST, *imports), OTHER_TEST, *HELPERS], APP, PROFILE, "app", "tests")
    assert [str(v).removeprefix(f"tests/{DOMAIN_TEST}:").lstrip() for v in found] == expected
    assert {v.fix for v in found} <= {"move what tests.modules.docs.domain.test_values holds that this test needs "
                                      "into test code of its folder that is no test file, and import it from there"}


NEAR = replace(PROFILE, framework=replace(PROFILE.framework, beside=True))
"""PROFILE, its tests beside the code."""


def beside_problems(path: str, *imports, checked=NEAR) -> list[str]:
    beside = replace(source(path, *imports), beside=True)
    return [f"{v}; fix: {v.fix}" for v in violations([beside, *HELPERS], APP, checked, "app", "tests")]


@pytest.mark.parametrize("path, expected", [
    pytest.param("platform/test_sql.py",
                 ["app/platform/test_sql.py: lies in no tier: its part is untested; fix: test the part with a tier, or "
                  "move the test"], id="in a part no tier tests"),
    pytest.param("scripts/test_seed.py",
                 ["app/scripts/test_seed.py: lies in no part; fix: test the part with a tier, or move the test"],
                 id="in no part"),
    pytest.param("modules/docs/domain/test_doc.py", [], id="in a tested part"),
])
def test_a_test_beside_the_code_with_no_tier_says_why(path, expected):
    assert beside_problems(path) == expected


def test_a_test_beside_the_code_imports_what_its_part_may_and_is_named_by_its_app_path():
    assert beside_problems("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
                           imp(3, "app.platform.sql")) == [
        "app/modules/docs/domain/test_doc.py:3: a test of domain/ (unit tier) may not import platform/ "
        "(app.platform.sql): it imports only what domain/ may (parts.domain.imports.may); fix: import here only what "
        "domain/ may; test platform/ from the folder that mirrors it"]


def test_a_mirrored_test_with_no_tier_keeps_its_text_under_beside():
    found = [str(v) for v in violations([in_tests("scripts/test_x.py"), *HELPERS], APP, NEAR, "app", "tests")]
    assert found == [f"tests/scripts/test_x.py: {NO_TIER}"]
