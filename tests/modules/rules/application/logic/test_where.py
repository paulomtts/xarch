"""Where a path sits and what code there may do, on a hand-built profile: the path given in any of its forms, a place
in a part, in the structure or in no part, and a test."""
from pathlib import Path

import pytest

from tests.modules.rules.builders import PYTHON
from xarch.kernel.placement import EVERYTHING, Place
from xarch.modules.rules.application.logic.where import describe, resolve
from xarch.modules.rules.domain.values import (
    FakePlace,
    PartAt,
    PartInfo,
    PartPlace,
    Profile,
    Resolved,
    StructurePlace,
    SuitePlace,
    UngovernedPlace,
)
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Fakes, Framework
from xarch.profile_values.tiers import CheckedTier as Tier

ROOT, APP, TESTS = Path("/p"), Path("/p/app"), Path("/p/tests")
NOW = ("datetime", "datetime", "now")
PARTS = {"kernel": ("kernel",), "domain": ("modules", "*", "domain"),
         "controller": ("modules", "*", "application", "controller.py"),
         "ports": ("modules", "*", "application", "ports"), "platform": ("platform",), "entry": ("front",)}
SHOWN = {"kernel": "kernel/", "domain": "domain/", "controller": "application/controller.py",
         "ports": "application/ports/", "platform": "platform/", "entry": "front/"}
PROFILE = Profile(
    parts=PARTS,
    rules={"kernel": (), "domain": (Target("kernel"),),
           "controller": (Target("domain", "own"), Target("ports", "own"), Target("kernel")),
           "ports": (Target("domain", "own"), Target("kernel")),
           "platform": (Target("kernel"),),
           "entry": (Target("controller", "any"), Target("kernel"))},
    folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain"),
             ("modules", "*", "application"), ("modules", "*", "application", "ports"), ("platform",), ("front",)),
    tiers=(Tier("unit", (Target("kernel"), Target("domain", "own")), None, (), True, "a rule", "nothing",
                "Does it call one rule?", "domain object"),
           Tier("integration", (Target("controller", "own"), Target("ports", "own")), None, (), False,
                "a use case", "real controllers; fakes", "Does it drive a controller?", "use case"),
           Tier("guard", (), ("architecture",), (), False, "a rule holds", "the source tree")),
    libraries={"kernel": (), "domain": (), "platform": ("yaml",), "entry": ("typer",)}, tests_folder="tests",
    fakes=Fakes(("fakes",), ("ports",), "Fake"), repeats=(Repeat("module", ("modules",)),),
    framework=Framework(("test_*.py",), "test_*"),
    forbidden={"domain": (NOW, ("builtins", "open"))},
    info={name: PartInfo(f"the {name} role", f"Is it {name}?", SHOWN[name],
                         "wraps a library" if name == "platform" else "") for name in PARTS},
    language=PYTHON)


def found(kind="app", *steps, exists=False) -> Resolved:
    base = {"app": APP, "tests": TESTS, "project": ROOT}[kind]
    return Resolved(kind, tuple(steps), base.joinpath(*steps), exists, base.joinpath(*steps).relative_to(ROOT).as_posix())


def where(*steps, exists=False, closed=False, profile=PROFILE):
    return describe(profile if not closed else Profile(**{**vars(profile), "closed_tree": True}),
                    found("app", *steps, exists=exists), APP, TESTS)


@pytest.mark.parametrize("given, existing, expected", [
    pytest.param("app/kernel/x.py", set(), ("app", ("kernel", "x.py"), False), id="given from the project root"),
    pytest.param("kernel/x.py", set(), ("app", ("kernel", "x.py"), False), id="given from the app folder"),
    pytest.param("/p/app/kernel/x.py", {"/p/app/kernel/x.py"}, ("app", ("kernel", "x.py"), True),
                 id="given in full, and there"),
    pytest.param("tests/modules/docs/domain/test_a.py", set(), ("tests", ("modules", "docs", "domain", "test_a.py"), False),
                 id="a test file to be"),
    pytest.param("README.md", {"/p/README.md"}, ("project", ("README.md",), True),
                 id="a file of the project that is neither app nor tests wins when it is there"),
    pytest.param("src/app/kernel/x.py", {"/p/src/app/kernel/x.py"}, ("project", ("src", "app", "kernel", "x.py"), True),
                 id="what exists beats what is guessed"),
    pytest.param("../app/kernel/x.py", set(), ("app", ("kernel", "x.py"), False), id="dots are resolved first"),
])
def test_a_path_is_taken_from_the_working_folder_the_project_root_or_the_app_folder(given, existing, expected):
    cwd = ROOT / "sub" if given.startswith("..") else ROOT
    resolved = resolve(Path(given), cwd, APP, TESTS, {Path(p) for p in existing})
    assert resolved is not None
    assert (resolved.within, resolved.steps, resolved.exists) == expected


def test_a_path_taken_from_a_folder_of_the_app_resolves_against_that_folder_first():
    resolved = resolve(Path("x.py"), APP / "kernel", APP, TESTS, {APP / "kernel" / "x.py"})
    assert resolved == Resolved("app", ("kernel", "x.py"), APP / "kernel" / "x.py", True, "app/kernel/x.py")


@pytest.mark.parametrize("given", ["/etc/passwd", "../../elsewhere/x.py", "/p/../q/x.py", "../kernel/x.py"])
def test_a_path_outside_the_project_is_not_placed(given):
    assert resolve(Path(given), ROOT, APP, TESTS, ()) is None


def test_the_tests_folder_may_lie_outside_the_project_root():
    resolved = resolve(Path("/elsewhere/t/a.py"), ROOT, APP, Path("/elsewhere/t"), ())
    assert resolved == Resolved("tests", ("a.py",), Path("/elsewhere/t/a.py"), False, "/elsewhere/t/a.py")


def test_code_in_a_part_gets_its_role_litmus_imports_libraries_forbidden_names_and_test():
    here = where("modules", "docs", "domain", "invoice.py")
    assert isinstance(here, PartPlace)
    assert (here.found.shown, here.place.part, here.info.role, here.info.litmus, here.info.shown) == (
        "app/modules/docs/domain/invoice.py", "domain", "the domain role", "Is it domain?", "domain/")
    assert (here.place.instance, here.singular) == ("docs", "module")
    assert here.reaches == (PartAt(Target("domain", "own"), "domain/", "app/modules/docs/domain/"),
                            PartAt(Target("kernel", "none"), "kernel/", "app/kernel/"))
    assert here.may_import_text == "its own module's `domain/`, `kernel/`"
    assert (here.libraries, here.forbidden) == ((), ("datetime.datetime.now", "builtins.open"))
    assert (here.tier, here.test_folder, here.test_file) == (PROFILE.tiers[0], "tests/modules/docs/domain/",
                                                             "test_invoice.py")


def test_what_a_part_may_import_names_the_instances_of_other_parts_by_a_placeholder():
    here = where("front", "main.py")
    assert here.reaches == (PartAt(Target("entry", "none"), "front/", "app/front/"),
                            PartAt(Target("controller", "any"), "application/controller.py",
                                   "app/modules/<module>/application/controller.py"),
                            PartAt(Target("kernel", "none"), "kernel/", "app/kernel/"))
    assert here.may_import_text == "`front/`, any module's `application/controller.py`, `kernel/`"
    assert here.libraries == ("typer",)


def test_a_part_that_is_one_file_has_its_test_by_use_case_in_the_folder_above():
    here = where("modules", "docs", "application", "controller.py")
    assert (here.tier.name, here.test_folder, here.test_file) == ("integration", "tests/modules/docs/application/",
                                                                 "test_<use case>.py")


def test_a_part_no_tier_tests_says_why():
    here = where("platform", "yaml_reader.py")
    assert (here.tier, here.untested, here.test_file) == (None, "wraps a library", "")


def test_a_folder_or_a_file_that_is_not_python_has_a_test_folder_and_no_test_file():
    assert (where("modules", "docs", "domain").test_folder, where("modules", "docs", "domain").test_file) == (
        "tests/modules/docs/domain/", "")
    assert where("modules", "docs", "domain", "__init__.py").test_file == ""


def test_a_folder_of_the_layout_no_part_claims_is_structure_with_the_parts_in_it():
    here = where("modules", "docs")
    assert isinstance(here, StructurePlace)
    assert here.nearest == (PartAt(Target("domain", "own"), "domain/", "app/modules/docs/domain/"),
                            PartAt(Target("controller", "own"), "application/controller.py",
                                   "app/modules/docs/application/controller.py"),
                            PartAt(Target("ports", "own"), "application/ports/", "app/modules/docs/application/ports/"))


@pytest.mark.parametrize("steps, nearest, closed", [
    pytest.param(("scripts", "run.py"), ["kernel", "domain", "controller", "ports", "platform", "entry"], False,
                 id="at the top of the app every part is near"),
    pytest.param(("modules", "docs", "helpers.py"), ["domain", "controller", "ports"], True,
                 id="in a folder of the layout the parts below it are near"),
    pytest.param(("modules", "docs", "application", "helpers.py"), ["controller", "ports"], False,
                 id="the nearest folder of the layout is the one that holds it"),
])
def test_a_path_in_no_part_is_ungoverned_and_names_the_parts_near_it(steps, nearest, closed):
    here = where(*steps, closed=closed)
    assert isinstance(here, UngovernedPlace)
    assert here.closed_tree == closed
    assert [n.target.part for n in here.nearest] == nearest


def test_a_path_outside_the_app_and_its_tests_is_ungoverned_without_parts_near_it():
    here = describe(PROFILE, found("project", "docs", "a.md"), APP, TESTS)
    assert isinstance(here, UngovernedPlace)
    assert (here.found.shown, here.nearest, here.closed_tree) == ("docs/a.md", (), None)
    assert here.note == "it lies outside the app folder and the tests folder"


def test_a_test_gets_its_tier_the_part_it_mirrors_what_it_may_import_and_whether_it_may_use_fakes():
    here = describe(PROFILE, found("tests", "modules", "docs", "domain", "test_invoice.py"), APP, TESTS)
    assert isinstance(here, SuitePlace)
    assert (here.test, here.found.shown, here.place) == (
        True, "tests/modules/docs/domain/test_invoice.py", Place("domain", "docs"))
    assert here.tier == PROFILE.tiers[0]
    assert here.reaches == (PartAt(Target("domain", "own"), "domain/", "app/modules/docs/domain/"),
                            PartAt(Target("kernel", "none"), "kernel/", "app/kernel/"))
    assert (here.may_use_fakes, here.test_code_from, here.forbidden) == (
        False, "tests/modules/docs/", ("datetime.datetime.now", "builtins.open"))


def test_a_test_of_a_use_case_may_use_the_fakes():
    here = describe(PROFILE, found("tests", "modules", "docs", "application", "test_publish.py"), APP, TESTS)
    assert (here.tier.name, here.place.part, here.may_use_fakes, here.fakes_path) == (
        "integration", "controller", True, "tests/fakes/")
    assert [r.target.part for r in here.reaches] == ["controller", "domain", "ports", "kernel"]


def test_a_test_that_lies_in_no_tier_says_so():
    here = describe(PROFILE, found("tests", "stray", "test_a.py"), APP, TESTS)
    assert isinstance(here, SuitePlace)
    assert (here.test, here.tier) == (True, None)
    assert here.note.startswith("lies in no tier")


def test_a_fake_and_a_helper_are_not_tests():
    assert isinstance(describe(PROFILE, found("tests", "fakes", "docs_repo.py"), APP, TESTS), FakePlace)
    helper = describe(PROFILE, found("tests", "modules", "docs", "domain", "builders.py"), APP, TESTS)
    assert isinstance(helper, SuitePlace) and not helper.test


def test_a_profile_that_checks_no_outside_package_has_no_libraries_to_list():
    bare = Profile(PARTS, PROFILE.rules, PROFILE.folders, info=PROFILE.info, language=PYTHON)
    assert where("kernel", "x.py", profile=bare).libraries is None


def test_a_rule_that_allows_everything_says_so():
    everything = Profile({"entry": ("front",)}, {"entry": (Target(EVERYTHING),)}, ((), ("front",)),
                         info={"entry": PartInfo("wires", "", "front/")}, language=PYTHON)
    here = describe(everything, found("app", "front", "x.py"), APP, None)
    assert (here.reaches, here.may_import_text) == ((), "everything")


def test_a_fake_is_told_where_the_fakes_live_and_that_it_may_import_any_test_code():
    here = describe(PROFILE, found("tests", "fakes", "docs_repo.py"), APP, TESTS)
    assert here == FakePlace(here.found, "tests/fakes/", "tests/", "a test fake: it stands in for a port, and is no test")


def test_a_helper_in_no_tier_has_no_note():
    here = describe(PROFILE, found("tests", "stray", "helpers.py"), APP, TESTS)
    assert isinstance(here, SuitePlace)
    assert (here.test, here.note) == (False, "")


def test_a_test_placed_by_its_tiers_example_folder_mirrors_no_part():
    here = describe(PROFILE, found("tests", "architecture", "test_rules.py"), APP, TESTS)
    assert isinstance(here, SuitePlace)
    assert (here.test, here.tier.name, here.place, here.may_use_fakes, here.test_code_from) == (
        True, "guard", None, False, "tests/architecture/")


def test_a_test_of_a_tier_not_held_to_forbidden_names_none_and_a_tier_s_types_only_parts_are_shown():
    rendering = Tier("rendering", (Target("entry"),), None, ("controller",))
    checked = Profile(**{**vars(PROFILE), "tiers": (*PROFILE.tiers, rendering)})
    here = describe(checked, found("tests", "front", "test_page.py"), APP, TESTS)
    assert (here.tier.name, here.forbidden, here.tier.types_only) == ("rendering", (), ("controller",))


def test_without_a_known_tests_folder_the_tests_are_shown_where_the_profile_says_they_are_when_none_is_given():
    assert (where("modules", "docs", "domain", "invoice.py").test_folder,
            describe(PROFILE, found("tests", "fakes", "x.py"), APP, None).fakes_path) == (
        "tests/modules/docs/domain/", "tests/fakes/")
    elsewhere = Profile(**{**vars(PROFILE), "tests_folder": "specs"})
    assert describe(elsewhere, found("tests", "fakes", "x.py"), APP, None).fakes_path == "specs/fakes/"


def test_a_one_file_part_whose_tier_names_no_file_per_has_a_stand_in_name():
    bare = Tier("integration", (Target("controller", "own"), Target("ports", "own")))
    checked = Profile(**{**vars(PROFILE), "tiers": (PROFILE.tiers[0], bare)})
    assert where("modules", "docs", "application", "controller.py", profile=checked).test_file == "test_<name>.py"


def test_a_part_that_a_tier_tests_does_not_say_why_it_is_untested():
    checked = Profile(**{**vars(PROFILE), "info": {**PROFILE.info, "domain": PartInfo("r", "l", "domain/", "why")}})
    assert where("modules", "docs", "domain", "invoice.py", profile=checked).untested == ""


def test_a_structure_folder_that_is_itself_in_the_layout_lists_the_parts_below_it():
    assert [n.target.part for n in where("modules", "docs", "application").nearest] == ["controller", "ports"]


def test_a_target_below_a_folder_part_is_shown_without_the_folders_slash():
    below = Profile(**{**vars(PROFILE), "rules": {**PROFILE.rules, "entry": (Target("ports", "any", ("repo",)),)}})
    assert where("front", "main.py", profile=below).reaches == (
        PartAt(Target("entry", "none"), "front/", "app/front/"),
        PartAt(Target("ports", "any", ("repo",)), "application/ports/repo", "app/modules/<module>/application/ports/repo"))


def test_what_exists_in_the_app_beats_what_exists_elsewhere_in_the_project():
    existing = {"/p/kernel/x.py", "/p/app/kernel/x.py"}
    resolved = resolve(Path("kernel/x.py"), ROOT, APP, TESTS, {Path(p) for p in existing})
    assert resolved == Resolved("app", ("kernel", "x.py"), APP / "kernel" / "x.py", True, "app/kernel/x.py")


def test_a_folder_of_the_layout_is_no_violation_of_the_closed_tree():
    assert isinstance(where("modules", "docs", closed=True), StructurePlace)


def test_a_test_of_a_listed_part_in_a_tier_not_held_to_the_list_is_told_no_forbidden_names():
    loose = Profile(**{**vars(PROFILE), "tiers": (Tier("unit", (Target("domain", "own"),)),)})
    here = describe(loose, found("tests", "modules", "docs", "domain", "test_invoice.py"), APP, TESTS)
    assert (here.tier.name, here.forbidden) == ("unit", ())


TWO_ROOTS = Profile(
    {**PARTS, "hooks": ("plugins", "*", "hooks")}, {**PROFILE.rules, "hooks": (Target("domain", "any"), Target("kernel"))},
    (*PROFILE.folders, ("plugins",), ("plugins", "*"), ("plugins", "*", "hooks")),
    tiers=(*PROFILE.tiers[:1], Tier("plugin", (Target("hooks", "own"),), None, (), False, "a hook", "nothing",
                                     "Does it run a hook?"), *PROFILE.tiers[1:]),
    framework=PROFILE.framework, fakes=PROFILE.fakes,
    repeats=(Repeat("module", ("modules",)), Repeat("plugin", ("plugins",))),
    info={**PROFILE.info, "hooks": PartInfo("what a plugin runs", "Does a plugin run it?", "hooks/")})


def test_a_path_in_the_second_repeating_folder_is_told_by_its_own_word_and_what_it_may_import_by_each_words():
    here = describe(TWO_ROOTS, found("app", "plugins", "seo", "hooks", "run.py"), APP, TESTS)
    assert (here.place.part, here.place.instance, here.singular, here.may_import_text) == (
        "hooks", "seo", "plugin", "its own plugin's `hooks/`, any module's `domain/`, `kernel/`")
    assert [(r.target.part, r.path) for r in here.reaches] == [
        ("hooks", "app/plugins/seo/hooks/"), ("domain", "app/modules/<module>/domain/"), ("kernel", "app/kernel/")]
    assert (here.test_folder, here.tier.name) == ("tests/plugins/seo/hooks/", "plugin")


def test_a_path_in_the_first_repeating_folder_keeps_its_word_beside_a_second_one():
    here = describe(TWO_ROOTS, found("app", "modules", "docs", "domain", "x.py"), APP, TESTS)
    assert (here.singular, here.place.instance) == ("module", "docs")


def test_a_test_in_the_second_repeating_folder_is_told_by_its_own_word():
    here = describe(TWO_ROOTS, found("tests", "plugins", "seo", "hooks", "test_run.py"), APP, TESTS)
    assert (here.test, here.place, here.singular, here.test_code_from) == (
        True, Place("hooks", "seo"), "plugin", "tests/plugins/seo/")


def test_a_part_outside_every_repeating_folder_has_no_word_when_there_are_several_and_the_only_one_when_there_is_one():
    assert describe(TWO_ROOTS, found("app", "kernel", "x.py"), APP, TESTS).singular == ""
    assert describe(PROFILE, found("app", "kernel", "x.py"), APP, TESTS).singular == "module"


def test_the_parts_near_a_path_in_the_second_repeating_folder_are_shown_with_its_word():
    here = describe(TWO_ROOTS, found("app", "plugins", "seo", "stray.py"), APP, TESTS)
    assert [(n.target.part, n.path) for n in here.nearest] == [("hooks", "app/plugins/seo/hooks/")]
