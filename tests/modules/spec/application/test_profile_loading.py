"""Use case: a profile file is read by the loader, and a profile that says what it is based on is compared with that
bundled profile, whatever bundled profile matches it higher."""
from pathlib import Path

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from tests.modules.spec.application.origins import BASE, OTHER
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import CheckProfile, Loosened, Problem, ProfileChecked

APP = Path("/p/app")
PRESET = {"files": ["test_*.py"], "declared": [{"function": "test_*"}]}
MINE = {"name": "mine", "testing": "kit", "parts": {
    "core/": {"role": "rules", "uses": {"never": "pure"}},
    "store/": {"role": "storage", "imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}},
    "edge/": {"role": "entry", "imports": {"may": "everything", "libraries": "everything"}}},
    "never": {"pure": ["socket"]}}


def ports(custom: dict) -> FakeArchitectureFiles:
    return FakeArchitectureFiles({"base": BASE, "other": OTHER}, {"mine.yaml": custom},
                                 {"guard.py": "check()\n"}, {"kit": PRESET})


def controller(custom: dict) -> SpecController:
    return spec_controller(ports(custom))


def problems(custom: dict) -> tuple[Problem, ...]:
    checked = controller(custom).check_profile(CheckProfile(APP, "mine.yaml"))
    assert isinstance(checked, ProfileChecked)
    return checked.problems


def test_a_profile_is_loaded_with_its_preset_read_from_the_files_port():
    assert problems(MINE) == ()
    framework = controller(MINE).profile("mine.yaml").framework
    assert framework is not None and framework.files == ("test_*.py",)


def test_a_preset_the_files_port_does_not_hold_is_refused_listing_the_ones_it_does():
    assert problems(MINE | {"testing": "nope"}) == (
        Problem("load", "mine.yaml: testing: no preset 'nope': use kit, or write the map {files, declared}"),)


def test_without_saying_so_a_profile_is_compared_with_the_bundled_one_of_highest_match():
    origin = controller(MINE).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("base", "closest")


def test_a_profile_says_which_bundled_profile_it_is_based_on_and_is_compared_with_that_one():
    origin = controller(MINE | {"based_on": "other"}).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("other", "based_on")
    assert origin.looser == ()


def test_based_on_a_bundled_profile_the_looseness_is_listed_against_it():
    origin = controller(MINE | {"based_on": "base"}).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("base", "based_on")
    assert Loosened("imports.libraries", "store", "requests",
                    "store may also import requests (parts.store.imports.libraries)") in origin.looser
