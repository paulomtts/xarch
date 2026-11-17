"""Use case: the skeleton of a profile, which the layout and scaffold modules build and check against."""
import keyword

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller
from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.contract import Entry, ProfileRefused, Skeleton

LAYERED = {"name": "layered", "parts": {"src": {"path": "src", "role": "code"}}}
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
