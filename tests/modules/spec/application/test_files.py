"""Use case: the files a profile has `init` write, for an app folder."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import ProjectFile
from xarch.modules.spec.domain.errors import InvalidArchitecture

LAYERED = {"xarch": 1, "name": "layered", "layout": {"src": {}}, "parts": {"src": {"path": "src", "role": "code"}},
           "rules": {"src": ["src"]}}
GUARD = {"tests/architecture/test_rules.py": {"from": "guard.py"}}
PRESET = {"preset/tokens.css": "a {{app}}\n", "preset/fonts/f.woff": b"\xff\x00"}
TEXTS = {"guard.py": "check('{{app}}')\n", **PRESET}
INTO_APP = {"{{app}}/src/design/": {"from": "preset/"}}


def controller(files: dict | None) -> SpecController:
    document = LAYERED | ({"files": files} if files is not None else {})
    architectures = ArchitectureService(FakeArchitectureFiles({"cli": document}, texts=TEXTS))
    return SpecController(SkeletonService(FakeSettings(None, None, None), architectures), architectures)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(GUARD, "shop", (ProjectFile(("tests", "architecture", "test_rules.py"), "check('shop')\n"),),
                 id="a file is its template with the app folder's name filled in"),
    pytest.param(None, "shop", (), id="a profile without files writes none"),
    pytest.param({"tests/rules.py": {"from": "guard.py", "pinned": True}}, "shop",
                 (ProjectFile(("tests", "rules.py"), "check('shop')\n", pinned=True),),
                 id="a pinned file says so"),
    pytest.param(INTO_APP, "shop",
                 (ProjectFile(("shop", "src", "design", "fonts", "f.woff"), b"\xff\x00", preset=True),
                  ProjectFile(("shop", "src", "design", "tokens.css"), b"a {{app}}\n", preset=True)),
                 id="a folder entry is copied unchanged below a target inside the app, file by file"),
])
def test_files(given, when, then):
    assert controller(given).files("cli", when) == then


def test_the_presets_can_be_left_out_so_that_a_check_reads_only_the_single_files():
    files = controller(GUARD | INTO_APP).files("cli", "shop", presets=False)
    assert [file.path for file in files] == [("tests", "architecture", "test_rules.py")]


def test_a_filled_preset_that_holds_a_binary_file_is_refused_naming_the_file():
    with pytest.raises(InvalidArchitecture) as caught:
        controller({"d/": {"from": "preset", "fill": True}}).files("cli", "shop")
    assert caught.value.problems == (
        "cli: files.d/: 'preset/fonts/f.woff' is not valid UTF-8 text: set `fill: false` to copy it unchanged",)


def test_a_file_the_skeleton_writes_is_refused_with_the_profile_named():
    with pytest.raises(InvalidArchitecture) as caught:
        controller({"shop/__init__.py": {"from": "guard.py"}}).files("cli", "shop")
    assert caught.value.problems == ("cli: files.shop/__init__.py: 'shop/__init__.py' is the package file the "
                                     "skeleton writes",)
