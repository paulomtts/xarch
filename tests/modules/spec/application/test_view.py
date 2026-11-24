"""Use case: a profile at a glance, its folder tree and its import table, for whoever approves it."""
from pathlib import Path

import pytest

from tests.modules.spec.application.builders import BASE, spec_controller
from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused, ProfileViewed, ViewProfile

APP = Path("/p/app")
TREE = "├── core/   the rules\n└── api/    the handlers"
IMPORTS = "| Part | May import |\n|---|---|\n| `core/` | nothing |\n| `api/` | `core/` |"


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(), ViewProfile(APP, "base"), ProfileViewed("base", "base", TREE, IMPORTS, True),
                 id="a profile is shown as its folder tree with roles and the table of what each part may import"),
    pytest.param(dict(), ViewProfile(APP, "nope"), ProfileRefused("unknown profile 'nope': use one of base"),
                 id="a profile that is not bundled is refused with the ones that are"),
    pytest.param(dict(files={"mine.yaml": {**BASE, "parts": {"core/": {"litmus": "q"}}}}), ViewProfile(APP, "mine.yaml"),
                 ProfileRefused("mine.yaml: parts.core: missing `role`"),
                 id="a profile that does not load is refused with its problems"),
    pytest.param(dict(), ViewProfile(APP, None), NoProfileChosen(("base",)),
                 id="with no profile named and none configured nothing is chosen, the known ones listed"),
])
def test_view(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.view(when) == then
