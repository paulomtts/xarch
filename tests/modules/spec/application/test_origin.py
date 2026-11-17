"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from tests.modules.spec.application.origins import BASE, OFF, OTHER, PARTS, TESTING, TIER, part
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import Loosened, Origin, ProfileRefused


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
    assert (origin.bundled, origin.closest, origin.looser) == (False, "base", ())
    assert origin.baseline_off == origin.guards_off


def test_every_way_a_custom_profile_is_looser_than_the_bundled_one_it_resembles_is_listed():
    parts = {**PARTS, "core": {**PARTS["core"], "may_import": ["store"], "libraries": ["yaml"]},
             "store": {"path": "store", "role": "storage", "may_import": ["core"],
                       "libraries": ["sqlmodel", "requests"], "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "forbidden": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "types_only"}
                        | {"apply_forbidden": False, "may_also_import": ["edge"]}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
              "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    origin = controller(custom).origin("mine.yaml")
    assert origin.closest == "base"
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", *OFF[2:])
    assert origin.baseline_off == OFF
    assert origin.looser == (
        Loosened("may_import", "core", "store", "core may also import store (parts.core.may_import)"),
        Loosened("libraries", "core", "yaml", "core may also import yaml (parts.core.libraries)"),
        Loosened("libraries", "store", "requests", "store may also import requests (parts.store.libraries)"),
        Loosened("forbidden", "core", "time.time", "core no longer forbids time.time (parts.core.forbidden)"),
        Loosened("untested", "store", "", "store is newly marked untested (parts.store.untested)"),
        Loosened("types_only", "unit", "store", "the unit tests may now call store (tiers.unit.types_only)"),
        Loosened("may_also_import", "unit", "edge", "the unit tests may also import edge (tiers.unit.may_also_import)"),
        Loosened("apply_forbidden", "unit", "",
                 "the unit tests are no longer held to their part's forbidden list (tiers.unit.apply_forbidden)"),
        Loosened("testing.skips", "", "pytest.mark.xfail", "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),
        Loosened("files.pinned", "", "tests/test_rules.py", "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)"))


def test_a_stricter_custom_profile_lists_nothing_and_a_broader_ban_covers_a_narrower_one():
    custom = {**BASE, "parts": part("store", may_import=[]) | part("core", forbidden="pure"),
              "forbidden": {"pure": ["time", "socket"]}}
    assert controller(custom).origin("mine.yaml").looser == ()


def test_a_part_that_may_import_any_outside_package_is_looser_than_one_that_lists_them():
    custom = {**BASE, "parts": part("store", libraries="everything")}
    assert controller(custom).origin("mine.yaml").looser == (
        Loosened("libraries", "store", "*", "store may import any outside package (parts.store.libraries)"),)


def test_a_custom_profile_sharing_no_part_resembles_no_bundled_profile_and_has_no_baseline():
    custom = {"name": "mine", "parts": {"x": {"path": "x", "role": "all"}}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.closest, origin.baseline_off, origin.looser) == (None, (), ())
    assert origin.guards_off == ("package-only", "scenario-coverage", "no-comments", *OFF[2:])


def test_the_closest_bundled_profile_is_the_one_sharing_the_most_parts_the_first_by_name_on_a_tie():
    custom = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"},
                                 "store": {"path": "store", "role": "y"}}}
    assert controller(custom).origin("mine.yaml").closest == "base"
    assert controller(OTHER).origin("mine.yaml").closest == "other"
    tie = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"}}}
    assert controller(tie).origin("mine.yaml").closest == "base"


def test_a_part_that_no_longer_has_to_import_or_may_meet_it_with_more_is_looser():
    base = {**BASE, "parts": part("store", may_import=["core", "edge"], must_import=["core"])}
    dropped = {**base, "parts": part("store", may_import=["core"])}
    wider = {**base, "parts": part("store", may_import=["core", "edge"], must_import=["core", "edge"])}
    same = {**base, "parts": part("store", may_import=["core", "edge"], must_import=["core"])}
    stricter = {**BASE, "parts": part("store", may_import=["core", "edge"], must_import=["core"])}
    files = FakeArchitectureFiles({"base": base}, {"dropped.yaml": dropped, "wider.yaml": wider, "same.yaml": same,
                                                   "stricter.yaml": stricter}, {"guard.py": "check()\n"})
    spec = spec_controller(files)
    assert spec.origin("dropped.yaml").looser == (
        Loosened("must_import", "store", "", "store no longer has to import anything (parts.store.must_import)"),)
    assert spec.origin("wider.yaml").looser == (
        Loosened("must_import", "store", "edge", "store may also meet must_import with edge (parts.store.must_import)"),)
    assert spec.origin("same.yaml").looser == ()
    assert spec.origin("stricter.yaml").looser == ()
