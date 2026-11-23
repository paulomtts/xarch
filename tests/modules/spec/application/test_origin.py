"""Use case: where the profile in force comes from, and how it is looser than the bundled profile it resembles."""
from dataclasses import replace

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from tests.modules.spec.application.origins import BASE, OFF, OTHER, PARTS, TESTING, TIER, part
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import Loosened, Origin, ProfileRefused, ProfileView


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


TEAM = {**BASE, "name": "team", "based_on": "base", "guards": {"no-comments": {}, "closed-tree": {}}}
"""A profile file based on base that switches closed-tree on too."""
LIT = {**BASE, "name": "lit", "parts": {**PARTS, "core": {**PARTS["core"], "litmus": "Does it decide?"},
                                       "store": {**PARTS["store"], "litmus": "Does it keep?"}}}
"""A bundled profile that gives core and store a litmus."""


def chained(files: dict, bundled: dict | None = None) -> SpecController:
    """The controller over base and other, bundled (or the bundled profiles given), and the profile files given, by
    their exact location: a file read from a wrong folder is a file that cannot be read."""
    return spec_controller(FakeArchitectureFiles({"base": BASE, "other": OTHER} if bundled is None else bundled, files,
                                                 {"guard.py": "check()\n"}))


def test_a_based_on_path_is_read_from_the_folder_of_the_profile_and_compared_with_as_written():
    decoy = {**BASE, "name": "decoy", "guards": {}}
    mine = {**TEAM, "name": "mine", "based_on": "../team.yaml"}
    origin = chained({"sub/mine.yaml": mine, "team.yaml": TEAM, "../team.yaml": decoy}).origin("sub/mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.anchor) == ("../team.yaml", "based_on", "base")
    assert (origin.match, origin.looser) == (1.0, ())


def test_a_based_on_path_with_no_suffix_is_read_as_a_file_and_never_as_a_bundled_name():
    mine = {**TEAM, "name": "mine", "based_on": "../team"}
    origin = chained({"sub/mine.yaml": mine, "team": TEAM}, {"base": BASE, "team": OTHER}).origin("sub/mine.yaml")
    assert (origin.compared, origin.match, origin.anchor) == ("../team", 1.0, "base")


MINE = {**BASE, "name": "mine", "based_on": "../team.yaml"}
"""A copy of base at sub/mine.yaml based on team.yaml, by its path from sub/."""


def test_a_file_of_the_chain_that_does_not_load_refuses_the_profile_with_its_first_problem():
    assert chained({"sub/mine.yaml": MINE, "team.yaml": {"name": "team"}}).origin("sub/mine.yaml") == ProfileRefused(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: missing `parts`")
    many = chained({"sub/mine.yaml": MINE, "team.yaml": {"colour": 1}}).origin("sub/mine.yaml")
    assert many.reason.startswith(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: unknown key 'colour'")
    assert many.reason.endswith(" (and 2 more)")
    assert chained({"sub/mine.yaml": MINE}).origin("sub/mine.yaml") == ProfileRefused(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: cannot read the file: no such file")


def test_a_deeper_file_that_does_not_load_is_said_from_the_file_of_the_chain_that_names_it():
    files = {"mine.yaml": {**BASE, "name": "mine", "based_on": "a.yaml"},
             "a.yaml": {**BASE, "name": "a", "based_on": "b.yaml"}, "b.yaml": {"name": "b"}}
    assert chained(files).origin("mine.yaml") == ProfileRefused(
        "a.yaml: based_on: b.yaml does not load: b.yaml: missing `parts`")


@pytest.mark.parametrize("files, location, reason", [
    pytest.param({"mine.yaml": {**BASE, "based_on": "a.yaml"}, "a.yaml": {**BASE, "based_on": "mine.yaml"}},
                 "mine.yaml", "mine.yaml: based_on: a.yaml is based on this profile", id="two files"),
    pytest.param({"p/q/mine.yaml": {**BASE, "based_on": "../a.yaml"}, "p/a.yaml": {**BASE, "based_on": "../b.yaml"},
                  "b.yaml": {**BASE, "based_on": "p/q/mine.yaml"}},
                 "p/q/mine.yaml", "p/q/mine.yaml: based_on: ../a.yaml is based on this profile, through ../b.yaml",
                 id="three files name the one between"),
    pytest.param({"mine.yaml": {**BASE, "based_on": "mine.yaml"}}, "mine.yaml",
                 "mine.yaml: based_on: mine.yaml is based on this profile", id="a profile based on itself"),
    pytest.param({"mine.yaml": {**BASE, "based_on": "a.yaml"}, "a.yaml": {**BASE, "based_on": "b.yaml"},
                  "b.yaml": {**BASE, "based_on": "a.yaml"}},
                 "mine.yaml", "a.yaml: based_on: b.yaml is based on this profile",
                 id="a loop the profile in force is not in"),
])
def test_a_chain_that_comes_back_to_a_file_of_it_refuses_the_profile(files, location, reason):
    assert chained(files).origin(location) == ProfileRefused(reason)


def test_the_anchor_is_the_bundled_profile_the_chain_ends_on_else_the_one_closest_to_its_last_file_else_none():
    ends = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": TEAM})
    assert ends.origin("mine.yaml").anchor == "base"
    closest = chained({"mine.yaml": {**OTHER, "name": "mine", "based_on": "team.yaml"},
                       "team.yaml": {**BASE, "name": "team"}}).origin("mine.yaml")
    assert (closest.anchor, closest.higher[0]) == ("base", "other")
    alone = {"name": "alone", "parts": {"y": {"path": "y", "role": "all"}}}
    none = chained({"mine.yaml": {**alone, "name": "mine", "based_on": "team.yaml"}, "team.yaml": alone}).origin(
        "mine.yaml")
    assert (none.anchor, none.baseline_off) == (None, ())


def test_a_guard_the_profile_file_leaves_off_and_the_anchor_switches_on_is_not_excused():
    lax = {**BASE, "guards": {}}
    origin = chained({"mine.yaml": {**lax, "name": "mine", "based_on": "team.yaml"},
                      "team.yaml": {**lax, "name": "team", "based_on": "base"}}).origin("mine.yaml")
    assert "no-comments" in origin.guards_off and "no-comments" not in origin.baseline_off
    assert origin.baseline_off == OFF


def test_a_guard_the_profile_file_switches_on_and_the_anchor_leaves_off_is_not_excused():
    origin = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"},
                      "team.yaml": TEAM}).origin("mine.yaml")
    assert "closed-tree" in origin.guards_off and "closed-tree" not in origin.baseline_off


def test_a_litmus_the_profile_file_gives_and_one_the_anchor_gives_are_both_demanded():
    team = {**BASE, "name": "team", "based_on": "lit", "parts": part("store", litmus="Does it keep?")}
    origin = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": team},
                     {"lit": LIT}).origin("mine.yaml")
    assert origin.looser == (
        Loosened("litmus", "store", "",
                 "store has no litmus, though the profile it is compared with gives it one (parts.store.litmus)"),
        Loosened("litmus", "core", "lit",
                 "core has no litmus, though lit, which --strict rests on, gives the part it pairs with one "
                 "(parts.core.litmus)"))


def test_with_against_a_path_based_on_is_said_beside_it_rests_on_nothing_and_its_chain_still_refuses():
    files = {"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": TEAM}
    origin = chained(files).origin("mine.yaml", against="other")
    assert (origin.compared, origin.chosen_by, origin.based_on, origin.anchor) == (
        "other", "against", "team.yaml", None)
    broken = chained({"mine.yaml": files["mine.yaml"]}).origin("mine.yaml", against="other")
    assert broken == ProfileRefused(
        "mine.yaml: based_on: team.yaml does not load: team.yaml: cannot read the file: no such file")


def test_a_bundled_based_on_or_the_closest_is_the_anchor_and_a_bundled_profile_rests_on_none():
    assert against({**BASE, "based_on": "base"}).origin("mine.yaml").anchor == "base"
    assert controller(BASE).origin("mine.yaml").anchor == "base"
    assert controller(BASE).origin("base").anchor is None


def test_only_the_origin_reads_the_chain_so_the_profile_loads_with_its_based_on_file_missing():
    spec = chained({"sub/mine.yaml": MINE})
    assert isinstance(spec.profile("sub/mine.yaml"), ProfileView)
    assert isinstance(spec.origin("sub/mine.yaml"), ProfileRefused)
