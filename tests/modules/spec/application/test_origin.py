"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
from dataclasses import replace

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


THEIRS = {**BASE, "name": "theirs"}
"""A copy of base at a path, for --against to name."""


def against(custom: dict) -> SpecController:
    """The controller over base and other, bundled, and mine.yaml (custom, as given), theirs.yaml (a copy of base) and
    broken.yaml (a profile that does not load), at their paths."""
    return spec_controller(FakeArchitectureFiles({"base": BASE, "other": OTHER},
                                                 {"mine.yaml": custom, "theirs.yaml": THEIRS,
                                                  "broken.yaml": {"name": "broken"}},
                                                 {"guard.py": "check()\n"}))


def test_against_a_bundled_profile_wins_over_the_one_based_on_names_and_keeps_based_on_to_say():
    origin = against({**BASE, "based_on": "base"}).origin("mine.yaml", against="other")
    assert (origin.bundled, origin.compared, origin.chosen_by, origin.based_on) == (False, "other", "against", "base")


def test_against_a_path_compares_with_the_profile_file_there():
    origin = against(BASE).origin("mine.yaml", against="theirs.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low, origin.looser) == (
        "theirs.yaml", "against", 1.0, False, ())


def test_against_the_profile_in_force_itself_matches_it_whole_and_finds_nothing_looser():
    origin = against(BASE).origin("mine.yaml", against="mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low, origin.looser) == (
        "mine.yaml", "against", 1.0, False, ())


@pytest.mark.parametrize("given, reason", [
    pytest.param("broken.yaml", "--against does not load: broken.yaml: missing `parts`",
                 id="a profile file that does not load is refused with the loader's problem"),
    pytest.param("gone.yaml", "--against does not load: gone.yaml: cannot read the file: no such file",
                 id="a path that holds no file is refused"),
    pytest.param("nosuch", "--against does not load: nosuch: no bundled architecture 'nosuch': use one of base, "
                           "other, or a path to a .yaml or .json file",
                 id="a name that is no bundled profile is refused with the ones that are"),
])
def test_against_a_profile_that_does_not_load_is_refused(given, reason):
    assert against(BASE).origin("mine.yaml", against=given) == ProfileRefused(reason)


def test_the_profile_in_force_is_loaded_before_against_is_read():
    assert against({"name": "mine"}).origin("mine.yaml", against="nosuch") == ProfileRefused(
        "mine.yaml: missing `parts`")


def test_a_bundled_profile_with_against_is_compared_as_a_copy_of_it_would_be():
    spec = against(BASE)
    origin = spec.origin("base", against="other")
    assert (origin.bundled, origin.compared, origin.chosen_by, origin.higher) == (True, "other", "against", None)
    assert origin.match is not None
    assert origin == replace(spec.origin("mine.yaml", against="other"), location="base", bundled=True)
    assert spec.origin("base", against="theirs.yaml").match == 1.0


def test_against_a_profile_no_part_pairs_with_is_still_compared_and_its_match_is_low():
    origin = against({"name": "mine", "parts": {"x": {"path": "x", "role": "all"}}}).origin("mine.yaml", against="base")
    assert (origin.compared, origin.chosen_by, origin.low) == ("base", "against", True)
    assert origin.counts[0][:2] == ("parts", 0)


def test_against_names_no_bundled_profile_of_higher_match():
    spec = against(BASE)
    assert spec.origin("mine.yaml").compared == "base"
    origin = spec.origin("mine.yaml", against="other")
    assert (origin.compared, origin.higher) == ("other", None)


def test_without_against_based_on_is_not_carried():
    origin = against({**BASE, "based_on": "base"}).origin("mine.yaml")
    assert (origin.chosen_by, origin.based_on) == ("based_on", "")
