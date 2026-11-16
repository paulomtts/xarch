"""Rules' Profiles read from spec's contract: the profile view becomes the profile as the checks see it (the checks it
writes itself as spec read them), the origin keeps each looseness, and the init files are compared as text."""
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.published import KeyFacts
from xarch.modules.rules.domain.values import InitFile, PartInfo, Profile, Standing
from xarch.modules.spec.contract import (
    Explain,
    ExplainResult,
    FilesResult,
    GuardsView,
    KeyExplained,
    KnownProfiles,
    Loosened,
    Origin,
    OriginResult,
    PartView,
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
                      closed_tree=True, no_duplicates=4, no_twins=3, no_twins_renamed=4, no_twins_subset=3, dead_code=True,
                      untested=True, pass_through=("api",),
                      private_imports=True),
    fakes=Fakes(("fakes",), ("api",), "Fake"), framework=Framework(("test_*.py",), "test_*", (("skip",),)),
    excluded=(Excluded(("vendor",), "not ours"),), hints={"rules": "ask first"},
    checks={"no-print": WrittenCheck(("call",), Scope(), Quantified("may_not", (WrittenTarget("path", ("builtins.print",)),)),
                                     (Saying("{where} prints", "log it"),))})


ORIGIN = Origin("mine.yaml", False, "cli", ("closed-tree",), (), (Loosened("untested", "api"),))


class Spec:
    """Spec's controller as rules' adapter uses it, answering from fixed values."""

    def __init__(self, files: tuple[ProjectFile, ...] | None = None, origin: OriginResult = ORIGIN):
        self._files, self._origin = files, origin

    def profile(self, location: str) -> ProfileView:
        return VIEW

    def origin(self, location: str) -> OriginResult:
        return self._origin

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult:
        return ProfileRefused("cannot write them") if self._files is None else ProjectFiles(self._files)

    def known(self, app: Path) -> KnownProfiles:
        return KnownProfiles(None if app == Path("/p/none") else "mine.yaml", ("cli",))

    def explain(self, cmd: Explain) -> ExplainResult:
        return KEY if cmd.key == KEY.key else UnknownKey(cmd.key, ())


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
        no_twins_renamed=4, no_twins_subset=3,
        dead_code=True, pass_through=("api",), untested=True, holds={"core": "functions"}, immutable=("core",),
        types_only={"api": ("core",)}, no_callbacks=("core",), names={"api": ("*Api",)}, built_by={"api": ("core",)},
        shared={"core": 2}, private_imports=True, hints={"rules": "ask first"}, written=VIEW.checks, tests_folder="tests")


def test_the_standing_keeps_the_guards_left_off_and_those_the_baseline_leaves_off_too():
    standing = SpecProfiles(Spec()).standing("mine.yaml", "app")
    assert (standing.guards_off, standing.baseline_off) == (("closed-tree",), ())


def test_the_standing_keeps_each_part_the_profile_redefines_without_its_litmus_as_spec_says_it():
    said = "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)"
    origin = Origin("mine.yaml", False, "cli", (), (), (Loosened("untested", "api"), Loosened("litmus", "cli", "", said)))
    assert SpecProfiles(Spec(origin=origin)).standing("mine.yaml", "app").unplaced == (said,)
    assert SpecProfiles(Spec()).standing("mine.yaml", "app").unplaced == ()


def test_the_init_files_are_compared_as_text_and_none_when_the_profile_cannot_write_them():
    files = (ProjectFile(("AGENTS.md",), "agents\n", True), ProjectFile(("logo.bin",), b"\xffok"))
    assert SpecProfiles(Spec(files)).standing("mine.yaml", "app") == Standing(("closed-tree",), (), (
        InitFile(("AGENTS.md",), "agents\n", True), InitFile(("logo.bin",), "�ok", False)))
    assert SpecProfiles(Spec()).standing("mine.yaml", "app").init_files == ()


def test_a_profile_whose_origin_spec_refuses_cannot_be_checked():
    with pytest.raises(ProfileUnusable, match="no such profile"):
        SpecProfiles(Spec(origin=ProfileRefused("no such profile"))).standing("mine.yaml", "app")


def test_the_profiles_a_project_knows_are_spec_s():
    assert SpecProfiles(Spec()).known(Path("/p/app")) == ("mine.yaml", "cli")
    assert SpecProfiles(Spec()).known(Path("/p/none")) == ("cli",)


def test_what_the_format_says_of_a_key_is_its_example_its_name_and_what_holds_it_and_nothing_for_no_key():
    assert SpecProfiles(Spec()).key("parts.types_only") == KeyFacts("parts:\n  a: {}\n", "types_only", "part")
    assert SpecProfiles(Spec()).key("parts.nothing") == KeyFacts()
