"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Loosened, ProfileOrigin

TESTS = {"files": ["test_*.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.mark.xfail"]}
TIER = {"name": "unit", "subject": ["core", "store"], "proves": "a rule", "may_touch": "nothing",
        "litmus": "Does it call a rule?", "forbidden": True, "types_only": ["store"]}
BASE = {"xarch": 1, "name": "base", "layout": {"core": {}, "store": {}, "edge": {}},
        "parts": {"core": {"path": "core", "role": "rules"}, "store": {"path": "store", "role": "storage"},
                  "edge": {"path": "edge", "role": "entry", "untested": "it only wires"}},
        "rules": {"core": [], "store": ["core"], "edge": ["*"]},
        "libraries": {"store": ["sqlmodel"]},
        "forbidden": {"core": ["time.time", "socket"]},
        "tests": TESTS, "tiers": [TIER],
        "guards": {"no-comments": {}},
        "files": {"tests/test_rules.py": {"from": "guard.py", "pinned": True}}}
OTHER = {"xarch": 1, "name": "other", "layout": {"web": {}}, "parts": {"web": {"path": "web", "role": "all"}},
         "rules": {"web": []}}


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
    custom = {**BASE, "rules": {"core": ["store"], "store": ["core"], "edge": ["*"]},
              "libraries": {"store": ["sqlmodel", "requests"], "core": ["yaml"]},
              "forbidden": {"core": ["socket"]},
              "parts": {**BASE["parts"], "store": {"path": "store", "role": "storage", "untested": "trust me"}},
              "tiers": [{key: value for key, value in TIER.items() if key != "types_only"}
                        | {"subject": ["core"], "forbidden": False}],
              "tests": {**TESTS, "skips": ["pytest.mark.skip"]},
              "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    origin = controller(custom).origin("mine.yaml")
    assert origin.closest == "base"
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree")
    assert origin.baseline_off == ("package-only", "scenario-coverage", "stand-ins", "closed-tree")
    assert origin.looser == (
        Loosened("rules", "core", "store"),
        Loosened("libraries", "core", "yaml"), Loosened("libraries", "store", "requests"),
        Loosened("forbidden", "core", "time.time"),
        Loosened("untested", "store"),
        Loosened("types_only", "unit", "store"),
        Loosened("tier_forbidden", "unit"),
        Loosened("skips", "", "pytest.mark.xfail"),
        Loosened("pinned", "", "tests/test_rules.py"))


def test_a_stricter_custom_profile_lists_nothing_and_a_broader_ban_covers_a_narrower_one():
    custom = {**BASE, "rules": {"core": [], "store": [], "edge": ["*"]}, "libraries": {},
              "forbidden": {"core": ["time", "socket"], "store": ["socket"]}}
    assert controller(custom).origin("mine.yaml").looser == ()


def test_unchecked_libraries_are_looser_than_checked_ones():
    custom = {key: value for key, value in BASE.items() if key != "libraries"}
    assert controller(custom).origin("mine.yaml").looser == (Loosened("libraries", ""),)


def test_a_custom_profile_sharing_no_part_resembles_no_bundled_profile_and_has_no_baseline():
    custom = {"xarch": 1, "name": "mine", "layout": {"x": {}}, "parts": {"x": {"path": "x", "role": "all"}},
              "rules": {"x": []}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.closest, origin.baseline_off, origin.looser) == (None, (), ())
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree")


def test_the_closest_bundled_profile_is_the_one_sharing_the_most_parts_the_first_by_name_on_a_tie():
    custom = {**OTHER, "layout": {"web": {}, "core": {}, "store": {}},
              "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"}, "store": {"path": "store", "role": "y"}},
              "rules": {"web": [], "core": [], "store": []}}
    assert controller(custom).origin("mine.yaml").closest == "base"
    assert controller(OTHER).origin("mine.yaml").closest == "other"
    tie = {**OTHER, "layout": {"web": {}, "core": {}}, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"}},
           "rules": {"web": [], "core": []}}
    assert controller(tie).origin("mine.yaml").closest == "base"
