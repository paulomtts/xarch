"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Loosened, ProfileOrigin

TESTING = {"files": ["test_*.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.mark.xfail"]}
TIER = {"proves": "a rule", "litmus": "Does it call a rule?", "apply_forbidden": True, "types_only": ["store"]}
PARTS = {"core": {"path": "core", "role": "rules", "may_import": [], "forbidden": "pure", "tier": "unit"},
         "store": {"path": "store", "role": "storage", "may_import": ["core"], "libraries": ["sqlmodel"],
                   "tier": "unit"},
         "edge": {"path": "edge", "role": "entry", "may_import": "everything", "libraries": "everything",
                  "untested": "it only wires"}}
BASE = {"xarch": 2, "name": "base", "parts": PARTS, "forbidden": {"pure": ["time.time", "socket"]},
        "testing": TESTING, "tiers": {"unit": TIER}, "guards": {"no-comments": {}},
        "files": {"tests/test_rules.py": {"from": "guard.py", "pinned": True}}}
OTHER = {"xarch": 2, "name": "other", "parts": {"web": {"path": "web", "role": "all"}}}


def part(name: str, **changes) -> dict:
    return {**PARTS, name: {**PARTS[name], **changes}}


def controller(custom: dict) -> SpecController:
    architectures = ArchitectureService(FakeArchitectureFiles({"base": BASE, "other": OTHER},
                                                              {"mine.yaml": custom}, {"guard.py": "check()\n"}))
    return SpecController(SkeletonService(FakeSettings(None, None, None), architectures), architectures)


def test_a_bundled_profile_lists_the_guards_it_leaves_off_as_its_own_defaults():
    origin = controller(BASE).origin("base")
    assert origin == ProfileOrigin("base", True, None, ("package-only", "scenario-coverage", "stand-ins", "closed-tree"),
                                   ("package-only", "scenario-coverage", "stand-ins", "closed-tree"), ())


def test_a_copy_of_a_bundled_profile_is_compared_with_it_and_found_no_looser():
    origin = controller(BASE).origin("mine.yaml")
    assert (origin.bundled, origin.closest, origin.looser) == (False, "base", ())
    assert origin.baseline_off == origin.guards_off


def test_every_way_a_custom_profile_is_looser_than_the_bundled_one_it_resembles_is_listed():
    parts = {**PARTS, "core": {**PARTS["core"], "may_import": ["store"], "libraries": ["yaml"]},
             "store": {"path": "store", "role": "storage", "may_import": ["core"],
                       "libraries": ["sqlmodel", "requests"], "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "forbidden": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "types_only"}
                        | {"apply_forbidden": False}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
              "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    origin = controller(custom).origin("mine.yaml")
    assert origin.closest == "base"
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree")
    assert origin.baseline_off == ("package-only", "scenario-coverage", "stand-ins", "closed-tree")
    assert origin.looser == (
        Loosened("may_import", "core", "store"),
        Loosened("libraries", "core", "yaml"), Loosened("libraries", "store", "requests"),
        Loosened("forbidden", "core", "time.time"),
        Loosened("untested", "store"),
        Loosened("types_only", "unit", "store"),
        Loosened("apply_forbidden", "unit"),
        Loosened("testing.skips", "", "pytest.mark.xfail"),
        Loosened("files.pinned", "", "tests/test_rules.py"))


def test_a_stricter_custom_profile_lists_nothing_and_a_broader_ban_covers_a_narrower_one():
    custom = {**BASE, "parts": part("store", may_import=[]) | part("core", forbidden="pure"),
              "forbidden": {"pure": ["time", "socket"]}}
    assert controller(custom).origin("mine.yaml").looser == ()


def test_a_part_that_may_import_any_outside_package_is_looser_than_one_that_lists_them():
    custom = {**BASE, "parts": part("store", libraries="everything")}
    assert controller(custom).origin("mine.yaml").looser == (Loosened("libraries", "store", "*"),)


def test_a_custom_profile_sharing_no_part_resembles_no_bundled_profile_and_has_no_baseline():
    custom = {"xarch": 2, "name": "mine", "parts": {"x": {"path": "x", "role": "all"}}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.closest, origin.baseline_off, origin.looser) == (None, (), ())
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree")


def test_the_closest_bundled_profile_is_the_one_sharing_the_most_parts_the_first_by_name_on_a_tie():
    custom = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"},
                                 "store": {"path": "store", "role": "y"}}}
    assert controller(custom).origin("mine.yaml").closest == "base"
    assert controller(OTHER).origin("mine.yaml").closest == "other"
    tie = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"}}}
    assert controller(tie).origin("mine.yaml").closest == "base"
