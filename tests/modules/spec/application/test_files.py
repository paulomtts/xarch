"""Use case: the files a profile has `init` write, for an app folder."""
import pytest

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import ProjectFile
from xarch.modules.spec.domain.errors import InvalidArchitecture
from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings

LAYERED = {"xarch": 1, "name": "layered", "layout": {"src": {}}, "parts": {"src": {"path": "src", "role": "code"}},
           "rules": {"src": ["src"]}}
GUARD = {"tests/architecture/test_rules.py": {"from": "guard.py"}}
TEXTS = {"guard.py": "check('{{app}}')\n"}


def controller(files: dict | None) -> SpecController:
    document = LAYERED | ({"files": files} if files is not None else {})
    architectures = ArchitectureService(FakeArchitectureFiles({"cli": document}, texts=TEXTS))
    return SpecController(SkeletonService(FakeSettings(None, None, None), architectures), architectures)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(GUARD, "shop", (ProjectFile(("tests", "architecture", "test_rules.py"), "check('shop')\n"),),
                 id="a file is its template with the app folder's name filled in"),
    pytest.param(None, "shop", (), id="a profile without files writes none"),
])
def test_files(given, when, then):
    assert controller(given).files("cli", when) == then


def test_a_file_in_the_app_folder_is_refused_with_the_profile_named():
    with pytest.raises(InvalidArchitecture) as caught:
        controller({"shop/guard.py": {"from": "guard.py"}}).files("cli", "shop")
    assert caught.value.problems == ("cli: files.shop/guard.py: lies inside the app folder 'shop'",)
