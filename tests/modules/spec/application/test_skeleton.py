"""Use case: the skeleton of a profile, which the layout and scaffold modules build and check against."""
import keyword

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller
from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.contract import Entry, ProfileRefused, Skeleton

LAYERED = {"name": "layered", "parts": {"src/": {"role": "code"}}}
SPEC = controller(FakeArchitectureFiles({"cli": LAYERED, "broken": {"name": "broken"}}))


@pytest.mark.parametrize("given, when, then", [
    pytest.param(SPEC, "cli", Skeleton((Entry(("src",), True, True),), (), PYTHON.checked.title,
                                       PYTHON.checked.package_file, PYTHON.checked.private,
                                       frozenset(keyword.kwlist), r"(?!\d)\w+"),
                 id="a profile that loads gives its layout and how its language names things"),
    pytest.param(SPEC, "broken", ProfileRefused("broken: missing `parts`"),
                 id="a profile that does not load is refused with why"),
])
def test_skeleton(given, when, then):
    assert given.skeleton(when) == then


NEAR = {"name": "near", "testing": {"files": ["test_*.py"], "declared": [{"function": "test_*"}], "beside": True},
        "parts": {"src/": {"role": "code", "tests": "unit"}},
        "tiers": {"unit": {}, "guard": {"folder": "architecture"}}, "fakes": {"folder": "fakes", "for": ["src"]}}


def test_the_skeleton_says_beside_the_test_files_and_the_folders_whose_tests_stay_below_the_tests_root():
    found = controller(FakeArchitectureFiles({"cli": NEAR})).skeleton("cli")
    assert (found.beside, found.test_files, found.kept) == (True, ("test_*.py",), (("architecture",), ("fakes",)))


def test_without_beside_the_skeleton_says_no_beside():
    found = SPEC.skeleton("cli")
    assert (found.beside, found.kept) == (False, ())


SPARSE = {"name": "sparse", "parts": {
    "api/": {"role": "a surface", "optional": True, "v1/": {"role": "its first version"}},
    "modules/<module>/": {"domain/": {"role": "rules"}, "config.py": {"role": "settings", "optional": True},
                          "settings/": {"defaults.py": {"role": "defaults", "optional": True}}}}}


def test_the_skeleton_says_which_entries_are_optional_parts_and_which_optional_part_each_lies_in():
    found = controller(FakeArchitectureFiles({"cli": SPARSE})).skeleton("cli")
    assert found.top_level == (Entry(("api",), True, False, True), Entry(("api", "v1"), True, True, False, ("api",)),
                               Entry(("modules",), True, True))
    assert found.repeating[0].entries == (
        Entry(("domain",), True, True), Entry(("config.py",), False, True, True),
        Entry(("settings",), True, True), Entry(("settings", "defaults.py"), False, True, True))
