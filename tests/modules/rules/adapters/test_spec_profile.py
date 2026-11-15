"""Rules' Profiles read from spec's contract: the profile view becomes the profile as the checks see it, the origin keeps
each looseness, and the init files are compared as text."""
import pytest

from xarch.kernel.logic.origin import Loosened, Origin
from xarch.kernel.logic.placement import Excluded, Repeat, Target
from xarch.kernel.logic.project_file import ProjectFile
from xarch.kernel.logic.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns, TierView
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.values import InitFile, PartInfo, Profile, Standing
from xarch.modules.spec.contract import (
    FilesResult,
    GuardsView,
    OriginResult,
    PartView,
    ProfileRefused,
    ProfileView,
    ProjectFiles,
)

TABLE = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id")
VIEW = ProfileView(
    parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/", forbidden=(("socket",),),
                    holds="functions", no_callbacks=True),
           PartView("api", ("src", "*", "api"), (Target("core"),), "handlers", shown="api/ of src/<module>",
                    untested="it only wires", must_import=(Target("core"),), types_only=("core",), names=("*Api",),
                    built_by=("core",))),
    folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
    tiers=(TierView("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
    libraries={"core": (), "api": ("fastapi",)}, repeats=(Repeat("module", ("src",)),),
    guards=GuardsView(package_only=("api",), scenarios=ScenarioCoverage("api", "unit", "Result", ("a", "b", "c"), TABLE,
                                                                     "test_{name}.py"),
                      no_comments=True,
                      stand_ins=StandIns((("m", "Mock"),), (), ("spec",), (Fixture("mocker", ("Mock",)),)),
                      closed_tree=True, no_duplicates=4, no_twins=3, dead_code=True, untested=True, pass_through=("api",),
                      private_imports=True),
    fakes=Fakes(("fakes",), ("api",), "Fake"), framework=Framework(("test_*.py",), "test_*", (("skip",),)),
    excluded=(Excluded(("vendor",), "not ours"),), hints={"rules": "ask first"})


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


def test_the_profile_view_becomes_the_profile_the_checks_see():
    assert SpecProfiles(Spec()).profile("mine.yaml") == Profile(
        parts={"core": ("core",), "api": ("src", "*", "api")}, rules={"core": (), "api": (Target("core"),)},
        folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
        tiers=(TierView("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
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
        dead_code=True, pass_through=("api",), untested=True, holds={"core": "functions"},
        types_only={"api": ("core",)}, no_callbacks=("core",), names={"api": ("*Api",)}, built_by={"api": ("core",)},
        private_imports=True, hints={"rules": "ask first"})


def test_the_origin_keeps_every_looseness():
    assert SpecProfiles(Spec()).standing("mine.yaml", "app").origin == Origin(
        "mine.yaml", False, "cli", ("closed-tree",), (), (Loosened("untested", "api"),))


def test_the_init_files_are_compared_as_text_and_none_when_the_profile_cannot_write_them():
    files = (ProjectFile(("AGENTS.md",), "agents\n", True), ProjectFile(("logo.bin",), b"\xffok"))
    assert SpecProfiles(Spec(files)).standing("mine.yaml", "app") == Standing(ORIGIN, (
        InitFile(("AGENTS.md",), "agents\n", True), InitFile(("logo.bin",), "�ok", False)))
    assert SpecProfiles(Spec()).standing("mine.yaml", "app").init_files == ()


def test_a_profile_whose_origin_spec_refuses_cannot_be_checked():
    with pytest.raises(ProfileUnusable, match="no such profile"):
        SpecProfiles(Spec(origin=ProfileRefused("no such profile"))).standing("mine.yaml", "app")
