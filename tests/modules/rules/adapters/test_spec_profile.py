"""Rules' Profiles read from spec's contract: the profile view becomes the profile as the checks see it (the checks it
writes itself as spec read them), the origin keeps each looseness, the init files are compared as text, and spec's
check of a profile becomes what rules reviews, or why it cannot."""
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.domain import published
from xarch.modules.rules.domain.errors import NoProfile, ProfileUnusable, Unloaded
from xarch.modules.rules.domain.published import KeyFacts, Resemblance, Reviewed
from xarch.modules.rules.domain.values import InitFile, Known, PartInfo, Profile, Standing
from xarch.modules.spec.contract import (
    CheckProfile,
    CheckResult,
    Explain,
    ExplainResult,
    FilesResult,
    GuardsView,
    KeyExplained,
    KnownProfiles,
    KnownResult,
    Loosened,
    NoProfileChosen,
    Origin,
    OriginResult,
    PartView,
    Problem,
    ProfileChecked,
    ProfileRefused,
    ProfileView,
    ProjectFile,
    ProjectFiles,
    UnknownKey,
)
from xarch.profile_values.checks import Quantified, Saying, Scope, WrittenCheck, WrittenTarget
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier

TABLE = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id")
VIEW = ProfileView(
    parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/", forbidden=(("socket",),),
                    holds="functions", no_callbacks=True, shared=2, immutable=True),
           PartView("api", ("src", "*", "api"), (Target("core"),), "handlers", shown="api/ of src/<module>",
                    untested="it only wires", must_import=(Target("core"),), types_only=("core",), names=("*Api",),
                    built_by=("core",))),
    folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
    tiers=(CheckedTier("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
    libraries={"core": (), "api": ("fastapi",)}, repeats=(Repeat("module", ("src",)),),
    guards=GuardsView(package_only=("api",), scenarios=ScenarioCoverage("api", "unit", "Result", ("a", "b", "c"), TABLE,
                                                                     "test_{name}.py"),
                      no_comments=True,
                      stand_ins=StandIns((("m", "Mock"),), (), ("spec",), (Fixture("mocker", ("Mock",)),)),
                      closed_tree=True, no_duplicates=4, no_twins=3, no_twins_renamed=4, no_twins_subset=3,
                      no_twins_translated=("api",), dead_code=True, untested=True, tests_only=True,
                      tests_only_known=("api/x.py:run",), pass_through=("api",), private_imports=True),
    fakes=Fakes(("fakes",), ("api",), "Fake"), framework=Framework(("test_*.py",), "test_*", (("skip",),)),
    excluded=(Excluded(("vendor",), "not ours"),), hints={"rules": "ask first"},
    checks={"no-print": WrittenCheck(("call",), Scope(), Quantified("may_not", (WrittenTarget("path", ("builtins.print",)),)),
                                     (Saying("{where} prints", "log it"),))})


ORIGIN = Origin("mine.yaml", False, "cli", ("closed-tree",), (), (Loosened("untested", "api"),))


class Spec:
    """Spec's controller as rules' adapter uses it, answering from fixed values."""

    def __init__(self, files: tuple[ProjectFile, ...] | None = None, origin: OriginResult = ORIGIN,
                 checked: CheckResult | None = None):
        self._files, self._origin, self._checked = files, origin, checked

    def profile(self, location: str) -> ProfileView:
        return VIEW

    def origin(self, location: str) -> OriginResult:
        return self._origin

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult:
        return ProfileRefused("cannot write them") if self._files is None else ProjectFiles(self._files)

    def known(self, app: Path) -> KnownResult:
        return {Path("/p/none"): NoProfileChosen(("cli",)),
                Path("/p/broken"): ProfileRefused("mine.yaml: missing `parts`")}.get(app, KnownProfiles("mine.yaml",
                                                                                                         ("cli",)))

    def explain(self, cmd: Explain) -> ExplainResult:
        if cmd.key == "parts.refused":
            return ProfileRefused("python: cannot read the data file")
        return KEY if cmd.key == KEY.key else UnknownKey(cmd.key, ())

    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        assert cmd == CheckProfile(Path("/p/app"), "mine.yaml"), cmd
        return self._checked


KEY = KeyExplained("parts.types_only", "parts.<part>", "m", "a", False, True, ("types-only",), "parts:\n  a: {}\n", (),
                   (), name="types_only", holder="part")


def test_the_profile_view_becomes_the_profile_the_checks_see():
    assert SpecProfiles(Spec()).profile("mine.yaml") == Profile(
        parts={"core": ("core",), "api": ("src", "*", "api")}, rules={"core": (), "api": (Target("core"),)},
        folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
        tiers=(CheckedTier("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
        libraries={"core": (), "api": ("fastapi",)}, fakes=Fakes(("fakes",), ("api",), "Fake"),
        repeats=(Repeat("module", ("src",)),), package_only=("api",),
        scenarios=ScenarioCoverage("api", "unit", "Result", ("a", "b", "c"),
                            CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id"), "test_{name}.py"),
        no_comments=True, stand_ins=StandIns((("m", "Mock"),), (), ("spec",), (Fixture("mocker", ("Mock",)),)),
        closed_tree=True, framework=Framework(("test_*.py",), "test_*", (("skip",),)),
        forbidden={"core": (("socket",),)},
        info={"core": PartInfo("the rules", "Is it a rule?", "core/"),
              "api": PartInfo("handlers", "", "api/ of src/<module>", "it only wires")},
        excluded=(Excluded(("vendor",), "not ours"),), must_import={"api": (Target("core"),)}, no_duplicates=4, no_twins=3,
        no_twins_renamed=4, no_twins_subset=3, no_twins_translated=("api",),
        dead_code=True, pass_through=("api",), untested=True, tests_only=True, tests_only_known=("api/x.py:run",),
        holds={"core": "functions"}, immutable=("core",),
        types_only={"api": ("core",)}, no_callbacks=("core",), names={"api": ("*Api",)}, built_by={"api": ("core",)},
        shared={"core": 2}, private_imports=True, hints={"rules": "ask first"}, written=VIEW.checks, default_tests="tests")


def test_the_standing_keeps_the_guards_left_off_and_those_the_baseline_leaves_off_too():
    standing = SpecProfiles(Spec()).standing("mine.yaml", "app")
    assert (standing.guards_off, standing.baseline_off) == (("closed-tree",), ())


def test_the_standing_keeps_every_way_the_profile_is_looser_as_spec_says_it():
    said = "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)"
    origin = Origin("mine.yaml", False, "cli", (), (), (Loosened("untested", "api"), Loosened("litmus", "cli", "", said)))
    assert SpecProfiles(Spec(origin=origin)).standing("mine.yaml", "app").looser == (
        published.Loosened("untested", "api"), published.Loosened("litmus", "cli", "", said))
    assert SpecProfiles(Spec(origin=Origin("mine.yaml", False, "cli"))).standing("mine.yaml", "app").looser == ()


def test_the_init_files_are_compared_as_text_and_none_when_the_profile_cannot_write_them():
    files = (ProjectFile(("AGENTS.md",), "agents\n", True), ProjectFile(("logo.bin",), b"\xffok"))
    assert SpecProfiles(Spec(files)).standing("mine.yaml", "app") == Standing(("closed-tree",), (), (
        InitFile(("AGENTS.md",), "agents\n", True), InitFile(("logo.bin",), "�ok", False)),
        (published.Loosened("untested", "api"),))
    assert SpecProfiles(Spec()).standing("mine.yaml", "app").init_files == ()


def test_a_profile_whose_origin_spec_refuses_cannot_be_checked():
    with pytest.raises(ProfileUnusable, match="no such profile"):
        SpecProfiles(Spec(origin=ProfileRefused("no such profile"))).standing("mine.yaml", "app")


def test_the_profiles_a_project_knows_are_spec_s_none_chosen_is_none_in_force_and_one_refused_raises_its_reason():
    assert SpecProfiles(Spec()).known(Path("/p/app")) == Known("mine.yaml", ("cli",))
    assert SpecProfiles(Spec()).known(Path("/p/none")) == Known(None, ("cli",))
    with pytest.raises(ProfileUnusable, match="^mine.yaml: missing `parts`$"):
        SpecProfiles(Spec()).known(Path("/p/broken"))


def test_what_the_format_says_of_a_key_is_its_example_its_name_and_what_holds_it_and_nothing_for_no_key():
    assert SpecProfiles(Spec()).key("parts.types_only") == KeyFacts("parts:\n  a: {}\n", "types_only", "part")
    assert SpecProfiles(Spec()).key("parts.nothing") == KeyFacts()


def test_an_explanation_spec_refuses_raises_its_reason():
    with pytest.raises(ProfileUnusable, match="^python: cannot read the data file$"):
        SpecProfiles(Spec()).key("parts.refused")


@pytest.mark.parametrize("checked, then", [
    pytest.param(ProfileChecked("mine.yaml", (Problem("examples", "example (core/a.py): imports app.api"),), 3, ORIGIN),
                 Reviewed("mine.yaml", ("example (core/a.py): imports app.api",), 3,
                          Resemblance(False, "cli", (published.Loosened("untested", "api"),))),
                 id="a profile that loads keeps its example problems, its files and how it resembles the bundled ones"),
    pytest.param(ProfileChecked("cli", (), 48, Origin("cli")), Reviewed("cli", (), 48, Resemblance(True)),
                 id="a bundled profile resembles itself and nothing else"),
])
def test_spec_s_check_of_a_profile_that_loads_is_what_rules_reviews(checked, then):
    assert SpecProfiles(Spec(checked=checked)).reviewed(Path("/p/app"), "mine.yaml") == then


def test_spec_s_check_of_a_profile_that_does_not_load_raises_with_where_it_is_and_every_problem():
    checked = ProfileChecked("mine.yaml", (Problem("load", "mine.yaml: unknown key 'colour'"),
                                           Problem("load", "mine.yaml: parts.core: missing `role`")), 0, None)
    with pytest.raises(Unloaded) as found:
        SpecProfiles(Spec(checked=checked)).reviewed(Path("/p/app"), "mine.yaml")
    assert (found.value.location, found.value.problems) == (
        "mine.yaml", ("mine.yaml: unknown key 'colour'", "mine.yaml: parts.core: missing `role`"))


def test_spec_choosing_no_profile_raises_with_the_profiles_known():
    with pytest.raises(NoProfile) as found:
        SpecProfiles(Spec(checked=NoProfileChosen(("cli", "web")))).reviewed(Path("/p/app"), "mine.yaml")
    assert found.value.known == ("cli", "web")


def test_a_profile_spec_refuses_to_check_raises_with_spec_s_reason():
    with pytest.raises(ProfileUnusable, match="^unknown profile 'nope'$"):
        SpecProfiles(Spec(checked=ProfileRefused("unknown profile 'nope'"))).reviewed(Path("/p/app"), "mine.yaml")
