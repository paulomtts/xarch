"""Rules' Profiles read from spec's contract: the profile view becomes the profile as the checks see it, the origin keeps
each looseness, and the init files are compared as text."""
from xarch.kernel.errors import DomainError
from xarch.kernel.logic.placement import Repeat, Target
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.domain.values import (
    Exclusion,
    Fakes,
    Fixture,
    Framework,
    InitFile,
    Loosened,
    Origin,
    PartInfo,
    Profile,
    Scenarios,
    TableForm,
)
from xarch.modules.rules.domain.values import StandIns as StandInNames
from xarch.modules.rules.domain.values import TestTier as Tier
from xarch.modules.spec.contract import (
    ExcludedView,
    FakesView,
    FixtureView,
    FrameworkView,
    GuardsView,
    PartView,
    ProfileOrigin,
    ProfileView,
    ProjectFile,
    ScenariosView,
    StandInsView,
    TableView,
    TierView,
)
from xarch.modules.spec.contract import Loosened as SpecLoosened

TABLE = TableView(("pytest", "mark", "parametrize"), ("pytest", "param"), "id")
VIEW = ProfileView(
    parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/", forbidden=(("socket",),),
                    holds="functions", no_callbacks=True),
           PartView("api", ("src", "*", "api"), (Target("core"),), "handlers", shown="api/ of src/<module>",
                    untested="it only wires", must_import=(Target("core"),), types_only=("core",), names=("*Api",),
                    built_by=("core",))),
    folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
    tiers=(TierView("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
    libraries={"core": (), "api": ("fastapi",)}, repeats=(Repeat("module", ("src",)),),
    guards=GuardsView(package_only=("api",), scenarios=ScenariosView("api", "unit", "Result", ("a", "b", "c"), TABLE,
                                                                     "test_{name}.py"),
                      no_comments=True,
                      stand_ins=StandInsView((("m", "Mock"),), (), ("spec",), (FixtureView("mocker", ("Mock",)),)),
                      closed_tree=True, no_duplicates=4, dead_code=True, untested=True, pass_through=("api",),
                      private_imports=True),
    fakes=FakesView(("fakes",), ("api",), "Fake"), framework=FrameworkView(("test_*.py",), "test_*", (("skip",),)),
    excluded=(ExcludedView(("vendor",), "not ours"),), hints={"rules": "ask first"})


class Spec:
    """Spec's controller as rules' adapter uses it, answering from fixed values."""

    def __init__(self, files: tuple[ProjectFile, ...] | None = None):
        self._files = files

    def profile(self, location: str) -> ProfileView:
        return VIEW

    def origin(self, location: str) -> ProfileOrigin:
        return ProfileOrigin("mine.yaml", False, "cli", ("closed-tree",), (), (SpecLoosened("untested", "api"),))

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]:
        if self._files is None:
            raise DomainError("cannot write them")
        return self._files


def test_the_profile_view_becomes_the_profile_the_checks_see():
    assert SpecProfiles(Spec()).profile("mine.yaml") == Profile(
        parts={"core": ("core",), "api": ("src", "*", "api")}, rules={"core": (), "api": (Target("core"),)},
        folders=((), ("core",), ("src",), ("src", "*"), ("src", "*", "api")),
        tiers=(Tier("unit", (Target("core", "none"),), None, ("api",), True, "a rule", "nothing", "Does it?"),),
        libraries={"core": (), "api": ("fastapi",)}, fakes=Fakes(("fakes",), ("api",), "Fake"),
        repeats=(Repeat("module", ("src",)),), package_only=("api",),
        scenarios=Scenarios("api", "unit", "Result", ("a", "b", "c"),
                            TableForm(("pytest", "mark", "parametrize"), ("pytest", "param"), "id"), "test_{name}.py"),
        no_comments=True, stand_ins=StandInNames((("m", "Mock"),), (), ("spec",), (Fixture("mocker", ("Mock",)),)),
        closed_tree=True, framework=Framework(("test_*.py",), "test_*", (("skip",),)),
        forbidden={"core": (("socket",),)},
        info={"core": PartInfo("the rules", "Is it a rule?", "core/"),
              "api": PartInfo("handlers", "", "api/ of src/<module>", "it only wires")},
        excluded=(Exclusion(("vendor",), "not ours"),), must_import={"api": (Target("core"),)}, no_duplicates=4,
        dead_code=True, pass_through=("api",), untested=True, holds={"core": "functions"},
        types_only={"api": ("core",)}, no_callbacks=("core",), names={"api": ("*Api",)}, built_by={"api": ("core",)},
        private_imports=True)


def test_the_origin_keeps_every_looseness():
    assert SpecProfiles(Spec()).origin("mine.yaml") == Origin("mine.yaml", False, "cli", ("closed-tree",), (),
                                                             (Loosened("untested", "api"),))


def test_the_init_files_are_compared_as_text_and_none_when_the_profile_cannot_write_them():
    files = (ProjectFile(("AGENTS.md",), "agents\n", True), ProjectFile(("logo.bin",), b"\xffok"))
    assert SpecProfiles(Spec(files)).init_files("mine.yaml", "app") == (
        InitFile(("AGENTS.md",), "agents\n", True), InitFile(("logo.bin",), "�ok", False))
    assert SpecProfiles(Spec()).init_files("mine.yaml", "app") == ()
