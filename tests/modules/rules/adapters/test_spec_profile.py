"""Rules' Profiles read from spec's contract: the profile view becomes the profile as the checks see it, the origin keeps
each looseness, and the init files are compared as text."""
import pytest

from xarch.kernel.logic.capabilities import EXACT, PARTIAL, Shortfall, Supply
from xarch.kernel.logic.language import LanguageView
from xarch.kernel.logic.origin import Loosened, Origin
from xarch.kernel.logic.placement import Excluded, Repeat, Target
from xarch.kernel.logic.project_file import ProjectFile
from xarch.kernel.logic.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns, TierView
from xarch.modules.rules.adapters.spec_profile import SpecProfiles, WrittenChecks
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.rule import APP, MAY_NOT, Condition, Match, Rule, Saying, Scope
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
                    holds="functions", no_callbacks=True, shared=2),
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
                      closed_tree=True, no_duplicates=4, no_twins=3, no_twins_renamed=4, no_twins_subset=3, dead_code=True,
                      untested=True, pass_through=("api",),
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
        no_twins_renamed=4, no_twins_subset=3,
        dead_code=True, pass_through=("api",), untested=True, holds={"core": "functions"},
        types_only={"api": ("core",)}, no_callbacks=("core",), names={"api": ("*Api",)}, built_by={"api": ("core",)},
        shared={"core": 2}, private_imports=True, hints={"rules": "ask first"})


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


CHECK = {"read": ("call",), "in": {"files": "app", "part": "core", "tier": "", "where": ()}, "keep": ("target-placed",),
         "except": (), "mode": "fail", "message": "{where} calls {path}", "fix": "do not", "once_per": ("line",),
         "cases": ({"when": ("of-kind call",), "message": "c", "fix": "f", "once_per": ()},),
         "examples": {"flagged": (("core/a.py", "x()\n"),), "clean": (("core/b.py", "\n"),)},
         "may_not": ({"kind": "path", "values": ("app.api", ".run()")}, {"kind": "part", "values": ("api",)})}
SUPPLIES = LanguageView("Toy", supplies=(Supply("call", EXACT), Supply("import", PARTIAL, "no star imports")))


def test_a_check_the_profile_writes_becomes_a_rule_with_its_examples_and_its_key():
    (own,) = WrittenChecks().own({"no-api": CHECK}, SUPPLIES)
    assert own.rule == Rule("no-api", Scope(APP, "core"), ("call",), MAY_NOT,
                            (Match("path", names=(("app", "api"), ("", "run()"))), Match("part", words=("api",))),
                            (Saying("c", "f", (Condition("of-kind", "call"),)), Saying("{where} calls {path}", "do not",
                                                                                      once=("line",))),
                            keep=(Condition("target-placed"),), key="checks.no-api")
    assert (own.flagged, own.clean) == ((("core/a.py", "x()\n"),), (("core/b.py", "\n"),))


def test_a_check_with_words_that_do_not_apply_or_a_fact_the_language_lacks_is_refused_naming_each_problem():
    bad = {**CHECK, "keep": ("publc",), "mode": "fial"}
    lacking = {**CHECK, "read": ("class",), "keep": (), "cases": (), "message": "{name}", "may_not": (
        {"kind": "exist", "values": ()},)}
    with pytest.raises(ProfileUnusable) as refused:
        WrittenChecks().own({"no-api": bad, "named": lacking}, SUPPLIES)
    assert refused.value.reason == (
        "checks.no-api.keep: no filter is named 'publc': did you mean public or placed?; checks.no-api.mode: is 'fial': "
        "write fail (a finding fails the check) or list (it is listed as weak and fails only `check --strict`); "
        "checks.named: needs class (the classes a file defines at the top level: name, bases, line), which the reader "
        "of Toy does not supply: read another kind of fact, or drop the check")


def test_a_check_that_reads_a_fact_the_language_supplies_partly_is_approximate():
    importing = {**CHECK, "read": ("import",), "keep": (), "cases": (), "message": "{package}", "may_not": (
        {"kind": "exist", "values": ()},)}
    checks = WrittenChecks().own({"imports": importing}, SUPPLIES)
    assert WrittenChecks().approximate(checks, SUPPLIES) == (Shortfall("checks.imports", "import", "no star imports"),)
