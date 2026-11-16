"""Use case: the files a profile has `init` write, for an app folder."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller as spec_controller
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import ProfileRefused, ProjectFiles
from xarch.modules.spec.domain.published import ProjectFile

LAYERED = {"xarch": 2, "name": "layered", "parts": {"src": {"path": "src", "role": "code"}}}
GUARD = {"tests/architecture/test_rules.py": {"from": "guard.py"}}
PRESET = {"preset/tokens.css": "a {{app}}\n", "preset/fonts/f.woff": b"\xff\x00"}
TEXTS = {"guard.py": "check('{{app}}')\n", **PRESET}
INTO_APP = {"{{app}}/src/design/": {"from": "preset/"}}


def controller(files: dict | None) -> SpecController:
    document = LAYERED | ({"files": files} if files is not None else {})
    files_port = FakeArchitectureFiles({"cli": document}, texts=TEXTS)
    return spec_controller(files_port)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(GUARD, "shop", ProjectFiles((ProjectFile(("tests", "architecture", "test_rules.py"), "check('shop')\n"),)),
                 id="a file is its template with the app folder's name filled in"),
    pytest.param(None, "shop", ProjectFiles(()), id="a profile without files writes none"),
    pytest.param({"tests/rules.py": {"from": "guard.py", "pinned": True}}, "shop",
                 ProjectFiles((ProjectFile(("tests", "rules.py"), "check('shop')\n", pinned=True),)),
                 id="a pinned file says so"),
    pytest.param(INTO_APP, "shop",
                 ProjectFiles((ProjectFile(("shop", "src", "design", "fonts", "f.woff"), b"\xff\x00"),
                               ProjectFile(("shop", "src", "design", "tokens.css"), b"a {{app}}\n"))),
                 id="a folder entry is copied unchanged below a target inside the app, file by file"),
    pytest.param({"d/": {"from": "preset", "fill": True}}, "shop", ProfileRefused(
        "cli: files.d/: 'preset/fonts/f.woff' is not valid UTF-8 text: set `fill: false` to copy it unchanged"),
                 id="a filled preset that holds a binary file is refused naming the file"),
])
def test_files(given, when, then):
    assert controller(given).files("cli", when) == then


def test_the_presets_can_be_left_out_so_that_a_check_reads_only_the_single_files():
    files = controller(GUARD | INTO_APP).files("cli", "shop", presets=False)
    assert isinstance(files, ProjectFiles)
    assert [file.path for file in files.files] == [("tests", "architecture", "test_rules.py")]


def test_a_file_the_skeleton_writes_is_refused_with_the_profile_named():
    assert controller({"shop/__init__.py": {"from": "guard.py"}}).files("cli", "shop") == ProfileRefused(
        "cli: files.shop/__init__.py: 'shop/__init__.py' is the package file the skeleton writes")
