"""Use case: a profile file is read by the loader of format 2, format 1 is refused, and a profile that says what it is
based on is compared with that bundled profile, whatever it shares most parts with."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from tests.modules.spec.application.origins import BASE, OTHER
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import Loosened
from xarch.modules.spec.domain.errors import InvalidArchitecture

PRESET = {"files": ["test_*.py"], "functions": "test_*"}
MINE = {"xarch": 2, "name": "mine", "testing": "kit", "parts": {
    "core": {"path": "core", "role": "rules", "forbidden": "pure"},
    "store": {"path": "store", "role": "storage", "may_import": ["core"], "libraries": ["sqlmodel", "requests"]},
    "edge": {"path": "edge", "role": "entry", "may_import": "everything", "libraries": "everything"}},
    "forbidden": {"pure": ["socket"]}}


def ports(custom: dict) -> FakeArchitectureFiles:
    return FakeArchitectureFiles({"base": BASE, "other": OTHER}, {"mine.yaml": custom},
                                 {"guard.py": "check()\n"}, {"kit": PRESET})


def service(custom: dict) -> ArchitectureService:
    return ArchitectureService(ports(custom))


def controller(custom: dict) -> SpecController:
    return spec_controller(ports(custom))


def test_a_profile_in_format_2_is_loaded_with_its_preset_read_from_the_files_port():
    architecture = service(MINE).load("mine.yaml")
    assert architecture.name == "mine"
    assert architecture.framework is not None and architecture.framework.files == ("test_*.py",)


def test_a_profile_in_format_1_is_refused_saying_to_migrate_it():
    with pytest.raises(InvalidArchitecture) as caught:
        service(MINE | {"xarch": 1}).load("mine.yaml")
    assert caught.value.problems == ("mine.yaml: format 1 is no longer read: run `xarch profile migrate mine.yaml` to "
                                     "convert it to format 2",)


def test_a_preset_the_files_port_does_not_hold_is_refused_listing_the_ones_it_does():
    with pytest.raises(InvalidArchitecture) as caught:
        service(MINE | {"testing": "nope"}).load("mine.yaml")
    assert caught.value.problems == ("mine.yaml: testing: no preset 'nope': use kit, or write the map {files, functions}",)


def test_without_saying_so_a_profile_resembles_the_bundled_one_sharing_most_parts():
    assert controller(MINE).origin("mine.yaml").closest == "base"


def test_a_profile_says_which_bundled_profile_it_is_based_on_and_is_compared_with_that_one():
    origin = controller(MINE | {"based_on": "other"}).origin("mine.yaml")
    assert origin.closest == "other"
    assert origin.looser == ()


def test_based_on_a_bundled_profile_the_looseness_is_listed_against_it():
    origin = controller(MINE | {"based_on": "base"}).origin("mine.yaml")
    assert origin.closest == "base"
    assert Loosened("libraries", "store", "requests") in origin.looser
