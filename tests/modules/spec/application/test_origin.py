"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from tests.modules.spec.application.origins import BASE, OFF, OTHER, PARTS, TESTING, TIER, part
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import Loosened, Origin, ProfileRefused


def held(may: list[str], must: list[str] | None = None) -> dict:
    """The imports of the store part with its outside packages kept: what it may import and must import."""
    return {"may": may, "libraries": ["sqlmodel"]} | ({"must": must} if must else {})


def controller(custom: dict) -> SpecController:
    return spec_controller(FakeArchitectureFiles({"base": BASE, "other": OTHER}, {"mine.yaml": custom},
                                                 {"guard.py": "check()\n"}))


@pytest.mark.parametrize("given, when, then", [
    pytest.param(BASE, "base", Origin("base", True, None, OFF, OFF, ()),
                 id="a bundled profile lists the guards it leaves off as its own defaults"),
    pytest.param({"name": "mine"}, "mine.yaml", ProfileRefused("mine.yaml: missing `parts`"),
                 id="a profile that does not load is refused with why"),
])
def test_origin(given, when, then):
    assert controller(given).origin(when) == then


def test_a_copy_of_a_bundled_profile_is_compared_with_it_and_found_no_looser():
    origin = controller(BASE).origin("mine.yaml")
    assert (origin.bundled, origin.compared, origin.looser) == (False, "base", ())
    assert (origin.chosen_by, origin.match, origin.low) == ("closest", 1.0, False)
    assert origin.baseline_off == origin.guards_off


def test_every_way_a_custom_profile_is_looser_than_the_bundled_one_it_resembles_is_listed():
    parts = {**PARTS, "core": {**PARTS["core"], "imports": {"may": ["store"], "libraries": ["yaml"]}},
             "store": {"path": "store", "role": "storage",
                       "imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "never": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "imports"}
                        | {"uses": {"apply_never": False}, "imports": {"also": ["edge"]}}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
              "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    origin = controller(custom).origin("mine.yaml")
    assert origin.compared == "base"
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", *OFF[2:])
    assert origin.baseline_off == OFF
    assert origin.looser == (
        Loosened("imports.may", "core", "store", "core may also import store (parts.core.imports.may)"),
        Loosened("imports.libraries", "core", "yaml", "core may also import yaml (parts.core.imports.libraries)"),
        Loosened("imports.libraries", "store", "requests", "store may also import requests (parts.store.imports.libraries)"),
        Loosened("uses.never", "core", "time.time", "core no longer forbids time.time (parts.core.uses.never)"),
        Loosened("untested", "store", "", "store is newly marked untested (parts.store.untested)"),
        Loosened("imports.types_only", "unit", "store",
                 "the unit tests may now call store (tiers.unit.imports.types_only)"),
        Loosened("imports.also", "unit", "edge", "the unit tests may also import edge (tiers.unit.imports.also)"),
        Loosened("uses.apply_never", "unit", "",
                 "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"),
        Loosened("testing.skips", "", "pytest.mark.xfail", "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),
        Loosened("files.pinned", "", "tests/test_rules.py", "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)"))


def test_a_stricter_custom_profile_lists_nothing_and_a_broader_ban_covers_a_narrower_one():
    custom = {**BASE, "parts": part("store", imports={"may": [], "libraries": ["sqlmodel"]}) | part("core", uses={"never": "pure"}),
              "never": {"pure": ["time", "socket"]}}
    assert controller(custom).origin("mine.yaml").looser == ()


def test_a_part_that_may_import_any_outside_package_is_looser_than_one_that_lists_them():
    custom = {**BASE, "parts": part("store", imports={"may": ["core"], "libraries": "everything"})}
    assert controller(custom).origin("mine.yaml").looser == (
        Loosened("imports.libraries", "store", "*", "store may import any outside package (parts.store.imports.libraries)"),)


def test_a_custom_profile_sharing_no_part_resembles_no_bundled_profile_and_has_no_baseline():
    custom = {"name": "mine", "parts": {"x": {"path": "x", "role": "all"}}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.compared, origin.match, origin.baseline_off, origin.looser) == (None, None, (), ())
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", *OFF[2:])


def test_the_closest_bundled_profile_is_the_one_of_highest_match_the_first_by_name_on_a_tie():
    custom = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"},
                                 "store": {"path": "store", "role": "y"}}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low) == ("base", "closest", 0.48, True)
    assert controller(OTHER).origin("mine.yaml").compared == "other"
    tie = spec_controller(FakeArchitectureFiles({"zeta": OTHER, "alpha": OTHER}, {"mine.yaml": OTHER}, {}))
    assert tie.origin("mine.yaml").compared == "alpha"


def test_a_part_that_no_longer_has_to_import_or_may_meet_it_with_more_is_looser():
    base = {**BASE, "parts": part("store", imports=held(["core", "edge"], ["core"]))}
    dropped = {**base, "parts": part("store", imports=held(["core"]))}
    wider = {**base, "parts": part("store", imports=held(["core", "edge"], ["core", "edge"]))}
    same = {**base, "parts": part("store", imports=held(["core", "edge"], ["core"]))}
    stricter = {**BASE, "parts": part("store", imports=held(["core", "edge"], ["core"]))}
    files = FakeArchitectureFiles({"base": base}, {"dropped.yaml": dropped, "wider.yaml": wider, "same.yaml": same,
                                                   "stricter.yaml": stricter}, {"guard.py": "check()\n"})
    spec = spec_controller(files)
    assert spec.origin("dropped.yaml").looser == (
        Loosened("imports.must", "store", "", "store no longer has to import anything (parts.store.imports.must)"),)
    assert spec.origin("wider.yaml").looser == (
        Loosened("imports.must", "store", "edge", "store may also meet imports.must with edge (parts.store.imports.must)"),)
    assert spec.origin("same.yaml").looser == ()
    assert spec.origin("stricter.yaml").looser == ()
